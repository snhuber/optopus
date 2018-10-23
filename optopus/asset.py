from dataclasses import dataclass
import datetime
from typing import Tuple, Any
from optopus.common import AssetType, Currency, Direction


@dataclass(frozen=True)
class Current:
    high: float
    low: float
    close: float
    bid: float
    bid_size: float
    ask: float
    ask_size: float
    last: float
    last_size: float
    volume: float
    time: float

    @property
    def midpoint(self):
        return (self.bid + self.ask) / 2

    @property
    def market_price(self):
        mp = None
        if self.bid <= self.last <= self.ask:
            mp = self.last
        if not mp:
            mp = self.midpoint
        if mp == -1:
            mp = self.close
        return mp


@dataclass(frozen=True)
class Bar:
    count: int
    open: float
    high: float
    low: float
    close: float
    average: float
    volume: float
    time: datetime.date


@dataclass(frozen=True)
class History:
    values: Tuple[Bar]
    created: datetime.datetime = datetime.datetime.now()


@dataclass(frozen=True)
class Measures:
    price_percentile: float
    price_pct: float
    iv: float
    iv_rank: float
    iv_percentile: float
    iv_pct: float
    stdev: float
    beta: float
    correlation: float
    directional_assumption: Direction


@dataclass
class Asset:
    code: str
    asset_type: AssetType
    currency: Currency
    contract: Any = None

    current: Current = None
    price_history: History = None
    iv_history: History = None
    measures: Measures = None
