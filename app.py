#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  5 07:34:45 2018

@author: ilia
"""
import datetime
from ib_insync.ib import IB
from optopus.ib_adapter import IBBrokerAdapter
from optopus.optopus import Optopus
from optopus.utils import pdo
from optopus.data_objects import IndexAsset, OptionChainAsset
from optopus.data_manager import DataSource


host = '127.0.0.1'
#port = 4002  # gateway
port = port = 7497  # TWS
client = 9

ib = IB()
ib.connect(host, port, client)

ib_adapter = IBBrokerAdapter(ib)

opt = Optopus(ib_adapter)
#opt.start()

SPX = IndexAsset('SPX', DataSource.IB)
RUT = IndexAsset('RUT', DataSource.IB)
f = ['high', 'low', 'close', 'bid', 'bid_size', 'ask', 'ask_size',
             'last', 'last_size', 'time', 'midpoint', 'market_price']
print(pdo(opt.current([SPX, RUT], f)))

of = ['high', 'low', 'close',
      'bid', 'bid_size', 'ask', 'ask_size', 'last', 'last_size',
      'volume', 'time']

of = ['delta', 'gamma', 'theta', 'vega', 
      'implied_volatility', 'underlying_price', 'underlying_dividens',
      'moneyness', 'intrinsic_value', 'extrinsic_value', 'time']

SPX_OPT = OptionChainAsset(SPX, underlying_distance=1.5)
print(pdo(opt.current([SPX_OPT], of)))

opt.update_assets()

print(pdo(opt.current([SPX_OPT], of)))

#for t in ib.timeRange(datetime.time(0, 0), datetime.datetime(2100, 1, 1, 0), 10):
#    print(t)
#    opt.beat()

ib.disconnect()
