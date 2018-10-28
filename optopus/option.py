from dataclasses import dataclass
import datetime
from enum import Enum
from typing import Any
from optopus.asset import AssetId
from optopus.common import AssetType, Currency


class RightType(Enum):
    Call = "C"
    Put = "P"


class Moneyness(Enum):
    AtTheMoney = "ATM"
    InTheMoney = "ITM"
    OutTheMoney = "OTM"
    NA = "NA"


@dataclass(frozen=True)
class OptionId:
    underlying_id: AssetId
    asset_type: AssetType
    expiration: datetime.date
    strike: int
    right: RightType
    multiplier: int
    contract: Any


@dataclass(frozen=True)
class Option:
    id: OptionId
    high: float = None
    low: float = None
    close: float = None
    bid: float = None
    bid_size: float = None
    ask: float = None
    ask_size: float = None
    last: float = None
    last_size: float = None
    option_price: float = None
    volume: int = None
    delta: float = None
    gamma: float = None
    theta: float = None
    vega: float = None
    iv: float = None
    underlying_price: float = None
    underlying_dividends: float = None
    time: datetime.datetime = None

    @property
    def midpoint(self):
        return (self.bid + self.ask) / 2

    @property
    def DTE(self):
        return (self.expiration - datetime.datetime.now().date()).days

