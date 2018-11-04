# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from optopus.settings import (MARKET_BENCHMARK, STDEV_PERIOD, BETA_PERIOD,
                              CORRELATION_PERIOD, HISTORICAL_YEARS,
                              PRICE_PERIOD, IV_PERIOD, RSI_WINDOW, SMA1_WINDOW, SMA2_WINDOW)
from optopus.asset import Asset
from optopus.common import Direction
from optopus.data_objects import (OwnershipType, 
                                  Position)
from optopus.strategy import Strategy
                            

# https://conceptosclaros.com/que-es-la-covarianza-y-como-se-calcula-estadistica-descriptiva/
# http://gouthamanbalaraman.com/blog/calculating-stock-beta.html
# https://www.quora.com/What-is-the-difference-between-beta-and-correlation-coefficient
# https://www.investopedia.com/articles/investing/102115/what-beta-and-how-calculate-beta-excel.asp


def calc_beta(values: Dict[str, Tuple]) -> Dict[str, float]:
    # calculate daily returns
    df = pd.DataFrame(data=values).pct_change().dropna()
    # SPY represents the market
    df.insert(0, 'benchmark', df[MARKET_BENCHMARK])
    np_array = df.values[0:BETA_PERIOD, :]

    covariance = np.cov(np_array, rowvar=False)
    beta = covariance[0, :]/covariance[0, 0]

    d = {}
    for i, col in enumerate(df.columns.values.tolist()):
        d[col] = beta[i]
    return d


def calc_correlation(values: Dict[str, Tuple]) -> Dict[str, float]:
    # calculate daily returns
    df = pd.DataFrame(data=values).pct_change().dropna()
    df.insert(0, 'benchmark', df[MARKET_BENCHMARK])
    np_array = df.values[0:CORRELATION_PERIOD, :]
    correlation = np.corrcoef(np_array, rowvar=False)

    d = {}
    for i, col in enumerate(df.columns.values.tolist()):
        d[col] = correlation[0, i]
    return d


def calc_stdev(values: Dict[str, Tuple]) -> Dict[str, float]:
    df = pd.DataFrame(data=values).pct_change().dropna()
    np_array = df.values[0:STDEV_PERIOD, :]
    stdev = np.std(np_array, axis=0)

    d = {}
    for i, col in enumerate(df.columns.values.tolist()):
        d[col] = stdev[i]
    return d

def calc_rsi(values: Dict[str, Tuple], window_length:int = 14) -> Dict[str, Tuple]:
    df = pd.DataFrame(data=values).diff()
    # delta=delta.dropna()
    up, down = df.copy(), df.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    
    roll_up = up.rolling(window=window_length).mean()
    roll_down = down.rolling(window=window_length).mean().abs()

    rs = roll_up / roll_down
    rsi = 100.0 - (100.0 / (1.0 + rs))

    d = {}
    for i, col in enumerate(df.columns.values.tolist()):
        d[col] = tuple(rsi[col].values)
    return d

def calc_sma(values: Dict[str, Tuple], window_length: int) -> Dict[str, Tuple]:
    df = pd.DataFrame(data=values).rolling(window_length).mean()
    d = {}
    for i, col in enumerate(df.columns.values.tolist()):
        d[col] = tuple(df[col].values)
    return d


def _iv_rank(asset: Asset, iv_value: float) -> float:
    min_iv_values = [b.low for b in asset.iv_history.values]
    max_iv_values = [b.high for b in asset.iv_history.values]
    iv_min = min(min_iv_values)
    iv_max = max(max_iv_values)
    iv_rank = (iv_value - iv_min) / (iv_max - iv_min)
    return iv_rank

def _iv_percentile(asset: Asset, iv_value: float) -> float:
    iv_values = [b.low for b in asset.iv_history.values if b.low < iv_value]
    return len(iv_values) / (HISTORICAL_YEARS * 252)


def _price_percentile(asset: Asset, value: float) -> float:
    values = [b.low for b in asset.price_history.values if b.low < value]
    return len(values) / (HISTORICAL_YEARS * 252)


