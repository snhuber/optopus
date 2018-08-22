#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 16:30:25 2018

@author: ilia
"""
from typing import List
from collections import OrderedDict
from optopus.account import Account, AccountItem
from optopus.data_manager import DataManager, DataSource
from optopus.data_objects import Asset, BarDataType
from optopus.portfolio_manager import PortfolioManager
from optopus.order_manager import OrderManager

class Optopus():
    """Class implementing automated trading system"""

    def __init__(self, broker, assets: list) -> None:
        self._broker = broker
        self._account = Account()
        self._universe = assets
        
    def start(self) -> None:
        print('[Initializating managers...]')
        self._data_manager = DataManager()
        self._data_manager.add_data_adapter(self._broker._data_adapter,
                                            DataSource.IB)
        self._portfolio_manager = PortfolioManager(self._data_manager)
        self._order_manager = OrderManager(self._broker)

        print('[Starting event listeners...]')
        self._broker.emit_account_item_event = self._change_account_item
        self._broker.emit_position_event = self._data_manager._position
        self._broker.emit_new_order = self._new_order
        self._broker.emit_order_status = self._order_status
        self._broker.emit_commission_report = self._data_manager._commission_report

        print('[Connecting to IB broker...]')
        self._broker.connect()
        self._broker.sleep(1)

        print('[Updating values...]')
        self._data_manager.match_trades_positions()
        self._data_manager.create_underlyings(self._universe)

    def stop(self) -> None:
        self._broker.disconnect()

    def pause(self, time: float) -> None:
        self._broker.sleep(time)

    def process(self, signals) -> None:
        self._order_manager.process(signals)

    def _new_order(self) -> None:
        pass

    def _order_status(self) -> None:
        pass

    def _change_account_item(self, item: AccountItem) -> None:
        try:
            self._account.update_item_value(item)
        except Exception as e:
            print('Error updating account item', e)

    def beat(self) -> None:
        print('.')
        self._data_manager.update_assets()
        self.dummy.calculate_signals()
        
    def positions(self) -> object:
        return self._portfolio_manager.positions()

    def current(self, assets: Asset, fields: list) -> object:
        return self._data_manager.current(assets, fields)

    def underlyings(self, fields: List[str]) -> List[OrderedDict]:
        return (self._data_manager.underlyings(fields))

    def historical(self, assets: list, fields: list) -> object:
        return self._data_manager.historical(assets, fields, BarDataType.Trades)
    
    def historical_IV(self, assets: list, fields: list) -> object:
        return self._data_manager.historical(assets, fields, BarDataType.IV)
    
    def IV_rank(self, asset: Asset, IV_value: float) -> float:
        return self._data_manager.IV_rank(asset, IV_value)
    
    def IV_percentile(self, asset: Asset, IV_value: float) -> float:
        return self._data_manager.IV_percentile(asset, IV_value)
        
