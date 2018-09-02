#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 17:27:47 2018

@author: ilia
"""
# Refactor using Data Classes
# https://stackoverflow.com/questions/34269772/type-hints-in-namedtuple

from collections import OrderedDict
from typing import NamedTuple
from optopus.money import Money


class AccountItem(NamedTuple):
    account_id: str = None
    tag: str = None
    value: str = None
    money: Money = None


class Account:
    """Class representing a broker account"""

    def __init__(self) -> None:
        self._id = None

        # The basis for determining the price of the assets in your account.
        # Total cash value + stock value + options value + bond value
        self.net_liquidation = None
        # Buying power serves as a measurement of the dollar value of 
        # securities that one may purchase in a securities account without
        # depositing additional funds
        self.buying_power = None
        # Cash recognized at the time of trade + futures PNL
        self.cash = None
        # This value tells what you have available for trading
        self.funds = None
        # The Number of Open/Close trades a user could put on before 
        # Pattern Day Trading is detected. A value of "-1" means that the user
        # can put on unlimited day trades.
        # Number of Open/Close trades in a day
        self.max_day_trades = None
        # Initial Margin requirement of whole portfolio
        self.initial_margin = None       
        #  Maintenance Margin requirement of whole portfolio
        self.maintenance_margin = None
        # This value shows your margin cushion, before liquidation
        self.excess_liquidity = None
        # Excess liquidity as a percentage of net liquidation value
        self.cushion = None
        # The sum of the absolute value of all stock and equity option positions
        # Leverage = GrossPositionValue / NetLiquidation
        self.gross_position_value = None
        # Forms the basis for determining whether a client has the 
        # necessary assets to either initiate or maintain security positions. 
        # Cash + stocks + bonds + mutual funds
        self.equity_with_loan = None
        # Special Memorandum Account: Line of credit created when the market 
        # value of securities in a Regulation T account increase in value
        self.SMA = None

    def update_item_value(self, item: AccountItem) -> bool:
        if item.value:
            setattr(self, item.tag, item.value)
        else:
            setattr(self, item.tag, item.money)

    @property
    def id(self) -> str:
        """Return de account identifier"""

        return self._id

    @id.setter
    def id(self, value):
        if not self._id:
            self._id = value

    def to_dict(self) -> OrderedDict:
        d = {}
        d['net_liquidation'] = self.net_liquidation
        d['buying_power'] = self.buying_power
        d['cash'] = self.cash
        d['funds'] = self.funds
        d['max_day_trades'] = self.max_day_trades
        d['initial_margin'] = self.initial_margin
        d['maintenance_margin'] = self.maintenance_margin
        d['excess_liquidity'] = self.excess_liquidity
        d['cushion'] = self.cushion
        d['gross_position_value'] = self.gross_position_value
        d['equity_with_loan'] = self.equity_with_loan
        d['SMA'] = self.SMA
        return d
        
