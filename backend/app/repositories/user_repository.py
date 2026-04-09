from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import Account, DeviceHistory, LoginHistory, User, UserBehaviorProfile


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.scalar(select(User).where(User.email == email))

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_primary_account(self, user_id: int) -> Optional[Account]:
        return self.db.scalar(select(Account).where(Account.user_id == user_id))

    def get_behavior_profile(self, user_id: int) -> Optional[UserBehaviorProfile]:
        return self.db.scalar(select(UserBehaviorProfile).where(UserBehaviorProfile.user_id == user_id))

    def get_known_device(self, user_id: int, device_id: str) -> Optional[DeviceHistory]:
        return self.db.scalar(select(DeviceHistory).where(DeviceHistory.user_id == user_id, DeviceHistory.device_id == device_id))

    def get_recent_login_failures(self, email: str, limit_minutes: int = 30) -> List[LoginHistory]:
        rows = self.db.scalars(select(LoginHistory).where(LoginHistory.email == email, LoginHistory.success.is_(False)).order_by(LoginHistory.created_at.desc())).all()
        return rows[:5]

    def create_login_history(self, history: LoginHistory) -> LoginHistory:
        self.db.add(history)
        self.db.flush()
        return history
