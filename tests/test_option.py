from dataclasses import FrozenInstanceError
import datetime
from optopus.asset import AssetId
from optopus.common import AssetType, Currency
from optopus.option import OptionId, Option, RightType
import pytest


def test_OptionId_init():
    id = AssetId("SPY", AssetType.Stock, Currency.USDollar, None)
    opt_id = OptionId(underlying_id=id,
                    asset_type=AssetType.Option, 
                    expiration=datetime.date(2018, 9, 21), 
                    strike=100,
                    right=RightType.Call,
                    multiplier=100,
                    contract=None)
    assert opt_id.underlying_id.code == "SPY"
    assert opt_id.asset_type == AssetType.Option
    assert opt_id.expiration == datetime.date(2018, 9, 21)
    assert opt_id.strike == 100
    assert opt_id.right == RightType.Call

def test_OptionId_immutable():
    id = AssetId("SPY", AssetType.Stock, Currency.USDollar, None)
    opt_id = OptionId(underlying_id=id,
                    asset_type=AssetType.Option, 
                    expiration=datetime.date(2018, 9, 21), 
                    strike=100,
                    right=RightType.Call,
                    multiplier=100,
                    contract=None)
    with pytest.raises(FrozenInstanceError):
        opt_id.underlying_id = id

def test_Option_init():
    id = AssetId("SPY", AssetType.Stock, Currency.USDollar, None)
    opt_id = OptionId(underlying_id=id,
                    asset_type=AssetType.Option, 
                    expiration=datetime.date(2018, 9, 21), 
                    strike=100,
                    right=RightType.Call,
                    multiplier=100,
                    contract=None,)
    time = datetime.datetime.now()
    opt = Option(id=opt_id,
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
                time=time)

    assert opt.id.underlying_id.code == 'SPY'
    assert opt.high ==10.0
    assert opt.low == 5.0
    assert opt.close == 8.0
    assert opt.bid == 6.0
    assert opt.bid_size == 100
    assert opt.ask == 7.0
    assert opt.ask_size == 130
    assert opt.last == 7.5
    assert opt.last_size == 67.0
    assert opt.option_price == 2.1
    assert opt.volume == 1000
    assert opt.delta == 0.98
    assert opt.gamma == 0.12
    assert opt.theta == 0.34
    assert opt.vega == 0.78
    assert opt.iv == 0.8
    assert opt.underlying_price == 102.0
    assert opt.underlying_dividends == 2.1
    assert opt.time == time


def test_Option_midpoint():
    id = AssetId("SPY", AssetType.Stock, Currency.USDollar, None)
    opt_id = OptionId(underlying_id=id,
                    asset_type=AssetType.Option, 
                    expiration=datetime.date(2018, 9, 21), 
                    strike=100,
                    right=RightType.Call,
                    multiplier=100,
                    contract=None,)
    time = datetime.datetime.now()
    opt = Option(id=opt_id,
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
                time=time)

    assert opt.midpoint == 6.5

def test_Option_DTE():
    id = AssetId("SPY", AssetType.Stock, Currency.USDollar, None)
    opt_id = OptionId(underlying_id=id,
                    asset_type=AssetType.Option, 
                    expiration=datetime.date.today() + datetime.timedelta(days=10), 
                    strike=100,
                    right=RightType.Call,
                    multiplier=100,
                    contract=None,)
    time = datetime.datetime.now()
    opt = Option(id=opt_id,
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
                time=time)
    assert opt.DTE == 10
