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
from ib_insync.objects import AccountValue, OptionComputation
from ib_insync.contract import Contract

from optopus.account import AccountItem
from optopus.money import Money
from optopus.data_manager import (DataSeriesType, DataAdapter, DataSeries, 
                          DataSeriesIndex, DataSeriesOption,
                          DataIndex, DataOption, OptionIndicators,
                          DataOptionChain, OptionRight, nan)
from optopus.settings import CURRENCY


class IBObject(Enum):
    account = 'ACCOUNT'
    order = 'ORDER'

class IBSeries():
    def __init__(self,
                 series_type: DataSeriesType,
                 contract: Contract,
                 ibs_underlying_id: str = None) -> None:
        self.series_type = series_type
        self.contract = contract
        self.data = []
        self.ibs_underlying_id = ibs_underlying_id


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

        if ib_currency == CURRENCY:
            m = Money(ib_value, CURRENCY)

        return m


class IBDataAdapter(DataAdapter):
    def __init__(self, broker: IB) -> None:
        self._broker = broker
        self._series = {}
        self._contracts = {}

    def connect_data_series(self, ds: DataSeries) -> bool:
        if ds.data_series_type == DataSeriesType.Index:
           self._connect_data_series_index(ds)
        elif ds.data_series_type == DataSeriesType.Option:
           self._connect_data_series_options(ds) 
        

    def _connect_data_series_index(self, ds: DataSeriesIndex) -> bool:
        started = False
        if ds.data_series_id not in self._series:
                contract = Index(ds.code)
                q_contract = self._broker.qualifyContracts(contract)
                if len(q_contract) == 1:
                    #create a new series object and add to series dict
                    ibs = IBSeries(series_type=ds.data_series_type,
                                   contract=q_contract[0])
                    self._series[ds.data_series_id] = ibs
                    #self._data_series[idx] = {'data_series': ds,
                    #                          'contract': q_contract[0]}
                    started = True
                else:
                    raise ValueError('Error: multiple contracts')
        return started

    def _connect_data_series_options(self, ds: DataSeriesOption) -> bool:
        if ds.data_series_id not in self._series:
            # if the underlying doesn't exists
            if ds.underlying.data_series_id not in self._series:
                self.connect_data_series(ds.underlying)

            ibs = IBSeries(series_type=ds.data_series_type,
                          contract=self._series[ds.underlying.data_series_id].contract,
                          ibs_underlying_id=ds.underlying.data_series_id)

            self._series[ds.data_series_id] = ibs

    def disconnect_data_series(self) -> bool:
        pass

    def update_data_series(self) -> None:
        for ds in self._series:
            self._fetch_data(self._series[ds])

    def _fetch_data(self, ibs: DataSeries) -> None:
        if ibs.series_type == DataSeriesType.Index:
            self._fetch_data_index(ibs)
        if ibs.series_type == DataSeriesType.Option:
            self._fecth_data_option(ibs)

    def _fetch_data_index(self, ibs: IBSeries) -> None:
        [d] = self._broker.reqTickers(ibs.contract)
        data_index = DataIndex(code=ibs.contract.symbol,
                               high=d.high,
                               low=d.low,
                               close=d.close,
                               bid=d.bid,
                               bid_size=d.bidSize,
                               ask=d.ask,
                               ask_size=d.askSize,
                               last=d.last,
                               last_size=d.lastSize,
                               time=d.time)
        ibs.data.append(data_index)


    def _fecth_data_option(self, ibs: IBSeries) -> None:
        #Ask for options chains
        chains = self._broker.reqSecDefOptParams(ibs.contract.symbol,
                                                 '',
                                                 ibs.contract.secType,
                                                 ibs.contract.conId)
        chain = next(c for c in chains if c.tradingClass == ibs.contract.symbol
                     and c.exchange == 'SMART')
        
        if chain:
            # Ask for last underlying price
            u_price = self._series[ibs.ibs_underlying_id].data[-1].market_price()
            
            # next three expiration dates
            expirations = sorted(exp for exp in chain.expirations)[:3]
            
            min_strike_price = u_price * 0.99 # underlying price - 2%
            max_strike_price = u_price * 1.01 # underlying price + 2%
            strikes = sorted(strike for strike in chain.strikes
                       if min_strike_price < strike < max_strike_price)
            
            rights=['P','C']
        
            contracts = [Option(ibs.contract.symbol,
                                expiration,
                                strike,
                                right,
                                'SMART')
                                for right in rights
                                for expiration in expirations
                                for strike in strikes]
        
            
            q_contracts=[]
            # IB has a limit of 50 requests per second
            for c in chunks(contracts, 50):
                q_contracts+=self._broker.qualifyContracts(*c)
                self._broker.sleep(2)
            #print("Option ", q_contracts[0])
            
            tickers=[]
            print("Unqualified contracts:", len(contracts) - len(q_contracts))
            for q in chunks(q_contracts, 50):
                tickers+=self._broker.reqTickers(*q)
                self._broker.sleep(2)
                print('+')
            
            options = []
            for t in tickers:
                #print('Ticker: ', t)
                bid_ind = self._create_option_indicators(t.bidGreeks)
                ask_ind = self._create_option_indicators(t.askGreeks)
                last_ind = self._create_option_indicators(t.lastGreeks)
                model_ind = self._create_option_indicators(t.modelGreeks)
            
                opt = DataOption(
                        code=t.contract.symbol,
                        expiration=parse_ib_date(t.contract.lastTradeDateOrContractMonth),
                        strike=t.contract.strike,
                        right=OptionRight.Call if t.contract.right =='C' else OptionRight.Put,
                        high=t.high,
                        low=t.low,
                        close=t.close,
                        bid=t.bid,
                        bid_size=t.bidSize,
                        ask=t.ask,
                        ask_size=t.askSize,
                        last=t.last,
                        last_size=t.lastSize,
                        volume=t.volume,
                        indicators=model_ind,
                        bid_indicators=bid_ind,
                        ask_indicators=ask_ind,
                        last_indicators=last_ind,
                        time=t.time)

                options.append(opt)
                # print(opt)

            # create a expiration dates dictionary
            exp_dict={}
            for e in expirations:
                exp_dict[parse_ib_date(e)] = {}
                for s in strikes:
                    exp_dict[parse_ib_date(e)][s] = {'C': None,
                                                     'P': None}

            # adding options in their expiration date slot
            for opt in options:
                if opt.right == OptionRight.Call:
                    exp_dict[opt.expiration][opt.strike]['C'] = opt
                else:
                    exp_dict[opt.expiration][opt.strike]['P'] = opt
    
        ibs.data.append(DataOptionChain(ibs.contract.symbol, exp_dict))

    def _create_option_indicators(self,
                                  oc: OptionComputation) -> OptionIndicators:
       if oc:
           i = OptionIndicators(delta=oc.delta,
                             gamma=oc.gamma,
                             theta=oc.theta,
                             vega=oc.vega,
                             option_price=oc.optPrice,
                             implied_volatility=oc.impliedVol,
                             underlying_price=oc.undPrice,
                             underlying_dividends=oc.pvDividend)
           return i

    def data(self, ds: DataSeries) -> object:
        if ds.data_series_id not in self._series:
            self.connect_data_series(ds)
            self._fetch_data(self._series[ds.data_series_id])
        
        return self._series[ds.data_series_id].data


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except Exception as e:
        return False

def chunks(l: list, n: int) -> list:
    # For item i in a range that is a lenght of l
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

def parse_ib_date(s: str) -> datetime.date:
    if len(s) == 8:
        # YYYYmmdd
        y = int(s[0:4])
        m = int(s[4:6])
        d = int(s[6:8])
        dt = datetime.date(y, m, d)
    return dt