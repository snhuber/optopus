#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  5 07:34:45 2018

@author: ilia
"""
from ib_insync.ib import IB
from optopus.ib_adapter import IBBrokerAdapter
from optopus.optopus import Optopus
from optopus.utils import to_df, notify
from optopus.taco import Taco

host = '127.0.0.1'
# port = 4002  # gateway
port = 7497  # TWS PAPER TRADING
#port = 7496 # TWS LIVE TRADING
client = 10

ib = IB()
opt = Optopus(IBBrokerAdapter(ib, host, port, client))

notify('strategy_opened', 'FXI', 'cara', 'cola')

algo = Taco(opt)
opt.register_algorithm(algo.produce_signal)

opt.start()
#print(opt.strategies())
#print(opt.assets())
#df = to_df(opt.assets())
#print(df)


#opt.loop()



#print(to_df(opt.asset_historical('SPY')))
#print(to_df(opt.asset_historical_IV('SPY')))
#opt.update_option_chain('SPY')
#print(to_df(opt.option_chain('SPY')))
#print(to_df(opt.account()))
#print(to_df(opt.portfolio()))
#print(opt.assets_matrix('bar_close'))
#print('POSITIONS\n', to_df(opt.positions()))


#ib.sleep(3)
#opt.update_positions()
#print(opt.positions())

#print('\nBeta weighted delta', opt.portfolio()['BWDelta'])

#opt.pause(10)
opt.stop()
