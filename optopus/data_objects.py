# -*- coding: utf-8 -*-
import datetime
from enum import Enum
from typing import List, Dict
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


class Asset():
    def __init__(self,
                 code: str,
                 asset_type: AssetType,
                 currency: Currency) -> None:
        self.code = code
        self.asset_type = asset_type
        self.currency = currency

        self.high = None
        self.low = None
        self.close = None
        self.bid = None
        self.bid_size = None
        self.ask = None
        self.ask_size = None
        self.last = None
        self.last_size = None
        self.time = None
        self.volume = None
        self.contract = None
        self.IV = None
        self.IV_rank = None
        self.IV_percentile = None
        self.IV_period = None
        self.volume = None
        self.stdev = None
        self.beta = None
        self.correlation = None
        self.price_period = None
        self.directional_assumption = None
        self.price_percentile = None
        self._contract = None
        self._historical_data = None
        self._historical_IV_data = None
        self._historical_updated = None
        self._historical_IV_updated = None

    @property
    def midpoint(self):
        return (self.bid + self.ask) / 2

    @property
    def market_price(self):
        market_price = nan
        if (is_nan(self.midpoint) or self.bid <= self.last <= self.ask):
            market_price = self.last

        if is_nan(market_price):
            market_price = self.midpoint
        if is_nan(market_price) or market_price == -1:
            market_price = self.close

        return market_price

    @property
    def historical(self):
        return self._historical_data

    @historical.setter
    def historical(self, values):
        self._historical_data = values
        self._historical_data_updated = datetime.datetime.now()

    @property
    def historical_IV(self):
        return self._historical_IV_data

    @historical_IV.setter
    def historical_IV(self, values):
        self._historical_IV_data = values
        self._historical_data_updated = datetime.datetime.now()

    def historical_is_updated(self) -> bool:
        if self._historical_updated:
            delta = datetime.datetime.now() - self._historical_updated
            if delta.days:
                return True
            else:
                return False
        else:
            return False

    def historical_IV_is_updated(self) -> bool:
        if self._historical_IV_updated:
            delta = datetime.datetime.now() - self._historical_IV_updated
            if delta.days:
                return True
            else:
                return False
        else:
            return False


class OptionData:
    def __init__(self,
                 code: str,
                 expiration: datetime.date,
                 strike: float,
                 right: RightType,
                 high: float = nan,
                 low: float = nan,
                 close: float = nan,
                 bid: float = nan,
                 bid_size: float = nan,
                 ask: float = nan,
                 ask_size: float = nan,
                 last: float = nan,
                 last_size: float = nan,
                 option_price: float = nan,
                 currency: str = None,
                 multiplier: int = 100,
                 volume: float = nan,
                 delta: float = nan,
                 gamma: float = nan,
                 theta: float = nan,
                 vega: float = nan,
                 implied_volatility: float = nan,
                 underlying_price: float = nan,
                 underlying_dividends: float = nan,
                 time: datetime.datetime = None,
                 contract: object = None)-> None:
        self.code = code
        self.asset_type = AssetType.Option
        self.expiration = expiration
        self.strike = strike
        self.right = right
        self.high = high
        self.low = low
        self.close = close
        self.bid = bid
        self.bid_size = bid_size
        self.ask = ask
        self.ask_size = ask_size
        self.last = last
        self.last_size = last_size
        self.option_price = option_price
        self.currency = currency
        self.multiplier = multiplier
        self.volume = volume
        self.delta = delta
        self.gamma = gamma
        self.theta = theta
        self.vega = vega
        self.implied_volatility = implied_volatility
        self.underlying_price = underlying_price
        self.underlying_dividends = underlying_dividends
        self.time = time
        self.contract = contract
        self.DTE = (self.expiration - datetime.datetime.now().date()).days

    @property
    def midpoint(self):
        return (self.bid + self.ask) / 2


class BarDataType(Enum):
    Trades = 'TRADES'
    IV = 'IMPLIED_VOLATILITY'


class BarData():
    def __init__(self,
                 code: str,
                 bar_time: float = nan,
                 bar_open: float = nan,
                 bar_high: float = nan,
                 bar_low: float = nan,
                 bar_close: float = nan,
                 bar_average: float = nan,
                 bar_volume: float = nan,
                 bar_count: float = nan) -> None:
        self.code = code
        self.bar_time = bar_time
        self.bar_open = bar_open
        self.bar_high = bar_high
        self.bar_low = bar_low
        self.bar_close = bar_close
        self.bar_average = bar_average
        self.bar_volume = bar_volume
        self.bar_count = bar_count


class PositionData():
    def __init__(self,
                 code: str,
                 asset_type: AssetType,
                 ownership: OwnershipType,
                 quantity: int,
                 expiration: datetime.date,
                 strike: float,
                 right: RightType,
                 average_cost: float = None) -> None:

        self.code = code
        self.asset_type = asset_type
        self.ownership = ownership
        self.expiration = expiration
        self.strike = strike
        self.right = right
        self.quantity = quantity
        self.position_id = self.code + ' ' + str(self.ownership.value) + ' ' + self.right.value + ' ' + str(round(self.strike, 1)) + ' ' + self.expiration.strftime('%d-%m-%Y')
        
        self.average_cost = average_cost
        #self.trades = []
        self.option_price = None
        self.trade_price = None
        self.trade_time = None
        self.underlying_price = None
        self.beta = None
        self.delta = None
        self.algorithm = None
        self.strategy = None
        self.rol = None
        self.DTE = None

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self.__dict__})')




# https://interactivebrokers.github.io/tws-api/order_submission.html
class TradeData:
    def __init__(self,
                 order_id: str,
                 status: OrderStatus,
                 remaining: int,
                 commission: float):
        self.order_id = order_id
        self.status = status
        self.remaining = remaining
        self.commission = commission

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'{self.__dict__})')


class Leg:
    def __init__(self,
                 option: OptionData,
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

    @opened.setter
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

    
    @property
    def strategy_id(self):
        return self._strategy_id


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