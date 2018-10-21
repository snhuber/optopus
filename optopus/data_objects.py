# -*- coding: utf-8 -*-
import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any
from optopus.utils import nan, is_nan


class DataSource(Enum):
    IB = 'IB'
    Quandl = 'Quandl'


class AssetType(Enum):
    Stock = 'STK'
    Option = 'OPT'
    Future = 'FUT'
    Forex = 'CASH'
    Index = 'IND'
    CFD = 'CFD'
    Bond = 'BOND'
    Commodity = 'CMDTY'
    FuturesOption = 'FOP'
    MutualFund = 'FUND'
    Warrant = 'IOPT'


class StrategyType(Enum):
    ShortPut = 'SP'
    ShortPutVerticalSpread = 'SPVS'
    ShortCallVerticalSpread = 'SCVS'


class OrderType(Enum):
    Market = 'MTK'
    Limit = 'LMT'
    Stop = 'STP'


class RightType(Enum):
    Call = 'C'
    Put = 'P'


class OptionMoneyness(Enum):
    AtTheMoney = 'ATM'
    InTheMoney = 'ITM'
    OutTheMoney = 'OTM'
    NA = 'NA'


class OwnershipType(Enum):
    Buyer = 1
    Seller = -1


class OrderRol(Enum):
    NewLeg = 'NL'
    TakeProfit = 'TP'
    StopLoss = 'SL'


class Currency(Enum):
    USDollar = 'USD'
    Euro = 'EUR'

class Direction(Enum):
    Bullish = 'Bullish'
    Neutral = 'Neutral'
    Bearish = 'Bearish'

class OrderStatus(Enum):
    APIPending = 'API pending'
    PendingSubmit = 'Pending submit'
    PendingCancel = 'Pending cancel'
    PreSubmitted = 'Presubmitted'
    Submitted = 'Submitted'
    APICancelled = 'API cancelled'
    Cancelled = 'Cancelled'
    Filled = 'Filled'
    Inactive = 'Inactive'


@dataclass(frozen=True)
class Current:
    high: float = None
    low: float = None
    close: float = None
    bid: float = None
    bid_size: float = None
    ask: float = None
    ask_size: float = None
    last: float = None
    last_size: float = None
    time: float = None
    volume: float = None

    @property
    def midpoint(self):
        return (self.bid + self.ask) / 2

    @property
    def market_price(self):
        mp = None
        if (not self.midpoint or self.bid <= self.last <= self.ask):
            mp = self.last
        if not mp:
            mp = self.midpoint
        if not mp or mp == -1:
            mp = self.close
        return mp

@dataclass(frozen=True)
class Bar():
    time: datetime.date
    open: float
    high: float
    low: float
    close: float
    average: float
    volume: float
    count: int

@dataclass(frozen=True)
class History:
    values: List[Bar]
    created: datetime.datetime = datetime.datetime.now()

@dataclass
class Measures:
    iv: float = None
    iv_rank: float = None
    iv_percentile: float = None
    iv_period: float = None
    stdev: float = None
    beta: float = None
    correlation: float = None
    price_percentile: float = None
    price_period: float = None
    directional_assumption: Direction = None

@dataclass
class Asset: 
    code: str
    asset_type: AssetType
    currency: Currency
    contract: Any = None

    current: Current = None
    price_history: History = None
    iv_history: History = None
    measures: Measures = Measures()

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
class Position():
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
        return self.code + ' ' + str(self.ownership.value) + ' ' + self.right.value + ' ' + str(round(self.strike, 1)) + ' ' + self.expiration.strftime('%d-%m-%Y')


# https://interactivebrokers.github.io/tws-api/order_submission.html
@dataclass(frozen=True)
class Trade:
    order_id: str
    status: OrderStatus
    remaining: float
    commission: float

class Leg:
    def __init__(self,
                 option: Option,
                 ownership: OwnershipType,
                 ratio: int) -> None:
        self.option = option
        self.ownership = ownership
        self.ratio = ratio
        self.created = datetime.datetime.now()
        self.filled = None
        self.commission = None
        
        self.leg_id = self.option.code + ' ' + str(self.ownership.value) + ' ' + self.option.right.value + ' ' + str(round(self.option.strike, 1)) + ' ' + self.option.expiration.strftime('%d-%m-%Y')

    @property
    def price(self):
        return (self.option.bid + self.option.ask) / 2

    def __repr__(self):
        return(f'{self.__class__.__name__}('
               f'{self.option.code, self.option.ownership.value, self.option.right.value, self.option.strike, self.option.expiration, self.option.multiplier, self.option.currency, self.option.quantity})')
        
    

class Strategy:
    def __init__(self,
                 code: str,
                 strategy_type: StrategyType,
                 ownership: OwnershipType,
                 currency: Currency,
                 take_profit_factor: float,
                 underlying_entry_price: float,
                 multiplier: int,
                 legs: Dict[str, Leg]):
        #self.asset = asset
        self._code = code
        self._strategy_type = strategy_type
        self._ownership = ownership
        self._currency = currency
        self._legs = legs
        self._created = datetime.datetime.now()
        self._strategy_id = self._code + ' ' + self._created.strftime('%d-%m-%Y %H:%M:%S')
        self._underlying_entry_price = underlying_entry_price
        self._entry_price = None
        self._take_profit_factor = take_profit_factor      
        #self._take_profit_price = None
        self._opened = None
        self._closed = None
        self._quantity = None
        self._multiplier = multiplier
        
        #self._spread_witdh = None
        #self._breakeven_price = None
        #self._maximum_profit = None
        #self._maximum_loss = None
        #self._POP = None
        #self._ROI = None

    @property
    def code(self):
        return self._code
    
    @property
    def strategy_type(self):
        return self._strategy_type
    
    @property
    def ownership(self):
        return self._ownership
    
    @property
    def currency(self):
        return self._currency

    @property
    def legs(self):
        return self._legs
    
    @property
    def strategy_id(self):
        return self._strategy_id

    @property
    def underlying_entry_price(self):
        return self._underlying_entry_price

    @property
    def entry_price(self):
        return self._entry_price
    
    @entry_price.setter
    def entry_price(self, value):
        self._entry_price = value
    
    @property
    def take_profit_price(self):
        return self._take_profit_price
    
    @take_profit_price.setter
    def take_profit_price(self, value):
        self._take_profit_price = value

    @property
    def created(self):
        return self._created

    @property
    def opened(self):
        return self._opened

    @opened.setter
    def opened(self, value):
        self._opened = value

    @property
    def closed(self):
        return self._closed

    @closed.setter
    def closed(self, value):
        self._closed = value

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        self._quantity = value

    @property
    def multiplier(self):
        return self._multiplier

    def __repr__(self):
        return(f'{self.__class__.__name__}('
               f'{self.code, self.strategy_type.value, self.created}'
               f'\n{self.legs!r}')




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
        return (f'{self.__class__.__name__}('
                f'{self.__dict__})')
        
class Portfolio:
    """Class representing a porfolio"""
    def __init__(self):
        self.bwd = None