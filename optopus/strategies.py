# -*- coding: utf-8 -*-
from optopus.data_objects import (Strategy, StrategyType, Leg, OwnershipType, Currency)


class ShortPutVerticalSpread(Strategy):
    def __init__(self,
                 code: str,
                 strategy_type: StrategyType,
                 ownership: OwnershipType,
                 currency: Currency,
                 take_profit_factor: float,
                 stop_loss_factor: float,
                 underlying_entry_price: float,
                 multiplier: int,
                 short_leg: Leg,
                 long_leg: Leg):
        legs = {}
        legs['short_leg'] = short_leg
        legs['long_leg'] = long_leg
        super().__init__(code, StrategyType.ShortPutVerticalSpread, ownership, currency, take_profit_factor, stop_loss_factor, underlying_entry_price, multiplier, legs)
        
    def calculate_measures(self):
        self._spread_entry_price = round(self.legs['short_leg'].price - self.legs['long_leg'].price, 2)
        self._spread_witdh = self.legs['short_leg'].option.strike - self.legs['long_leg'].option.strike
        self._breakeven_price = self.legs['short_leg'].option.strike - self.legs['short_leg'].price
        self._maximum_profit = self._spread_entry_price * self.multiplier
        self._maximum_loss = (self._spread_witdh - self._spread_entry_price) * self.multiplier
        self._POP = (1 - self.legs['short_leg'].price / self._spread_witdh) * 100
        # ROI target 15-50 %
        self._ROI = self._maximum_profit / self._maximum_loss
        
        
    @property
    def spread_entry_price(self):
        return self._spread_entry_price

    @property
    def spread_witdh(self):
        return self._spread_witdh

    @property
    def breakeven_price(self):
        return self._breakeven_price

    @property
    def maximum_profit(self):
        return self._maximum_profit
    
    @property
    def maximum_loss(self):
        return self._maximum_loss
    
    @property
    def POP(self):
        return self._POP

    @property
    def ROI(self):
        return self._ROI