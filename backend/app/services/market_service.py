from sqlalchemy.orm import Session

from app.market.factory import get_market_provider
from app.repositories.market_repository import MarketRepository


class MarketService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = MarketRepository(db)
        self.provider = get_market_provider()

    def list_stocks(self):
        return self.repository.list_stocks()

    def get_quote(self, stock_code: str) -> dict:
        stock = self.repository.get_stock(stock_code)
        if not stock:
            raise ValueError("Stock not found")
        return self.provider.get_quote(stock_code)
