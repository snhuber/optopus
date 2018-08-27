# -*- coding: utf-8 -*-
from collections import OrderedDict
import datetime
from enum import Enum
from typing import List
from optopus.utils import nan, is_nan
from optopus.currency import Currency
from optopus.settings import CURRENCY


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
    SellNakedPut = 'Sell naked put'


class OrderType(Enum):
    Market = 'MTK'
    Limit = 'LMT'


class OrderAction(Enum):
    Buy = 'BUY'
    Sell = 'SELL'


class OptionRight(Enum):
    Call = 'C'
    Put = 'P'


class OptionMoneyness(Enum):
    AtTheMoney = 'ATM'
    InTheMoney = 'ITM'
    OutTheMoney = 'OTM'
    NA = 'NA'


class Asset():
    def __init__(self,
                 code: str,
                 asset_type: AssetType,
                 data_source: DataSource = DataSource.IB,
                 currency: Currency = CURRENCY) -> None:
        self.code = code
        self.asset_type = asset_type
        self.data_source = data_source
        self.currency = CURRENCY
        self._data = None
        self._data_source_id = None
        self._historical_data = None
        self._historical_IV_data = None
        self._historical_updated = None
        self._historical_IV_updated = None
        self._option_chain = None

    @property
    def current(self):
        return self._data

    @current.setter
    def current(self, values):
        self._data = values

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

    @property
    def market_price(self):
        return self._data.market_price

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


class AssetData():
    def __init__(self,
                 code: str,
                 asset_type: AssetType,
                 high: float = nan,
                 low: float = nan,
                 close: float = nan,
                 bid: float = nan,
                 bid_size: float = nan,
                 ask: float = nan,
                 ask_size: float = nan,
                 last: float = nan,
                 last_size: float = nan,
                 volume: float = nan,
                 time: datetime.datetime = None) -> None:
        self.code = code
        self.asset_type = asset_type
        self.high = high
        self.low = low
        self.close = close
        self.bid = bid
        self.bid_size = bid_size
        self.ask = ask
        self.ask_size = ask_size
        self.last = last
        self.last_size = last_size
        self.time = time
        self.volume = volume
        self.IV_h = None
        self.IV_rank_h = None
        self.IV_percentile_h = None
        self.volume_h = None
        #self.stdev = None
        self.beta = None
        self.one_month_return = None
        self.correlation = None

    @property
    def midpoint(self) -> float:
        return(self.bid + self.ask) / 2

    @property
    def market_price(self) -> float:
        """
        Return the first available one of:
        * last price if within current bid/ask;
        * average of bid and ask (midpoint);
        * close price.
        """
        midpoint = self.midpoint
        if (is_nan(midpoint) or self.bid <= self.last <= self.ask):
            price = self.last
        else:
            price = nan

        if is_nan(price):
            price = midpoint
        if is_nan(price) or price == -1:
            price = self.close
        return price

    def to_dict(self, fields: List[str]) -> OrderedDict:
        d = OrderedDict()
        d['code'] = getattr(self, 'code')
        for field in fields:
            if hasattr(self, field):
                d[field] = getattr(self, field)
        return d


class OptionData():
    def __init__(self,
                 code: str,
                 expiration: datetime.date,
                 strike: int,
                 right: OptionRight,
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
                 volume: float = nan,
                 delta: float = nan,
                 gamma: float = nan,
                 theta: float = nan,
                 vega: float = nan,
                 implied_volatility: float = nan,
                 underlying_price: float = nan,
                 underlying_dividends: float = nan,
                 moneyness: float = nan,
                 intrinsic_value: float = nan,
                 extrinsic_value: float = nan,
                 time: datetime.datetime = None)-> None:
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
        self.volume = volume
        self.delta = delta
        self.gamma = gamma
        self.theta = theta
        self.vega = vega
        self.implied_volatility = implied_volatility
        self.underlying_price = underlying_price
        self.underlying_dividends = underlying_dividends
        self.moneyness = moneyness
        self.intrinsic_value = intrinsic_value
        self.extrinsic_value = extrinsic_value
        self.time = time
        self.DTE = None

    def to_dict(self, fields: List[str]) -> OrderedDict:
        d = OrderedDict()
        d['code'] = getattr(self, 'code')
        d['expiration'] = getattr(self, 'expiration')
        d['strike'] = getattr(self, 'strike')
        d['right'] = getattr(self, 'right')
        for field in fields:
            if hasattr(self, field):
                d[field] = getattr(self, field)
        return d


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

    def to_dict(self) -> OrderedDict:
        d = OrderedDict()
        d['code'] = self.code
        d['bar_time'] = self.bar_time
        d['bar_open'] = self.bar_open
        d['bar_high'] = self.bar_high
        d['bar_low'] = self.bar_low
        d['bar_close'] = self.bar_close
        d['bar_average'] = self.bar_average
        d['bar_volume'] = self.bar_volume
        d['bar_count'] = self.bar_count
        return d

