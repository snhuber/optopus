#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  5 07:34:45 2018

@author: ilia
"""
from ib_adapter import IBAdapter
from optopus import Optopus


host = '127.0.0.1'
port = 4002  #paper trading
# port = 4001

client = 4

ib_adapter = IBAdapter(host, port, client)

opt = Optopus(ib_adapter)

opt.start()
opt.pause(1)
print('ID', opt._account.id)
print('FUNDS', opt._account.funds)
print('BUYING POWER', opt._account.buying_power)
print('CASH', opt._account.cash)
print('MAX_DAY_TRADES', opt._account.max_day_trades)
opt.stop()
