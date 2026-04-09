from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class OrderCreateRequest(BaseModel):
    account_id: int
    stock_code: str
    side: str
    order_type: str
    quantity: int = Field(gt=0)
    price: float = Field(ge=0)
    device_id: str
    ip_address: str
    region: str

    @field_validator("side")
    @classmethod
    def validate_side(cls, value: str) -> str:
        if value not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        return value

    @field_validator("order_type")
    @classmethod
    def validate_order_type(cls, value: str) -> str:
        if value not in {"MARKET", "LIMIT"}:
            raise ValueError("order_type must be MARKET or LIMIT")
        return value


class OrderAmendRequest(BaseModel):
    quantity: int = Field(gt=0)
    price: Optional[float] = Field(default=None, ge=0)
    order_type: Optional[str] = None

    @field_validator("order_type")
    @classmethod
    def validate_order_type(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if value not in {"MARKET", "LIMIT"}:
            raise ValueError("order_type must be MARKET or LIMIT")
        return value


class AdditionalAuthVerifyRequest(BaseModel):
    code: str


class AdditionalAuthVerifyResponse(BaseModel):
    order_id: int
    order_status: str
    auth_status: str


class OrderResponse(BaseModel):
    id: int
    stock_code: str
    side: str
    order_type: str
    quantity: int
    filled_quantity: int
    remaining_quantity: int
    price: float
    average_filled_price: float
    status: str
    risk_score: int
    risk_level: str
    decision: str
    created_at: datetime

    model_config = {"from_attributes": True}
