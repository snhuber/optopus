# -*- coding: utf-8 -*-
import datetime
from collections import OrderedDict
import copy
import logging
import os
import pickle
from typing import List

from pathlib import Path
from optopus.account import Account, AccountItem
from optopus.data_objects import (DataSource,
                                  PositionData, TradeData, BarData,
                                  Asset, AssetData, OptionData,
                                  AssetType, OwnershipType, RightType, Strategy)
from optopus.settings import (HISTORICAL_YEARS, DATA_DIR, STRATEGY_DIR,
                              POSITIONS_FILE)
from optopus.utils import is_nan, format_ib_date
from optopus.computation import asset_computation, assets_computation
from optopus.strategy import StrategyFactory


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
    _positions : Dict[str, PositionData]
        the positions of the account
    _strategies : Dict[str, Strategy]
        the strategies grouping the positions
    _da : DataAdapter
        adapter object for ib_insyinc
    _logger: Looger
        class logger
    
    Methods
    -------
    
    """
    def __init__(self,  data_adapter: DataAdapter, watch_list: dict) -> None:
        """
        Parameters
        ----------
        data_adapter : DataAdapter
            Adapter object for ib_insyinc
        watch_list: Dict[str, AssetType]
            The code and type of assets we can trade
        """
        self._da = data_adapter
        self.account = None
        # create the assets
        self._assets = {code: Asset(code, asset_type)
                        for code, asset_type in watch_list.items()}
        self._positions = {}
        self._strategies = {}
        
        self._strategy_repository = StrategyRepository()
        self._strategies = self._strategy_repository.all_items()
        
        self._log = logging.getLogger(__name__)
        

    def _account_item(self, item: AccountItem) -> None:
        """Updates a attribute of account object. Executed by a event.
        Parameters
        ----------
        item : AccountItem
            The name and value of the attribute to update
        """
        try:
            self._account.update_item_value(item)
        except Exception as e:
            self._log.error('Failed to update the account object',
                            exc_info=True)

    def _position(self, position: PositionData) -> None:
        """Adds a position values to the positions set. Executed by a event.
        Parameters
        ----------
        position : PositionData
            the new position values
        """
        key = self._position_key(position.code,
                                 position.asset_type,
                                 position.expiration,
                                 position.strike,
                                 position.right,
                                 position.ownership)

        self._positions[key] = position
        
        self._log.debug('[_position] position event fired')

    def _commission_report(self, trade: TradeData) -> None:
        """Adds a new trade to a position. After update the position, save all
        the positions to a file. Exected by a event

        Parameters
        ----------
        trade : TradeData
            the new trade
        """
        self._log.debug('[_commission_report] commission report event fired')
        key = self._position_key(trade.code,
                                 trade.asset_type,
                                 trade.expiration,
                                 trade.strike,
                                 trade.right,
                                 trade.ownership)
        pos = self._positions[key]
        self._log.debug(f'[_commission_report]: new trade {trade}')
        pos.trades.append(trade)
        # save the positions beacause we have updated one position
        self._write_positions()
        #self.update_positions()

    def initialize_assets(self) -> None:
        """Retrieves the ids of the assets (contracts) from IB
        """
        contracts = self._da.initialize_assets(self._assets.values())
        for i in contracts:
                self._assets[i].contract = contracts[i]

    def update_current_assets(self) -> None:
        """Updates the current asset values.
        """
        ads = self._da.update_assets(self._assets.values())
        for ad in ads:
            self._assets[ad.code].current = ad

    def update_historical_assets(self) -> None:
        """Updates historical assets values
        """
        for a in self._assets.values():
            if not a.historical_is_updated():
                a.historical = self._da.update_historical(a)
                a._historical_updated = datetime.datetime.now()

    def update_historical_IV_assets(self) -> None:
        """Updates historical IV asset values
        """
        for a in self._assets.values():
            if not a.historical_IV_is_updated():
                a.historical_IV = self._da.update_historical_IV(a)
                a._historical_IV_updated = datetime.datetime.now()

    def compute_assets(self) -> None:
        """Computes some asset measures
        """
        # measures computed one by one
        asset_computation(self._assets)
        # measures computed all at one
        assets_computation(self._assets, self.assets_matrix('bar_close'))
        
    def assets_matrix(self, field: str) -> dict:
        """Returns a attribute from historical for every asset
        
        Parameters
        ----------
        field: str
            attribute from historical assets
            
        Returns
        -------
            A series for each asset. 
        """
        d = {}
        for a in self._assets.values():
            d[a.code] = [getattr(bd, field) for bd in a._historical_data]
        return d

    def update_option_chain(self, code: str) -> None:
        """Update option chain values

        Parameters
        ----------
        code: str
            code of the underlying
        """
        a = self._assets[code]
        a._option_chain = self._da.create_optionchain(a)

    def _position_key(self,
                      code: str,
                      asset_type: AssetType,
                      expiration: datetime.date,
                      strike: float,
                      right: RightType,
                      ownership: OwnershipType) -> str:
        """Create a identifier from parameters
        
        Parameters
        ----------
        code: str
            code of underlying
        asset_type: AssetType
            type of underlying
        expiration: date
            expiration date of the option
        strike: float
            strike value of the option
        right: RightType
            right of the option
        ownershiop: OwnershipType
            ownership of the option
        """
        ownership = ownership.value if ownership else 'NA'
        expiration = format_ib_date(expiration) if expiration else 'NA'
        strike = str(strike) if not is_nan(strike) else 'NA'
        right = right.value if right else 'NA'

        key = code + '_' + asset_type.value + '_' \
            + expiration + '_' + strike + '_' + right + '_' + ownership

        return key

    def _write_positions(self) -> None:
        """Saves the position to file
        """
        file_name = Path.cwd() / DATA_DIR / POSITIONS_FILE
        try:
            with open(file_name, 'wb') as file_handler:
                    pickle.dump(self._positions, file_handler)
        except Exception as e:
            self._log.error('[_write_positions] failed to open positions file', exc_info=True)

    def update_positions_trades(self) -> None:
        """Update current positions adding the trades from file
        """
        file_name = Path.cwd() / DATA_DIR / POSITIONS_FILE
        try:
            with open(file_name, 'rb') as file_handler:
                positions_bk = pickle.load(file_handler)
                for k, p in self._positions.items():
                    self._log.debug(f'[update_positions_trades] key {k}')
                    if k in positions_bk.keys():
                        if positions_bk[k].trades:
                            p.trades = positions_bk[k].trades
                            self._log.debug(f'[update_positions_trades] position trades updated {p}')

        except FileNotFoundError as e:
            self._log.error('Failed to open positions file', exc_info=True)

    def update_positions(self):
        """Updates the positions. First the function assigns the trades to
        each position and then it updates the positions values. Finally
        it persits the positions.
        """
        self.update_positions_trades()
        
        trades = [p.trades[-1] for p in self._positions.values() if p.trades and p.quantity]
        
        self._log.debug(f'[update_positions] positions to update: {len(trades)}')
        
        for trade in trades:
            [option] = self._da.create_options([trade.contract])
            key = self._position_key(option.code,
                                     option.asset_type,
                                     option.expiration,
                                     option.strike,
                                     option.right,
                                     trade.ownership)

            position = self._positions[key]
            position.option_price = option.option_price
            position.underlying_price = option.underlying_price
            position.delta = option.delta
            position.DTE = option.DTE
            position.trade_price = trade.price
            position.trade_time = trade.time
            position.algorithm = trade.algorithm
            position.strategy_type = trade.strategy_type
            position.strategy_id = trade.strategy_id
            position.rol = trade.rol
            position.beta = self._assets[option.code].current.beta
            self._log.debug(f'[update_positions] position updated {position}')

        # persits the current positions
        self._write_positions()

    def update_strategies(self):
        """Update the strategies from positions
        """
        for k, p in self._positions.items():
            if p.strategy_id not in self._positions.keys():
                s = StrategyFactory.create_strategy(p.strategy_type,
                                                    p.strategy_id)
                self._strategies[s] = s

            s.add_position(p)

    def update_strategy_options(self) -> None:
        for strategy_key, strategy in self._strategies.items():
            for leg_key, leg in strategy.legs.items():
                leg.option = self._da.get_options([leg.contract])[0]
                self._log.debug(f'Updated contract {leg.contract}')
                
    def update_account(self) -> None:
        self.account = self._da.get_account_values()

    def check_strategy_positions(self):
        positions = self._da.get_positions()
        for strategy_key, strategy in self._strategies.items():
            for leg_key, leg in strategy.legs.items():
                try:
                    position = positions[leg.leg_id]
                    if position.ownership == leg.ownership:
                        if position.quantity >= leg.quantity:
                            position.quantity -= leg.quantity
                            #leg.position_quantity = leg.order_quantity
                            if position.quantity == 0:
                                del positions[position.position_id]
                        else:
                            self._log.warning(f'The leg {leg.leg_id} doesn\'t have enough positions')
                    else:
                        self._log.warning(f'The leg {leg.leg_id} and position ownerships don\'t match')
                                       
                except KeyError as e:
                    self._log.warning(f'The leg {leg.leg_id} doesn\'t have any position')
                
                
        if len(positions):
            self._log.warning(f'There are excess positions')
            

    def get_strategy(self, strategy_id: str) -> Strategy:
        return copy.deepcopy(self._strategies[strategy_id])
        
    def add_strategy(self, strategy: Strategy) -> None:
        self._strategy_repository.add(strategy)
        self._strategies[strategy.strategy_id] = copy.deepcopy(strategy)
        
    def update_strategy(self, strategy: Strategy) -> None:
        self._strategy_repository.update(strategy)
        self._strategies[strategy.strategy_id] = copy.deepcopy(strategy)
        self._strategies[strategy.strategy_id].updated = datetime.datetime.now()

class StrategyRepository:
    """Repository class for mananging strategies
    """
    def __init__(self) -> None:
        self._path = Path(Path.cwd() / DATA_DIR / STRATEGY_DIR)
        self._log = logging.getLogger(__name__)

    def add(self, item: Strategy) -> None:
        file_name = self._file_name(item)
        try:
            with open(file_name, 'wb') as file_handler:
                    pickle.dump(item, file_handler)
        except Exception as e:
            self._log.error('[add] failed to write strategy file', exc_info=True)

    def update(self, item: Strategy) -> None:
        self.add(item)

    def delete(self, item: Strategy) -> None:
        file_name = self._file_name(item)
        try:
            os.remove(file_name)
        except Exception as e:
            self._log.error('[delete] faile to delete strategy file', exce_info=True)

    def all_items(self) -> List[Strategy]:
        strategies = {}
        for f in self._path.glob('*.pckl'):
            file_name = self._path / f
            try:
                with open(file_name, 'rb') as file_handler:
                    s = pickle.load(file_handler)
                    strategies[s.strategy_id] = s
                self._log.debug(f'Loaded {f}')
            except FileNotFoundError as e:
                self._log.error('Failed to open strategy file', exc_info=True)
        return strategies

    def _file_name(self, item: Strategy) -> str:
        return self._path / (item.strategy_id + '.pckl')