# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np
from optopus.settings import (MARKET_BENCHMARK, STDEV_WINDOW, BETA_WINDOW,
                              CORRELATION_WINDOW, HISTORICAL_YEARS,
                              PRICE_WINDOW, IV_WINDOW, RSI_WINDOW,
                              FAST_SMA_WINDOW, SLOW_SMA_WINDOW, VERY_SLOW_SMA_WINDOW)
from optopus.asset import Asset, AssetType
from optopus.common import Direction
from optopus.data_objects import (OwnershipType, 
                                  Position)
from optopus.strategy import Strategy
                            

# https://conceptosclaros.com/que-es-la-covarianza-y-como-se-calcula-estadistica-descriptiva/
# http://gouthamanbalaraman.com/blog/calculating-stock-beta.html
# https://www.quora.com/What-is-the-difference-between-beta-and-correlation-coefficient
# https://www.investopedia.com/articles/investing/102115/what-beta-and-how-calculate-beta-excel.asp

def assets_matrix(assets: Asset, field: str) -> dict:
        """Returns a attribute from historical for every asset
        """
        d = {}
        for a in assets.values():
            d[a.id.code] = [getattr(bar, field) for bar in a.price_history.values]
        return d


def calc_beta(values: Dict[str, Tuple]) -> Dict[str, float]:
    # calculate daily returns
    df = pd.DataFrame(data=values).pct_change().dropna()
    # SPY represents the market
    df.insert(0, 'benchmark', df[MARKET_BENCHMARK])
    np_array = df.values[0:BETA_WINDOW, :]

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
    np_array = df.values[0:CORRELATION_WINDOW, :]
    correlation = np.corrcoef(np_array, rowvar=False)

    d = {}
    for i, col in enumerate(df.columns.values.tolist()):
        d[col] = correlation[0, i]
    return d


def calc_stdev(values: Dict[str, Tuple]) -> Dict[str, float]:
    df = pd.DataFrame(data=values).pct_change().dropna()
    np_array = df.values[0:STDEV_WINDOW, :]
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
    for _, col in enumerate(df.columns.values.tolist()):
        d[col] = tuple(df[col].values)
    return d

def calc_pct_change(values: Dict[str, Tuple], window_length: int) -> Dict[str, Tuple]:
    df = pd.DataFrame(data=values).rolling(window_length).mean()
    df = df.pct_change(window_length)
    d = {}
    for _, col in enumerate(df.columns.values.tolist()):
        d[col] = tuple(df[col].values)
    return d

def calc_diff(values: Dict[str, Tuple], window_length: int) -> Dict[str, Tuple]:
    df = pd.DataFrame(data=values).rolling(window_length).mean()
    df = df.diff(window_length)
    d = {}
    for _, col in enumerate(df.columns.values.tolist()):
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


def assets_loop_computation(assets: Dict[str, Asset], measures: Dict[str, Any]) -> Dict[str, Dict]:
    computable_assets = {
            a.id.code: a
            for a in assets.values()
            if a.id.asset_type == AssetType.Stock or a.id.asset_type == AssetType.ETF
        }
    
    for a in computable_assets.values():
        measures[a.id.code]['volume'] = a.price_history.values[-1].volume
        # TODO: get price_pct from vector calculation
        #measures[a.id.code]['price_pct'] = (a.price_history.values[-1].close - a.price_history.values[-1 * PRICE_PERIOD].close) / a.price_history.values[-1 * PRICE_PERIOD].close
        measures[a.id.code]['price_percentile'] = _price_percentile(a, a.current.market_price)
        # TODO: get iv_pct from vector calculation
        measures[a.id.code]['iv_pct'] = (a.iv_history.values[-1].close - a.iv_history.values[-1 * IV_WINDOW].close) / a.iv_history.values[-1 * IV_WINDOW].close
        measures[a.id.code]['iv'] = a.iv_history.values[-1].close
        measures[a.id.code]['iv_rank'] = _iv_rank(a, measures[a.id.code]['iv'])
        measures[a.id.code]['iv_percentile'] = _iv_percentile(a, measures[a.id.code]['iv'])
    return measures


def assets_vector_computation(assets: Dict[str, Asset], measures: Dict[str, Any]) -> Dict[str, Dict]:
    computable_assets = assets
    close_values = assets_matrix(computable_assets, "close")
    fast_sma = calc_sma(close_values, FAST_SMA_WINDOW)
    slow_sma = calc_sma(close_values, SLOW_SMA_WINDOW)
    very_slow_sma = calc_sma(close_values, VERY_SLOW_SMA_WINDOW)
    price_pct = calc_pct_change(close_values, 1)
    fast_sma_speed = calc_pct_change(fast_sma, FAST_SMA_WINDOW)
    fast_sma_speed_diff = calc_diff(fast_sma_speed, 1)


    for code in close_values.keys():
        measures[code]['fast_sma'] = fast_sma[code]
        measures[code]['slow_sma'] = slow_sma[code]
        measures[code]['very_slow_sma'] = very_slow_sma[code]
        measures[code]['price_pct'] = price_pct[code][-1]
        measures[code]['fast_sma_speed'] = fast_sma_speed[code]
        measures[code]['fast_sma_speed_diff'] = fast_sma_speed_diff[code]

    computable_assets = {
            a.id.code: a
            for a in assets.values()
            if a.id.asset_type == AssetType.Stock or a.id.asset_type == AssetType.ETF
        }

    close_values = assets_matrix(computable_assets, "close")
    beta = calc_beta(close_values)
    correlation = calc_correlation(close_values)
    stdev = calc_stdev(close_values)
    rsi = calc_rsi(close_values, RSI_WINDOW)

    for code in close_values.keys():
        measures[code]['beta'] = beta[code]
        measures[code]['correlation'] = correlation[code]
        measures[code]['stdev'] = stdev[code]
        measures[code]['rsi'] = rsi[code]

    return measures



def assets_directional_assumption(assets: Dict[str, Asset]) -> Dict[str, Dict]:

    computable_assets = {
            a.id.code: a
            for a in assets.values()
            if a.id.asset_type == AssetType.Stock or a.id.asset_type == AssetType.ETF
        }

    asset_directions = {}
    for a in computable_assets.values():
        fast_sma = a.measures.fast_sma
        slow_sma = a.measures.slow_sma
        directions = []
        for i in (range(len(fast_sma))):
            if np.isnan(fast_sma[i]) or np.isnan(slow_sma[i]):
                directions.append(np.nan)
            elif fast_sma[i] > slow_sma[i]:
                directions.append(Direction.Bullish.value)
            else:
                directions.append(Direction.Bearish.value)
        asset_directions[a.id.code] = tuple(directions)

    return asset_directions


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