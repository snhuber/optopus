# -*- coding: utf-8 -*-
#from signal import Signal
from optopus.data_objects import OrderData, OrderType

class OrderManager():
    def __init__(self, broker) -> None:
        self._broker = broker

    def process(self, signals):
        orders=[]
        for s in signals:
            reference = s.algorithm + '-' + s.strategy.value + '-' \
                        + s.rol
          
            
            o = OrderData(asset=s.asset,
                      action=s.action,
                      quantity=s.quantity,
                      price=s.price,
                      order_type=OrderType.Limit,
                      expiration=s.expiration,
                      strike=s.strike,
                      right=s.right,
                      reference=reference)
            orders.append(o)
        self._broker.place_order(orders)
            
        