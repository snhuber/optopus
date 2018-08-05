#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  5 07:21:38 2018

@author: ilia
"""
# from ib_insync import *
from enum import Enum

from ib_insync.ib import IB
from ib_insync.objects import AccountValue
from ib_insync import util

from account import AccountItem

class IBObject(Enum):
    account = 'ACCOUNT'
    order = 'ORDER'



class IBBroker:
    """Class implementing the Interactive Brokers interface"""

    def __init__(self, host: str, port: int, client: int=0) -> None:
        self._host = host
        self._port = port
        self._client = client

        self._translator = IBTranslator()
        self._broker = IB()

        # Callable objects. Optopus direcction
        self.emit_account_item_event = None

        # Cannect to ib_insync events
        self._broker.accountValueEvent += self._onAccountValueEvent

    def connect(self) -> None:
        self._broker.connect(self._host, self._port, self._client)

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
        if account_item.tag:
            self.emit_account_item_event(account_item)


class IBTranslator:
    """Translate the IB tags and values to Ocptopus"""
    def __init__(self) -> None:
        self._account_translation = {'AccountCode': 'id'}

    def translate_from_IB(self,
                          ib_object: IBObject,
                          ib_account: str,
                          ib_tag: str,
                          ib_value: object,
                          ib_currency: str) -> AccountItem:

        if ib_object == IBObject.account:         
                return AccountItem(ib_account,
                                   self._translate_account_tag(ib_tag),
                                   ib_value,
                                   ib_currency)

    def _translate_account_tag(self, ib_tag: str) -> str:
            tag = None
            if ib_tag in self._account_translation:
                tag = self._account_translation[ib_tag]
            return tag
