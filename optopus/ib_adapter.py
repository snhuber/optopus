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
from ib_insync.contract import Index, Stock, Option
from ib_insync.objects import AccountValue
from ib_insync import util

from account import AccountItem
from money import Money
from data_manager import DataSeries, DataSeriesType, DataAdapter
from settings import p_currency


class IBObject(Enum):
    account = 'ACCOUNT'
    order = 'ORDER'


class IBBrokerAdapter:
    """Class implementing the Interactive Brokers interface"""

    def __init__(self, ib: IB) -> None:
        

        self._broker = ib
        self._translator = IBTranslator()
        self._data_adapter = IBDataAdapter(self._broker)

        # Callable objects. Optopus direcction
        self.emit_account_item_event = None
        self.execute_every_period = None

        # Cannect to ib_insync events
        self._broker.accountValueEvent += self._onAccountValueEvent

    def sleep(self, time: float) -> None:
        self._broker.sleep(time)

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
                else:  # for no money value.
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


class IBDataAdapter(DataAdapter):
    def __init__(self, broker: IB) -> None:
        self._broker = broker
        self._data_series = {}
        self._contracts = {}

    def connect_data_series(self, ds: DataSeries) -> bool:
        if ds.data_series_type == DataSeriesType.Index:
           self._connect_data_series_index(ds)
        elif ds.data_series_type == DataSeriesType.Option:
           self._connect_data_series_options(ds) 
        

    def _connect_data_series_index(self, ds: DataSeries) -> bool:
        started = False
        idx = ds.code + '_' + ds.data_series_type.value
        if idx not in self._data_series:
                contract = Index(ds.code)
                q_contract = self._broker.qualifyContracts(contract)

                if len(q_contract) == 1:
                    self._data_series[idx] = {'data_series': ds,
                                              'contract': q_contract[0]}
                    started = True
                else:
                    raise(ValueError, 'Error: multiple contracts')
        return started

    def _connect_data_series_options(self, ds: DataSeries) -> bool:
        started = False
        idx = ds.code + '_' + ds.data_series_type.value
        if idx not in self._data_series:
                if ds.data_series_type_underlying == DataSeriesType.Index:           
                    #Create the underlying contract
                    contract = Index(ds.code)
                    q_contract = self._broker.qualifyContracts(contract)
                    
                    if len(q_contract) == 1:
                        chains = self._broker.reqSecDefOptParams(
                                q_contract[0].symbol,
                                '',
                                q_contract[0].secType,
                                q_contract[0].conId)
                        
                        self._data_series[idx] = {'data_series': ds,
                                                  'contract': q_contract[0],
                                                  'chains': chains}
                        started = True
                    else:
                        raise(ValueError, 'Error: multiple contracts')
        return started

    def disconnect_data_series(self) -> bool:
        pass

    def ticket(self, ds: DataSeries) -> DataSeries:
        idx = ds.code + '_' + ds.data_series_type.value
        print(idx)
        t = self._broker.reqTickers(self._data_series[idx]['contract'])
        if ds.data_series_type == DataSeriesType.Option:
            print ('CHAINS: ',self._data_series[idx]['chains'])

def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except:
        return False
