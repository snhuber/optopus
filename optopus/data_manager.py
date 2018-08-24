# -*- coding: utf-8 -*-
import datetime
from typing import List
from collections import OrderedDict
import pickle
from pathlib import Path
from statistics import stdev
from optopus.data_objects import (DataSource,
                                  PositionData, TradeData, BarData,
                                  Asset, AssetData)
from optopus.settings import HISTORICAL_YEARS, DATA_DIR, STDEV_DAYS
from optopus.utils import is_nan, format_ib_date
from optopus.computation import calc_beta


# I dond't like this class
class DataAdapter:
    pass


class DataManager():
    def __init__(self,  watch_list: dict) -> None:
        self._assets = {code: Asset(code, asset_type)
                        for code, asset_type in watch_list.items()}
        self._catalog = {}
        self._data_adapters = {}
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

    def initialize_assets(self) -> None:
        # All the underlyings retrieve the data from the same data_source
        print('- Initializing underlyings: ', end='')
        data_source_ids = self._data_adapters[DataSource.IB].initialize_assets(self._assets.values())
        for i in data_source_ids:
                self._assets[i].data_source_id = data_source_ids[i]
                print('.', end='')

    def assets(self, fields: List[str]) -> List[OrderedDict]:
        values_list = list()
        for a in self._assets.values():
            values_list.append(a.current.to_dict(fields))
        return values_list

    def update_assets(self) -> None:
        print('\n- Retriving current data: ', end='')
        self._update_current_assets()
        print('\n- Retriving historical data: ', end='')
        self._update_historical_assets()
        print('\n- Retriving historical IV data: ', end='')
        self._update_historical_IV_assets()
        print('\n- Computing fields: ', end='')
        self._assets_computation()

    def _update_current_assets(self) -> None:
        # All the underlyings retrieve the data from the same data_source
        ads = self._data_adapters[DataSource.IB].update_assets(self._assets.values())
        for ad in ads:
            self._assets[ad.code].current = ad
            print('.', end='')

    def _update_historical_assets(self) -> None:
        for a in self._assets.values():
            if not a.historical_is_updated():
                a.historical = self._data_adapters[DataSource.IB].update_historical(a)
                a._historical_updated = datetime.datetime.now()
                print('.', end='')

    def _update_historical_IV_assets(self) -> None:
        for a in self._assets.values():
            if not a.historical_IV_is_updated():
                a.historical_IV = self._data_adapters[DataSource.IB].update_historical_IV(a)
                a._historical_IV_updated = datetime.datetime.now()
                print('.', end='')

    def _assets_computation(self):
        for a in self._assets.values(): 
            a.current.stdev = stdev([bd.bar_close for bd in a._historical_data[:(-1 * STDEV_DAYS)]])
            # last historical value
            a.current.volume_h = a._historical_data[-1].bar_volume
            a.current.IV_h = a._historical_IV_data[-1].bar_close
            a.current.IV_rank_h = self._IV_rank(a, a.current.IV_h)
            a.current.IV_percentile_h = self._IV_percentile(a, a.current.IV_h)
            print('.', end='')

        self._calculate_beta()

    def _IV_rank(self, ad: AssetData, IV_value: float) -> float:
            min_IV_values = [b.bar_low for b in ad.historical_IV]
            max_IV_values = [b.bar_high for b in ad.historical_IV]
            IV_min = min(min_IV_values)
            IV_max = max(max_IV_values)
            IV_rank = (IV_value - IV_min) / (IV_max - IV_min) * 100
            return IV_rank

    def _calculate_beta(self) -> None:
        for code, beta in calc_beta(self._assets_matrix('bar_close')).items():
            self._assets[code].current.beta = beta

    def _IV_percentile(self, ad: AssetData, IV_value: float) -> float:
            IV_values = [b.bar_low for b in ad.historical_IV if b.bar_low < IV_value]
            return len(IV_values) / (HISTORICAL_YEARS * 252) * 100

    def _create_optionchain(self, a: Asset) -> None:
        a._option_chain = self._data_adapters[DataSource.IB].create_optionchain(a)
        self._option_chain_computation(a)
        print('.', end='')

    def option_chain(self, code: str, fields: List[str]) -> List[OrderedDict]:
        a = self._assets[code]
        self._create_optionchain(a)
        values_list = list()
        for od in a._option_chain:
            values_list.append(od.to_dict(fields))
        return values_list

    def _option_chain_computation(self, a: Asset) -> None:
        for od in a._option_chain:
            od.DTE = (od.expiration - datetime.datetime.now().date()).days

    def asset_historic(self, code: str) -> List[OrderedDict]:
        return self._bar(self._assets[code]._historical_data)

    def asset_historic_IV(self, code: str) -> List[OrderedDict]:
        return self._bar(self._assets[code]._historical_IV_data)

    def _bar(self, bds: List[BarData]) -> List[OrderedDict]:
        bar_list = []
        for bd in bds:
            bar_list.append(bd.to_dict())
        return bar_list

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
        for position in self._data_positions.values():
            position_list.append(position.to_dict())
        return position_list

    def _assets_matrix(self, field: str) -> dict:
        d = {}
        for a in self._assets.values():
            d[a.code] = [getattr(bd, field) for bd in a._historical_data]
        return d
