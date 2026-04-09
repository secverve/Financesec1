from abc import ABC, abstractmethod
from typing import Dict, List


class MarketDataProvider(ABC):
    @abstractmethod
    def get_quote(self, stock_code: str) -> Dict:
        raise NotImplementedError

    @abstractmethod
    def get_daily_prices(self, stock_code: str) -> List[Dict]:
        raise NotImplementedError
