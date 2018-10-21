# -*- coding: utf-8 -*-
import logging
from optopus.data_objects import (OrderType, OrderRol,
                                  OrderStatus)
from optopus.strategy import Strategy
from optopus.data_manager import DataManager
from optopus.utils import notify


class OrderManager():
    def __init__(self, broker, data_manager: DataManager) -> None:
        self._broker = broker
        self._data_manager = data_manager
        self._log = logging.getLogger(__name__)

    def order_status_changed(self, trade) -> None:
        if trade.status == OrderStatus.Filled and trade.remaining == 0:
            self._log.info(f'Order filled (remaining {trade.remaining}): {trade.order_id}')
      
        self._log.debug(f'Order status changed {trade.order_id} : {trade.status.value}')

    def new_strategy(self, strategy: Strategy) -> None:
        #self._price_strategy(strategy)
        self._size_strategy(strategy)
        self._data_manager.update_strategy(strategy)
        print(str(strategy))
        self._broker.open_strategy(strategy)
        

    def _size_strategy(self, strategy: Strategy) -> None:
        strategy.quantity = 1

    #def _price_strategy(self, strategy: Strategy) -> None:
    #    for leg in strategy.legs.values():
    #        leg.price =  (leg.option.bid + leg.option.ask) / 2
    #        print(leg.option.strike, leg.option.option_price, leg.option.bid, leg.option.ask, leg.price)