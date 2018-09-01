# -*- coding: utf-8 -*-
import datetime
from typing import List
from collections import OrderedDict
import pickle
from pathlib import Path
from statistics import stdev
from optopus.account import Account, AccountItem
from optopus.data_objects import (DataSource,
                                  PositionData, TradeData, BarData,
                                  Asset, AssetData, OptionData,
                                  AssetType, OwnershipType, OptionRight)
from optopus.settings import HISTORICAL_YEARS, DATA_DIR, STDEV_DAYS
from optopus.utils import is_nan, format_ib_date
from optopus.computation import calc_beta, calc_correlation, calc_stdev
from optopus.strategy import StrategyFactory


# I dond't like this class
class DataAdapter:
    pass


class DataManager():
    def __init__(self,  data_adapter: DataAdapter, watch_list: dict) -> None:
        self._account = Account()
        self._assets = {code: Asset(code, asset_type)
                        for code, asset_type in watch_list.items()}
        #self._catalog = {}
        #self._data_adapters = {}
        self._positions = {}
        self._strategies = {}
        self._da = data_adapter

    def _account_item(self, item: AccountItem) -> None:
        try:
            self._account.update_item_value(item)
        except Exception as e:
            print('Error updating account item', e)

    def _position(self, position: PositionData) -> None:
        key = self._position_key(position.code,
                                 position.asset_type,
                                 position.expiration,
                                 position.strike,
                                 position.right,
                                 position.ownership)

        self._positions[key] = position

    def _commission_report(self, trade: TradeData) -> None:
        self._add_trade(trade)

    def _add_trade(self, trade: TradeData) -> None:
        key = self._position_key(trade.code,
                                 trade.asset_type,
                                 trade.expiration,
                                 trade.strike,
                                 trade.right,
                                 trade.ownership)
        pos = self._positions[key]
        pos.trades.append(trade)
        self._write_positions()

    def _position_key(self,
                      code: str,
                      asset_type: AssetType,
                      expiration: datetime.date,
                      strike: float,
                      right: OptionRight,
                      ownership: OwnershipType):

        ownership = ownership.value if ownership else 'NA'
        expiration = format_ib_date(expiration) if expiration else 'NA'
        strike = str(strike) if not is_nan(strike) else 'NA'
        right = right.value if right else 'NA'

        key = code + '_' + asset_type.value + '_' \
            + expiration + '_' + strike + '_' + right + '_' + ownership

        return key

    def _write_positions(self) -> None:
        file_name = Path.cwd() / DATA_DIR / "positions.pckl"
        with open(file_name, 'wb') as file_handler:
                pickle.dump(self._positions, file_handler)

    def initialize_assets(self) -> None:
        # All the underlyings retrieve the data from the same data_source
        print('- Initializing underlyings:\t', end='')
        data_source_ids = self._da.initialize_assets(self._assets.values())
        for i in data_source_ids:
                self._assets[i].data_source_id = data_source_ids[i]
                print('.', end='')

    def assets(self, fields: List[str]) -> List[OrderedDict]:
        values_list = list()
        for a in self._assets.values():
            values_list.append(a.current.to_dict(fields))
        return values_list

    def update_assets(self) -> None:
        print('\n- Retriving current data:\t', end='')
        self._update_current_assets()
        print('\n- Retriving historical data:\t', end='')
        self._update_historical_assets()
        print('\n- Retriving historical IV data:\t', end='')
        self._update_historical_IV_assets()
        print('\n- Computing fields:\t\t', end='')
        self._assets_computation()

    def _update_current_assets(self) -> None:
        # All the underlyings retrieve the data from the same data_source
        ads = self._da.update_assets(self._assets.values())
        for ad in ads:
            self._assets[ad.code].current = ad
            print('.', end='')

    def _update_historical_assets(self) -> None:
        for a in self._assets.values():
            if not a.historical_is_updated():
                a.historical = self._da.update_historical(a)
                a._historical_updated = datetime.datetime.now()
                print('.', end='')

    def _update_historical_IV_assets(self) -> None:
        for a in self._assets.values():
            if not a.historical_IV_is_updated():
                a.historical_IV = self._da.update_historical_IV(a)
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
            a.current.one_month_return = (a._historical_data[-1].bar_close - a._historical_data[-22].bar_close) / a._historical_data[-22].bar_close
            print('.', end='')

        close_matrix = self._assets_matrix('bar_close')
        # Calculate beta
        beta = calc_beta(close_matrix)
        for code, value in beta.items():
            self._assets[code].current.beta = value
        # Calculate correlation
        correlation = calc_correlation(close_matrix)
        for code, value in correlation.items():
            self._assets[code].current.correlation = value
        # Calculate standard desviation
        correlation = calc_stdev(close_matrix)
        for code, value in correlation.items():
            self._assets[code].current.stdev = value


    def _IV_rank(self, ad: AssetData, IV_value: float) -> float:
            min_IV_values = [b.bar_low for b in ad.historical_IV]
            max_IV_values = [b.bar_high for b in ad.historical_IV]
            IV_min = min(min_IV_values)
            IV_max = max(max_IV_values)
            IV_rank = (IV_value - IV_min) / (IV_max - IV_min)
            return IV_rank

    def _IV_percentile(self, ad: AssetData, IV_value: float) -> float:
            IV_values = [b.bar_low for b in ad.historical_IV if b.bar_low < IV_value]
            return len(IV_values) / (HISTORICAL_YEARS * 252)

    #def _create_optionchain(self, a: Asset) -> None:
    #    a._option_chain = self._da.create_optionchain(a)
    #    self._option_chain_computation(a)
    #    print('.', end='')

    def option_chain(self, code: str, fields: List[str]) -> List[OrderedDict]:
        a = self._assets[code]
        self._create_optionchain(a)
        values_list = list()
        for od in a._option_chain:
            values_list.append(od.to_dict(fields))
        return values_list

    #def update_option(self, q_contracts: List[object]) -> List[OptionData]:
    #    return self._da.create_options(q_contracts)
        
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
        try:
            with open(file_name, 'rb') as file_handler:
                positions_bk = pickle.load(file_handler)
                for k, p in self._positions.items():
                    if k in positions_bk.keys():
                        if positions_bk[k].trades:
                            p.trades = positions_bk[k].trades

                self._write_positions()
        except FileNotFoundError as e:
            print('positions.pckl not found')

    def update_positions(self):
        trades = [p.trades[-1] for p in self._positions.values() if p.trades]
        
        for trade in trades:
            [option] = self._da.create_options([trade.data_source_id])
            key = self._position_key(option.code,
                                     option.asset_type,
                                     option.expiration,
                                     option.strike,
                                     option.right,
                                     trade.ownership)

            position = self._positions[key]
            position.option_price = option.option_price
            position.underlying_price = option.underlying_price
            position.delta = option.delta
            position.DTE = option.DTE
            position.trade_price = trade.price
            position.trade_time = trade.time
            position.algorithm = trade.algorithm
            position.strategy_type = trade.strategy_type
            position.strategy_id = trade.strategy_id
            position.rol = trade.rol
            position.beta = self._assets[option.code].current.beta

    def update_strategies(self):
        for k, p in self._positions.items():
            if p.strategy_id not in self._positions.keys():
                s = StrategyFactory.create_strategy(p.strategy_type,
                                                    p.strategy_id)
                self._strategies[s] = s
            
            s.add_position(p)


    def positions(self) -> object:
        position_list = list()
        for position in self._positions.values():
            position_list.append(position.to_dict())
        return position_list

    def _assets_matrix(self, field: str) -> dict:
        d = {}
        for a in self._assets.values():
            d[a.code] = [getattr(bd, field) for bd in a._historical_data]
        #print([len(i) for i in d.values()])
        return d

    def account(self) -> OrderedDict:
        return self._account.to_dict()
