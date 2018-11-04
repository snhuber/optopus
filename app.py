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
#import logging
host = '127.0.0.1'
#port = 4002  # gateway
port = 7497  # TWS PAPER TRADING
#port = 7496 # TWS LIVE TRADING
client = 11

ib = IB()
opt = Optopus(IBBrokerAdapter(ib, host, port, client))

#notify('strategy_opened', 'FXI', 'cara', 'cola')

#algo = Taco(opt)
algo = Taco(opt)
opt.register_algorithm(algo.execute)

#logging.getLogger('ib_insync.wrapper').disabled = True

opt.start()

#df = to_df(opt.assets().values())
#print(df)
opt.loop()

opt.stop()
