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
# port = 4002  # gateway
port = port = 7497  # TWS
client = 10

ib = IB()
opt = Optopus(IBBrokerAdapter(ib, host, port, client))
opt.start()


opt.stop()
