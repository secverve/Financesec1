from typing import Dict, List

from app.core.config import settings
from app.market.mock_provider import MockMarketDataProvider
from app.market.providers import MarketDataProvider


class RealMarketDataProvider(MarketDataProvider):
    def get_quote(self, stock_code: str) -> Dict:
        raise NotImplementedError("Real provider integration is not configured yet")

    def get_daily_prices(self, stock_code: str) -> List[Dict]:
        raise NotImplementedError("Real provider integration is not configured yet")


def get_market_provider() -> MarketDataProvider:
    if settings.market_data_provider == "mock":
        return MockMarketDataProvider()
    return RealMarketDataProvider()
