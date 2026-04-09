from typing import Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def log(self, user_id: Optional[int], action: str, resource_type: str, resource_id: str, detail: str) -> None:
        self.db.add(
            AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                detail=detail,
            )
        )
        self.db.flush()
