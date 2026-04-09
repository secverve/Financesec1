from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class RiskEvent(Base):
    __tablename__ = "risk_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orders.id"), nullable=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    stock_code: Mapped[str] = mapped_column(String(20), index=True)
    stock_name: Mapped[str] = mapped_column(String(120))
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(20))
    decision: Mapped[str] = mapped_column(String(20))
    reason_summary: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="OPEN")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RuleHit(Base):
    __tablename__ = "rule_hits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    risk_event_id: Mapped[int] = mapped_column(ForeignKey("risk_events.id"), index=True)
    rule_code: Mapped[str] = mapped_column(String(40), index=True)
    rule_name: Mapped[str] = mapped_column(String(120))
    score: Mapped[int] = mapped_column(Integer)
    severity: Mapped[str] = mapped_column(String(20))
    reason: Mapped[str] = mapped_column(Text)


class AdminAction(Base):
    __tablename__ = "admin_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    risk_event_id: Mapped[Optional[int]] = mapped_column(ForeignKey("risk_events.id"), nullable=True, index=True)
    admin_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    action_type: Mapped[str] = mapped_column(String(40))
    target_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    detail: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
