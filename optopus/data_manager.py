# -*- coding: utf-8 -*-
from optopus.data_objects import DataSource, Asset


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

    def update_assets(self) -> None:
        for da in self._data_adapters:
            self._data_adapters[da].update_assets()
    
    def current(self, assets: Asset, fields: list) -> object:
        nan = float('nan')
        data_assets=[]
        if not isinstance(assets, list):
            assets = [assets]
        
        for asset in assets:
            data = self._data_adapters[asset.data_source].current(asset)
            data_assets.append(data)
            
        values_list=[]
        for data in data_assets:
            d = {}
            d['code'] = getattr(data, 'code')
            for field in fields:
                if hasattr(data, field):
                  d[field] = getattr(data, field)
                else:
                    d[field] = nan
            values_list.append(d)
            
        return values_list