#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 16:30:25 2018

@author: ilia
"""
import datetime
from typing import List
from collections import OrderedDict
from optopus.account import Account
from optopus.data_manager import DataManager, DataSource
from optopus.portfolio_manager import PortfolioManager
from optopus.order_manager import OrderManager
from optopus.watch_list import WATCH_LIST
from optopus.data_objects import AssetData, OptionData, PositionData


class Optopus():
    """Class implementing automated trading system"""

    def __init__(self, broker) -> None:
        self._broker = broker

    def start(self) -> None:
        print('[Initializating managers]')
        self._data_manager = DataManager(self._broker._data_adapter,
                                         WATCH_LIST)
        self._portfolio_manager = PortfolioManager(self._data_manager)
        self._order_manager = OrderManager(self._broker)

        # Events
        self._broker.emit_account_item_event = self._data_manager._account_item
        self._broker.emit_position_event = self._data_manager._position
        self._broker.emit_new_order = self._new_order
        self._broker.emit_order_status = self._order_status
        self._broker.emit_commission_report = self._data_manager._commission_report

        print('[Connecting to IB broker]')
        self._broker.connect()
        self._broker.sleep(1)

        print('[Adding underlyings]')
        self._data_manager.initialize_assets()
        self.update_assets()

        print('\n[Updating portfolio]')
        self._portfolio_manager.update_positions()

        print('\n[Started]\n')

        # self._beat()

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

    def _beat(self) -> None:
        # PIECE OF SHIT!!!!
        for t in self._broker._broker.timeRange(datetime.time(0, 0), datetime.datetime(2100, 1, 1, 0), 10):
            print('+')
        # self._data_manager.update_assets()
        # self.dummy.calculate_signals()



    def assets(self) -> List[AssetData]:
        return [a.current for a in self._data_manager._assets.values()]

    def asset_historical(self, code: str) -> List[OrderedDict]:
        return self._data_manager._assets[code]._historical_data

    def asset_historical_IV(self, code: str) -> List[OrderedDict]:
        return self._data_manager._assets[code]._historical_IV_data

    def assets_matrix(self, field: str) -> dict:
        return self._data_manager.assets_matrix(field)

    def update_assets(self):
        self._data_manager.update_current_assets()
        self._data_manager.update_historical_assets()
        self._data_manager.update_historical_IV_assets()
        self._data_manager.compute_assets()
    
    def update_positions(self):
        return(self._data_manager.update_positions())

    def option_chain(self, code: str) -> List[OptionData]:
        return self._data_manager._assets[code]._option_chain
    
    def update_option_chain(self, code: str) -> None:
        self._data_manager.update_option_chain(code)

    def positions(self) -> List[PositionData]:
        return [p for p in self._data_manager._positions.values()]

    def account(self) -> Account:
        return [self._data_manager._account]

    def portfolio(self) -> PortfolioManager:
        pass
        # return [self._portfolio_manager]
