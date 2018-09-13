#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 16:30:25 2018

@author: ilia
"""
import datetime
from typing import List, Callable
from collections import OrderedDict
import logging
from optopus.data_manager import DataManager
from optopus.portfolio_manager import PortfolioManager
from optopus.order_manager import OrderManager
from optopus.watch_list import WATCH_LIST
from optopus.data_objects import AssetData, OptionData, PositionData, Strategy
from optopus.settings import SLEEP_LOOP


class Optopus():
    """Class implementing automated trading system"""

    def __init__(self, broker) -> None:
        self._broker = broker
        self._algorithms = []
        self._log = logging.getLogger(__name__)

    def start(self) -> None:
        self._data_manager = DataManager(self._broker._data_adapter,
                                         WATCH_LIST)
        self._portfolio_manager = PortfolioManager(self._data_manager)
        self._order_manager = OrderManager(self._broker, self._data_manager)

        # Events
        #self._broker.emit_account_item_event = self._data_manager._account_item
        #self._broker.emit_position_event = self._data_manager._position
        #self._broker.emit_new_order = self._new_order
        self._broker.emit_order_status = self._order_manager.order_status_changed
        #self._broker.emit_commission_report = self._data_manager._commission_report

        self._log.debug('Connecting to IB broker')
        self._broker.connect()
        self._broker.sleep(1)
        
        self._data_manager.update_account()

        self._log.debug('Retrieving underling data')
        self._data_manager.initialize_assets()
        self.update_assets()

        self._log.info('System started')
        self._loop()

    def stop(self) -> None:
        self._broker.disconnect()

    def pause(self, time: float) -> None:
        self._broker.sleep(time)

    def _loop(self) -> None:
        for t in self._broker._broker.timeRange(datetime.time(0, 0), datetime.datetime(2100, 1, 1, 0), 10):
            self._data_manager.check_strategy_positions()
            self._data_manager.update_strategy_options()
            for algorithm in self._algorithms:
                algorithm()
            self._broker.sleep(SLEEP_LOOP)

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

    def option_chain(self, code: str) -> List[OptionData]:
        return self._data_manager._assets[code]._option_chain
    
    def register_algorithm(self, algo: Callable[[], None]) -> None:
        self._algorithms.append(algo)
    
    def new_strategy(self, strategy: Strategy) -> None:
        self._data_manager.add_strategy(strategy)
        self._order_manager.execute_new_strategy(strategy)