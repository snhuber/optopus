#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 16:30:25 2018

@author: ilia
"""
import datetime
from typing import List, Callable, Dict, Tuple
from collections import OrderedDict
import logging
from optopus.data_manager import DataManager
from optopus.order_manager import OrderManager
from optopus.watch_list import WATCH_LIST
from optopus.asset import Asset, AssetType
from optopus.data_objects import Account, Portfolio
from optopus.option import Option
from optopus.strategy import Strategy
from optopus.settings import (
    SLEEP_LOOP,
    EXPIRATIONS,
    PRESERVED_CASH_FACTOR,
    MAXIMUM_RISK_FACTOR,
)


class Optopus:
    """Class implementing automated trading system"""

    def __init__(self, broker) -> None:
        self._broker = broker
        self._algorithms = []
        self._log = logging.getLogger(__name__)

    def start(self) -> None:
        self._data_manager = DataManager(self._broker._data_adapter, WATCH_LIST)
        self._order_manager = OrderManager(self._broker, self._data_manager)

        # Events
        # self._broker.emit_account_item_event = self._data_manager._account_item
        # self._broker.emit_position_event = self._data_manager._position
        # self._broker.emit_new_order = self._new_order
        self._broker.emit_order_status = self._order_manager.order_status_changed
        # self._broker.emit_commission_report = self._data_manager._commission_report

        self._log.debug("Connecting to IB broker")
        self._broker.connect()
        self._broker.sleep(1)

        self._data_manager.update_account()

        self._log.debug("Retrieving underling data")
        self._data_manager.create_assets()

        self._data_manager.update_assets()
        self._data_manager.update_historical_assets()
        self._data_manager.update_historical_IV_assets()
        self._data_manager.compute()

        self._data_manager.update_strategy_options()
        self._data_manager.check_strategy_positions()

        self._log.info("System started")

    @property
    def account(self) -> Account:
        return self._data_manager.account

    @property
    def portfolio(self) -> Portfolio:
        return self._data_manager.portfolio

    @property
    def assets(self) -> Dict[str, Asset]:
        return self._data_manager.assets

    @property
    def etfs(self) -> Dict[str, Asset]:
        return {
            k: v
            for (k, v) in self._data_manager.assets.items()
            if v.id.asset_type == AssetType.ETF
        }

    @property
    def strategies(self) -> Dict[str, Strategy]:
        return self._data_manager.strategies

    def stop(self) -> None:
        self._broker.disconnect()

    def pause(self, time: float) -> None:
        self._broker.sleep(time)

    def loop(self) -> None:

        for t in self._broker._broker.timeRange(
            datetime.time(0, 0), datetime.datetime(2100, 1, 1, 0), 10
        ):
            self._log.debug("Initiating loop iteration")
            self._data_manager.update_assets()
            self._data_manager.update_strategy_options()
            self._data_manager.check_strategy_positions()
            # FIXME: Compute must be before check_strategy?
            self._data_manager.compute()

            for algorithm in self._algorithms:
                algorithm()
            self._broker.sleep(SLEEP_LOOP)

    def series(self, code: str, item: str) -> Tuple:
        if item == "time":
            return [b.time for b in self._data_manager.assets[code].price_history.values]
        elif item == "value":
            return [b.close for b in self._data_manager.assets[code].price_history.values]
        elif item == "iv":
            return [b.close for b in self._data_manager.assets[code].iv_history.values]
        elif item == "rsi":
            return self._data_manager.assets[code].measures.rsi
        elif item == "sma_rsi":
            return self._data_manager.assets[code].measures.rsi_sma
        elif item == "fast_sma":
            return self._data_manager.assets[code].measures.fast_sma
        elif item == "slow_sma":
            return self._data_manager.assets[code].measures.slow_sma
        elif item == "very_slow_sma":
            return self._data_manager.assets[code].measures.very_slow_sma
        elif item == "fast_sma_speed":
            return self._data_manager.assets[code].measures.fast_sma_speed
        elif item == "fast_sma_speed_diff":
            return self._data_manager.assets[code].measures.fast_sma_speed_diff        
        elif item == "direction":
            return self._data_manager.assets[code].forecast.direction
        else:
            return None



    def price_history(self, code: str) -> Tuple:
        return self._data_manager.assets[code].price_history

    def iv_history(self, code: str) -> Tuple:
        return self._data_manager.assets[code].iv_history

    def rsi_history(self, code:str) -> Tuple:
        return self._data_manager.assets[code].measures.rsi
    
    def rsi_sma_history(self, code:str) -> Tuple:
        return self._data_manager.assets[code].measures.rsi_sma

    def sma1_history(self, code:str) -> Tuple:
        return self._data_manager.assets[code].measures.sma1
    
    def sma2_history(self, code:str) -> Tuple:
        return self._data_manager.assets[code].measures.sma2

    def assets_matrix(self, field: str) -> dict:
        return self._data_manager.assets_matrix(field)

    def option_chain(self, code: str, expiration: datetime.date) -> List[Option]:
        return self._data_manager.option_chain(code, expiration)
        # return self._data_manager._assets[code]._option_chain

    def register_algorithm(self, algo: Callable[[], None]) -> None:
        self._algorithms.append(algo)

    def new_strategy(self, strategy: Strategy) -> None:
        self._data_manager.add_strategy(strategy)
        self._order_manager.new_strategy(strategy)

    def expiration_target(self) -> datetime.date:
        for expiration in EXPIRATIONS:
            DTE = (expiration - datetime.datetime.now().date()).days
            if DTE >= 30 and DTE <= 60:
                return expiration

    def maximum_risk_per_trade(self) -> float:
        account = self.account
        preserved_cash = account.net_liquidation * PRESERVED_CASH_FACTOR
        available_cash = account.cash - preserved_cash

        maximum_risk = account.net_liquidation * MAXIMUM_RISK_FACTOR

        return min(maximum_risk, available_cash)

