#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 16:30:25 2018

@author: ilia
"""
from account import Account, AccountItem
from data_manager import DataManager, DataSource
from strategy import DummyStrategy

class Optopus():
    """Class implementing automated trading system"""

    def __init__(self, broker) -> None:
        self._broker = broker
        self._account = Account()
        # Events
        self._broker.emit_account_item_event = self._change_account_item
        
        
        self._data_manager = DataManager()
        self._data_manager.add_data_adapter(self._broker._data_adapter,
                                            DataSource.IB)
        
        #strategies
        

    def start(self) -> None:
        self._start_strategies()
        
    def stop(self) -> None:
        pass

    def pause(self, time: float) -> None:
        self._broker.sleep(time)

    def _start_strategies(self) -> None:
        self.dummy = DummyStrategy(self._data_manager)

    def _change_account_item(self, item: AccountItem) -> None:
        try:
            self._account.update_item_value(item)
        except Exception as e:
            print('Error updating account item', e)

    def beat(self) -> None:
        print('.')
        self._data_manager.update_data_series()
        self.dummy.calculate_signals()






