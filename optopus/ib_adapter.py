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
from ib_insync.objects import (AccountValue, OptionComputation, Position)
from ib_insync.contract import Contract

from optopus.account import AccountItem
from optopus.money import Money
from optopus.data_objects import (AssetType, Asset, IndexAsset, IndexData,
                                  OptionChainAsset, OptionData, OptionIndicators,
                                  OptionRight, DataSource,
                                  OptionMoneyness, BarDataType, BarData, 
                                  PositionData, OwnershipType)
from optopus.data_manager import DataAdapter
from optopus.settings import CURRENCY, HISTORICAL_DAYS
from optopus.utils import nan, parse_ib_date


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
        self._historical_data_updated = None
        self._historical_IV_data_updated = None

    def historical_data_is_updated(self) -> bool:
        if self._historical_data_updated:
            delta = datetime.datetime.now() - self._historical_data_updated
            if delta.days:
                return True
            else:
                return False

    def historical_IV_data_is_updated(self) -> bool:
        if self._historical_IV_data_updated:
            delta = datetime.datetime.now() - self._historical_IV_data_updated
            if delta.days:
                return True
            else:
                return False


class IBOptionChainAsset(OptionChainAsset):
    def __init__(self,
                 underlying: Asset,
                 contract: Contract,
                 n_expiration_dates: int,
                 underlying_distance: float) -> None:
        super().__init__(underlying, n_expiration_dates, underlying_distance)
        self.contract = contract


class IBBrokerAdapter:
    """Class implementing the Interactive Brokers interface"""

    def __init__(self, ib: IB, host: str, port: int, client: int) -> None:
        self._broker = ib
        self._host = host
        self._port = port
        self._client = client
        self._translator = IBTranslator()
        self._data_adapter = IBDataAdapter(self._broker)

        # Callable objects. Optopus direcction
        self.emit_account_item_event = None
        self.emit_position_event = None
        self.execute_every_period = None

        # Cannect to ib_insync events
        self._broker.accountValueEvent += self._onAccountValueEvent
        self._broker.positionEvent += self._onPositionEvent

    def connect(self) -> None:
        self._broker.connect(self._host, self._port, self._client)
        
    def disconnect(self) ->None:
        self._broker.disconnect()

    def sleep(self, time: float) -> None:
        self._broker.sleep(time)

    def _onAccountValueEvent(self, item: AccountValue) -> None:
        account_item = self._translator.translate_account_value(item)
        if account_item.tag:  # item translated
            self.emit_account_item_event(account_item)

    def _onPositionEvent(self, item: Position) -> PositionData:
        position = self._translator.translate_position(item)
        if position:
            self.emit_position_event(position)
        
        
class IBTranslator:
    """Translate the IB tags and values to Ocptopus"""
    def __init__(self) -> None:
        self._account_translation = {'AccountCode': 'id',
                                     'AvailableFunds': 'funds',
                                     'BuyingPower': 'buying_power',
                                     'CashBalance': 'cash',
                                     'DayTradesRemaining': 'max_day_trades'}
        self._sectype_translation = {'STK': AssetType.Stock,
                                     'OPT': AssetType.Option,
                                     'FUT': AssetType.Future,
                                     'CASH': AssetType.Future,
                                     'IND': AssetType.Index,
                                     'CFD': AssetType.CFD,
                                     'BOND': AssetType.Bond,
                                     'CMDTY': AssetType.Commodity,
                                     'FOP': AssetType.FuturesOption,
                                     'FUND': AssetType.MutualFund,
                                     'IOPT': AssetType.Warrant}
        self._right_translation = {'C': OptionRight.Call,
                                  'P': OptionRight.Put}

    def translate_account_value(self, item: AccountValue) -> AccountItem:
        opt_money = None
        opt_value = None

        opt_tag = self._translate_account_tag(item.tag)

        if item.currency and is_number(item.value):
            opt_money = self._translate_value_currency(item.value,
                                                       item.currency)
        else:  # for no money value.
            opt_value = item.value

        return AccountItem(item.account, opt_tag, opt_value, opt_money)

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

    def translate_position(self, item: Position) -> PositionData:
        code = item.contract.symbol
        asset_type = self._sectype_translation[item.contract.secType]
        
        if item.position > 0:
            ownership = OwnershipType.Buyer
        elif item.position < 0:
            ownership = OwnershipType.Seller
        else:
            ownership = None
        
        expiration = item.contract.lastTradeDateOrContractMonth
        if expiration:
            expiration = parse_ib_date(expiration)
        else:
            expiration = None
            
        right = item.contract.right
        if right:
            right = self._right_translation[right]
        else:
            right = None

        position = PositionData(code=code,
                                asset_type=asset_type,
                                expiration=expiration,
                                strike=item.contract.strike,
                                right=right,
                                ownership=ownership,
                                quantity=abs(item.position),
                                average_cost=item.avgCost)
        return position
   

