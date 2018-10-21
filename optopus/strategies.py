# -*- coding: utf-8 -*-
from optopus.data_objects import (Strategy, StrategyType, Leg, OwnershipType, Currency, Option)


class ShortPutVerticalSpread(Strategy):
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
        self._spread_witdh = None
        legs = {}
        legs['sell_leg'] = Leg(sell_put, OwnershipType.Seller, 1)
        legs['buy_leg'] = Leg(buy_put, OwnershipType.Buyer, 1)
        super().__init__(code, StrategyType.ShortPutVerticalSpread, ownership, currency, take_profit_factor , underlying_entry_price, multiplier, legs)
        
   
    @property
    def entry_price(self):
        print('-----')
        for l in self.legs.values():
            print(l.price, l.ownership.value)
        return round(sum([l.ownership.value * l.price for l in self.legs.values()]), 2)
    
    @property
    def take_profit_price(self):
        return round(self.entry_price * self.take_profit_factor, 2)
    
    @property
    def breakeven_price(self):
        return self.legs['sell_leg'].option.strike - self.legs['sell_leg'].price
    
    @property
    def maximum_profit(self):
        return self.entry_price * self.multiplier
    
    @property
    def maximum_loss(self):
        return ((self.legs['sell_leg'].option.strike - self.legs['buy_leg'].option.strike) - self.entry_price) * self.multiplier
    
    @property
    def POP(self):
        return (1 - self.legs['sell_leg'].price / (self.legs['sell_leg'].option.strike - self.legs['buy_leg'].option.strike)) * 100
    
    @property
    def ROI(self):
        return self.maximum_profit / self.maximum_loss
    
    def __str__(self):
        return(f'{self.strategy_type.value}\n'
               f'entry price {self.entry_price}\n'
               f'max_profit {self.maximum_profit}\n'
               f'max_loss {self.maximum_loss}\n'
               f'POP {self.POP}\n'
               f'ROI {self.ROI}\n')
    