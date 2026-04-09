from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.market import StockListResponse, StockQuoteResponse
from app.services.market_service import MarketService

router = APIRouter()


@router.get("/stocks", response_model=List[StockListResponse])
def list_stocks(db: Session = Depends(get_db)):
    rows = MarketService(db).list_stocks()
    return [StockListResponse(stock_code=row.stock_code, stock_name=row.stock_name, market_type=row.market_type, is_monitored=row.is_monitored) for row in rows]


@router.get("/stocks/{stock_code}/quote", response_model=StockQuoteResponse)
def get_quote(stock_code: str, db: Session = Depends(get_db)):
    try:
        return StockQuoteResponse(**MarketService(db).get_quote(stock_code))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
