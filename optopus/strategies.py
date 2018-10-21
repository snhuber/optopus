# -*- coding: utf-8 -*-
from optopus.data_objects import OwnershipType, Currency, Option
from optopus.strategy import Strategy, StrategyType, Leg

class ShortPutVerticalSpread:
    def __init__(self,
                 code: str,
                 strategy_type: StrategyType,
                 ownership: OwnershipType,
                 currency: Currency,
                 take_profit_factor: float,
                 underlying_entry_price: float,
                 multiplier: int,
                 sell_put: Option,
                 buy_put: Option):
        
        legs = {}
        legs['sell_leg'] = Leg(sell_put, OwnershipType.Seller, 1)
        legs['buy_leg'] = Leg(buy_put, OwnershipType.Buyer, 1)
        self.strategy = Strategy(code, StrategyType.ShortPutVerticalSpread, ownership, currency, take_profit_factor, multiplier, legs)
        self.underlying_entry_price = underlying_entry_price
        # TODO: make properties
        self._opened = None
        self._closed = None
        self._quantity = None
   
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
    