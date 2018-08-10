#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  5 07:34:45 2018

@author: ilia
"""
import datetime
from ib_insync.ib import IB
from ib_adapter import IBBrokerAdapter
from optopus import Optopus


host = '127.0.0.1'
port = 4002  # paper trading
# port = 4001
client = 9

ib = IB()
ib.connect(host, port, client)

ib_adapter = IBBrokerAdapter(ib)

opt = Optopus(ib_adapter)
opt.start()

for t in ib.timeRange(datetime.time(0, 0), datetime.datetime(2100, 1, 1, 0), 10):
    print(t)
    opt.beat()

ib.disconnect()
