from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.risk_repository import RiskRepository


class AdminService:
    def __init__(self, db: Session):
        self.repository = RiskRepository(db)

    def list_risk_events(self, risk_level: Optional[str] = None):
        return self.repository.list_events(risk_level=risk_level)
