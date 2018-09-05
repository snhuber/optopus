#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  5 07:34:45 2018

@author: ilia
"""
from ib_insync.ib import IB
from optopus.ib_adapter import IBBrokerAdapter
from optopus.optopus import Optopus
from optopus.utils import to_df
from optopus.taco import Taco

print(__name__)


host = '127.0.0.1'
# port = 4002  # gateway
port = 7497  # TWS PAPER TRADING
#port = 7496 # TWS LIVE TRADING
client = 10

ib = IB()
opt = Optopus(IBBrokerAdapter(ib, host, port, client))
opt.start()


print('\n\n\n[TACO]\n')
algo = Taco(opt)
algo.produce_signal()
#print(opt.account())
#print(pdo(opt.assets(['market_price', 'IV_h', 'IV_rank_h',
#                      'IV_percentile_h', 'volume_h', 'volume',
#                      'bid', 'ask', 'stdev', 'beta'])))

#print(pdo(opt.option_chain('EEM', ['option_price', 'delta', 'DTE'])))

#print(pdo(opt.asset_historic('EEM')))
#print(pdo(opt.asset_historic_IV('EEM')))
#print(opt.assets_matrix('bar_close'))
#print(to_df(opt.assets()))

#print(to_df(opt.asset_historical('SPY')))
#print(to_df(opt.asset_historical_IV('SPY')))
#print(to_df(opt.option_chain('SPY')))
#print(to_df(opt.account()))
#print(to_df(opt.portfolio()))
#print(opt.assets_matrix('bar_close'))
#print('POSITIONS\n', to_df(opt.positions()))


#ib.sleep(3)
#opt.update_positions()
#print(opt.positions())

#print('\nBeta weighted delta', opt.portfolio()['BWDelta'])

opt.stop()
