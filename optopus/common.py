from enum import Enum


class AssetType(Enum):
    Stock = "STK"
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


class OwnershipType(Enum):
    Buyer = 1
    Seller = -1


class Direction(Enum):
    Bullish = "Bullish"
    Neutral = "Neutral"
    Bearish = "Bearish"
