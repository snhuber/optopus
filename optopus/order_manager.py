# -*- coding: utf-8 -*-
#from signal import Signal
from optopus.data_objects import OrderData, OrderType

class OrderManager():
    def __init__(self, broker) -> None:
        self._broker = broker

    def process(self, signal):
        reference = signal.algorithm + '-' + signal.strategy_id + '-' \
                    + signal.rol
      
        
        order = OrderData(asset=signal.asset,
                          action=signal.action,
                          quantity=signal.quantity,
                          price=signal.price,
                          order_type=OrderType.Limit,
                          expiration=signal.expiration,
                          strike=signal.strike,
                          right=signal.right,
                          reference=reference)
        
        self._broker.place_order(order)
            
        