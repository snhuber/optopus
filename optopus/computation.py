# -*- coding: utf-8 -*-
from typing import Dict, List
import pandas as pd
import numpy as np
from optopus.settings import (MARKET_BENCHMARK, STDEV_PERIOD, BETA_PERIOD, 
                              CORRELATION_PERIOD, HISTORICAL_YEARS)
from optopus.data_objects import Asset, AssetData

# https://conceptosclaros.com/que-es-la-covarianza-y-como-se-calcula-estadistica-descriptiva/
# http://gouthamanbalaraman.com/blog/calculating-stock-beta.html
# https://www.quora.com/What-is-the-difference-between-beta-and-correlation-coefficient
# https://www.investopedia.com/articles/investing/102115/what-beta-and-how-calculate-beta-excel.asp


def calc_beta(values: dict) -> dict:
    # calculate daily returns
    df = pd.DataFrame(data=values).pct_change().dropna()
    # SPY represents the market
    df.insert(0, 'benchmark', df[MARKET_BENCHMARK])
    np_array = df.values[0:BETA_PERIOD, :]

    covariance = np.cov(np_array, rowvar=False)
    beta = covariance[0, :]/covariance[0, 0]

    names = df.columns.values
    d = {}
    for i in range(1, len(names)):
        d[names[i]] = beta[i]
    return d


def calc_correlation(values: dict) -> dict:
    # calculate daily returns
    df = pd.DataFrame(data=values).pct_change().dropna()
    df.insert(0, 'benchmark', df[MARKET_BENCHMARK])
    np_array = df.values[0:CORRELATION_PERIOD, :]
    correlation = np.corrcoef(np_array, rowvar=False)
    names = df.columns.values
    d = {}
    for i in range(1, len(names)):
        d[names[i]] = correlation[0, i]
    return d


def calc_stdev(values: dict) -> dict:
    df = pd.DataFrame(data=values).pct_change().dropna()
    np_array = df.values[0:STDEV_PERIOD, :]
    stdev = np.std(np_array, axis=0)
    names = df.columns.values
    d = {}
    for i in range(1, len(names)):
        d[names[i]] = stdev[i]
    return d

def _IV_rank(ad: AssetData, IV_value: float) -> float:
    min_IV_values = [b.bar_low for b in ad.historical_IV]
    max_IV_values = [b.bar_high for b in ad.historical_IV]
    IV_min = min(min_IV_values)
    IV_max = max(max_IV_values)
    IV_rank = (IV_value - IV_min) / (IV_max - IV_min)
    return IV_rank

def _IV_percentile(ad: AssetData, IV_value: float) -> float:
    IV_values = [b.bar_low for b in ad.historical_IV if b.bar_low < IV_value]
    return len(IV_values) / (HISTORICAL_YEARS * 252)


def assets_loop_computation(ads: Dict[str, Asset]) -> None:
    for a in ads.values():
        a.current.volume_h = a._historical_data[-1].bar_volume
        a.current.IV_h = a._historical_IV_data[-1].bar_close
        a.current.IV_rank_h = _IV_rank(a, a.current.IV_h)
        a.current.IV_percentile_h = _IV_percentile(a, a.current.IV_h)
        a.current.one_month_return = (a._historical_data[-1].bar_close - a._historical_data[-22].bar_close) / a._historical_data[-22].bar_close

def assets_vector_computation(ads: Dict[str, Asset], close_values: Dict[str, List]) -> None:
    # Calculate beta
    beta = calc_beta(close_values)
    for code, value in beta.items():
        ads[code].current.beta = value
    # Calculate correlation
    correlation = calc_correlation(close_values)
    for code, value in correlation.items():
        ads[code].current.correlation = value
    # Calculate standard desviation
    correlation = calc_stdev(close_values)
    for code, value in correlation.items():
        ads[code].current.stdev = value




