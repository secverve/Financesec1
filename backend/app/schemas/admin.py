from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator


class RiskEventResponse(BaseModel):
    id: int
    user_id: int
    stock_code: str
    stock_name: str
    risk_score: int
    risk_level: str
    decision: str
    reason_summary: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RiskEventActionRequest(BaseModel):
    action_type: str

    @field_validator("action_type")
    @classmethod
    def validate_action_type(cls, value: str) -> str:
        allowed = {"APPROVE", "BLOCK", "REQUIRE_AUTH"}
        if value not in allowed:
            raise ValueError("action_type must be one of APPROVE, BLOCK, REQUIRE_AUTH")
        return value


class RiskEventActionResponse(BaseModel):
    risk_event_id: int
    action_type: str
    risk_event_status: str
    order_status: Optional[str] = None


class UserLockResponse(BaseModel):
    user_id: int
    is_locked: bool
