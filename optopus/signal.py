# -*- coding: utf-8 -*-
import datetime
from enum import Enum
import uuid
from security import SecurityType
from money import Money
from settings import CURRENCY


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

        self.item_signal_id = uuid.uuid4()
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
        if limit <= Money(0, CURRENCY):
            raise(ValueError)
        self.limit = limit


class Signal():
    def __init__(self, origin: str) -> None:
        self.created = datetime.datetime.now()
        if not origin:
            raise(ValueError)
        self.origin = origin
        if not items:
            raise(ValueError)
        self.items = items

    def add_item(self,
                 symbol: str,
                 security_type: SecurityType,
                 expiration: datetime.date,
                 strike: int,
                 right: RightType,
                 action: ActionType,
                 quantity: int,
                 limit: Money) -> None:

        i = ItemSignal(symbol, security_type, expiration, strike, right,
                       action, quantity, limit)

        self.items.append(i)
