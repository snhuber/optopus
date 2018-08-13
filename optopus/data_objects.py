# -*- coding: utf-8 -*-
from enum import Enum
import datetime
from collections import namedtuple

nan = float('nan')


def is_nan(x: float) -> bool:
    """
    Not a number test.
    """
    return x != x


class DataSource(Enum):
    IB = 'IB'
    Quandl = 'Quandl'


class OptionRight(Enum):
    Call = 'C'
    Put = 'P'


class DataSeriesType(Enum):
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


IndexRecord = namedtuple('IndexRecord', 'code high low close\
               bid bid_size ask ask_size last last_size time')

class DataIndex():
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

    def midpoint(self) -> float:
        return(self.bid + self.ask) / 2

    def market_price(self) -> float:
        """
        Return the first available one of:
        * last price if within current bid/ask;
        * average of bid and ask (midpoint);
        * close price.
        """
        midpoint = self.midpoint()
        if (is_nan(midpoint) or self.bid <= self.last <= self.ask):
            price = self.last
        else:
            price = nan

        if is_nan(price):
            price = midpoint
        if is_nan(price) or price == -1:
            price = self.close
        return price

    @property
    def values(self):
        return(IndexRecord(self.code, self.last, self.last_size, self.high,
                           self.low, self.close, self.bid, self.bid_size,
                           self.ask, self.ask_size, self.time))


# https://interactivebrokers.github.io/tws-api/rtd_simple_syntax.html#rtd_simple_syntax_basic_ticks
OptionRecord = namedtuple('OptionRecord', 'code expiration strike righ\
                          high low close\
                          bid bid_size ask ask_size last last_size volume\
                          time')


class OptionIndicators():
    def __init__(self,
                 delta=nan,
                 gamma=nan,
                 theta=nan,
                 vega=nan,
                 option_price=nan,
                 implied_volatility=nan,
                 underlying_price=nan,
                 underlying_dividends=nan) -> None:
        self.delta = delta
        self.gamma = gamma
        self.theta = theta
        self.vega = vega
        self.option_price = option_price
        self.implied_volatility = implied_volatility
        self.underlying_price = underlying_price
        self.underlying_dividends = underlying_dividends


class DataOption():
    def __init__(self,
                 code: str,
                 expiration: datetime.date,
                 strike: int,
                 right: OptionRight,
                 high=nan,
                 low=nan,
                 close=nan,
                 bid=nan,
                 bid_size=nan,
                 ask=nan,
                 ask_size=nan,
                 last=nan,
                 last_size=nan,
                 volume=nan,
                 indicators: OptionIndicators = None,
                 bid_indicators: OptionIndicators = None,
                 ask_indicators: OptionIndicators = None,
                 last_indicators: OptionIndicators = None,
                 time: datetime.datetime = None)-> None:
        self.code = code
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
        self.volume = volume
        self.indicators = indicators
        self.bid_indicators = bid_indicators
        self.ask_indicators = ask_indicators
        self.last_indicators = last_indicators
        self.time = time

    @property
    def values(self):
        return(OptionRecord(self.code, self.expiration, self.strike, self.right,
                            self.high, self.low, self.close, 
                            self.bid, self.bid_size, self.ask, self.ask_size, 
                            self.last, self.last_size, self.volume, self.time))

StrikeRecord = namedtuple('StrikeRecord', 'code expiration strike\
                          c_high c_low c_close\
                          c_bid c_bid_size c_ask c_ask_size c_last c_last_size\
                          c_volume c_time\
                          p_high p_low p_close\
                          p_bid p_bid_size p_ask p_ask_size p_last p_last_size\
                          p_volume p_time')
class DataOptionChain():
    def __init__(self, code: str, data: dict) -> None:
        self.code = code
        self._data = data
    @property
    def values(self):
        records=[]
        for exp, vexp in self._data.items():
            for s, sv in vexp.items():
                r = StrikeRecord(self.code, exp, s,
                                 sv['C'].high, sv['C'].low, sv['C'].close,
                                 sv['C'].bid, sv['C'].bid_size, sv['C'].ask, sv['C'].ask_size,
                                 sv['C'].last, sv['C'].last_size, sv['C'].volume, sv['C'].time,
                                 sv['P'].high, sv['P'].low, sv['P'].close,
                                 sv['P'].bid, sv['P'].bid_size, sv['P'].ask, sv['P'].ask_size,
                                 sv['P'].last, sv['P'].last_size, sv['P'].volume, sv['P'].time)
                records.append(r)
        return(records)

class DataSeries():
    def __init__(self,
                 code: str,
                 data_series_type: DataSeriesType,
                 data_source: DataSource) -> None:
        self.code = code
        self.data_series_type = data_series_type
        self.data_source = data_source

    @property
    def data_series_id(self) -> str:
        return self.code + '_' + self.data_series_type.value


class DataSeriesIndex(DataSeries):
    def __init__(self,
                 code: str,
                 data_source: DataSource) -> None:
        super().__init__(code, DataSeriesType.Index, data_source)


class DataSeriesOption(DataSeries):
    def __init__(self, 
                 underlying: DataSeries,
                 max_expirations: int = None) -> None:
        super().__init__(underlying.code,
                         DataSeriesType.Option,
                         underlying.data_source)
        self.underlying = underlying

