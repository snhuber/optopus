# -*- coding: utf-8 -*-
from enum import Enum
import datetime
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

    @property
    def asset_id(self) -> str:
        return self.code + '_' + self.asset_type.value
class IndexAsset(Asset):
    def __init__(self, 
                 code: str, 
                 data_source: DataSource = DataSource.IB,
                 currency: Currency = CURRENCY) -> None:
        super().__init__(code, AssetType.Index, data_source, currency)


class IndexDataAsset(IndexAsset):
    def __init__(self,
                 code: str,
                 data_source: DataSource = DataSource.IB,
                 currency: Currency = CURRENCY) -> None:
        super().__init__(code, data_source, currency)
        self._data = None
        self._historical_data = None
        self._historical_IV_data = None

    @property
    def current_data(self):
        return [self._data]

    @current_data.setter
    def current_data(self, values):
        self._data = values

    @property
    def historical_data(self):
        return self._historical_data

    @historical_data.setter
    def historical_data(self, values):
        self._historical_data = values
        self._historical_data_updated = datetime.datetime.now()

    @property
    def historical_IV_data(self):
        return self._historical_IV_data

    @historical_IV_data.setter
    def historical_IV_data(self, values):
        self._historical_IV_data = values
        self._historical_data_updated = datetime.datetime.now()

    @property
    def market_price(self):
        return self._data.market_price


class IndexData():
    def __init__(self,
                 code: str,
                 high: float = nan,
                 low: float = nan,
                 close: float = nan,
                 bid: float = nan,
                 bid_size: float = nan,
                 ask: float = nan,
                 ask_size: float = nan,
                 last: float = nan,
                 last_size: float = nan,
                 time: datetime.datetime = None) -> None:
        self.code = code
        self.asset_type = AssetType.Index
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


class StockAsset(Asset):
    def __init__(self,
                 code: str,
                 data_source: DataSource = DataSource.IB,
                 currency: Currency = CURRENCY) -> None:
        super().__init__(code, AssetType.Stock, data_source, currency)


class StockDataAsset(StockAsset):
    def __init__(self,
                 code: str,
                 data_source: DataSource = DataSource.IB,
                 currency: Currency = CURRENCY) -> None:
        super().__init__(code, data_source, currency)
        self._data = None
        self._historical_data = None
        self._historical_IV_data = None

    @property
    def current_data(self):
        return [self._data]

    @current_data.setter
    def current_data(self, values):
        self._data = values

    @property
    def historical_data(self):
        return self._historical_data

    @historical_data.setter
    def historical_data(self, values):
        self._historical_data = values
        self._historical_data_updated = datetime.datetime.now()

    @property
    def historical_IV_data(self):
        return self._historical_IV_data

    @historical_IV_data.setter
    def historical_IV_data(self, values):
        self._historical_IV_data = values
        self._historical_data_updated = datetime.datetime.now()

    @property
    def market_price(self):
        return self._data.market_price


class StockData():
    def __init__(self,
                 code: str,
                 high: float = nan,
                 low: float = nan,
                 close: float = nan,
                 bid: float = nan,
                 bid_size: float = nan,
                 ask: float = nan,
                 ask_size: float = nan,
                 last: float = nan,
                 last_size: float = nan,
                 time: datetime.datetime = None) -> None:
        self.code = code
        self.asset_type = AssetType.Index
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


class OptionChainAsset(Asset):
    def __init__(self,
                 underlying: Asset,
                 n_expiration_dates: int = 3,
                 underlying_distance: float = 1) -> None:
        super().__init__(underlying.code, AssetType.Option, underlying.data_source, underlying.currency)
        self.underlying = underlying
        self.n_expiration_dates = n_expiration_dates
        self.underlying_distance = underlying_distance


class OptionChainDataAsset(OptionChainAsset):
    def __init__(self,
                 underlying: Asset,
                 n_expiration_dates: int = 3,
                 underlying_distance: float = 1) -> None:
        super().__init__(underlying, n_expiration_dates, underlying_distance)
        self._data = None

    @property
    def current_data(self):
        return self._data

    @current_data.setter
    def current_data(self, values):
        self._data = values


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
                 bar_volumen: float = nan,
                 bar_count: float = nan) -> None:
        self.code = code
        self.bar_time = bar_time
        self.bar_open = bar_open
        self.bar_high = bar_high
        self.bar_low = bar_low
        self.bar_close = bar_close
        self.bar_average = bar_average
        self.bar_volumen = bar_volumen
        self.bar_count = bar_count


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
                 commission: float = None):

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

