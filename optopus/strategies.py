# -*- coding: utf-8 -*-
import datetime
from optopus.asset import Asset
from optopus.data_objects import OwnershipType, Currency, Option
from optopus.strategy import Strategy, StrategyType, Leg
class DefinedStrategy:
    def __init__(self):
        self._created: datetime.datetime = datetime.datetime.now()
        self._opened: datetime.datetime = None
        self._closed: datetime.datetime = None
        # TODO: quantity must be in smart_strategy
        self._quantity: int = None

    @property
    def created(self):
        return self.created

    @property
    def opened(self):
        return self.opened

    @property 
    def closed(self):
        return self._closed


class ShortPutVerticalSpread:
    def __init__(self,
                asset: Asset,
                sell_put: Option,
                buy_put: Option,
                ownership: OwnershipType,
                take_profit_factor: float = 0.5):
        
        legs = {}
        legs['sell_leg'] = Leg(sell_put, OwnershipType.Seller, 1)
        legs['buy_leg'] = Leg(buy_put, OwnershipType.Buyer, 1)
        self.strategy = Strategy(asset.code, StrategyType.ShortPutVerticalSpread, ownership, asset.currency, take_profit_factor, sell_put.multiplier, legs)
        self.underlying_entry_price = asset.market_price
        # TODO: make properties
        
   
    @property
    def entry_price(self):
        return round(sum([l.ownership.value * l.price for l in self.strategy.legs.values()]), 2)
    
    @property
    def take_profit_price(self):
        return round(self.entry_price * self.strategy.take_profit_factor, 2)
    
    @property
    def breakeven_price(self):
        return self.strategy.legs['sell_leg'].option.strike - self.strategy.legs['sell_leg'].price
    
    @property
    def maximum_profit(self):
        return self.entry_price * self.strategy.multiplier
    
    @property
    def maximum_loss(self):
        return ((self.strategy.legs['sell_leg'].option.strike - self.strategy.legs['buy_leg'].option.strike) - self.entry_price) * self.strategy.multiplier
    
    @property
    def POP(self):
        return (1 - self.strategy.legs['sell_leg'].price / (self.strategy.legs['sell_leg'].option.strike - self.strategy.legs['buy_leg'].option.strike)) * 100
    
    @property
    def ROI(self):
        return self.maximum_profit / self.maximum_loss
    
    def __str__(self):
        return(f'{self.strategy.strategy_type.value}\n'
               f'entry price {self.entry_price}\n'
               f'max_profit {self.maximum_profit}\n'
               f'max_loss {self.maximum_loss}\n'
               f'POP {self.POP}\n'
               f'ROI {self.ROI}\n')
    