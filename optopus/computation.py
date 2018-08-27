# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from optopus.settings import MARKET_BENCHMARK

# https://conceptosclaros.com/que-es-la-covarianza-y-como-se-calcula-estadistica-descriptiva/
# http://gouthamanbalaraman.com/blog/calculating-stock-beta.html
# https://www.quora.com/What-is-the-difference-between-beta-and-correlation-coefficient
# https://www.investopedia.com/articles/investing/102115/what-beta-and-how-calculate-beta-excel.asp

def calc_beta(values: dict) -> dict:
    # calculate daily returns
    df = pd.DataFrame(data=values).pct_change().dropna()
    # SPY represents the market
    df.insert(0, 'benchmark', df[MARKET_BENCHMARK])
    np_array = df.values
    m = np_array[:, 0]  # market returns are column zero
    us = np_array[:, 1:]

    covariance = np.cov(m, us, rowvar=False)
    beta = covariance[0, :]/covariance[0, 0]

    names = df.columns.values
    d = {}
    for i in range(1, len(names)):
        d[names[i]] = beta[i]
    return d


def calc_correlation(values: dict) -> dict:
    # calculate daily returns
    df = pd.DataFrame(data=values).pct_change().dropna()
    s_corr = df.corr()[MARKET_BENCHMARK]
    d = {}
    for i, v in s_corr.iteritems():
        d[i] = v
    return d
