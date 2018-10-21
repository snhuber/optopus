from collections import OrderedDict
from dataclasses import dataclass
import datetime
from enum import Enum
from typing import List, Dict
from optopus.data_objects import Option, OwnershipType, Currency

class StrategyType(Enum):
    ShortPut = 'SP'
    ShortPutVerticalSpread = 'SPVS'
    ShortCallVerticalSpread = 'SCVS'

@dataclass(frozen=True)
class Leg:
    option: Option
    ownership: OwnershipType
    ratio: int
    # TODO: Become Leg class immutable (filled & commission are position fields?)
    #filled: int
    #commission: float
    created: datetime.datetime = datetime.datetime.now()

    @property
    def price(self):
        return (self.option.bid + self.option.ask) / 2

    @property
    def leg_id(self):
        return self.option.code + ' ' + str(self.ownership.value) + ' ' + self.option.right.value + ' ' + str(round(self.option.strike, 1)) + ' ' + self.option.expiration.strftime('%d-%m-%Y')
        
    
@dataclass(frozen=True)
class Strategy:
    code: str
    strategy_type: StrategyType
    ownership: OwnershipType
    currency: Currency
    take_profit_factor: float
    multiplier: int
    legs: Dict[str, Leg]    
    created: datetime.datetime = datetime.datetime.now()

    @property
    def strategy_id(self):
        return self.code + ' ' + self.created.strftime('%d-%m-%Y %H:%M:%S')
    
