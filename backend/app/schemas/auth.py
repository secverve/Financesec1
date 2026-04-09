from typing import Optional

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    ip_address: str = "127.0.0.1"
    region: str = "KR-SEOUL"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int


class MeResponse(BaseModel):
    user_id: int
    email: EmailStr
    full_name: str
    role: str
    is_locked: bool
    primary_account_id: Optional[int] = None
