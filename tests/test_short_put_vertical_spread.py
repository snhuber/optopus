from dataclasses import FrozenInstanceError
import datetime
import pytest
from optopus.asset import AssetId, AssetType
from optopus.common import Currency, OwnershipType
from optopus.option import OptionId, Option, RightType
from optopus.strategy import StrategyType, Leg, Strategy, DefinedStrategy
from optopus.short_put_vertical_spread import ShortPutVerticalSpread


@pytest.fixture
def sell_put_option():
    id = AssetId("SPY", AssetType.Stock, Currency.USDollar, None)
    opt_id = OptionId(
        underlying_id=id,
        asset_type=AssetType.Option,
        expiration=datetime.date(2018, 9, 21),
        strike=100,
        right=RightType.Put,
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
def buy_put_option():
    id = AssetId("SPY", AssetType.Stock, Currency.USDollar, None)
    opt_id = OptionId(
        underlying_id=id,
        asset_type=AssetType.Option,
        expiration=datetime.date(2018, 9, 21),
        strike=95,
        right=RightType.Put,
        multiplier=100,
        contract=None,
    )
    time = datetime.datetime.now()
    opt = Option(
        id=opt_id,
        high=10.0,
        low=5.0,
        close=8.0,
        bid=5.0,
        bid_size=100,
        ask=6.0,
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
def call_option():
    id = AssetId("SPY", AssetType.Stock, Currency.USDollar, None)
    opt_id = OptionId(
        underlying_id=id,
        asset_type=AssetType.Option,
        expiration=datetime.date(2018, 9, 21),
        strike=95,
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
        bid=5.0,
        bid_size=100,
        ask=6.0,
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
def spvs(buy_put_option, sell_put_option):
    return ShortPutVerticalSpread(buy_put_option, sell_put_option)


def test_ShortPutVerticalSpread_init(buy_put_option, sell_put_option):
    spvs = ShortPutVerticalSpread(buy_put_option, sell_put_option)
    assert spvs.strategy.legs[0].option.id.right == RightType.Put


def test_ShortPutVerticalSpread_wrong_puts_strikes(buy_put_option, sell_put_option):
    with pytest.raises(ValueError):
        ShortPutVerticalSpread(sell_put_option, buy_put_option)


def test_ShortPutVerticalSpread_wrong_puts_right(call_option, sell_put_option):
    with pytest.raises(ValueError):
        ShortPutVerticalSpread(call_option, buy_put_option)


def test_ShortPutVerticalSpread_entry_price(spvs):
    assert spvs.entry_price == -1.0


def test_ShortPutVerticalSpread_profit_price(spvs):
    assert spvs.profit_price == -0.5


def test_ShortPutVerticalSpread_breakeven_price(spvs):
    assert spvs.breakeven_price == 99.0


def test_ShortPutVerticalSpread_maximum_profit(spvs):
    assert spvs.maximum_profit == -100.0


def test_ShortPutVerticalSpread_maximum_losss(spvs):
    assert spvs.maximum_loss == 400.0


def test_ShortPutVerticalSpread_ROI(spvs):
    assert spvs.ROI == 0.25

def test_ShortPutVerticalSpread_str(spvs):
    s="SPVS\nentry price -1.0\nmax_profit -100.0\nmax_loss 400.0\nROI 0.25\n"
    assert str(spvs) == s