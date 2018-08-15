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
from ib_insync.contract import Index,  Option
from ib_insync.objects import AccountValue, OptionComputation
from ib_insync.contract import Contract

from optopus.account import AccountItem
from optopus.money import Money
from optopus.data_objects import (AssetType, Asset, 
                                  IndexAsset, OptionChainAsset,
                                  DataIndex, DataOption, OptionIndicators,
                                  DataOptionChain, OptionRight, DataSource,
                                  OptionMoneyness, nan)
from optopus.data_manager import DataAdapter
from optopus.settings import CURRENCY


class IBObject(Enum):
    account = 'ACCOUNT'
    order = 'ORDER'


class IBIndexAsset(IndexAsset):
    def __init__(self,
                 code: str,
                 data_source: DataSource,
                 contract: Contract) -> None:
        super().__init__(code, data_source)
        self.contract = contract
        self._data = None

    @property
    def data(self):
        return [self._data]

    @data.setter
    def data(self, values):
        self._data = values

    @property
    def market_price(self):
        return self._data.market_price

class IBOptionChainAsset(OptionChainAsset):
    def __init__(self,
                 code: str,
                 underlying: Asset,
                 contract: Contract) -> None:
        super().__init__(code, underlying)
        self.contract = contract
        self._data = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, values):
        self._data = values

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
        self.assets = {}
        self._contracts = {}

    def register_asset(self, asset: Asset) -> bool:
        if asset.asset_type == AssetType.Index:
           self._register_index(asset)
        elif asset.asset_type == AssetType.Option:
           self._register_option(asset) 
        

    def _register_index(self, asset: IndexAsset) -> bool:
        started = False
        if asset.asset_id not in self.assets:
                contract = Index(asset.code)
                q_contract = self._broker.qualifyContracts(contract)
                if len(q_contract) == 1:
                    # create a new series object and add to series dict
                    iba = IBIndexAsset(code=asset.code,
                                       data_source=asset.data_source,
                                       contract=q_contract[0])

                    self.assets[asset.asset_id] = iba
                    #self._data_series[idx] = {'data_series': ds,
                    #                          'contract': q_contract[0]}
                    started = True
                else:
                    raise ValueError('Error: multiple contracts')
        return started

    def _register_option(self, asset: OptionChainAsset) -> bool:
        if asset.asset_id not in self.assets:
            # if the underlying doesn't exists
            if asset.underlying.asset_id not in self.assets:
                self.register_asset(asset.underlying)

            iba = IBOptionChainAsset(code=asset.code,
                                     underlying=asset.underlying,
                                     contract=self.assets[asset.underlying.asset_id].contract)

            self.assets[asset.asset_id] = iba

    def update_assets(self) -> None:
        for asset in self.assets:
            self._fetch_data_asset(self.assets[asset])

    def _fetch_data_asset(self, iba: Asset) -> None:
        if iba.asset_type == AssetType.Index:
            self._fetch_data_index(iba)
        if iba.asset_type == AssetType.Option:
            self._fecth_data_option(iba)

    def _fetch_data_index(self, iba: IBIndexAsset) -> None:
        [d] = self._broker.reqTickers(iba.contract)
        data_index = DataIndex(code=iba.contract.symbol,
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
        iba.data = data_index

    def _fecth_data_option(self, iba: IBOptionChainAsset) -> None:
        # Ask for options chains
        chains = self._broker.reqSecDefOptParams(iba.contract.symbol,
                                                 '',
                                                 iba.contract.secType,
                                                 iba.contract.conId)
        chain = next(c for c in chains if c.tradingClass == iba.contract.symbol
                     and c.exchange == 'SMART')

        if chain:
            # Ask for last underlying price
            u_price = self.assets[iba.underlying.asset_id].market_price

            # next three expiration dates
            expirations = sorted(exp for exp in chain.expirations)[:3]

            min_strike_price = u_price * 0.99  # underlying price - 2%
            max_strike_price = u_price * 1.01  # underlying price + 2%
            strikes = sorted(strike for strike in chain.strikes
                       if min_strike_price < strike < max_strike_price)

            rights=['P','C']
            # Create the options contracts
            contracts = [Option(iba.contract.symbol,
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
                # There others Greeks for bid, ask and last prices
                delta = gamma = theta = vega = option_price = \
                implied_volatility = underlying_price = \
                underlying_dividends = nan
                
                if t.modelGreeks:
                    delta = t.modelGreeks.delta,
                    gamma = t.modelGreeks.gamma,
                    theta = t.modelGreeks.theta,
                    vega = t.modelGreeks.vega,
                    option_price = t.modelGreeks.optPrice,
                    implied_volatility = t.modelGreeks.impliedVol,
                    underlying_price = t.modelGreeks.undPrice,
                    underlying_dividends = t.modelGreeks.pvDividend
        
                    moneyness, intrinsic_value, extrinsic_value = \
                    self._calculate_moneyness(t.contract.strike,
                                              option_price[0],
                                              underlying_price[0],
                                              t.contract.right)   

                    
                opt = DataOption(
                        code=t.contract.symbol,
                        expiration=parse_ib_date(t.contract.lastTradeDateOrContractMonth),
                        strike=t.contract.strike,
                        right=OptionRight.Call.value if t.contract.right =='C' else OptionRight.Put.value,
                        high=t.high,
                        low=t.low,
                        close=t.close,
                        bid=t.bid,
                        bid_size=t.bidSize,
                        ask=t.ask,
                        ask_size=t.askSize,
                        last=t.last,
                        last_size=t.lastSize,
                        option_price=option_price,
                        volume=t.volume,
                        delta=delta[0],
                        gamma=gamma[0],
                        theta=theta[0],
                        vega=vega[0],
                        implied_volatility=implied_volatility[0],
                        underlying_price=underlying_price[0],
                        underlying_dividends=underlying_dividends,
                        moneyness=moneyness.value,
                        intrinsic_value = intrinsic_value,
                        extrinsic_value = extrinsic_value,
                        time=t.time)

                options.append(opt)
                # print(opt)

            # create a expiration dates dictionary
            #exp_dict = {}
            #for e in expirations:
            #    exp_dict[parse_ib_date(e)] = {}
            #    for s in strikes:
            #        exp_dict[parse_ib_date(e)][s] = {'C': None,
            #                                         'P': None}

            # adding options in their expiration date slot
            #for opt in options:
            #    if opt.right == OptionRight.Call:
            #        exp_dict[opt.expiration][opt.strike]['C'] = opt
            #    else:
            #        exp_dict[opt.expiration][opt.strike]['P'] = opt
    
        #iba.data = DataOptionChain(iba.contract.symbol, exp_dict)
        iba.data = options

    def _calculate_moneyness(self, strike: float,
                             option_price: float,
                             underlying_price: float, 
                             right: str) -> OptionMoneyness:
        
        intrinsic_value = 0;
        extrinsic_value = 0;
        
        if right == 'C':
            intrinsic_value = max(0, underlying_price - strike)
            if underlying_price > strike:                
                moneyness = OptionMoneyness.InTheMoney
            elif underlying_price < strike:
                moneyness = OptionMoneyness.OutTheMoney
            else:
                moneyness = OptionMoneyness.InTheMoney
            
        if right == 'P':
            intrinsic_value = max(0, strike - underlying_price)
            if underlying_price < strike:
                moneyness = OptionMoneyness.InTheMoney
            elif underlying_price > strike:
                moneyness = OptionMoneyness.OutTheMoney
            else:
                moneyness = OptionMoneyness.InTheMoney
            
        extrinsic_value = option_price - intrinsic_value
        
        return moneyness, intrinsic_value, extrinsic_value
            

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

    def current(self, asset: Asset) -> object:
        if asset.asset_id not in self.assets:
            self.register_asset(asset)
            self._fetch_data_asset(self.assets[asset.asset_id])
        
        return self.assets[asset.asset_id].data

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