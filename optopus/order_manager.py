# -*- coding: utf-8 -*-
import logging
from optopus.data_objects import (OrderType, Strategy, OrderRol,
                                  OrderStatus)
from optopus.data_manager import DataManager


class OrderManager():
    def __init__(self, broker, data_manager: DataManager) -> None:
        self._broker = broker
        self._data_manager = data_manager
        self._log = logging.getLogger(__name__)

    def order_status_changed(self, trade) -> None:
        if trade.status == OrderStatus.Filled and trade.remaining == 0:
            self._log.info(f'Order filled (remaining {trade.remaining}): {trade.order_id}')
      
        self._log.debug(f'Order status changed {trade.order_id} : {trade.status.value}')

    def execute_new_strategy(self, strategy: Strategy) -> None:
        
        self._size_strategy(strategy)
        self._price_strategy(strategy)
        strategy.calculate_measures()
        


        self._data_manager.update_strategy(strategy)
        self._broker.place_orders(strategy)

    def _size_strategy(self, strategy: Strategy) -> None:
        strategy.quantity = 1

    def _price_strategy(self, strategy: Strategy) -> None:
        for leg in strategy.legs.values():
            print(leg.option)
            leg.price =  (leg.option.bid + leg.option.ask) / 2
