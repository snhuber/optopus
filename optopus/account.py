#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 17:27:47 2018

@author: ilia
"""
# Refactor using Data Classes
# https://stackoverflow.com/questions/34269772/type-hints-in-namedtuple

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
        # Cash Account: Minimum (Equity with Loan Value, Previous Day Equity
        # with Loan Value)-Initial Margin, Standard Margin Account: Minimum
        # (Equity with Loan Value, Previous Day Equity with Loan Value)
        # - Initial Margin *4
        self.buying_power = None
        # Cash recognized at the time of trade + futures PNL
        self.cash = None
        # This value tells what you have available for trading
        self.funds = None
        # Number of Open/Close trades in a day
        self.max_day_trades = None

    def update_item_value(self, item: AccountItem) -> bool:
        if hasattr(self, item.tag):
            if item.value:
                setattr(self, item.tag, item.value)
            else:
                setattr(self, item.tag, item.money)
        else:
            raise(AttributeError)

    @property
    def id(self) -> str:
        """Return de account identifier"""

        return self._id

    @id.setter
    def id(self, value):
        if not self._id:
            self._id = value


