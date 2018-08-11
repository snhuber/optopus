# -*- coding: utf-8 -*-
from enum import Enum

nan = float('nan') 


def is_nan(x: float) -> bool:
    """
    Not a number test.
    """
    return x != x

class DataSource(Enum):
    IB = 'IB'
    Quandl = 'Quandl'


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

class DataIndex():
    def __init__(self,               
                 last=nan,
                 last_size=nan,
                 high=nan,
                 low=nan,
                 close=nan,
                 bid=nan,
                 bid_size=nan,
                 ask=nan,
                 ask_size=nan,
                 time=None) -> None:
        self.last = last
        self.last_size = last_size
        self.high = high
        self.low = low
        self.close = close
        self.bid = bid
        self.bid_size = bid_size
        self.ask = ask
        self.ask_size = ask_size
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


class DataOption():
    pass

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


class DataSeriesOption_old(DataSeries):
    def __init__(self,
                 code: str,
                 data_source: DataSource,
                 data_series_type_underlying: DataSeriesType,
                 max_expirations: int = None) -> None:
        super().__init__(code, DataSeriesType.Option, data_source)
        self.data_series_type_underlying = data_series_type_underlying

class DataSeriesOption(DataSeries):
    def __init__(self, 
                 underlying: DataSeries,
                 max_expirations: int = None) -> None:
        super().__init__(underlying.code,
                         DataSeriesType.Option,
                         underlying.data_source)
        self.underlying = underlying


class DataAdapter():
    pass


class DataManager():
    def __init__(self) -> None:
        self._catalog = {}
        self._data_adapters = {}

    def add_data_adapter(self,
                         data_adapter: DataAdapter,
                         data_source: DataSource) -> None:
        self._data_adapters[data_source] = data_adapter

    def update_data_series(self) -> None:
        for da in self._data_adapters:
            self._data_adapters[da].update_data_series()

    def data(self, ds: DataSeries) -> list:
        l = self._data_adapters[ds.data_source].data(ds)
        return l