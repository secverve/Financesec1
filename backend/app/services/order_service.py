from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppException
from app.fds.engine import RiskEngine
from app.models.additional_auth_request import AdditionalAuthRequest
from app.models.order import Execution, Order
from app.models.risk import RiskEvent, RuleHit
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
        account = self.users.get_primary_account(user_id)
        if not account or account.id != payload.account_id:
            raise AppException("ORDER_ACCOUNT_INVALID", "Invalid account")

        stock = self.markets.get_stock(payload.stock_code)
        tick = self.markets.get_latest_tick(payload.stock_code)
        profile = self.users.get_behavior_profile(user_id)
        if not stock or not tick or not profile:
            raise AppException("ORDER_REFERENCE_NOT_FOUND", "Order reference data not found")

        known_device = self.users.get_known_device(user_id, payload.device_id)
        user = self.users.get_by_id(user_id)
        recent_fails = len(self.users.get_recent_login_failures(user.email if user else ""))
        same_stock_orders = self.orders.count_recent_orders(user_id, payload.stock_code)
        same_ip_orders = self.orders.find_recent_by_ip(payload.ip_address)
        same_ip_users = len({order.user_id for order in same_ip_orders if order.user_id != user_id}) + (1 if same_ip_orders else 0)
        order_price = tick.current_price if payload.order_type == "MARKET" else payload.price
        order_amount = order_price * payload.quantity

        context = {
            "is_new_device": known_device is None,
            "order_amount": order_amount,
            "avg_order_amount": profile.avg_order_amount,
            "recent_login_region": payload.region,
            "login_failures": recent_fails,
            "preferred_stocks": profile.preferred_stocks.split(","),
            "stock_code": payload.stock_code,
            "same_stock_order_count": same_stock_orders,
            "same_ip_order_users": same_ip_users,
        }
        result = self.engine.evaluate(context)

        status = "ACCEPTED"
        if result["decision"] == "HOLD":
            status = "HELD"
        elif result["decision"] == "BLOCK":
            status = "BLOCKED"

        order = self.orders.create_order(
            Order(
                user_id=user_id,
                account_id=payload.account_id,
                stock_code=payload.stock_code,
                side=payload.side,
                order_type=payload.order_type,
                quantity=payload.quantity,
                price=order_price,
                status=status,
                device_id=payload.device_id,
                ip_address=payload.ip_address,
                region=payload.region,
                risk_score=result["score"],
                risk_level=result["risk_level"],
                decision=result["decision"],
            )
        )

        reason_summary = "; ".join(hit["reason"] for hit in result["hits"]) or "정상 주문"
        if result["hits"]:
            event = self.risks.create_event(
                RiskEvent(
                    order_id=order.id,
                    user_id=user_id,
                    stock_code=payload.stock_code,
                    stock_name=stock.stock_name,
                    risk_score=result["score"],
                    risk_level=result["risk_level"],
                    decision=result["decision"],
                    reason_summary=reason_summary,
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

        if status == "ACCEPTED":
            self.orders.create_execution(
                Execution(
                    order_id=order.id,
                    stock_code=payload.stock_code,
                    executed_quantity=payload.quantity,
                    executed_price=order_price,
                )
            )
            order.status = "EXECUTED"
            account.cash_balance -= order_amount if payload.side == "BUY" else 0
        elif status == "HELD":
            self.db.add(AdditionalAuthRequest(order_id=order.id, user_id=user_id, code_hint=settings.additional_auth_code))

        self.audit.log(user_id, "ORDER_CREATED", "order", str(order.id), f"{payload.side} {payload.stock_code} x {payload.quantity} status={order.status}")
        self.db.commit()
        self.db.refresh(order)
        return order
