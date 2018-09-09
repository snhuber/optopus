from collections import OrderedDict
from typing import List
from optopus.data_objects import StrategyType, PositionData


class Strategy():
    def __init__(self, strategy_type: StrategyType, strategy_id: str):
        self.strategy_type = strategy_type
        self.strategy_id = strategy_id
        self.positions = []
        self.n_position = None
        self.max_profit = None
        self.max_loss = None
        self.breakeven = None
        self.pop = None # Probability of profit / success

    def add_position(self, position: PositionData):
        self.positions.append(position)
    def to_dict(self):
        d = OrderedDict()
        for attr, value in vars(self).items():
            try: 
                iter(value)
            except TypeError:
                d[attr] = value
        return d



class SellNakedPut():
    def __init__(self, strategy_id: str):
        super.__init__(StrategyType.SellNakedPut, strategy_id)
        self.n_positions = 1

    def update(self):
        position = self.positios[0]
        self.max_profit = position.trade_price * 100
        self.breakeven = position.strike - position.trade_price
        self.max_loss = self.breakeven * 100
        self.pop = 1 + position.delta  # 1 - (-1*delta)


class StrategyFactory():
    @staticmethod
    def create_strategy(self,
                        strategy_type: StrategyType,
                        strategy_id: str) -> Strategy:
        if strategy_type == StrategyType.SellNakedPut:
            return (SellNakedPut(strategy_id))
        else:
            print('unknow strategy type')