class IBDataAdapter(DataAdapter):
    def __init__(self, broker: IB) -> None:
        self._broker = broker
        self.assets = {}
        self._contracts = {}

    def register_index(self, asset: IndexAsset) -> bool:
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
                    started = True
                else:
                    raise ValueError('Error: multiple contracts')
        return started

    def register_option(self, asset: OptionChainAsset) -> bool:
        if asset.asset_id not in self.assets:
            # if the underlying doesn't exists
            if asset.underlying.asset_id not in self.assets:
                self.register_asset(asset.underlying)

            iba = IBOptionChainAsset(underlying=asset.underlying,
                                     contract=self.assets[asset.underlying.asset_id].contract,
                                     n_expiration_dates=asset.n_expiration_dates,
                                     underlying_distance=asset.underlying_distance)

            self.assets[asset.asset_id] = iba

    def fetch_current_data_index(self, asset: Asset) -> object:
        iba = self.assets[asset.asset_id]
        [d] = self._broker.reqTickers(iba.contract)
        data_index = IndexData(code=iba.contract.symbol,
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
        return data_index

    def fecth_current_data_option(self, asset: Asset) -> object:
        # Ask for options chains
        iba = self.assets[asset.asset_id]
        chains = self._broker.reqSecDefOptParams(iba.contract.symbol,
                                                 '',
                                                 iba.contract.secType,
                                                 iba.contract.conId)
        chain = next(c for c in chains if c.tradingClass == iba.contract.symbol
                     and c.exchange == 'SMART')

        if chain:
            # Ask for last underlying price
            u_price = self.assets[iba.underlying.asset_id].market_price

            # next n expiration dates
            expirations = sorted(exp for exp in chain.expirations)[:iba.n_expiration_dates]
            # underlying price - %distance
            min_strike_price = u_price * ((100 - iba.underlying_distance)/100)  
            # underlying price + %distance
            max_strike_price = u_price * ((100 + iba.underlying_distance)/100)  
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

            q_contracts = []
            # IB has a limit of 50 requests per second
            for c in chunks(contracts, 50):
                q_contracts += self._broker.qualifyContracts(*c)
                self._broker.sleep(2)

            tickers = []
            print("Contracts: {} Unqualified: {}".
                  format(len(contracts), len(contracts) - len(q_contracts)))
            for q in chunks(q_contracts, 50):
                tickers += self._broker.reqTickers(*q)
                self._broker.sleep(1)

            options = []
            for t in tickers:
                # There others Greeks for bid, ask and last prices
                delta = gamma = theta = vega = option_price = \
                implied_volatility = underlying_price = \
                underlying_dividends = nan

                if t.modelGreeks:                    

                    delta = t.modelGreeks.delta
                    gamma = t.modelGreeks.gamma
                    theta = t.modelGreeks.theta
                    vega = t.modelGreeks.vega
                    option_price = t.modelGreeks.optPrice
                    implied_volatility = t.modelGreeks.impliedVol
                    underlying_price = t.modelGreeks.undPrice
                    underlying_dividends = t.modelGreeks.pvDividend
                        
                    moneyness = intrinsic_value = extrinsic_value = nan
                    if underlying_price:
                        moneyness, intrinsic_value, extrinsic_value = \
                        self._calculate_moneyness(t.contract.strike,
                                                  option_price,
                                                  underlying_price,
                                                  t.contract.right)

                opt = OptionData(
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
                        delta=delta,
                        gamma=gamma,
                        theta=theta,
                        vega=vega,
                        implied_volatility=implied_volatility,
                        underlying_price=underlying_price,
                        underlying_dividends=underlying_dividends,
                        moneyness=moneyness.value,
                        intrinsic_value = intrinsic_value,
                        extrinsic_value = extrinsic_value,
                        time=t.time)

                options.append(opt)

        return options

    def _calculate_moneyness(self, strike: float,
                             option_price: float,
                             underlying_price: float, 
                             right: str) -> OptionMoneyness:

        intrinsic_value = extrinsic_value = 0

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

    def _process_bars(self, code: str, ibbars: list) -> list:
        bars = []
        for ibb in ibbars:
            b = BarData(code=code,
                        bar_time=ibb.date,
                        bar_open=ibb.open,
                        bar_high=ibb.high,
                        bar_low=ibb.low,
                        bar_close=ibb.close,
                        bar_average=ibb.average,
                        bar_count=ibb.barCount)
            bars.append(b)
        return bars

    def fetch_historical_data_asset(self, asset: Asset) -> None:
        iba = self.assets[asset.asset_id]
        if iba.asset_type == AssetType.Index:
            if not iba.historical_data_is_updated():
                duration = str(HISTORICAL_DAYS) + ' D'
                bars = self._broker.reqHistoricalData(iba.contract,
                                                      endDateTime='',
                                                      durationStr=duration,
                                                      barSizeSetting='1 day',
                                                      whatToShow='TRADES',
                                                      useRTH=True,
                                                      formatDate=1)
                return self._process_bars(iba.code, bars)

    def fetch_historical_IV_data_asset(self, asset: Asset) -> None:
        iba = self.assets[asset.asset_id]
        if iba.asset_type == AssetType.Index:
            if not iba.historical_IV_data_is_updated():
                duration = str(HISTORICAL_DAYS) + ' D'
                bars = self._broker.reqHistoricalData(iba.contract,
                                                      endDateTime='',
                                                      durationStr=duration,
                                                      barSizeSetting='1 day',
                                                      whatToShow='OPTION_IMPLIED_VOLATILITY',
                                                      useRTH=True,
                                                      formatDate=1)
                return self._process_bars(iba.code, bars)

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