#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 16:30:25 2018

@author: ilia
"""
from optopus.account import Account, AccountItem


class Optopus():
    """Class implementing automated trading system"""

    def __init__(self, broker) -> None:
        self._broker = broker
        self._account = Account()
        # Events
        self._broker.emit_account_item_event = self._change_account_item

    def start(self) -> None:
        self._broker.connect()

    def stop(self) -> None:
        self._broker.disconnect()

    def pause(self, time: float) -> None:
        self._broker.sleep(time)

    def _change_account_item(self, item: AccountItem) -> None:
        try:
            self._account.update_item_value(item)
        except Exception as e:
            print('Error updating account item', e)








