from pydantic import BaseModel


class StockQuoteResponse(BaseModel):
    stock_code: str
    stock_name: str
    market_type: str
    current_price: float
    day_open: float
    day_high: float
    day_low: float
    volume: int


class StockListResponse(BaseModel):
    stock_code: str
    stock_name: str
    market_type: str
    is_monitored: bool
