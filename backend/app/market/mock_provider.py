from typing import Dict, List

from app.market.providers import MarketDataProvider


class MockMarketDataProvider(MarketDataProvider):
    DATA = {
        "005930": {"stock_code": "005930", "stock_name": "삼성전자", "market_type": "KOSPI", "current_price": 83500, "day_open": 82000, "day_high": 84000, "day_low": 81900, "volume": 12403450},
        "000660": {"stock_code": "000660", "stock_name": "SK하이닉스", "market_type": "KOSPI", "current_price": 201000, "day_open": 197500, "day_high": 202000, "day_low": 196800, "volume": 3120450},
        "035420": {"stock_code": "035420", "stock_name": "NAVER", "market_type": "KOSPI", "current_price": 224500, "day_open": 220000, "day_high": 226000, "day_low": 219500, "volume": 1102300},
    }

    def get_quote(self, stock_code: str) -> Dict:
        return self.DATA[stock_code]

    def get_daily_prices(self, stock_code: str) -> List[Dict]:
        quote = self.DATA[stock_code]
        return [
            {"date": "2026-04-07", "close": quote["current_price"] - 1200, "volume": quote["volume"] - 10000},
            {"date": "2026-04-08", "close": quote["current_price"] - 300, "volume": quote["volume"] - 3000},
            {"date": "2026-04-09", "close": quote["current_price"], "volume": quote["volume"]},
        ]
