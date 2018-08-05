#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  5 07:34:45 2018

@author: ilia
"""
from ibbroker import IBBroker
from optopus import Optopus



host = '127.0.0.1'
port = 4002
client = 2

broker = IBBroker(host, port, client)

opt = Optopus(broker)

opt.start()
opt.pause(2)
print(opt._account.id)
opt.stop()


