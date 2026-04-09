from typing import Dict, List

from pydantic import BaseModel


class DashboardStockResponse(BaseModel):
    stock_code: str
    stock_name: str
    market_type: str
    current_price: float
    volume: int
    is_monitored: bool


class PortfolioPositionResponse(BaseModel):
    stock_code: str
    stock_name: str
    quantity: int
    avg_price: float
    current_price: float
    evaluation_amount: float
    profit_loss: float


class AdditionalAuthPendingResponse(BaseModel):
    order_id: int
    status: str
    code_hint: str


class UserDashboardResponse(BaseModel):
    user_id: int
    account_id: int
    account_number: str
    cash_balance: float
    portfolio_value: float
    total_evaluation_amount: float
    positions: List[PortfolioPositionResponse]
    watch_stocks: List[DashboardStockResponse]
    recent_orders: List[Dict]
    pending_auth: List[AdditionalAuthPendingResponse]


class RiskLevelCountResponse(BaseModel):
    risk_level: str
    count: int


class TopRiskUserResponse(BaseModel):
    email: str
    event_count: int


class AdminDashboardSummaryResponse(BaseModel):
    total_events: int
    open_events: int
    critical_events: int
    suspicious_events: int
    held_orders: int
    blocked_orders: int
    same_ip_multi_account_events: int
    risk_levels: List[RiskLevelCountResponse]
    top_risk_users: List[TopRiskUserResponse]
