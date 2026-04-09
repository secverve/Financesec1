from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    stock_code: Mapped[str] = mapped_column(String(20), index=True)
    side: Mapped[str] = mapped_column(String(10))
    order_type: Mapped[str] = mapped_column(String(10))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[float] = mapped_column(Float, default=0)
    filled_quantity: Mapped[int] = mapped_column(Integer, default=0)
    average_filled_price: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(30), default="PENDING")
    device_id: Mapped[str] = mapped_column(String(128))
    ip_address: Mapped[str] = mapped_column(String(64))
    region: Mapped[str] = mapped_column(String(64), default="KR-SEOUL")
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    risk_level: Mapped[str] = mapped_column(String(20), default="NORMAL")
    decision: Mapped[str] = mapped_column(String(20), default="ALLOW")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    account = relationship("Account", back_populates="orders")
    executions = relationship("Execution", back_populates="order", cascade="all, delete-orphan")

    @property
    def remaining_quantity(self) -> int:
        return max(self.quantity - self.filled_quantity, 0)


class Execution(Base):
    __tablename__ = "executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    stock_code: Mapped[str] = mapped_column(String(20), index=True)
    executed_quantity: Mapped[int] = mapped_column(Integer)
    executed_price: Mapped[float] = mapped_column(Float)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="executions")
