from collections import OrderedDict
from dataclasses import dataclass
import datetime
from enum import Enum
from typing import Tuple
from optopus.common import OwnershipType
from optopus.option import Option


class StrategyType(Enum):
    ShortPut = "SP"
    ShortPutVerticalSpread = "SPVS"
    ShortCallVerticalSpread = "SCVS"


@dataclass(frozen=True)
class Leg:
    option: Option
    ownership: OwnershipType
    ratio: int
    # FIXME: filled & commission are position fields?
    # filled: int
    # commission: float
    # created: datetime.datetime = datetime.datetime.now()

    @property
    def price(self):
        return self.option.midpoint

    # FIXME: I have to use a leg_id property?

    # @property
    # def leg_id(self):
    #    return (
    #        self.option.code
    #        + " "
    #        + str(self.ownership.value)
    #        + " "
    #        + self.option.right.value
    #        + " "
    #        + str(round(self.option.strike, 1))
    #        + " "
    #        + self.option.expiration.strftime("%d-%m-%Y")
    #    )


@dataclass(frozen=True)
class Strategy:
    # code: str
    legs: Tuple[Leg]
    strategy_type: StrategyType
    ownership: OwnershipType
    take_profit_factor: float

    # FIXME: Do I need a strategy_id?
    # @property
    # def strategy_id(self):
    #    return self.code + ' ' + self.created.strftime('%d-%m-%Y %H:%M:%S')


class DefinedStrategy:
    def __init__(self, strategy: Strategy, quantity=1):
        if quantity < 1:
            raise ValueError("Strategy quantity must be greater than 0")
        self._strategy = strategy
        self._quantity: int = quantity

        self._created: datetime.datetime = datetime.datetime.now()
        self._opened: datetime.datetime = None
        self._closed: datetime.datetime = None

    @property
    def strategy(self):
        return self._strategy

    @property
    def created(self):
        return self._created

    @property
    def opened(self):
        return self._opened

    @opened.setter
    def opened(self, val):
        if val <= self.created:
            raise ValueError("Opened time must be after created time")
        self._opened = val

    @property
    def closed(self):
        return self._closed

    @closed.setter
    def closed(self, val):
        if not self.opened:
            raise ValueError("Opened time must be defined")
        if val <= self.opened:
            raise ValueError("Closed time must be after opened time")

    @property
    def quantity(self):
        return self._quantity
