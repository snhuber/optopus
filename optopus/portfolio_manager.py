# -*- coding: utf-8 -*-
from optopus.data_objects import DataSource, OwnershipType
from optopus.data_manager import DataManager
from optopus.settings import MARKET_BENCHMARK
from collections import OrderedDict

class PortfolioManager():
    def __init__(self, data_manager: DataManager) -> None:
        self._data_manager = data_manager

    # http://www.nishatrades.com/blog/beta-weighted-delta
    # https://www.dough.com/blog/beta-weighted-portfolio
    def _beta_weighted_delta(self) -> float:
        total = 0
        benchmark_price = self._data_manager._assets[MARKET_BENCHMARK].current.market_price
        for p in self._data_manager._positions.values():
            underlying_price = self._data_manager._assets[p.code].current.market_price
            ownership = 1 if p.ownership == OwnershipType.Buyer else -1
            BWDelta = (underlying_price / benchmark_price) * p.beta * p.delta * p.quantity * ownership
            total += BWDelta
        return total

    def update_positions(self):
        self._data_manager.update_positions()

    def to_dict(self) -> OrderedDict:
        d = OrderedDict()
        d['BWDelta'] = self._beta_weighted_delta()
        return d
