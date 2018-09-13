# -*- coding: utf-8 -*-
from optopus.data_objects import (Asset, AssetType,
                                  StrategyType, RightType, OwnershipType,
                                  Strategy, Leg)
import datetime
from optopus.optopus import Optopus
from optopus.currency import Currency
from optopus.settings import CURRENCY

from ib_insync.contract import Option


class Taco():
    def __init__(self, opt: Optopus):
        self._opt = opt
        self.produced = False

    def produce_signal(self):
        if self.produced: return
        symbol = 'SPY'
        underlying = Asset(symbol, AssetType.Stock)
        ownership = OwnershipType.Seller
        right = RightType.Put
        strike = 287.0
        s_expiration = '20180921'
        expiration = datetime.datetime.strptime(s_expiration, '%Y%m%d').date()
        multiplier = 100
        currency = CURRENCY
        take_profit_factor = 0.5
        stop_loss_factor = 2.0
        price = 0.5
        ratio = 1

        contract = Option(symbol=symbol, lastTradeDateOrContractMonth=s_expiration, strike=str(strike), right=right.value, exchange='SMART')

        leg = Leg(underlying, ownership, right, expiration, strike, multiplier, price, ratio, currency, take_profit_factor, stop_loss_factor, contract)
        legs = [leg]

        strategy_type = StrategyType.SellNakedPut
        strategy = Strategy(underlying, strategy_type, legs)

        #print('leg id', leg.leg_id)
        #print(leg)
        #print('strategy_id', strategy.strategy_id)
        #print(strategy)
        
        self._opt.new_strategy(strategy)
        
        self.produced = True
