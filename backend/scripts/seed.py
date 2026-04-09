from app.core.config import settings
from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.additional_auth_request import AdditionalAuthRequest
from app.models.blacklists import BlacklistedAccount, BlacklistedStock
from app.models.market import MarketTick, Stock
from app.models.order import Execution, Order
from app.models.risk import AdminAction, RiskEvent, RuleHit
from app.models.user import Account, DeviceHistory, LoginHistory, Portfolio, User, UserBehaviorProfile


Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return

        admin = User(
            email=settings.default_admin_email,
            full_name="Admin Analyst",
            password_hash=get_password_hash(settings.default_admin_password),
            role="ADMIN",
        )
        user = User(
            email=settings.default_user_email,
            full_name="Trader Kim",
            password_hash=get_password_hash(settings.default_user_password),
            role="USER",
        )
        db.add_all([admin, user])
        db.flush()

        user_account = Account(user_id=user.id, account_number="100-000-0001", cash_balance=41800000)
        admin_account = Account(user_id=admin.id, account_number="999-000-0001", cash_balance=0)
        db.add_all([user_account, admin_account])
        db.flush()

        db.add_all(
            [
                UserBehaviorProfile(
                    user_id=user.id,
                    avg_order_amount=1200000,
                    avg_daily_order_count=4,
                    preferred_stocks="005930,000660",
                    usual_login_regions="KR-SEOUL",
                    usual_devices="device-main",
                ),
                UserBehaviorProfile(
                    user_id=admin.id,
                    avg_order_amount=0,
                    avg_daily_order_count=0,
                    preferred_stocks="",
                    usual_login_regions="KR-SEOUL",
                    usual_devices="admin-console",
                ),
            ]
        )
        db.add_all(
            [
                DeviceHistory(user_id=user.id, device_id="device-main", device_name="iPhone 17", last_ip_address="1.1.1.1", region="KR-SEOUL"),
                LoginHistory(user_id=user.id, email=user.email, ip_address="1.1.1.1", region="KR-SEOUL", success=True),
                LoginHistory(user_id=user.id, email=user.email, ip_address="203.0.113.10", region="OVERSEAS-SG", success=False),
                LoginHistory(user_id=user.id, email=user.email, ip_address="203.0.113.10", region="OVERSEAS-SG", success=False),
                LoginHistory(user_id=user.id, email=user.email, ip_address="203.0.113.10", region="OVERSEAS-SG", success=False),
            ]
        )

        db.add_all(
            [
                Stock(stock_code="005930", stock_name="삼성전자", market_type="KOSPI", is_monitored=True),
                Stock(stock_code="000660", stock_name="SK하이닉스", market_type="KOSPI", is_monitored=False),
                Stock(stock_code="035420", stock_name="NAVER", market_type="KOSPI", is_monitored=False),
            ]
        )
        db.add_all(
            [
                MarketTick(stock_code="005930", current_price=83500, day_open=82000, day_high=84000, day_low=81900, volume=12403450),
                MarketTick(stock_code="000660", current_price=201000, day_open=197500, day_high=202000, day_low=196800, volume=3120450),
                MarketTick(stock_code="035420", current_price=224500, day_open=220000, day_high=226000, day_low=219500, volume=1102300),
            ]
        )
        db.flush()

        db.add_all(
            [
                Portfolio(account_id=user_account.id, stock_code="005930", quantity=80, avg_price=79200),
                Portfolio(account_id=user_account.id, stock_code="000660", quantity=12, avg_price=189000),
            ]
        )

        executed_order = Order(
            user_id=user.id,
            account_id=user_account.id,
            stock_code="000660",
            side="BUY",
            order_type="MARKET",
            quantity=12,
            price=201000,
            filled_quantity=12,
            average_filled_price=201000,
            status="EXECUTED",
            device_id="device-main",
            ip_address="1.1.1.1",
            region="KR-SEOUL",
            risk_score=0,
            risk_level="NORMAL",
            decision="ALLOW",
        )
        db.add(executed_order)
        db.flush()
        db.add(Execution(order_id=executed_order.id, stock_code="000660", executed_quantity=12, executed_price=201000))

        suspicious_order = Order(
            user_id=user.id,
            account_id=user_account.id,
            stock_code="005930",
            side="BUY",
            order_type="LIMIT",
            quantity=120,
            price=83500,
            status="HELD",
            device_id="device-new",
            ip_address="203.0.113.10",
            region="OVERSEAS-SG",
            risk_score=110,
            risk_level="CRITICAL",
            decision="BLOCK",
        )
        db.add(suspicious_order)
        db.flush()
        db.add(AdditionalAuthRequest(order_id=suspicious_order.id, user_id=user.id, status="PENDING", code_hint=settings.additional_auth_code))

        risk_event = RiskEvent(
            order_id=suspicious_order.id,
            user_id=user.id,
            stock_code="005930",
            stock_name="삼성전자",
            risk_score=110,
            risk_level="CRITICAL",
            decision="BLOCK",
            reason_summary="신규 디바이스 고액 주문; 해외 로그인 직후 주문; 로그인 실패 반복 후 주문",
            status="OPEN",
        )
        db.add(risk_event)
        db.flush()
        db.add_all(
            [
                RuleHit(risk_event_id=risk_event.id, rule_code="R001", rule_name="신규 디바이스 고액 주문", score=35, severity="MEDIUM", reason="신규 디바이스에서 최근 평균 주문금액 대비 8.3배 높은 주문이 접수되었습니다."),
                RuleHit(risk_event_id=risk_event.id, rule_code="R002", rule_name="해외 IP 로그인 후 즉시 주문", score=45, severity="HIGH", reason="해외 IP 또는 비정상 지역 로그인 직후 주문이 발생했습니다."),
                RuleHit(risk_event_id=risk_event.id, rule_code="R003", rule_name="로그인 실패 반복 후 주문", score=30, severity="MEDIUM", reason="최근 로그인 실패 이력 3건 이후 주문이 접수되었습니다."),
                RuleHit(risk_event_id=risk_event.id, rule_code="R006", rule_name="동일 IP 다계정 유사 주문", score=50, severity="HIGH", reason="동일 IP에서 여러 계정의 유사 주문이 발생했습니다."),
            ]
        )

        resolved_event = RiskEvent(
            order_id=executed_order.id,
            user_id=user.id,
            stock_code="000660",
            stock_name="SK하이닉스",
            risk_score=40,
            risk_level="CAUTION",
            decision="ALLOW",
            reason_summary="평균 주문금액 대비 5배 높은 주문입니다.",
            status="RESOLVED",
        )
        db.add(resolved_event)
        db.flush()
        db.add(
            AdminAction(
                risk_event_id=resolved_event.id,
                admin_user_id=admin.id,
                action_type="APPROVE",
                target_user_id=user.id,
                detail="seed admin approval history",
            )
        )

        db.add(BlacklistedStock(stock_code="091990", reason="사내 감시종목"))
        db.add(BlacklistedAccount(user_id=9999, reason="테스트 블랙리스트"))

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
