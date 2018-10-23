# -*- coding: utf-8 -*-
import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Tuple
from optopus.common import AssetType, Currency


# TODO: Create a new file asset.py for Asset, Current, Measures, History...


class DataSource(Enum):
    IB = "IB"
    Quandl = "Quandl"


class OrderType(Enum):
    Market = "MTK"
    Limit = "LMT"
    Stop = "STP"


class RightType(Enum):
    Call = "C"
    Put = "P"


class OptionMoneyness(Enum):
    AtTheMoney = "ATM"
    InTheMoney = "ITM"
    OutTheMoney = "OTM"
    NA = "NA"


class OwnershipType(Enum):
    Buyer = 1
    Seller = -1


class OrderRol(Enum):
    NewLeg = "NL"
    TakeProfit = "TP"
    StopLoss = "SL"


class OrderStatus(Enum):
    APIPending = "API pending"
    PendingSubmit = "Pending submit"
    PendingCancel = "Pending cancel"
    PreSubmitted = "Presubmitted"
    Submitted = "Submitted"
    APICancelled = "API cancelled"
    Cancelled = "Cancelled"
    Filled = "Filled"
    Inactive = "Inactive"


@dataclass(frozen=True)
class Option:
    code: str
    asset_type: AssetType
    expiration: datetime.date
    strike: int
    right: RightType
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
    currency: Currency = None
    multiplier: int = None
    volume: int = None
    delta: float = None
    gamma: float = None
    theta: float = None
    vega: float = None
    iv: float = None
    underlying_price: float = None
    underlying_dividends: float = None
    time: datetime.datetime = None
    contract: Any = None

    @property
    def midpoint(self):
        return (self.bid + self.ask) / 2

    @property
    def DTE(self):
        return (self.expiration - datetime.datetime.now().date()).days


@dataclass(frozen=True)
class Position:
    code: str
    asset_type: AssetType
    ownership: OwnershipType
    expiration: datetime.date
    strike: int
    right: RightType
    quantity: int
    average_cost: float
    option_price: float
    trade_price: float
    trade_time: datetime.datetime
    underlying_price: float
    beta: float
    delta: float
    algorithm: str
    strategy: str
    rol: str

    @property
    def DTE(self):
        return (self.expiration - datetime.datetime.now().date()).days

    @property
    def position_id(self):
        return (
            self.code
            + " "
            + str(self.ownership.value)
            + " "
            + self.right.value
            + " "
            + str(round(self.strike, 1))
            + " "
            + self.expiration.strftime("%d-%m-%Y")
        )


# https://interactivebrokers.github.io/tws-api/order_submission.html
@dataclass(frozen=True)
class Trade:
    order_id: str
    status: OrderStatus
    remaining: float
    commission: float


# TODO: Become Account to immutable class
class Account:
    """Class representing a account"""

    def __init__(self) -> None:
        self._id = None
        # The basis for determining the price of the assets in your account.
        # Total cash value + stock value + options value + bond value
        self.net_liquidation = None
        # Buying power serves as a measurement of the dollar value of
        # securities that one may purchase in a securities account without
        # depositing additional funds
        self.buying_power = None
        # Cash recognized at the time of trade + futures PNL
        self.cash = None
        # This value tells what you have available for trading
        self.funds = None
        # The Number of Open/Close trades a user could put on before
        # Pattern Day Trading is detected. A value of "-1" means that the user
        # can put on unlimited day trades.
        # Number of Open/Close trades in a day
        self.max_day_trades = None
        # Initial Margin requirement of whole portfolio
        self.initial_margin = None
        #  Maintenance Margin requirement of whole portfolio
        self.maintenance_margin = None
        # This value shows your margin cushion, before liquidation
        self.excess_liquidity = None
        # Excess liquidity as a percentage of net liquidation value
        self.cushion = None
        # The sum of the absolute value of all stock and equity option positions
        # Leverage = GrossPositionValue / NetLiquidation
        self.gross_position_value = None
        # Forms the basis for determining whether a client has the
        # necessary assets to either initiate or maintain security positions.
        # Cash + stocks + bonds + mutual funds
        self.equity_with_loan = None
        # Special Memorandum Account: Line of credit created when the market
        # value of securities in a Regulation T account increase in value
        self.SMA = None

    def __repr__(self):
        return f"{self.__class__.__name__}(" f"{self.__dict__})"


class Portfolio:
    """Class representing a porfolio"""

    def __init__(self):
        self.bwd = None
