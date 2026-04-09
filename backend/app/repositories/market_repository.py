from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.market import MarketTick, Stock


class MarketRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_stocks(self):
        return list(self.db.scalars(select(Stock).order_by(Stock.stock_code)).all())

    def get_stock(self, stock_code: str) -> Optional[Stock]:
        return self.db.scalar(select(Stock).where(Stock.stock_code == stock_code))

    def get_latest_tick(self, stock_code: str) -> Optional[MarketTick]:
        return self.db.scalar(select(MarketTick).where(MarketTick.stock_code == stock_code).order_by(MarketTick.as_of.desc()))