def assets_loop_computation(assets: Dict[str, Asset]) -> Dict[str, Dict]:
    measures = {}
    for a in assets.values():
        values={}
        #a.measures.volume = a.price_history.values[-1].volume
        #a.measures.price_pct = (a.price_history.values[-1].close - a.price_history.values[-1 * PRICE_PERIOD].close) / a.price_history.values[-1 * PRICE_PERIOD].close
        #a.measures.price_percentile = _price_percentile(a, a.current.market_price)
        #a.measures.iv_pct = (a.iv_history.values[-1].close - a.iv_history.values[-1 * IV_PERIOD].close) / a.iv_history.values[-1 * IV_PERIOD].close
        #a.measures.iv = a.iv_history.values[-1].close
        #a.measures.iv_rank = _iv_rank(a, a.measures.iv)
        #a.measures.iv_percentile = _iv_percentile(a, a.measures.iv)

        values['volume'] = a.price_history.values[-1].volume
        values['price_pct'] = (a.price_history.values[-1].close - a.price_history.values[-1 * PRICE_PERIOD].close) / a.price_history.values[-1 * PRICE_PERIOD].close
        values['price_percentile'] = _price_percentile(a, a.current.market_price)
        values['iv_pct'] = (a.iv_history.values[-1].close - a.iv_history.values[-1 * IV_PERIOD].close) / a.iv_history.values[-1 * IV_PERIOD].close
        values['iv'] = a.iv_history.values[-1].close
        values['iv_rank'] = _iv_rank(a, values['iv'])
        values['iv_percentile'] = _iv_percentile(a, values['iv'])
        measures[a.id.code] = values
    return measures


def assets_vector_computation(assets: Dict[str, Asset], close_values: Dict[str, List]) -> Dict[str, Dict]:
    measures = {}
    beta = calc_beta(close_values)
    correlation = calc_correlation(close_values)
    stdev = calc_stdev(close_values)
    rsi = calc_rsi(close_values, RSI_WINDOW)
    rsi_sma = calc_sma(rsi, 9)
    sma1 = calc_sma(close_values, SMA1_WINDOW)
    sma2 = calc_sma(close_values, SMA2_WINDOW)


    for code in close_values.keys():
        values = {}
        values['beta'] = beta[code]
        values['correlation'] = correlation[code]
        values['stdev'] = stdev[code]
        values['rsi'] = rsi[code]
        values['rsi_sma'] = rsi_sma[code]
        values['sma1'] = sma1[code]
        values['sma2'] = sma2[code]
        measures[code] = values         
    return measures

def assets_directional_assumption(assets: Dict[str, Asset], close_values: Dict[str, List]) -> Dict[str, Dict]:
    measures = {}
    df = pd.DataFrame(data=close_values)
    diff = (df.iloc[-1] - df.iloc[-1 * PRICE_PERIOD]) / df.iloc[-1 * PRICE_PERIOD]
    for code, price_pct in diff.iteritems():
        values={}
        if price_pct > 0.02:
                values['directional_assumption'] = Direction.Bullish
        elif price_pct < -0.2:
            values['directional_assumption'] = Direction.Bearish
        else:
            values['directional_assumption'] = Direction.Neutral
        measures[code] = values
    return measures 

def assets_directional_assumption_old(assets: Dict[str, Asset], close_values: Dict[str, List]) -> None:
    measures = {}
    df = pd.DataFrame(data=close_values)
    diff = (df.iloc[-1] - df.iloc[-1 * PRICE_PERIOD]) / df.iloc[-1 * PRICE_PERIOD]
    for code, price_period in diff.iteritems():
        values = {}        
        if assets[code].measures.price_percentile < 0.1:            
            if price_period > 0.01:
                values['directional_assumption'] = Direction.Bullish
            elif price_period < -0.5:
                values['directional_assumption'] = Direction.Bearish
            else:
                values['directional_assumption'] = Direction.Neutral
                
        elif assets[code].measures.price_percentile > 0.9:            
            if price_period < 0.01:
                values['directional_assumption'] = Direction.Bearish
            elif price_period > 0.5:
                values['directional_assumption'] = Direction.Bulish
            else:
                values['directional_assumption'] = Direction.Neutral

        else:
            if price_period > 0.5:
                values['directional_assumption'] = Direction.Bullish
            elif price_period < 0.5:
                values['directional_assumption'] = Direction.Bearish
            else:
                values['directional_assumption'] = Direction.Neutral
        
        measures[code] = values
        return measures

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
