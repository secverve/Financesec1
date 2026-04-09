from datetime import datetime

from pydantic import BaseModel


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
