# -*- coding: utf-8 -*-
from optopus.currency import Currency
import datetime

CURRENCY = Currency.USD
HISTORICAL_YEARS = 1
STDEV_DAYS = 22
SELL_COLOR = 'tomato'
BUY_COLOR = 'green'
UNDERLYING_COLOR = 'lightseagreen'
DATA_DIR = 'data'
DTE_MAX = 50
DTE_MIN = 25
EXPIRATIONS = [datetime.date(2018, 9, 21),
               datetime.date(2018, 10, 19),
               datetime.date(2018, 11, 16),
               datetime.date(2018, 12, 21)]

