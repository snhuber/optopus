# -*- coding: utf-8 -*-
from optopus.data_manager import DataManager


class PortfolioManager():
    def __init__(self, data_manager: DataManager) -> None:
        self._data_manager = data_manager

    def positions(self) -> object:
        return self._data_manager.positions()

    # http://www.nishatrades.com/blog/beta-weighted-delta
    # https://www.dough.com/blog/beta-weighted-portfolio
    def beta_weighted_delta(self) -> float:
        pass
    
    def update_positions(self):
        for p in self._data_manager._data_positions.values():
            print(p.trades)
            t = p.trades[-1]
            o = self._data_manager.update_option(t.data_source_id)
            p.option_price = o.option_price
            p.trade_time = t.time
            p.underlying_price = o.underlying_price
            p.commission = o.commission
            p.beta = o.beta
            p.delta = o.delta
            p.algorithm = t.algorithm
            p.strategy = t.strategy
            p.rol = t.rol
            
            
            
    
