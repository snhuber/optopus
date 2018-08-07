# -*- coding: utf-8 -*-
from enum import Enum


class SecurityType(Enum):
    Stock = 'STK'
    Option = 'OPT'
    Future = 'FUT'
    Forex = 'CASH'
    Index = 'IND'
    CFD = 'CFD'
    Bond = 'BOND'
    Commodity = 'CMDTY'
    FuturesOption = 'FOP'
    MutualFund = 'FUND'
    Warrant = 'IOPT'


class Security:
    def __init__(self,
                 symbol: str,
                 name: str,
                 security_type: SecurityType) -> None:
        
        assert security_type.name in SecurityType.__members__
        self.symbol = symbol
        self.name = name
        self.security_type = security_type


universe = {'SPX': Security('SPX', 'S&P 500 Index', SecurityType.Index)}
