#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 17:27:47 2018

@author: ilia
"""
# Refactor using Data Classes
# https://stackoverflow.com/questions/34269772/type-hints-in-namedtuple

from typing import NamedTuple


class Account:
    """Class representing a broker account"""

    def __init__(self) -> None:
        self._id = None

    @property
    def id(self) -> str:
        """Return de account identifier"""

        return self._id

    @id.setter
    def id(self, value):
        if not self._id:
            self._id = value


class AccountItem(NamedTuple):
    account_id: str = None
    tag: str = None
    value: object = None
    currency: str = None