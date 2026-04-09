from collections import Counter

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.additional_auth_request import AdditionalAuthRequest
from app.models.market import MarketTick, Stock
from app.models.order import Order
from app.models.risk import RiskEvent, RuleHit
from app.models.user import Portfolio, User
from app.repositories.user_repository import UserRepository


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def get_user_dashboard(self, user_id: int) -> dict:
        account = self.users.get_primary_account(user_id)
        if not account:
            raise AppException("ACCOUNT_NOT_FOUND", "Account not found")

        positions = []
        portfolio_value = 0
        rows = self.db.execute(
            select(Portfolio, Stock.stock_name, MarketTick.current_price)
            .join(Stock, Stock.stock_code == Portfolio.stock_code)
            .join(MarketTick, MarketTick.stock_code == Portfolio.stock_code)
            .where(Portfolio.account_id == account.id)
        ).all()
        for portfolio, stock_name, current_price in rows:
            evaluation_amount = current_price * portfolio.quantity
            profit_loss = (current_price - portfolio.avg_price) * portfolio.quantity
            portfolio_value += evaluation_amount
            positions.append(
                {
                    "stock_code": portfolio.stock_code,
                    "stock_name": stock_name,
                    "quantity": portfolio.quantity,
                    "avg_price": portfolio.avg_price,
                    "current_price": current_price,
                    "evaluation_amount": evaluation_amount,
                    "profit_loss": profit_loss,
                }
            )

        stocks = self.db.execute(
            select(Stock, MarketTick)
            .join(MarketTick, MarketTick.stock_code == Stock.stock_code)
            .order_by(Stock.stock_code)
        ).all()
        watch_stocks = [
            {
                "stock_code": stock.stock_code,
                "stock_name": stock.stock_name,
                "market_type": stock.market_type,
                "current_price": tick.current_price,
                "volume": tick.volume,
                "is_monitored": stock.is_monitored,
            }
            for stock, tick in stocks
        ]

        recent_orders = self.db.scalars(
            select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc()).limit(20)
        ).all()
        pending_auth = self.db.scalars(
            select(AdditionalAuthRequest).where(
                AdditionalAuthRequest.user_id == user_id,
                AdditionalAuthRequest.status == "PENDING",
            )
        ).all()

        return {
            "user_id": user_id,
            "account_id": account.id,
            "account_number": account.account_number,
            "cash_balance": account.cash_balance,
            "portfolio_value": portfolio_value,
            "total_evaluation_amount": account.cash_balance + portfolio_value,
            "positions": positions,
            "watch_stocks": watch_stocks,
            "recent_orders": [
                {
                    "id": order.id,
                    "stock_code": order.stock_code,
                    "side": order.side,
                    "order_type": order.order_type,
                    "quantity": order.quantity,
                    "filled_quantity": order.filled_quantity,
                    "remaining_quantity": order.remaining_quantity,
                    "price": order.price,
                    "status": order.status,
                    "risk_level": order.risk_level,
                    "created_at": order.created_at.isoformat(),
                }
                for order in recent_orders
            ],
            "pending_auth": [
                {"order_id": item.order_id, "status": item.status, "code_hint": item.code_hint}
                for item in pending_auth
            ],
        }

    def get_admin_summary(self) -> dict:
        total_events = self.db.scalar(select(func.count(RiskEvent.id))) or 0
        open_events = self.db.scalar(select(func.count(RiskEvent.id)).where(RiskEvent.status.in_(["OPEN", "PENDING_AUTH"]))) or 0
        critical_events = self.db.scalar(select(func.count(RiskEvent.id)).where(RiskEvent.risk_level == "CRITICAL")) or 0
        suspicious_events = self.db.scalar(select(func.count(RiskEvent.id)).where(RiskEvent.risk_level == "SUSPICIOUS")) or 0
        held_orders = self.db.scalar(select(func.count(Order.id)).where(Order.status == "HELD")) or 0
        blocked_orders = self.db.scalar(select(func.count(Order.id)).where(Order.status == "BLOCKED")) or 0
        same_ip_multi_account_events = self.db.scalar(select(func.count(RuleHit.id)).where(RuleHit.rule_code == "R006")) or 0

        level_rows = self.db.execute(
            select(RiskEvent.risk_level, func.count(RiskEvent.id)).group_by(RiskEvent.risk_level)
        ).all()
        risk_levels = [{"risk_level": level, "count": count} for level, count in level_rows]

        top_rows = self.db.execute(
            select(User.email, func.count(RiskEvent.id).label("event_count"))
            .join(RiskEvent, RiskEvent.user_id == User.id)
            .group_by(User.email)
            .order_by(func.count(RiskEvent.id).desc())
            .limit(5)
        ).all()
        top_risk_users = [{"email": email, "event_count": event_count} for email, event_count in top_rows]

        return {
            "total_events": total_events,
            "open_events": open_events,
            "critical_events": critical_events,
            "suspicious_events": suspicious_events,
            "held_orders": held_orders,
            "blocked_orders": blocked_orders,
            "same_ip_multi_account_events": same_ip_multi_account_events,
            "risk_levels": risk_levels,
            "top_risk_users": top_risk_users,
        }
