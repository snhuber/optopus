# -*- coding: utf-8 -*-
from typing import Dict, List
import pandas as pd
import numpy as np
from optopus.settings import (MARKET_BENCHMARK, STDEV_PERIOD, BETA_PERIOD,
                              CORRELATION_PERIOD, HISTORICAL_YEARS,
                              PRICE_PERIOD, IV_PERIOD)
from optopus.data_objects import (Asset, OwnershipType, 
                                  PositionData, Strategy, Direction)

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

def _IV_rank(asset: Asset, IV_value: float) -> float:
    min_IV_values = [b.bar_low for b in asset.historical_IV]
    max_IV_values = [b.bar_high for b in asset.historical_IV]
    IV_min = min(min_IV_values)
    IV_max = max(max_IV_values)
    IV_rank = (IV_value - IV_min) / (IV_max - IV_min)
    return IV_rank

def _IV_percentile(asset: Asset, IV_value: float) -> float:
    IV_values = [b.bar_low for b in asset.historical_IV if b.bar_low < IV_value]
    return len(IV_values) / (HISTORICAL_YEARS * 252)


def _price_percentile(asset: Asset, value: float) -> float:
    values = [b.bar_low for b in asset._historical_data if b.bar_low < value]
    return len(values) / (HISTORICAL_YEARS * 252)


def assets_loop_computation(assets: Dict[str, Asset]) -> None:
    for a in assets.values():
        a.volume = a._historical_data[-1].bar_volume
        a.IV_period = (a._historical_IV_data[-1].bar_close - a._historical_IV_data[-1 * IV_PERIOD].bar_close) / a._historical_IV_data[-1 * IV_PERIOD].bar_close
        a.IV = a._historical_IV_data[-1].bar_close
        a.IV_rank = _IV_rank(a, a.IV)
        a.IV_percentile = _IV_percentile(a, a.IV)
        a.price_percentile = _price_percentile(a, a.market_price)

def assets_vector_computation(assets: Dict[str, Asset], close_values: Dict[str, List]) -> None:
    # Calculate beta
    beta = calc_beta(close_values)
    for code, value in beta.items():
        assets[code].beta = value
    # Calculate correlation
    correlation = calc_correlation(close_values)
    for code, value in correlation.items():
        assets[code].correlation = value
    # Calculate standard desviation
    stdev = calc_stdev(close_values)
    for code, value in stdev.items():
        assets[code].stdev = value


def assets_directional_assumption(assets: Dict[str, Asset], close_values: Dict[str, List]) -> None:
    df = pd.DataFrame(data=close_values)
    diff = (df.iloc[-1] - df.iloc[-1 * PRICE_PERIOD]) / df.iloc[-1 * PRICE_PERIOD]
    for code, price_period in diff.iteritems():
        assets[code].price_period = price_period
        
        if assets[code].price_percentile < 0.1:            
            if price_period > 0.01:
                assets[code].directional_assumption = Direction.Bullish
            elif price_period < -0.5:
                assets[code].directional_assumption = Direction.Bearish
            else:
                assets[code].directional_assumption = Direction.Neutral
                
        elif assets[code].price_percentile > 0.9:            
            if price_period < 0.01:
                assets[code].directional_assumption = Direction.Bearish
            elif price_period > 0.5:
                assets[code].directional_assumption = Direction.Bulish
            else:
                assets[code].directional_assumption = Direction.Neutral

        else:
            if price_period > 0.5:
                assets[code].directional_assumption = Direction.Bullish
            elif price_period < 0.5:
                assets[code].directional_assumption = Direction.Bearish
            else:
                assets[code].directional_assumption = Direction.Neutral


def portfolio_bwd(strategies: Dict[str, Strategy], ads: Dict[str, Asset], benchmark_price: float) -> float:
    if not len(strategies):
        return None
    total = 0
    for strategy_key, strategy in strategies.items():
        for leg_key, leg in strategy.legs.items():
            underlying_price = leg.option.underlying_price
            ownership = 1 if leg.ownership == OwnershipType.Buyer else -1
            BWDelta = (underlying_price / benchmark_price) * ads[leg.option.code].beta * leg.option.delta * strategy.quantity * leg.ratio * ownership
            total += BWDelta
    return total
