# -*- coding: utf-8 -*-
from optopus.data_objects import DataSource, Asset, AssetType
import collections


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
        data_assets = list()
        if not isinstance(assets, list):
            #if only receive one asset
            assets = [assets]
        
        # All the assests have the same type
        if not all([t.asset_type == assets[0].asset_type for t in assets]):
            raise ValueError('There are more than one type of asset')
        
        for asset in assets:
            data = self._data_adapters[asset.data_source].current(asset)
            for e in data:
                data_assets.append(e)

        values_list = list()
        for data in data_assets:
            d = collections.OrderedDict()
            d['code'] = getattr(data, 'code')
            # If the asset is a Option, add others default fields
            if data.asset_type == AssetType.Option:
                d['expiration'] = getattr(data, 'expiration')
                d['strike'] = getattr(data, 'strike')
                d['right'] = getattr(data, 'right')
                
            for field in fields:
                if hasattr(data, field):
                  d[field] = getattr(data, field)
            values_list.append(d)
            
        return values_list