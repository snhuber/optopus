# -*- coding: utf-8 -*-
import datetime
from optopus.asset import Asset
from optopus.common import Currency
from optopus.data_objects import OwnershipType
from optopus.option import Option, RightType
from optopus.strategy import Strategy, StrategyType, Leg, DefinedStrategy


class ShortPutVerticalSpread(DefinedStrategy):
    def __init__(self, buy_put: Option, sell_put: Option, profit_factor: float = 0.5):
        if (
            not (buy_put.id.right == RightType.Put
            and sell_put.id.right == RightType.Put)
        ):
            raise ValueError("Wrong options right")

        if buy_put.id.strike >= sell_put.id.strike:
            raise ValueError("Buy put's strike must be lower than shell put's strike")

        legs = (
            Leg(option=buy_put, ownership=OwnershipType.Buyer, ratio=1),
            Leg(option=sell_put, ownership=OwnershipType.Seller, ratio=1),
        )
        super().__init__(
            Strategy(
                legs=legs,
                strategy_type=StrategyType.ShortPutVerticalSpread,
                ownership=OwnershipType.Buyer,
            )
        )

        self._profit_factor = profit_factor
        # self.underlying_entry_price = asset.market_price
        # TODO: make properties

    @property
    def entry_price(self):
        return round(sum([l.ownership.value * l.price for l in self.strategy.legs]), 2)

    @property
    def profit_price(self):
        return round(self.entry_price * self._profit_factor, 2)

    @property
    def breakeven_price(self):
        return self.strategy.legs[1].strike + self.entry_price

    @property
    def maximum_profit(self):
        return self.entry_price * self.strategy.multiplier

    @property
    def maximum_loss(self):
        return (
            self.strategy.legs[1].strike
            - self.strategy.legs[0].strike
            + self.entry_price
        ) * self.strategy.multiplier

    @property
    def ROI(self):
        return abs(self.maximum_profit / self.maximum_loss)

    def __str__(self):
        return (
            f"{self.strategy.strategy_type.value}\n"
            f"entry price {self.entry_price}\n"
            f"max_profit {self.maximum_profit}\n"
            f"max_loss {self.maximum_loss}\n"
            f"ROI {self.ROI}\n"
        )

