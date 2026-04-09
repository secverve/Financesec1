from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.security import create_access_token, verify_password
from app.models.user import LoginHistory
from app.repositories.user_repository import UserRepository
from app.services.audit_service import AuditService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.audit = AuditService(db)

    def login(self, email: str, password: str, ip_address: str, region: str) -> dict:
        user = self.users.get_by_email(email)
        success = bool(user and verify_password(password, user.password_hash) and user.is_active and not user.is_locked)
        self.users.create_login_history(LoginHistory(user_id=user.id if user else None, email=email, ip_address=ip_address, region=region, success=success))

        if not success or user is None:
            self.db.commit()
            raise AppException("AUTH_FAILED", "Invalid credentials")

        token = create_access_token(str(user.id))
        self.audit.log(user.id, "LOGIN_SUCCESS", "user", str(user.id), f"login from {ip_address} {region}")
        self.db.commit()
        return {"access_token": token, "role": user.role, "user_id": user.id}
