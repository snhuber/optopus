from dataclasses import FrozenInstanceError
import datetime
import pytest
from optopus.asset import AssetId, AssetType
from optopus.common import Currency, OwnershipType
from optopus.option import OptionId, Option, RightType
from optopus.strategy import StrategyType, Leg, Strategy, DefinedStrategy


@pytest.fixture
def option():
    id = AssetId("SPY", AssetType.Stock, Currency.USDollar, None)
    opt_id = OptionId(
        underlying_id=id,
        asset_type=AssetType.Option,
        expiration=datetime.date(2018, 9, 21),
        strike=100,
        right=RightType.Call,
        multiplier=100,
        contract=None,
    )
    time = datetime.datetime.now()
    opt = Option(
        id=opt_id,
        high=10.0,
        low=5.0,
        close=8.0,
        bid=6.0,
        bid_size=100,
        ask=7.0,
        ask_size=130,
        last=7.5,
        last_size=67.0,
        option_price=2.1,
        volume=1000,
        delta=0.98,
        gamma=0.12,
        theta=0.34,
        vega=0.78,
        iv=0.8,
        underlying_price=102.0,
        underlying_dividends=2.1,
        time=time,
    )
    return opt


@pytest.fixture
def leg(option):
    leg = Leg(option=option, ownership=OwnershipType.Buyer, ratio=1)
    return leg


@pytest.fixture
def strategy(leg):
    legs = (leg,)
    strategy = Strategy(
        legs=legs,
        strategy_type=StrategyType.ShortPutVerticalSpread,
        ownership=OwnershipType.Buyer,
        take_profit_factor=0.5,
    )
    return strategy


def test_Leg_init(option):
    leg = Leg(option=option, ownership=OwnershipType.Buyer, ratio=1)
    assert leg.option.id.underlying_id.code == "SPY"
    assert leg.ownership == OwnershipType.Buyer
    assert leg.ratio == 1


def test_Leg_immutable(option):
    leg = Leg(option=option, ownership=OwnershipType.Buyer, ratio=1)
    with pytest.raises(FrozenInstanceError):
        leg.ratio = 2


def test_Leg_price(option):
    leg = Leg(option=option, ownership=OwnershipType.Buyer, ratio=1)
    assert leg.price == 6.5


def test_Strategy_init(leg):
    legs = (leg,)
    strategy = Strategy(
        legs=legs,
        strategy_type=StrategyType.ShortPutVerticalSpread,
        ownership=OwnershipType.Buyer,
        take_profit_factor=0.5,
    )
    assert strategy.legs[0].option.id.underlying_id.code == "SPY"
    assert strategy.strategy_type == StrategyType.ShortPutVerticalSpread
    assert strategy.ownership == OwnershipType.Buyer
    assert strategy.take_profit_factor == 0.5


def test_Strategy_immutable(leg):
    legs = (leg,)
    strategy = Strategy(
        legs=legs,
        strategy_type=StrategyType.ShortPutVerticalSpread,
        ownership=OwnershipType.Buyer,
        take_profit_factor=0.5,
    )
    with pytest.raises(FrozenInstanceError):
        strategy.take_profit_factor = 0.3


def test_DefinedStrategy_init(strategy):
    dstrategy = DefinedStrategy(strategy=strategy, quantity=2)
    assert dstrategy.quantity == 2


def test_DefinedStrategy_quantity_greater_0(strategy):
    with pytest.raises(ValueError):
        DefinedStrategy(strategy=strategy, quantity=0)


def test_DefinedStrategy_opened_after_created(strategy):
    dstrategy = DefinedStrategy(strategy=strategy)
    time = dstrategy.created
    with pytest.raises(ValueError):
        dstrategy.opened = time


def test_DefinedStrategy_closed_and_opened_is_none(strategy):
    dstrategy = DefinedStrategy(strategy=strategy)
    time = dstrategy.opened
    with pytest.raises(ValueError):
        dstrategy.closed = time

def test_DefinedStrategy_opened_after_closed(strategy):
    dstrategy = DefinedStrategy(strategy=strategy)
    dstrategy.opened = datetime.datetime.now()
    time = dstrategy.opened
    with pytest.raises(ValueError):
        dstrategy.closed = time