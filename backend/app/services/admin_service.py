from fastapi import status
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.risk import AdminAction
from app.repositories.order_repository import OrderRepository
from app.repositories.risk_repository import RiskRepository
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService
from app.services.order_service import OrderService


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = RiskRepository(db)
        self.orders = OrderRepository(db)
        self.users = UserRepository(db)
        self.order_service = OrderService(db)
        self.audit = AuditService(db)

    def list_risk_events(self, risk_level=None):
        return self.repository.list_events(risk_level=risk_level)

    def handle_risk_event_action(self, admin_user_id: int, risk_event_id: int, action_type: str):
        event = self.repository.get_event(risk_event_id)
        if not event:
            raise AppException("RISK_EVENT_NOT_FOUND", "Risk event not found", status.HTTP_404_NOT_FOUND)

        order = self.orders.get_by_id(event.order_id) if event.order_id else None
        if action_type == "APPROVE" and order:
            order = self.order_service.approve_held_order(order)
            event.status = "RESOLVED"
            event.decision = "APPROVE"
        elif action_type == "BLOCK" and order:
            order = self.order_service.block_order(order)
            event.status = "RESOLVED"
            event.decision = "BLOCK"
        elif action_type == "REQUIRE_AUTH" and order:
            order = self.order_service.require_additional_auth(order)
            event.status = "PENDING_AUTH"
            event.decision = "REQUIRE_AUTH"
        else:
            raise AppException("RISK_ACTION_INVALID", "Invalid risk event action")

        self.repository.create_admin_action(
            AdminAction(
                risk_event_id=event.id,
                admin_user_id=admin_user_id,
                action_type=action_type,
                target_user_id=event.user_id,
                detail="admin reviewed risk event",
            )
        )
        self.audit.log(admin_user_id, "ADMIN_RISK_ACTION", "risk_event", str(event.id), action_type)
        self.db.commit()
        self.db.refresh(event)
        if order:
            self.db.refresh(order)
        return event, order

    def set_user_lock(self, admin_user_id: int, user_id: int, is_locked: bool):
        user = self.users.set_user_lock(user_id, is_locked)
        if not user:
            raise AppException("USER_NOT_FOUND", "User not found", status.HTTP_404_NOT_FOUND)

        self.repository.create_admin_action(
            AdminAction(
                risk_event_id=None,
                admin_user_id=admin_user_id,
                action_type="LOCK_USER" if is_locked else "UNLOCK_USER",
                target_user_id=user_id,
                detail="account lock state changed",
            )
        )
        self.audit.log(admin_user_id, "ADMIN_USER_LOCK", "user", str(user_id), "LOCK" if is_locked else "UNLOCK")
        self.db.commit()
        self.db.refresh(user)
        return user
