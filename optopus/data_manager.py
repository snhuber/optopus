# -*- coding: utf-8 -*-
from typing import List
from collections import OrderedDict
import pickle
from pathlib import Path
from optopus.data_objects import (DataSource, Asset, AssetType, BarDataType, 
                                  OptionChainDataAsset,
                                  PositionData, TradeData,
                                  UnderlyingAsset, UnderlyingDataAsset)
from optopus.settings import HISTORICAL_DAYS, DATA_DIR
from optopus.utils import nan, is_nan, parse_ib_date, format_ib_date



class DataAdapter():
    pass


class DataManager():
    def __init__(self) -> None:
        self._catalog = {}
        self._data_adapters = {}
        self._underlyings = {}
        self._data_positions = {}

    def add_data_adapter(self,
                         data_adapter: DataAdapter,
                         data_source: DataSource) -> None:
        self._data_adapters[data_source] = data_adapter

    def _position(self, p: PositionData) -> None:
        ownership = p.ownership.value if p.ownership else 'NA'
        expiration = format_ib_date(p.expiration) if p.expiration else 'NA'
        strike = str(p.strike) if not is_nan(p.strike) else 'NA'
        right = p.right.value if p.right else 'NA'

        key = p.code + '_' + p.asset_type.value + '_' \
            + expiration + '_' + strike + '_' + right + '_' + ownership

        self._data_positions[key] = p

    def _commission_report(self, trade: TradeData) -> None:
        self._add_trade(trade)

    def _add_trade(self, trade: TradeData) -> None:
        ownership = trade.ownership.value if trade.ownership else 'NA'
        expiration = format_ib_date(trade.expiration) if trade.expiration else 'NA'
        strike = str(trade.strike) if not is_nan(trade.strike) else 'NA'
        right = trade.right.value if trade.right else 'NA'

        key = trade.code + '_' + trade.asset_type.value + '_' \
            + expiration + '_' + strike + '_' + right + '_' + ownership

        pos = self._data_positions[key]
        pos.trades.append(trade)
        self._write_positions()

    def _write_positions(self) -> None:
        file_name = Path.cwd() / DATA_DIR / "positions.pckl"
        with open(file_name, 'wb') as file_handler:
                pickle.dump(self._data_positions, file_handler)

    def create_underlyings(self, assets: list) -> None:
        # All the underlyings retrieve the data from the same data_source
        udas = self._data_adapters[DataSource.IB].create_underlyings(assets)
        for uda in udas:
                self._underlyings[uda.asset_id] = uda

    def _update_underlyings(self) -> None:
        # All the underlyings retrieve the data from the same data_source
        udas = [uda for uda in self._underlyings.values()]
        uds = self._data_adapters[DataSource.IB].update_underlyings(udas)
        for ud in uds:
            self._underlyings[ud.asset_id].current = ud
            
    def _update_historical_underlyings(self) -> None:
        for u in self._underlyings.values():
            if not u.historical_is_updated():
                u.historical = self._data_adapters[DataSource.IB].update_historical(u)

    def _update_historical_IV_underlyings(self) -> None:
        for u in self._underlyings.values():
            if not u.historical_IV_is_updated():
                u.historical_IV = self._data_adapters[DataSource.IB].update_historical_IV(u)


    def match_trades_positions(self) -> None:
        file_name = Path.cwd() / DATA_DIR / "positions.pckl"
        with open(file_name, 'rb') as file_handler:
                positions_bk = pickle.load(file_handler)

        for k, p in self._data_positions.items():
            if k in positions_bk.keys():
                if positions_bk[k].trades:
                    p.trades = positions_bk[k].trades
 
        self._write_positions()

    def positions(self) -> object:
        position_list = list()
        for k, position in self._data_positions.items():
            d = OrderedDict()
            d['code'] = position.code
            d['asset_type'] = position.asset_type.value
            d['expiration'] = position.expiration
            d['strike'] = position.strike
            d['right'] = position.right.value
            d['ownership'] = position.ownership.value
            d['quantity'] = position.quantity
            d['average_cost'] = position.average_cost
            position_list.append(d)
        return position_list


    def underlyings(self, fields: list) -> object:
        self._update_underlyings()
        self._update_historical_underlyings()
        self._update_historical_IV_underlyings()
        self._underlying_computation()
        
        values_list = list()
        for u in self._underlyings.values():
            d = OrderedDict()
            d['code'] = getattr(u.current, 'code')       
        
            for field in fields:
                if hasattr(u.current, field):
                  d[field] = getattr(u.current, field)
            values_list.append(d)           
        return values_list


    def _underlying_computation(self):
        for u in self._underlyings.values():
            u.current.IV_rank = self._IV_rank(u, u.current.market_price)
            u.current.IV_percentile = self._IV_percentile(u, u.current.market_price)

    def _IV_rank(self, uda: UnderlyingDataAsset, IV_value: float) -> float:
            #data_asset = self._data_assets[asset.asset_id]
            min_IV_values = [b.bar_low for b in uda.historical_IV]
            max_IV_values = [b.bar_high for b in uda.historical_IV]
            IV_min = min(min_IV_values) 
            IV_max = max(max_IV_values)
            IV_rank = (IV_value -IV_min) / (IV_max - IV_min) * 100
            return IV_rank
            
    def _IV_percentile(self, uda: UnderlyingDataAsset, IV_value: float) -> float:
            #data_asset = self._data_assets[asset.asset_id]
            IV_values = [b.bar_low for b in uda.historical_IV if b.bar_low < IV_value]
            return len(IV_values) / HISTORICAL_DAYS * 100

            # If the asset is a Option, add others default fields
            #if data.asset_type == AssetType.Option:
            #    d['expiration'] = getattr(data, 'expiration')
            #    d['strike'] = getattr(data, 'strike')
            #    d['right'] = getattr(data, 'right')