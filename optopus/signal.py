# -*- coding: utf-8 -*-
from enum import Enum
from optopus.security import SecurityType
from optopus.money import Money
from optopus.parameter import p_currency
import datetime


class RightType(Enum):
    Call = 'C'
    Put = 'P'


class ActionType(Enum):
    Buy = 'BUY'
    Sell = 'SELL'


class ItemSignal():
    def __init__(self,
                 symbol: str,
                 security_type: SecurityType,
                 expiration: datetime.date,
                 strike: int,
                 right: RightType,
                 action: ActionType,
                 quantity: int,
                 limit: Money) -> None:

        self.symbol = symbol
        self.security_type = security_type
        if strike <= 0:
            raise(ValueError)
        self.strike = strike
        self.right = right
        self.action = action
        if quantity < 1:
            raise(ValueError)
        self.quantity = quantity
        if limit <= Money(0,p_currency):
            raise(ValueError)
        self.limit = limit

class Signal():
    def __init__(self, items: list) -> None:
        self.created = datetime.datetime.now()
        if not items:
            raise(ValueError)
        self.items = items
