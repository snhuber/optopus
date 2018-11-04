from enum import Enum
from typing import NamedTuple


class AssetType(Enum):
    Stock = "STK"
    ETF = "ETF"
    Option = "OPT"
    Future = "FUT"
    Forex = "CASH"
    Index = "IND"
    CFD = "CFD"
    Bond = "BOND"
    Commodity = "CMDTY"
    FuturesOption = "FOP"
    MutualFund = "FUND"
    Warrant = "IOPT"


class Currency(Enum):
    USDollar = "USD"
    Euro = "EUR"


class AssetDefinition(NamedTuple):
    code: str
    asset_type: AssetType
    exchange: str = None
    currency: Currency = Currency.USDollar


class OwnershipType(Enum):
    Buyer = 1
    Seller = -1


class Direction(Enum):
    Bullish = "Bullish"
    Neutral = "Neutral"
    Bearish = "Bearish"
