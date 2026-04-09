from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import RiskEventActionRequest, RiskEventActionResponse, RiskEventResponse, UserLockResponse
from app.services.admin_service import AdminService

router = APIRouter()


@router.get("/risk-events", response_model=List[RiskEventResponse])
def list_risk_events(risk_level: Optional[str] = Query(default=None), _: object = Depends(require_admin), db: Session = Depends(get_db)):
    events = AdminService(db).list_risk_events(risk_level)
    return [RiskEventResponse.model_validate(event) for event in events]


@router.post("/risk-events/{risk_event_id}/actions", response_model=RiskEventActionResponse)
def handle_risk_event_action(risk_event_id: int, payload: RiskEventActionRequest, admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    event, order = AdminService(db).handle_risk_event_action(admin_user.id, risk_event_id, payload.action_type)
    return RiskEventActionResponse(
        risk_event_id=event.id,
        action_type=payload.action_type,
        risk_event_status=event.status,
        order_status=order.status if order else None,
    )


@router.post("/users/{user_id}/lock", response_model=UserLockResponse)
def lock_user(user_id: int, admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = AdminService(db).set_user_lock(admin_user.id, user_id, True)
    return UserLockResponse(user_id=user.id, is_locked=user.is_locked)


@router.post("/users/{user_id}/unlock", response_model=UserLockResponse)
def unlock_user(user_id: int, admin_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = AdminService(db).set_user_lock(admin_user.id, user_id, False)
    return UserLockResponse(user_id=user.id, is_locked=user.is_locked)
