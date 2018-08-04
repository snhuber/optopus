#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  4 16:30:25 2018

@author: ilia
"""

from ib_insync import *

ib = IB()

host = '127.0.0.1'
port = 4002
client = 1

ib.connect(host, port, client)

