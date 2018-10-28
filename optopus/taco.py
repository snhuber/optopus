# -*- coding: utf-8 -*-
import datetime
from typing import List
from optopus.asset import Asset
from optopus.data_objects import OwnershipType
from optopus.option import RightType
from optopus.strategy import Strategy, StrategyType, Leg

from optopus.strategies import ShortPutVerticalSpread
from optopus.optopus import Optopus
from optopus.utils import to_df



class Taco():
    def __init__(self, opt: Optopus):
        self._opt = opt
        self._maximum_spread_risk = 5
        self._minimum_ROI = 0.25
        self._minimum_iv = 0.4
        self._minimum_iv_percentile = 0.75
        self._minimum_underlying_volume = 1000
        self._minimum_option_volume = 1 # 1000
        self._maximum_price_spread = 0.2
        self._minimum_reward = 0.5
        self._minimum_ROI = 0.30

    def execute(self):
        assets = self._opt.assets
        strategies = self._opt.strategies
        expiration = self._opt.expiration_target()
        maximum_risk = self._opt.maximum_risk_per_trade()
        
        df = to_df(self._opt.assets.values())
        # Implied volatily filter
        df = df[(df['iv'] > self._minimum_iv) & (df['iv_percentile'] > self._minimum_iv_percentile)]
        # Underlying volume filter
        df = df[df['volume'] > self._minimum_underlying_volume]
        
        print(df['code'])
        assets_with_positions = {s.code for s in strategies.values()}
        
        for _, row in df.iterrows():
            asset = assets[row['code']]
            if asset.code not in assets_with_positions:
                self._bull_put_spread(asset, expiration, maximum_risk)

    def _bull_put_spread(self, asset: Asset, expiration: datetime.date, maximum_risk: float):
        
        """
        chain = self._opt.option_chain(asset.code, expiration)
        OTM = [o for o in chain if o.strike < asset.market_price and o.right == RightType.Put]
        print([(o.strike, o.expiration, o.right) for o in OTM])
        
        sell_put = OTM[-1]
        maximum_width = int(maximum_risk / sell_put.multiplier)
         
        buy_put = OTM[0]
        for o in OTM[0:-2]:
            width = sell_put.strike - o.strike
            credit= sell_put.midpoint - o.midpoint
            if width <= maximum_width and width/credit > self._minimum_ROI:
                buy_put = o
                break
        
        print('SELL PUT', sell_put.contract)
        print('BUY PUT', buy_put.contract)

        strategy = ShortPutVerticalSpread(asset.code,
                                          StrategyType.ShortPutVerticalSpread,
                                          OwnershipType.Buyer,
                                          asset.currency,
                                          self._take_profit_factor,
                                          asset.market_price,
                                          sell_put.multiplier,
                                          sell_put,
                                          buy_put)
        
        self._opt.new_strategy(strategy)

        """
        options = self._opt.option_chain(asset.code, expiration)
        df = to_df(options.values())
        df['spread'] = df['ask'] - df['bid']
        # OTM puts filter
        df = df[(df['right'] == RightType.Put.value) & (df['strike'] <= asset.market_price)]
        # nearest ATM option
        sell_strike = df.iloc[-1, df.columns.get_loc('strike')]
        sell_midpoint = df.iloc[-1, df.columns.get_loc('midpoint')]        
        df['risk'] = sell_strike - df['strike']
        df['reward'] = sell_midpoint - df['midpoint']
        df['ROI'] = df['reward'] / df['risk']
        
        # Liquidity filter
        df = df[(df['spread'] <= self._maximum_price_spread) & (df['volume'] > self._minimum_option_volume)]
        
        print(df[['code', 'strike', 'right', 'spread', 'volume', 'risk', 'reward', 'ROI']])
        
        if (sell_strike in df['strike'].values):
            # Long put filter
            df = df[(df['reward'] > self._minimum_reward) & (df['ROI'] > self._minimum_ROI)]
            buy_strike = df.loc[df['ROI'].idxmax()]['strike']
            
            sell_option = options[f'{sell_strike}{RightType.Put.value}']
            buy_option = options[f'{buy_strike}{RightType.Put.value}']
            
            print(sell_option)
            print(buy_option)
            
            strategy = ShortPutVerticalSpread(asset, sell_option, buy_option, OwnershipType.Buyer)        
            self._opt.new_strategy(strategy)
        
        
        
        

