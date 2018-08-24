# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np


# https://conceptosclaros.com/que-es-la-covarianza-y-como-se-calcula-estadistica-descriptiva/
# http://gouthamanbalaraman.com/blog/calculating-stock-beta.html
# https://www.quora.com/What-is-the-difference-between-beta-and-correlation-coefficient
def calc_beta(values: dict) -> dict:
    df = pd.DataFrame(data=values)
    # calculate daily returns
    df_r = df / df.shift(1) - 1
    df_r = df_r.dropna()

    # SPY represents the market
    df_r.insert(0, 'benchmark', df_r['SPY'])
    np_array = df_r.values
    m = np_array[:, 0]  # market returns are column zero
    us = np_array[:, 1:]

    covariance = np.cov(m, us, rowvar=False)
    beta = covariance[0, :]/covariance[0, 0]

    names = df_r.columns.values
    d = {}
    for i in range(1, len(names)):
        d[names[i]] = beta[i]
    return d
