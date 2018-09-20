# -*- coding: utf-8 -*-
from optopus.data_objects import (Asset, AssetType,
                                  StrategyType, RightType, OwnershipType,
                                  Strategy, Leg)

from optopus.strategies import ShortPutVerticalSpread

import datetime
from optopus.optopus import Optopus
from optopus.settings import CURRENCY

from ib_insync.contract import Option


class Taco():
    def __init__(self, opt: Optopus):
        self._opt = opt
        self.produced = False

    def produce_signal(self):
        if self.produced: return
        symbol = 'SPY'
        underlying = Asset(symbol, AssetType.Stock, CURRENCY)
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

        leg = Leg(underlying.code, ownership, right, expiration, strike, multiplier, price, ratio, currency, take_profit_factor, stop_loss_factor, contract)
        legs = [leg]

        strategy_type = StrategyType.SellNakedPut
        strategy = Strategy(underlying.code, strategy_type, legs)

        #print('leg id', leg.leg_id)
        #print(leg)
        #print('strategy_id', strategy.strategy_id)
        #print(strategy)
        
        self._opt.new_strategy(strategy)
        
        self.produced = True


class BullPutSpreadAlgo:
    def __init__(self, opt: Optopus):
        self._opt = opt
    
    def calculate_signal(self):
        code = 'SPY'
        underlying = Asset(code, AssetType.Stock, CURRENCY)
        s_expiration = '20181019'
        expiration = datetime.datetime.strptime(s_expiration, '%Y%m%d').date()
        ratio = 1
        take_profit_factor = 0.5
        stop_loss_factor = 2.0
        
        
        max_spread_width = 4
        chain = self._opt.option_chain(code, expiration)
        #print([(o.strike, o.expiration, o.right) for o in chain])
        OTM = [o for o in chain if o.strike < o.underlying_price and o.right == RightType.Put]
        print([(o.strike, o.expiration, o.right) for o in OTM])
        sell_put = OTM[-1]
        buy_put = OTM[0]
        for o in OTM[0:-2]:
            if sell_put.strike - o.strike <= max_spread_width:
                buy_put = o
                break
        
        print('SELL PUT', sell_put.contract)
        print('BUY PUT', buy_put.contract)
        
        short_leg = Leg(sell_put, OwnershipType.Seller, ratio)
        long_leg = Leg(buy_put, OwnershipType.Buyer, ratio)
        
        strategy = ShortPutVerticalSpread(underlying.code,
                                          StrategyType.ShortPutVerticalSpread,
                                          OwnershipType.Buyer,
                                          short_leg.option.currency,
                                          sell_put.underlying_price,
                                          take_profit_factor,
                                          stop_loss_factor,
                                          sell_put.multiplier,
                                          short_leg,
                                          long_leg)
        
        self._opt.new_strategy(strategy)
        
        
    def manage(self):
        pass
    
class ShortCallSpread:
    def calculate_signal(self):
        pass
    def manage(self):
        pass
     
    