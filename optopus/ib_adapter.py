#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  5 07:21:38 2018

@author: ilia
"""
# from ib_insync import *
import datetime
from enum import Enum

from ib_insync.ib import IB
from ib_insync.objects import AccountValue
from ib_insync import util

from money import Money
from currency import Currency

from account import AccountItem

from settings import p_currency

class IBObject(Enum):
    account = 'ACCOUNT'
    order = 'ORDER'


class IBAdapter:
    """Class implementing the Interactive Brokers interface"""

    def __init__(self, host: str, port: int, client: int=0) -> None:
        self._host = host
        self._port = port
        self._client = client

        self._translator = IBTranslator()
        self._broker = IB()

        # Callable objects. Optopus direcction
        self.emit_account_item_event = None
        self.execute_every_period = None

        # Cannect to ib_insync events
        self._broker.accountValueEvent += self._onAccountValueEvent

    def connect(self) -> None:
        self._broker.connect(self._host, self._port, self._client)
        for t in self._broker.timeRange(datetime.time(0, 0),
                                        datetime.datetime(2100, 1, 1, 0),
                                        10):
            self.execute_every_period()

    def disconnect(self) -> None:
        self._broker.disconnect()

    def sleep(self, time: float) -> None:
        util.sleep(time)

    def _onAccountValueEvent(self, item: AccountValue) -> None:
        account_item = self._translator.translate_from_IB(IBObject.account,
                                                          item.account,
                                                          item.tag,
                                                          item.value,
                                                          item.currency)
        if account_item.tag:  # item translated
            self.emit_account_item_event(account_item)


class IBTranslator:
    """Translate the IB tags and values to Ocptopus"""
    def __init__(self) -> None:
        self._account_translation = {'AccountCode': 'id',
                                     'AvailableFunds': 'funds',
                                     'BuyingPower': 'buying_power',
                                     'CashBalance': 'cash', 
                                     'DayTradesRemaining': 'max_day_trades'}

    def translate_from_IB(self,
                          ib_object: IBObject,
                          ib_account: str,
                          ib_tag: str,
                          ib_value: object,
                          ib_currency: str) -> AccountItem:
        # print(ib_tag, ' ', ib_value, ' ', ib_currency)
        if ib_object == IBObject.account:   
                opt_money = None
                opt_value = None
                
                opt_tag = self._translate_account_tag(ib_tag)              
                
                if ib_currency and is_number(ib_value):
                    opt_money = self._translate_value_currency(ib_value,
                                                               ib_currency)
                else: #for no money value.
                    opt_value = ib_value
                
                return AccountItem(ib_account, opt_tag, opt_value, opt_money)

    def _translate_account_tag(self, ib_tag: str) -> str:
            tag = None
            if ib_tag in self._account_translation:
                tag = self._account_translation[ib_tag]
            return tag

    def _translate_value_currency(self,
                                  ib_value: str,
                                  ib_currency: str) -> Money:
        m = None

        if ib_currency == p_currency:
            m = Money(ib_value, p_currency)

        return m


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except:
        return False
