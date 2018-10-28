from dataclasses import FrozenInstanceError
import datetime
import pytest
from optopus.asset import AssetId, Asset, Current, Bar, History, Measures
from optopus.common import AssetType, Currency, Direction


def test_Asset_value_objet_init():
    id = AssetId("SPY", AssetType.Stock, Currency.USDollar, None)
    assert id.code == "SPY"
    assert id.asset_type == AssetType.Stock
    assert id.currency == Currency.USDollar


def test_Asset_value_objet_init_immutable():
    id = AssetId("SPY", AssetType.Stock, Currency.USDollar, None)
    with pytest.raises(FrozenInstanceError):
        id.code = "XXX"


def test_Current_value_object_init():
    test_time = datetime.datetime.now()
    current = Current(
        high=100.0,
        low=50.0,
        close=75.0,
        bid=2.0,
        bid_size=10,
        ask=3.0,
        ask_size=20,
        last=2.5,
        last_size=5,
        volume=1000,
        time=test_time,
    )

    assert current.high == 100.0
    assert current.low == 50.0
    assert current.close == 75.0
    assert current.bid == 2.0
    assert current.bid_size == 10
    assert current.ask == 3.0
    assert current.ask_size == 20
    assert current.last == 2.5
    assert current.last_size == 5
    assert current.volume == 1000
    assert current.time == test_time


def test_Current_value_object_immutable():
    current = Current(
        high=100.0,
        low=50.0,
        close=75.0,
        bid=2.0,
        bid_size=10,
        ask=3.0,
        ask_size=20,
        last=2.5,
        last_size=5,
        volume=1000,
        time=datetime.datetime.now(),
    )
    with pytest.raises(FrozenInstanceError):
        current.high = 300.0


def test_Current_value_object_midprice():
    current = Current(
        high=100.0,
        low=50.0,
        close=75.0,
        bid=2.0,
        bid_size=10,
        ask=3.0,
        ask_size=20,
        last=2.5,
        last_size=5,
        volume=1000,
        time=datetime.datetime.now(),
    )
    assert current.midpoint == 2.5


def test_Current_value_object_market_price_bid_last_ask():
    current = Current(
        high=100.0,
        low=50.0,
        close=75.0,
        bid=2.0,
        bid_size=10,
        ask=3.0,
        ask_size=20,
        last=2.75,
        last_size=5,
        volume=1000,
        time=datetime.datetime.now(),
    )
    assert current.market_price == 2.75


def test_Current_value_object_market_price_bid_ask_last():
    current = Current(
        high=100.0,
        low=50.0,
        close=75.0,
        bid=2.0,
        bid_size=10,
        ask=3.0,
        ask_size=20,
        last=4.0,
        last_size=5,
        volume=1000,
        time=datetime.datetime.now(),
    )
    assert current.market_price == 2.5


def test_Current_value_object_market_price_1():
    current = Current(
        high=100.0,
        low=50.0,
        close=75.0,
        bid=-1,
        bid_size=10,
        ask=-1,
        ask_size=20,
        last=4.0,
        last_size=5,
        volume=1000,
        time=datetime.datetime.now(),
    )
    assert current.market_price == 75.0


def test_Bar_value_object_init():
    test_time = datetime.datetime.now()
    bar = Bar(
        count=44,
        open=50.0,
        high=70.0,
        low=40.0,
        close=60.0,
        average=45.5,
        volume=2000,
        time=test_time,
    )
    assert bar.count == 44
    assert bar.open == 50.0
    assert bar.high == 70.0
    assert bar.low == 40.0
    assert bar.close == 60.0
    assert bar.average == 45.5
    assert bar.volume == 2000
    assert bar.time == test_time


def test_Bar_value_object_immutable():
    bar = Bar(
        count=44,
        open=50.0,
        high=70.0,
        low=40.0,
        close=60.0,
        average=45.5,
        volume=2000,
        time=datetime.datetime.now(),
    )
    with pytest.raises(FrozenInstanceError):
        bar.count = 45


def test_History_value_object_init():
    bar = Bar(
        count=44,
        open=50.0,
        high=70.0,
        low=40.0,
        close=60.0,
        average=45.5,
        volume=2000,
        time=datetime.datetime.now(),
    )
    history = History((bar,))
    assert len(history.values) == 1


def test_History_value_object_immutable():
    bar = Bar(
        count=44,
        open=50.0,
        high=70.0,
        low=40.0,
        close=60.0,
        average=45.5,
        volume=2000,
        time=datetime.datetime.now(),
    )
    history = History((bar,))

    with pytest.raises(FrozenInstanceError):
        history.values = (bar, bar)


def test_Measures_value_object_init():
    m = Measures(
        iv=0.45,
        iv_rank=0.78,
        iv_percentile=0.91,
        iv_pct=0.03,
        stdev=0.04,
        beta=0.2,
        correlation=0.5,
        price_percentile=0.56,
        price_pct=0.02,
        directional_assumption=Direction.Bullish,
    )
    assert m.iv == 0.45
    assert m.iv_rank == 0.78
    assert m.iv_percentile == 0.91
    assert m.iv_pct == 0.03
    assert m.stdev == 0.04
    assert m.beta == 0.2
    assert m.correlation == 0.5
    assert m.price_percentile == 0.56
    assert m.price_pct == 0.02
    assert m.directional_assumption == Direction.Bullish


def test_Measures_value_object_immutable():
    m = Measures(
        iv=0.45,
        iv_rank=0.78,
        iv_percentile=0.91,
        iv_pct=0.03,
        stdev=0.04,
        beta=0.2,
        correlation=0.5,
        price_percentile=0.56,
        price_pct=0.02,
        directional_assumption=Direction.Bullish,
    )
    with pytest.raises(FrozenInstanceError):
        m.iv = 0.5


def test_Asset_entity_init():
    id = AssetId("SPY", AssetType.Stock, Currency.USDollar, None)
    asset = Asset(id)
    asset.current = Current(
        high=100.0,
        low=50.0,
        close=75.0,
        bid=2.0,
        bid_size=10,
        ask=3.0,
        ask_size=20,
        last=2.5,
        last_size=5,
        volume=1000,
        time=datetime.datetime.now(),
    )
    bar = Bar(
        count=44,
        open=50.0,
        high=70.0,
        low=40.0,
        close=60.0,
        average=45.5,
        volume=2000,
        time=datetime.datetime.now(),
    )
    m = Measures(
        iv=0.45,
        iv_rank=0.78,
        iv_percentile=0.91,
        iv_pct=0.03,
        stdev=0.04,
        beta=0.2,
        correlation=0.5,
        price_percentile=0.56,
        price_pct=0.02,
        directional_assumption=Direction.Bullish,
    )

    asset.price_history = History((bar,))
    asset.iv_history = History((bar, bar))
    asset.measures = m

    assert asset.id.code == "SPY"
    assert asset.id.asset_type == AssetType.Stock
    assert asset.id.currency == Currency.USDollar
    assert asset.current.high == 100.0
    assert len(asset.price_history.values) == 1
    assert len(asset.iv_history.values) == 2
    assert asset.measures.iv == 0.45


def test_Asset_not_change_asset_id():
    id = AssetId("SPY", AssetType.Stock, Currency.USDollar, None)
    asset = Asset(id)
    with pytest.raises(AttributeError):
        asset.id = id
