# -*- coding: utf-8 -*-
import datetime
import logging
from optopus.data_objects import OrderData, OrderType, Strategy, OrderRol
from optopus.data_manager import DataManager


class OrderManager():
    def __init__(self, broker, data_manager: DataManager) -> None:
        self._broker = broker
        self._data_manager = data_manager
        self._log = logging.getLogger(__name__)

    def order_status_changed(self, trade) -> None:
        order_id = trade.order_id
        strategy_id, leg_id, _ = order_id.split('_')
        strategy = self._data_manager.get_strategy(strategy_id)
        order = strategy.legs[leg_id].orders[order_id]
        order.status = trade.status
        order.updated = datetime.datetime.now()
        self._data_manager.update_strategy(strategy)

        self._log.debug(f'Order status changed {order_id} : {order.status.value}')

    def execute_new_strategy(self, strategy: Strategy) -> None:
        self._size_strategy(strategy)
        self._price_strategy(strategy)
        for leg in strategy.legs.values():
            reference = strategy.strategy_id + '_' + leg.leg_id
            order = OrderData(asset=leg.asset,
                              rol=OrderRol.NewLeg,
                              ownership=leg.ownership,
                              quantity=leg.order_quantity,
                              price=leg.order_price,
                              order_type=OrderType.Limit,
                              expiration=leg.expiration,
                              strike=leg.strike,
                              right=leg.right,
                              reference=reference)
            profit = OrderData(asset=leg.asset,
                               rol=OrderRol.TakeProfit,
                               ownership=leg.ownership,
                               quantity=leg.order_quantity,
                               price=leg.order_price * leg.take_profit_factor,
                               order_type=OrderType.Limit,
                               expiration=leg.expiration,
                               strike=leg.strike,
                               right=leg.right,
                               reference=reference)
            stop = OrderData(asset=leg.asset,
                             rol=OrderRol.StopLoss,
                             ownership=leg.ownership,
                             quantity=leg.order_quantity,
                             price=leg.order_price * leg.stop_loss_factor,
                             order_type=OrderType.Stop,
                             expiration=leg.expiration,
                             strike=leg.strike,
                             right=leg.right,
                             reference=reference)
            leg.orders[order.order_id] = order
            leg.orders[profit.order_id] = profit
            leg.orders[stop.order_id] = stop

        self._data_manager.update_strategy(strategy)
        self._broker.place_new_strategy(strategy)

    def _size_strategy(self, strategy: Strategy) -> None:
        for leg in strategy.legs.values():
            leg.order_quantity = leg.strategy_quantity

    def _price_strategy(self, strategy: Strategy) -> None:
        for leg in strategy.legs.values():
            leg.order_price = leg.strategy_price
