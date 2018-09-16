# -*- coding: utf-8 -*-
import logging
from optopus.data_objects import (OrderData, OrderType, Strategy, OrderRol,
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
        for leg in strategy.legs.values():
            reference = strategy.strategy_id + '_' + leg.leg_id
            profit_price = round(leg.order_price * leg.take_profit_factor, 2)
            stop_price = round(leg.order_price * leg.stop_loss_factor, 2)
            parent = OrderData(code=leg.code,
                              rol=OrderRol.NewLeg,
                              ownership=leg.ownership,
                              quantity=leg.quantity,
                              price=leg.order_price,
                              order_type=OrderType.Limit,
                              expiration=leg.expiration,
                              strike=leg.strike,
                              right=leg.right,
                              reference=reference,
                              contract=leg.contract)
            profit = OrderData(code=leg.code,
                               rol=OrderRol.TakeProfit,
                               ownership=leg.ownership,
                               quantity=leg.quantity,
                               price=profit_price,
                               order_type=OrderType.Limit,
                               expiration=leg.expiration,
                               strike=leg.strike,
                               right=leg.right,
                               reference=reference,
                               contract=leg.contract)
            stop = OrderData(code=leg.code,
                             rol=OrderRol.StopLoss,
                             ownership=leg.ownership,
                             quantity=leg.quantity,
                             price=stop_price,
                             order_type=OrderType.Stop,
                             expiration=leg.expiration,
                             strike=leg.strike,
                             right=leg.right,
                             reference=reference,
                             contract=leg.contract)

        self._data_manager.update_strategy(strategy)
        self._broker.place_orders(strategy, parent, profit, stop)

    def _size_strategy(self, strategy: Strategy) -> None:
        for leg in strategy.legs.values():
            leg.quantity = leg.ratio

    def _price_strategy(self, strategy: Strategy) -> None:
        for leg in strategy.legs.values():
            leg.order_price = leg.strategy_price
