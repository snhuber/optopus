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
from optopus.utils import pdo, plot_option_positions
from optopus.data_manager import DataSource
from optopus.data_objects import Asset, AssetType, SignalData, OrderAction, StrategyType, OptionRight

host = '127.0.0.1'
# port = 4002  # gateway
port = 7497  # TWS PAPER TRADING
#port = 7496 # TWS LIVE TRADING
client = 10

ib = IB()
opt = Optopus(IBBrokerAdapter(ib, host, port, client))
opt.start()

#print(opt.account())
#print(pdo(opt.assets(['market_price', 'IV_h', 'IV_rank_h',
#                      'IV_percentile_h', 'volume_h', 'volume',
#                      'bid', 'ask', 'stdev', 'beta'])))

#print(pdo(opt.option_chain('EEM', ['option_price', 'delta', 'DTE'])))

#print(pdo(opt.asset_historic('EEM')))
#print(pdo(opt.asset_historic_IV('EEM')))
#print(opt.assets_matrix('bar_close'))
#print(opt.assets(['IV_h', 'IV_rank_h']))

symbol = 'SPY'
u = Asset(symbol, AssetType.Stock)
s = SignalData(asset=u, 
               action=OrderAction.Sell, 
               quantity=1, 
               price=1.06, 
               expiration=datetime.datetime.strptime('21092018', "%d%m%Y").date(),
               strike=283,
               right=OptionRight.Put,
               algorithm='foo',
               strategy=StrategyType.SellNakedPut,
               rol='no_rol')  

opt.process([s])

opt.stop()
