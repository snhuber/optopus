# -*- coding: utf-8 -*-
from optopus.data_objects import (DataSource, Asset, AssetType, BarDataType, 
                                  IndexDataAsset, OptionChainDataAsset)
from optopus.settings import HISTORICAL_DAYS
import collections


class DataAdapter():
    pass


class DataManager():
    def __init__(self) -> None:
        self._catalog = {}
        self._data_adapters = {}
        self._data_assets = {}

    def add_data_adapter(self,
                         data_adapter: DataAdapter,
                         data_source: DataSource) -> None:
        self._data_adapters[data_source] = data_adapter

    def _register_data_asset(self, asset: Asset) -> bool:
        
        if asset.asset_type == AssetType.Index:
            self._data_adapters[asset.data_source].register_index(asset)
            self._data_assets[asset.asset_id] = IndexDataAsset(asset.code, asset.data_source)
        elif asset.asset_type == AssetType.Option:
            self._data_adapters[asset.data_source].register_option(asset)
            self._data_assets[asset.asset_id] = OptionDataAsset(asset.underlying, asset.n_expiration_dates, asset.underlying_distance)

    #def update_assets(self) -> None:
    #    for da in self._data_adapters:
    #        self._data_adapters[da].update_assets()

    def current(self, assets: list, fields: list) -> object:
        data_assets = list()
        if not isinstance(assets, list):
            #if only receive one asset
            assets = [assets]
        
        # All the assests have the same type
        if not all([t.asset_type == assets[0].asset_type for t in assets]):
            raise ValueError('There are more than one type of asset')

        for asset in assets:
            if asset.asset_id not in self._data_assets:
                self._register_data_asset(asset)

            if asset.asset_type == AssetType.Index:
                self._data_assets[asset.asset_id].current_data = self._data_adapters[asset.data_source].fetch_current_data_index(asset)
            if asset.asset_type == AssetType.Option:
                self._data_assets[asset.asset_id].current_data = self._data_adapters[asset.data_source].fetch_current_data_option(asset)
            
            for e in self._data_assets[asset.asset_id].current_data:
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
    
    def historical(self,
                   assets: list,
                   fields: list,
                   bar_type: BarDataType) -> object:
        
        data_assets = list()
        if not isinstance(assets, list):
            #if only receive one asset
            assets = [assets]
        
        # All the assests have the same type
        if not all([t.asset_type == assets[0].asset_type for t in assets]):
            raise ValueError('There are more than one type of asset')

        for asset in assets:
            if asset.asset_id not in self._data_assets:
                self._register_data_asset(asset)
            if bar_type == BarDataType.Trades:
                self._data_assets[asset.asset_id].historical_data = self._data_adapters[asset.data_source].fetch_historical_data_asset(asset)
                data = self._data_assets[asset.asset_id].historical_data
                #data = self._data_adapters[asset.data_source].historical(asset)
                #self._data_assets[asset.asset_id].historical_data = data
            elif bar_type == BarDataType.IV:
                self._data_assets[asset.asset_id].historical_IV_data = self._data_adapters[asset.data_source].fetch_historical_IV_data_asset(asset)
                data = self._data_assets[asset.asset_id].historical_IV_data
                #data = self._data_adapters[asset.data_source].historical_IV(asset)
                #self._data_assets[asset.asset_id].historial_IV_data = data        
            for e in data:
                data_assets.append(e)

        values_list = list()
        for data in data_assets:
            d = collections.OrderedDict()
            d['code'] = getattr(data, 'code')
            for field in fields:
                if hasattr(data, field):
                    d[field] = getattr(data, field)
            values_list.append(d)

        return values_list

    def IV_rank(self, asset: Asset, IV_value: float) -> float:
            data_asset = self._data_assets[asset.asset_id]    
            min_IV_values = [b.bar_low for b in data_asset.historical_IV_data]
            max_IV_values = [b.bar_high for b in data_asset.historical_IV_data]
            IV_min = min(min_IV_values) 
            IV_max = max(max_IV_values)
            IV_rank = (IV_value -IV_min) / (IV_max - IV_min) * 100
            return IV_rank
            
    def IV_percentile(self, asset: Asset, IV_value: float) -> float:
            data_asset = self._data_assets[asset.asset_id]
            IV_values = [b.bar_low for b in data_asset.historical_IV_data if b.bar_low < IV_value]
            return len(IV_values) / HISTORICAL_DAYS * 100

            