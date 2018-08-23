# -*- coding: utf-8 -*-
import datetime
from typing import List
from collections import OrderedDict
import pickle
from pathlib import Path
from statistics import stdev
from optopus.data_objects import (DataSource,
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
        print('- Creating underlyings: ', end='')
        udas = self._data_adapters[DataSource.IB].create_underlyings(assets)
        for uda in udas:
                self._underlyings[uda.asset_id] = uda
                print('.', end='')

    def underlyings(self, fields: list) -> object:
        values_list = list()
        for u in self._underlyings.values():
            d = OrderedDict()
            d['code'] = getattr(u.current, 'code')

            for field in fields:
                if hasattr(u.current, field):
                    d[field] = getattr(u.current, field)
            values_list.append(d)
        return values_list

    def update_underlyings(self) -> None:
        print('\n- Retriving current data: ', end='')
        self._update_current_underlyings()
        print('\n- Retriving historical data: ', end='')
        self._update_historical_underlyings()
        print('\n- Retriving historical IV data: ', end='')
        self._update_historical_IV_underlyings()
        print('\n- Computing fields: ', end='')
        self._underlying_computation()

    def _update_current_underlyings(self) -> None:
        # All the underlyings retrieve the data from the same data_source
        udas = [uda for uda in self._underlyings.values()]
        uds = self._data_adapters[DataSource.IB].update_underlyings(udas)
        for ud in uds:
            self._underlyings[ud.asset_id].current = ud
            print('.', end='')

    def _update_historical_underlyings(self) -> None:
        for u in self._underlyings.values():
            if not u.historical_is_updated():
                u.historical = self._data_adapters[DataSource.IB].update_historical(u)
                u._historical_updated = datetime.datetime.now()
                print('.', end='')

    def _update_historical_IV_underlyings(self) -> None:
        for u in self._underlyings.values():
            if not u.historical_IV_is_updated():
                u.historical_IV = self._data_adapters[DataSource.IB].update_historical_IV(u)
                u._historical_IV_updated = datetime.datetime.now()
                print('.', end='')

    def _underlying_computation(self):
        for u in self._underlyings.values():
            #22 days = 1 month
            u.current.stdev = stdev([bd.bar_close for bd in u._historical_data[:-22]])
            #last historical value
            u.current.volume_h = u._historical_data[-1].bar_volume
            u.current.IV_h = u._historical_IV_data[-1].bar_close
            u.current.IV_rank_h = self._IV_rank(u, u.current.IV_h)
            u.current.IV_percentile_h = self._IV_percentile(u, u.current.IV_h)
            print('.', end='')

    def _IV_rank(self, uda: UnderlyingDataAsset, IV_value: float) -> float:
            min_IV_values = [b.bar_low for b in uda.historical_IV]
            max_IV_values = [b.bar_high for b in uda.historical_IV]
            IV_min = min(min_IV_values)
            IV_max = max(max_IV_values)
            IV_rank = (IV_value - IV_min) / (IV_max - IV_min) * 100
            return IV_rank
            
    def _IV_percentile(self, uda: UnderlyingDataAsset, IV_value: float) -> float:
            IV_values = [b.bar_low for b in uda.historical_IV if b.bar_low < IV_value]
            return len(IV_values) / HISTORICAL_DAYS * 100

    def _create_optionchain(self, uda: UnderlyingDataAsset) -> None:
        uda._option_chain = self._data_adapters[DataSource.IB].create_optionchain(uda)
        self._option_chain_computation(uda)
        print('.', end='')

    def option_chain(self, ua: UnderlyingAsset, fields: List[str]) -> List[OrderedDict]:
        uda = self._underlyings[ua.asset_id]
        self._create_optionchain(uda)
        values_list = list()
        for data in uda._option_chain:
            d = OrderedDict()
            d['code'] = getattr(data, 'code')
            d['expiration'] = getattr(data, 'expiration')
            d['strike'] = getattr(data, 'strike')
            d['right'] = getattr(data, 'right')
            for field in fields:
                if hasattr(data, field):
                    d[field] = getattr(data, field)
            values_list.append(d)
        return values_list

    def _option_chain_computation(self, uda: UnderlyingDataAsset) -> None:
        for od in uda._option_chain:
            od.DTE = (od.expiration - datetime.datetime.now().date()).days

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

    

            # If the asset is a Option, add others default fields
            #if data.asset_type == AssetType.Option:
            #    d['expiration'] = getattr(data, 'expiration')
            #    d['strike'] = getattr(data, 'strike')
            #    d['right'] = getattr(data, 'right')