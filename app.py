#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  5 07:34:45 2018

@author: ilia
"""
from ib_insync.ib import IB
from optopus.ib_adapter import IBBrokerAdapter
from optopus.optopus import Optopus
from optopus.utils import pdo, plot_option_positions
from optopus.data_objects import IndexAsset, StockAsset, OptionChainAsset
from optopus.data_manager import DataSource


host = '127.0.0.1'
#port = 4002  # gateway
port = port = 7497  # TWS
client = 10

ib = IB()
opt = Optopus(IBBrokerAdapter(ib, host, port, client))
opt.start()

f = ['high', 'low', 'close', 'bid', 'bid_size', 'ask', 'ask_size',
             'last', 'last_size', 'time', 'midpoint', 'market_price']

print('---- SPY ----')
SPY = StockAsset('SPY', DataSource.IB)
print(pdo(opt.current(SPY, f)))

SPX = IndexAsset('SPX', DataSource.IB)
RUT = IndexAsset('RUT', DataSource.IB)

print(pdo(opt.current([SPX, RUT], f)))

print(pdo(opt.historical([SPX], ['bar_low'])))

print(pdo(opt.historical_IV([SPX], ['bar_high'])))

print(opt.IV_rank(SPX, 0.1))
print(opt.IV_percentile(SPX, 0.1))
#print(pdo(opt.historical_IV([SPX], ['bar_min'])))
of = ['high', 'low', 'close',
      'bid', 'bid_size', 'ask', 'ask_size', 'last', 'last_size',
      'volume', 'time']

of = ['delta', 'gamma', 'theta', 'vega', 
      'implied_volatility', 'underlying_price', 'underlying_dividens',
      'moneyness', 'intrinsic_value', 'extrinsic_value', 'time']

SPX_OPT = OptionChainAsset(SPX)
print(pdo(opt.current([SPX_OPT], of)))



#opt.update_assets()

#print(pdo(opt.current([SPX_OPT], of)))

#for t in ib.timeRange(datetime.time(0, 0), datetime.datetime(2100, 1, 1, 0), 10):
#    print(t)
#    opt.beat()

opt.stop()