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