class OwnershipType(Enum):
    Buyer = 'BUY'
    Seller = 'SELL'


class PositionData():
    def __init__(self,
                 code: str,
                 asset_type: AssetType,
                 ownership: OwnershipType,
                 quantity: int,
                 expiration: datetime.date = None,
                 strike: int = None,
                 right: OptionRight = None,
                 average_cost: float = None) -> None:

        self.code = code
        self.asset_type = asset_type
        self.ownership = ownership
        self.expiration = expiration
        self.strike = strike
        self.right = right
        self.quantity = quantity
        self.average_cost = average_cost
        self.trades = []

        self.option_price = None
        self.trade_option_price = None
        self.trade_time = None
        self.underlying_price = None
        self.commission = None
        self.beta = None
        self.delta = None
        self.algorithm = None
        self.strategy = None
        self.rol = None

    def to_dict(self) -> OrderedDict:
        d = OrderedDict()
        d['code'] = self.code
        d['asset_type'] = self.asset_type.value
        d['expiration'] = self.expiration
        d['strike'] = self.strike
        d['right'] = self.right.value
        d['ownership'] = self.ownership.value
        d['quantity'] = self.quantity
        d['average_cost'] = self.average_cost
        return(d)


class SignalData():
    def __init__(self,
                 asset: Asset,
                 action: OrderAction,
                 quantity: int,
                 price: float,
                 expiration: datetime.date = None,
                 strike: int = None,
                 right: OptionRight = None,
                 algorithm: str = None,
                 strategy: StrategyType = None,
                 rol: str = None) -> None:

        self.asset = asset
        self.action = action
        self.quantity = quantity
        self.price = price

        self.expiration = expiration
        self.strike = strike
        self.right = right

        self.algorithm = algorithm
        self.strategy = strategy
        self.rol = rol

        self.time = datetime.datetime.now()


class OrderStatus(Enum):
    PendingSubmit = 'Pending submit'
    PendingCancel = 'Pending cancel'
    PreSubmitted = 'Presubmitted'
    Submitted = 'Submitted'
    Cancelled = 'Cancelled'
    Filled = 'Filled'
    Inactive = 'Inactive'


class OrderData():
    def __init__(self,
                 asset: Asset,
                 action: OrderAction,
                 quantity: int,
                 price: float,
                 order_type: OrderType,
                 expiration: datetime.date = None,
                 strike: int = None,
                 right: OptionRight = None,
                 reference: str = None):

        self.asset = asset
        self.action = action
        self.quantity = quantity
        self.price = price
        self.order_type = order_type

        self.expiration = expiration
        self.strike = strike
        self.right = right

        self.reference = reference

        self.time = datetime.datetime.now()


# https://interactivebrokers.github.io/tws-api/order_submission.html
class TradeData:
    def __init__(self,
                 code: str,
                 asset_type: AssetType,
                 ownership: OwnershipType,
                 quantity: int,
                 expiration: datetime.date = None,
                 strike: int = None,
                 right: OptionRight = None,
                 algorithm: str = None,
                 strategy: StrategyType = None,
                 rol: str = None,
                 implied_volatility: float = None,
                 order_status: OrderStatus = None,
                 time: datetime.datetime = None,
                 price: float = None,
                 commission: float = None,
                 data_source_id: object = None):

        self.code = code
        self.asset_type = asset_type
        self.ownership = ownership
        self.quantity = quantity
        self.expiration = expiration
        self.strike = strike
        self.right = right
        self.algorithm = algorithm
        self.strategy = strategy
        self.rol = rol
        self.implied_volatility = implied_volatility
        self.order_status = order_status
        self.time = time
        self.price = price
        self.commission = commission
        self.data_source_id = data_source_id
