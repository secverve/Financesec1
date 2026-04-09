from fastapi import status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppException
from app.fds.engine import RiskEngine
from app.models.additional_auth_request import AdditionalAuthRequest
from app.models.order import Execution, Order
from app.models.risk import RiskEvent, RuleHit
from app.models.user import Portfolio
from app.repositories.market_repository import MarketRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.risk_repository import RiskRepository
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService


class OrderService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.markets = MarketRepository(db)
        self.orders = OrderRepository(db)
        self.risks = RiskRepository(db)
        self.audit = AuditService(db)
        self.engine = RiskEngine()

    def create_order(self, user_id: int, payload) -> Order:
        account = self._validate_account(user_id, payload.account_id)
        stock, tick, profile = self._get_order_reference_data(user_id, payload.stock_code)
        order_price = self._resolve_order_price(payload.order_type, payload.price, tick.current_price)
        order_amount = order_price * payload.quantity

        if payload.side == "BUY" and account.cash_balance < order_amount:
            raise AppException("ORDER_INSUFFICIENT_CASH", "Insufficient cash balance")
        if payload.side == "SELL":
            self._validate_sell_capacity(account.id, payload.stock_code, payload.quantity)

        result = self._evaluate_risk(user_id, payload, order_amount, profile.avg_order_amount, profile.preferred_stocks)
        order = self.orders.create_order(
            Order(
                user_id=user_id,
                account_id=payload.account_id,
                stock_code=payload.stock_code,
                side=payload.side,
                order_type=payload.order_type,
                quantity=payload.quantity,
                price=order_price,
                status=self._initial_status(result["decision"]),
                device_id=payload.device_id,
                ip_address=payload.ip_address,
                region=payload.region,
                risk_score=result["score"],
                risk_level=result["risk_level"],
                decision=result["decision"],
            )
        )

        if result["hits"]:
            self._create_risk_event(order, stock.stock_name, result)

        if order.status == "HELD":
            self._ensure_additional_auth(order.id, user_id)
        elif order.status == "ACCEPTED":
            self._attempt_execution(order)

        self.audit.log(user_id, "ORDER_CREATED", "order", str(order.id), f"{payload.side} {payload.stock_code} x {payload.quantity} status={order.status}")
        self.db.commit()
        self.db.refresh(order)
        return order

    def amend_order(self, user_id: int, order_id: int, payload) -> Order:
        order = self._get_user_order(user_id, order_id)
        if order.status not in {"ACCEPTED", "PARTIALLY_FILLED", "HELD"}:
            raise AppException("ORDER_AMEND_INVALID", "Order cannot be amended in current status")
        if payload.quantity < order.filled_quantity:
            raise AppException("ORDER_AMEND_INVALID", "Quantity cannot be lower than filled quantity")

        account = self._validate_account(user_id, order.account_id)
        tick = self._get_market_tick(order.stock_code)
        next_order_type = payload.order_type or order.order_type
        next_price = self._resolve_order_price(next_order_type, payload.price if payload.price is not None else order.price, tick.current_price)
        next_total_amount = next_price * payload.quantity

        if order.side == "BUY":
            spent_amount = order.average_filled_price * order.filled_quantity
            if account.cash_balance + spent_amount < next_total_amount:
                raise AppException("ORDER_INSUFFICIENT_CASH", "Insufficient cash balance for amendment")
        else:
            self._validate_sell_capacity(account.id, order.stock_code, payload.quantity, order.filled_quantity)

        order.quantity = payload.quantity
        order.order_type = next_order_type
        order.price = next_price

        if order.status in {"ACCEPTED", "PARTIALLY_FILLED"}:
            self._attempt_execution(order)

        self.audit.log(user_id, "ORDER_AMENDED", "order", str(order.id), f"quantity={order.quantity} price={order.price} type={order.order_type}")
        self.db.commit()
        self.db.refresh(order)
        return order

    def cancel_order(self, user_id: int, order_id: int) -> Order:
        order = self._get_user_order(user_id, order_id)
        if order.status not in {"ACCEPTED", "PARTIALLY_FILLED", "HELD"}:
            raise AppException("ORDER_CANCEL_INVALID", "Order cannot be cancelled in current status")

        order.status = "CANCELLED"
        self.audit.log(user_id, "ORDER_CANCELLED", "order", str(order.id), f"remaining_quantity={order.remaining_quantity}")
        self.db.commit()
        self.db.refresh(order)
        return order

    def list_orders(self, user_id: int):
        return self.orders.list_user_orders(user_id)

    def verify_additional_auth(self, user_id: int, order_id: int, code: str) -> dict:
        order = self._get_user_order(user_id, order_id)
        pending_auth = self.orders.get_pending_additional_auth(order_id)
        if not pending_auth:
            raise AppException("AUTH_REQUEST_NOT_FOUND", "Pending additional auth request not found", status.HTTP_404_NOT_FOUND)
        if code != pending_auth.code_hint:
            raise AppException("AUTH_CODE_INVALID", "Invalid additional auth code", status.HTTP_400_BAD_REQUEST)

        pending_auth.status = "VERIFIED"
        order.decision = "ALLOW"
        if order.status == "HELD":
            order.status = "ACCEPTED"
            self._attempt_execution(order)

        event = self.risks.get_event_by_order_id(order.id)
        if event:
            event.status = "AUTH_VERIFIED"
            event.decision = "ALLOW_AFTER_AUTH"

        self.audit.log(user_id, "ADDITIONAL_AUTH_VERIFIED", "order", str(order.id), "additional auth verified")
        self.db.commit()
        self.db.refresh(order)
        return {"order_id": order.id, "order_status": order.status, "auth_status": pending_auth.status}

    def approve_held_order(self, order: Order) -> Order:
        if order.status not in {"HELD", "BLOCKED"}:
            raise AppException("ORDER_APPROVE_INVALID", "Order is not in a reviewable state")
        order.decision = "ALLOW"
        order.status = "ACCEPTED"
        self._attempt_execution(order)
        self.db.flush()
        return order

    def block_order(self, order: Order) -> Order:
        order.status = "BLOCKED"
        order.decision = "BLOCK"
        self.db.flush()
        return order

    def require_additional_auth(self, order: Order) -> Order:
        order.status = "HELD"
        self._ensure_additional_auth(order.id, order.user_id)
        self.db.flush()
        return order

    def _validate_account(self, user_id: int, account_id: int):
        account = self.users.get_account_by_id(account_id)
        if not account or account.user_id != user_id:
            raise AppException("ORDER_ACCOUNT_INVALID", "Invalid account", status.HTTP_404_NOT_FOUND)
        return account

    def _get_order_reference_data(self, user_id: int, stock_code: str):
        stock = self.markets.get_stock(stock_code)
        tick = self.markets.get_latest_tick(stock_code)
        profile = self.users.get_behavior_profile(user_id)
        if not stock or not tick or not profile:
            raise AppException("ORDER_REFERENCE_NOT_FOUND", "Order reference data not found", status.HTTP_404_NOT_FOUND)
        return stock, tick, profile

    def _get_market_tick(self, stock_code: str):
        tick = self.markets.get_latest_tick(stock_code)
        if not tick:
            raise AppException("ORDER_MARKET_TICK_NOT_FOUND", "Market tick not found", status.HTTP_404_NOT_FOUND)
        return tick

    def _get_user_order(self, user_id: int, order_id: int) -> Order:
        order = self.orders.get_user_order(user_id, order_id)
        if not order:
            raise AppException("ORDER_NOT_FOUND", "Order not found", status.HTTP_404_NOT_FOUND)
        return order

    def _evaluate_risk(self, user_id: int, payload, order_amount: float, avg_order_amount: float, preferred_stocks: str):
        known_device = self.users.get_known_device(user_id, payload.device_id)
        user = self.users.get_by_id(user_id)
        recent_fails = len(self.users.get_recent_login_failures(user.email if user else ""))
        same_stock_orders = self.orders.count_recent_orders(user_id, payload.stock_code)
        same_ip_orders = self.orders.find_recent_by_ip(payload.ip_address)
        same_ip_users = len({order.user_id for order in same_ip_orders if order.user_id != user_id}) + (1 if same_ip_orders else 0)
        context = {
            "is_new_device": known_device is None,
            "order_amount": order_amount,
            "avg_order_amount": avg_order_amount,
            "recent_login_region": payload.region,
            "login_failures": recent_fails,
            "preferred_stocks": preferred_stocks.split(","),
            "stock_code": payload.stock_code,
            "same_stock_order_count": same_stock_orders,
            "same_ip_order_users": same_ip_users,
        }
        return self.engine.evaluate(context)

    def _initial_status(self, decision: str) -> str:
        if decision == "HOLD":
            return "HELD"
        if decision == "BLOCK":
            return "BLOCKED"
        return "ACCEPTED"

    def _create_risk_event(self, order: Order, stock_name: str, result: dict) -> None:
        event = self.risks.create_event(
            RiskEvent(
                order_id=order.id,
                user_id=order.user_id,
                stock_code=order.stock_code,
                stock_name=stock_name,
                risk_score=result["score"],
                risk_level=result["risk_level"],
                decision=result["decision"],
                reason_summary="; ".join(hit["reason"] for hit in result["hits"]),
            )
        )
        for hit in result["hits"]:
            self.risks.create_rule_hit(
                RuleHit(
                    risk_event_id=event.id,
                    rule_code=hit["rule_code"],
                    rule_name=hit["rule_name"],
                    score=hit["score"],
                    severity=hit["severity"],
                    reason=hit["reason"],
                )
            )

    def _resolve_order_price(self, order_type: str, request_price: float, market_price: float) -> float:
        return market_price if order_type == "MARKET" else request_price

    def _attempt_execution(self, order: Order) -> None:
        if order.remaining_quantity <= 0:
            order.status = "EXECUTED"
            return

        tick = self._get_market_tick(order.stock_code)
        if not self._is_marketable(order, tick.current_price):
            if order.filled_quantity > 0:
                order.status = "PARTIALLY_FILLED"
            else:
                order.status = "ACCEPTED"
            self.db.flush()
            return

        fill_quantity = self._determine_fill_quantity(order.remaining_quantity)
        self._apply_execution(order, fill_quantity, tick.current_price)

    def _is_marketable(self, order: Order, market_price: float) -> bool:
        if order.order_type == "MARKET":
            return True
        if order.side == "BUY":
            return order.price >= market_price
        return order.price <= market_price

    def _determine_fill_quantity(self, remaining_quantity: int) -> int:
        if remaining_quantity >= 100:
            return max(1, remaining_quantity // 2)
        return remaining_quantity

    def _apply_execution(self, order: Order, executed_quantity: int, executed_price: float) -> None:
        account = self.users.get_account_by_id(order.account_id)
        if not account:
            raise AppException("ORDER_ACCOUNT_INVALID", "Invalid account", status.HTTP_404_NOT_FOUND)
        execution_amount = executed_quantity * executed_price

        if order.side == "BUY":
            if account.cash_balance < execution_amount:
                raise AppException("ORDER_INSUFFICIENT_CASH", "Insufficient cash balance")
            account.cash_balance -= execution_amount
            self._apply_portfolio_change(order.account_id, order.stock_code, executed_quantity, executed_price, "BUY")
        else:
            self._apply_portfolio_change(order.account_id, order.stock_code, executed_quantity, executed_price, "SELL")
            account.cash_balance += execution_amount

        self.orders.create_execution(
            Execution(
                order_id=order.id,
                stock_code=order.stock_code,
                executed_quantity=executed_quantity,
                executed_price=executed_price,
            )
        )

        total_filled_amount = (order.average_filled_price * order.filled_quantity) + execution_amount
        order.filled_quantity += executed_quantity
        order.average_filled_price = total_filled_amount / order.filled_quantity if order.filled_quantity else 0
        order.status = "EXECUTED" if order.remaining_quantity == 0 else "PARTIALLY_FILLED"
        self.db.flush()

    def _apply_portfolio_change(self, account_id: int, stock_code: str, quantity: int, executed_price: float, side: str) -> None:
        portfolio = self.users.get_portfolio(account_id, stock_code)
        if side == "BUY":
            if not portfolio:
                portfolio = self.users.create_portfolio(Portfolio(account_id=account_id, stock_code=stock_code, quantity=0, avg_price=0))
            total_cost = (portfolio.avg_price * portfolio.quantity) + (executed_price * quantity)
            portfolio.quantity += quantity
            portfolio.avg_price = total_cost / portfolio.quantity if portfolio.quantity else 0
            return

        if not portfolio or portfolio.quantity < quantity:
            raise AppException("ORDER_INSUFFICIENT_HOLDINGS", "Insufficient holdings to sell")
        portfolio.quantity -= quantity
        if portfolio.quantity == 0:
            portfolio.avg_price = 0

    def _validate_sell_capacity(self, account_id: int, stock_code: str, requested_total_quantity: int, already_filled_quantity: int = 0) -> None:
        portfolio = self.users.get_portfolio(account_id, stock_code)
        available_quantity = (portfolio.quantity if portfolio else 0) + already_filled_quantity
        if available_quantity < requested_total_quantity:
            raise AppException("ORDER_INSUFFICIENT_HOLDINGS", "Insufficient holdings to sell")

    def _ensure_additional_auth(self, order_id: int, user_id: int) -> None:
        pending = self.orders.get_pending_additional_auth(order_id)
        if pending:
            return
        self.orders.create_additional_auth(
            AdditionalAuthRequest(order_id=order_id, user_id=user_id, code_hint=settings.additional_auth_code)
        )
