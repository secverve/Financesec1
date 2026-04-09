from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.schemas.admin import RiskEventResponse
from app.services.admin_service import AdminService

router = APIRouter()


@router.get("/risk-events", response_model=List[RiskEventResponse])
def list_risk_events(risk_level: Optional[str] = Query(default=None), _: object = Depends(require_admin), db: Session = Depends(get_db)):
    events = AdminService(db).list_risk_events(risk_level)
    return [RiskEventResponse.model_validate(event) for event in events]
