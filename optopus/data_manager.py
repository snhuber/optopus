# -*- coding: utf-8 -*-
from enum import Enum
from optopus.data_objects import DataSource, DataSeries


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