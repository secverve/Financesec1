from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="USER")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    behavior_profile = relationship("UserBehaviorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    account_number: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    cash_balance: Mapped[float] = mapped_column(Float, default=10000000)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="accounts")
    portfolios = relationship("Portfolio", back_populates="account", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="account")


class Portfolio(Base):
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    stock_code: Mapped[str] = mapped_column(String(20), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    avg_price: Mapped[float] = mapped_column(Float, default=0)

    account = relationship("Account", back_populates="portfolios")


class Watchlist(Base):
    __tablename__ = "watchlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    stock_code: Mapped[str] = mapped_column(String(20), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LoginHistory(Base):
    __tablename__ = "login_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    ip_address: Mapped[str] = mapped_column(String(64))
    region: Mapped[str] = mapped_column(String(64), default="KR-SEOUL")
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DeviceHistory(Base):
    __tablename__ = "device_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    device_id: Mapped[str] = mapped_column(String(128), index=True)
    device_name: Mapped[str] = mapped_column(String(128))
    last_ip_address: Mapped[str] = mapped_column(String(64))
    region: Mapped[str] = mapped_column(String(64), default="KR-SEOUL")
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserBehaviorProfile(Base):
    __tablename__ = "user_behavior_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    avg_order_amount: Mapped[float] = mapped_column(Float, default=1000000)
    avg_daily_order_count: Mapped[float] = mapped_column(Float, default=3)
    preferred_stocks: Mapped[str] = mapped_column(Text, default="005930,000660")
    usual_login_regions: Mapped[str] = mapped_column(Text, default="KR-SEOUL")
    usual_devices: Mapped[str] = mapped_column(Text, default="device-main")
    usual_trading_hours: Mapped[str] = mapped_column(String(64), default="09:00-15:20")
    last_active_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="behavior_profile")
