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
    high: float 
    low: float
    close: float
    bid: float
    bid_size: float
    ask: float
    ask_size: float
    last: float
    last_size: float
    option_price: float
    volume: int
    delta: float
    gamma: float
    theta: float
    vega: float
    iv: float
    underlying_price: float
    underlying_dividends: float
    time: datetime.datetime

    @property
    def midpoint(self):
        return (self.bid + self.ask) / 2

    @property
    def DTE(self):
        return (self.id.expiration - datetime.date.today()).days

