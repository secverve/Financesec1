from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.risk import AdminAction, RiskEvent, RuleHit


class RiskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_event(self, event: RiskEvent) -> RiskEvent:
        self.db.add(event)
        self.db.flush()
        return event

    def get_event(self, risk_event_id: int) -> Optional[RiskEvent]:
        return self.db.get(RiskEvent, risk_event_id)

    def get_event_by_order_id(self, order_id: int) -> Optional[RiskEvent]:
        return self.db.scalar(select(RiskEvent).where(RiskEvent.order_id == order_id))

    def create_rule_hit(self, rule_hit: RuleHit) -> RuleHit:
        self.db.add(rule_hit)
        self.db.flush()
        return rule_hit

    def create_admin_action(self, action: AdminAction) -> AdminAction:
        self.db.add(action)
        self.db.flush()
        return action

    def list_events(self, risk_level: Optional[str] = None):
        stmt = select(RiskEvent).order_by(RiskEvent.created_at.desc())
        if risk_level:
            stmt = stmt.where(RiskEvent.risk_level == risk_level)
        return list(self.db.scalars(stmt).all())
