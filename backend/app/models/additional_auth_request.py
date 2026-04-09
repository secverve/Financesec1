from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AdditionalAuthRequest(Base):
    __tablename__ = "additional_auth_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    code_hint: Mapped[str] = mapped_column(String(20), default="000000")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
