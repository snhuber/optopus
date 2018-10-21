# -*- coding: utf-8 -*-
import copy
import datetime
import logging
from typing import Dict
from optopus.data_objects import (Asset, History, Measures, Portfolio)
from optopus.strategy import Strategy
from optopus.computation import (assets_loop_computation,
                                 assets_vector_computation,
                                 assets_directional_assumption,
                                 portfolio_bwd)
from optopus.strategy_repository import StrategyRepository
from optopus.settings import CURRENCY, MARKET_BENCHMARK

class DataAdapter:
    pass


class DataManager():
    """
    A class used to store the data and manage the their updates

    Attributes
    ----------
    _account : Account
        the data of the broker account
    _assets : Dict[str, Asset]
        the assets we can trade
    _strategies : Dict[str, Strategy]
        the strategies grouping the positions
    _da : DataAdapter
        adapter object for ib_insyinc
    _logger: Looger
        class logger
    """
    def __init__(self,  data_adapter: DataAdapter, watch_list: dict) -> None:
        self._da = data_adapter
        self._account = None
        self.portfolio = Portfolio()
        self._assets = {code: Asset(code, asset_type, CURRENCY)
                        for code, asset_type in watch_list.items()}
        
        self._strategies = {}

        self._strategy_repository = StrategyRepository()
        self._strategies = self._strategy_repository.all_items()

        self._log = logging.getLogger(__name__)
    
    @property    
    def assets(self):
        return self._assets
    
    @property
    def strategies(self):
        return self._strategies
    
    @property
    def account(self):
        return self._account
    
    @account.setter
    def account(self, values):
        self._account = values

    def update_account(self) -> None:
        self.account = self._da.get_account_values()

    def initialize_assets(self) -> None:
        """Retrieves the ids of the assets (contracts) from IB
        """
        self._da.initialize_assets(self.assets)
        
    def update_assets(self) -> None:
        """Updates the current asset values.
        """
        current_values = self._da.update_assets(self.assets)
        for code, current in current_values.items():
            self._assets[code].current = current 

    def update_historical_assets(self) -> None:
        """Updates historical assets values
        """
        for a in self._assets.values():
            if a.price_history:
                delta = datetime.datetime.now() - a.price_history.created
                if delta.days:
                    a.price_history = self._da.get_price_history(a)
            else:
                a.price_history = self._da.get_price_history(a)

    def update_historical_IV_assets(self) -> None:
        """Updates historical IV asset values
        """
        for a in self._assets.values():
            if a.iv_history:
                delta = datetime.datetime.now() - a.iv_history.created
                if delta.days:
                    a.iv_history = self._da.get_iv_history(a)
            else:
                a.iv_history = self._da.get_iv_history(a)

    def compute(self) -> None:
        """Computes some asset measures
        """
        # TODO: Do Measures class immutable
        loop_m = assets_loop_computation(self._assets)
        vector_m = assets_vector_computation(self._assets, self.assets_matrix('close'))
        #print({k: a.current.market_price for (k, a) in self._assets.items()})
        directional_m = assets_directional_assumption(self._assets, self.assets_matrix('close'))
        #self.portfolio.bwd = portfolio_bwd(self.strategies,
        #                                   self._assets,
        #                                   self._assets[MARKET_BENCHMARK].current.market_price)

        for a in self._assets.values():
            a.measures = Measures(
                                price_percentile=loop_m[a.code]['price_percentile'], 
                                price_pct=loop_m[a.code]['price_pct'], 
                                iv=loop_m[a.code]['iv'], 
                                iv_rank=loop_m[a.code]['iv_rank'], 
                                iv_percentile=loop_m[a.code]['iv_percentile'],
                                iv_pct=loop_m[a.code]['iv_pct'], 
                                stdev=vector_m[a.code]['stdev'],
                                beta=vector_m[a.code]['beta'], 
                                correlation=vector_m[a.code]['correlation'],
                                directional_assumption=directional_m[a.code]['directional_assumption'])

    def assets_matrix(self, field: str) -> dict:
        """Returns a attribute from historical for every asset
        """
        d = {}
        for a in self._assets.values():
            d[a.code] = [getattr(bar, field) for bar in a.price_history.values]
        return d

    def option_chain(self, code: str, expiration: datetime.date) -> None:
        """Update option chain values
        """
        a = self._assets[code]
        return self._da.get_optionchain(a, expiration)

    def update_strategy_options(self) -> None:
        for strategy_key, strategy in self._strategies.items():
            for leg_key, leg in strategy.legs.items():
                leg.option = self._da.get_options([leg.option.contract])[0]
                self._log.debug(f'Updated contract {leg.option.contract}')

    def check_strategy_positions(self):
        positions = self._da.get_positions()
        strategies_to_remove = []
        for strategy_key, strategy in self._strategies.items():
            strategy_positions = 0     
            for leg_key, leg in strategy.legs.items():
                try:
                    position = positions[leg.leg_id]
                    quantity = strategy.quantity * leg.ratio
                    if position.ownership == leg.ownership:
                        if position.quantity >= quantity:
                            position.quantity -= quantity
                            strategy_positions += quantity
                            if not position.quantity:
                                del positions[position.position_id]
                        else:
                            strategy_positions += position.quantity
                            self._log.warning(f'Leg {leg.leg_id} doesn\'t have enough positions')
                    else:
                        self._log.warning(f'Leg {leg.leg_id} and position ownership don\'t match')
                except KeyError as e:
                    self._log.warning(f'Leg {leg.leg_id} doesn\'t have any position')       

            if strategy_positions == sum([leg.ratio * strategy.quantity
                                          for leg in strategy.legs.values()]) and not strategy.opened:
                strategy.opened = datetime.datetime.now()
                self.update_strategy(strategy)
                self._log.info(f'Strategy {strategy_key} opened')
            
            if not strategy_positions and strategy.opened and not strategy.closed:
                strategy.closed = datetime.datetime.now()
                self.update_strategy(strategy)
                self.delete_strategy(strategy)
                strategies_to_remove.append(strategy.strategy_id)
                self._log.info(f'Strategy {strategy_key} closed')

        if len(positions):
            self._log.warning(f'There are excess positions')

        for s in strategies_to_remove:
            del self._strategies[s]
        #self._strategies = self._strategy_repository.all_items()

    #def get_strategy(self, strategy_id: str) -> Strategy:
    #    return self._strategies[strategy_id]


    def add_strategy(self, strategy: Strategy) -> None:
        self._strategy_repository.add(strategy)
        self._strategies[strategy.strategy_id] = strategy

    def update_strategy(self, strategy: Strategy) -> None:
        self._strategies[strategy.strategy_id].updated = datetime.datetime.now()
        self._strategy_repository.update(strategy)

    def delete_strategy(self, strategy: Strategy) -> None:
        self._strategy_repository.delete(strategy)
