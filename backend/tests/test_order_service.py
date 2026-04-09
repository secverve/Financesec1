from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.market import MarketTick, Stock
from app.models.risk import RiskEvent
from app.models.user import Account, LoginHistory, User, UserBehaviorProfile
from app.services.admin_service import AdminService
from app.services.order_service import OrderService


def build_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


def seed_user_context(db):
    admin = User(email="admin@test.local", full_name="Admin", password_hash="hashed", role="ADMIN")
    user = User(email="user@test.local", full_name="Trader", password_hash="hashed", role="USER")
    db.add_all([admin, user])
    db.flush()

    account = Account(user_id=user.id, account_number="100-000-0001", cash_balance=50000000)
    db.add(account)
    db.flush()

    db.add(
        UserBehaviorProfile(
            user_id=user.id,
            avg_order_amount=1000000,
            avg_daily_order_count=3,
            preferred_stocks="005930,000660",
            usual_login_regions="KR-SEOUL",
            usual_devices="device-main",
        )
    )
    db.add_all(
        [
            Stock(stock_code="005930", stock_name="삼성전자", market_type="KOSPI", is_monitored=True),
            MarketTick(stock_code="005930", current_price=83500, day_open=82000, day_high=84000, day_low=81900, volume=1000000),
        ]
    )
    db.commit()
    return admin, user, account


def test_create_market_order_updates_portfolio_and_balance():
    db = build_session()
    _, user, account = seed_user_context(db)
    service = OrderService(db)

    payload = SimpleNamespace(
        account_id=account.id,
        stock_code="005930",
        side="BUY",
        order_type="MARKET",
        quantity=10,
        price=0,
        device_id="device-main",
        ip_address="10.0.0.1",
        region="KR-SEOUL",
    )

    order = service.create_order(user.id, payload)
    portfolio = service.users.get_portfolio(account.id, "005930")

    assert order.status == "EXECUTED"
    assert order.filled_quantity == 10
    assert order.remaining_quantity == 0
    assert portfolio.quantity == 10
    assert account.cash_balance == 50000000 - (83500 * 10)


def test_amend_open_limit_order_executes_after_price_change():
    db = build_session()
    _, user, account = seed_user_context(db)
    service = OrderService(db)

    create_payload = SimpleNamespace(
        account_id=account.id,
        stock_code="005930",
        side="BUY",
        order_type="LIMIT",
        quantity=20,
        price=80000,
        device_id="device-main",
        ip_address="10.0.0.1",
        region="KR-SEOUL",
    )
    order = service.create_order(user.id, create_payload)
    assert order.status == "ACCEPTED"

    amend_payload = SimpleNamespace(quantity=20, price=84000, order_type="LIMIT")
    amended = service.amend_order(user.id, order.id, amend_payload)

    assert amended.status == "EXECUTED"
    assert amended.filled_quantity == 20
    assert amended.average_filled_price == 83500


def test_admin_approves_held_order_and_executes_it():
    db = build_session()
    admin, user, account = seed_user_context(db)
    db.add_all(
        [
            LoginHistory(user_id=user.id, email=user.email, ip_address="10.0.0.2", region="KR-SEOUL", success=False),
            LoginHistory(user_id=user.id, email=user.email, ip_address="10.0.0.2", region="KR-SEOUL", success=False),
            LoginHistory(user_id=user.id, email=user.email, ip_address="10.0.0.2", region="KR-SEOUL", success=False),
        ]
    )
    db.commit()

    order_service = OrderService(db)
    payload = SimpleNamespace(
        account_id=account.id,
        stock_code="005930",
        side="BUY",
        order_type="LIMIT",
        quantity=40,
        price=83500,
        device_id="device-new",
        ip_address="10.0.0.2",
        region="KR-SEOUL",
    )
    held_order = order_service.create_order(user.id, payload)
    assert held_order.status == "HELD"

    risk_event = db.query(RiskEvent).filter(RiskEvent.order_id == held_order.id).first()
    event, approved_order = AdminService(db).handle_risk_event_action(admin.id, risk_event.id, "APPROVE")

    assert event.status == "RESOLVED"
    assert approved_order.status == "EXECUTED"
    assert approved_order.filled_quantity == 40
