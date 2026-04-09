from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    stock_name: Mapped[str] = mapped_column(String(120), index=True)
    market_type: Mapped[str] = mapped_column(String(20), default="KOSPI")
    is_monitored: Mapped[bool] = mapped_column(Boolean, default=False)


class MarketTick(Base):
    __tablename__ = "market_ticks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_code: Mapped[str] = mapped_column(String(20), index=True)
    current_price: Mapped[float] = mapped_column(Float)
    day_open: Mapped[float] = mapped_column(Float)
    day_high: Mapped[float] = mapped_column(Float)
    day_low: Mapped[float] = mapped_column(Float)
    volume: Mapped[int] = mapped_column(Integer)
    as_of: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
