from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.order import Execution, Order


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_order(self, order: Order) -> Order:
        self.db.add(order)
        self.db.flush()
        return order

    def create_execution(self, execution: Execution) -> Execution:
        self.db.add(execution)
        self.db.flush()
        return execution

    def list_user_orders(self, user_id: int):
        return list(self.db.scalars(select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())).all())

    def count_recent_orders(self, user_id: int, stock_code: Optional[str] = None) -> int:
        stmt = select(Order).where(Order.user_id == user_id)
        if stock_code:
            stmt = stmt.where(Order.stock_code == stock_code)
        return len(list(self.db.scalars(stmt).all()))

    def find_recent_by_ip(self, ip_address: str):
        return list(self.db.scalars(select(Order).where(Order.ip_address == ip_address).order_by(Order.created_at.desc())).all())
