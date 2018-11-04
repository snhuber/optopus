# -*- coding: utf-8 -*-
# TODO: import from a cfg file
from optopus.data_objects import Currency
import datetime

CURRENCY = Currency.USDollar
HISTORICAL_YEARS = 1
STDEV_DAYS = 22
SELL_COLOR = 'tomato'
BUY_COLOR = 'green'
UNDERLYING_COLOR = 'lightseagreen'
DATA_DIR = 'data'
STRATEGY_DIR = 'strategy'
POSITIONS_FILE = 'positions.pckl'
DTE_MAX = 50
DTE_MIN = 0
EXPIRATIONS = [datetime.date(2018, 9, 21),
               datetime.date(2018, 10, 19),
               datetime.date(2018, 11, 16),
               datetime.date(2018, 12, 21),
               datetime.date(2019, 1, 18),
               datetime.date(2019, 2, 15),
               datetime.date(2019, 3, 15),
               datetime.date(2019, 4, 19),
               datetime.date(2019, 5, 17),
               datetime.date(2019, 6, 21),
               datetime.date(2019, 7, 19),
               datetime.date(2019, 8, 16),
               datetime.date(2019, 9, 20),
               datetime.date(2019, 10, 18),
               datetime.date(2019, 11, 15),
               datetime.date(2019, 12, 20)]
MARKET_BENCHMARK = 'SPY'
STDEV_PERIOD = 22
BETA_PERIOD = 252
CORRELATION_PERIOD = 252
PRICE_PERIOD = 22
IV_PERIOD = 22
SLEEP_LOOP = 20
PRESERVED_CASH_FACTOR = 0.4
MAXIMUM_RISK_FACTOR = 0.05
RSI_WINDOW = 14
SMA1_WINDOW = 20
SMA2_WINDOW = 50
