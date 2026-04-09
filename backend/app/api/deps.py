from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppException
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise AppException("AUTH_INVALID", "Invalid token", status.HTTP_401_UNAUTHORIZED)
    except JWTError as exc:
        raise AppException("AUTH_INVALID", "Invalid token", status.HTTP_401_UNAUTHORIZED) from exc

    user = UserRepository(db).get_by_id(int(user_id))
    if not user:
        raise AppException("AUTH_NOT_FOUND", "User not found", status.HTTP_401_UNAUTHORIZED)
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "ADMIN":
        raise AppException("AUTH_FORBIDDEN", "Admin role required", status.HTTP_403_FORBIDDEN)
    return user
