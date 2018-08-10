# -*- coding: utf-8 -*-
from enum import Enum


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


class DataSeries():
    def __init__(self,
                 code: str,
                 data_series_type: DataSeriesType,
                 data_series_type_underlying: DataSeriesType,
                 data_source: DataSource,
                 historic: bool=False) -> None:
        self.code = code
        self.data_series_type = data_series_type
        self.data_series_type_underlying = data_series_type_underlying
        self.data_source = data_source
        self._historic = historic


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

    def start_data_series(self, ds: DataSeries) -> bool:
        if self._data_adapters[ds.data_source].connect_data_series(ds):
            self._catalog[ds.code] = ds
            return True
        else:
            False

    def stop_data_series(self, ds: DataSeries) -> bool:
        if self._data_adapters[ds.data_source].disconnect_data_series(ds):
            del self._catalog[ds.code]
            return True
        else:
            False

    def ticket(self, ds: DataSeries) -> DataSeries:
        if ds.code not in self._catalog:
            self.start_data_series(ds)
        self._data_adapters[ds.data_source].ticket(ds)
