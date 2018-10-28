import datetime
from dataclasses import FrozenInstanceError
import pytest
from optopus.asset import AssetId, Asset, Current, Bar, History
from optopus.common import AssetType, Currency, Direction
from optopus.stock import Stock

# TODO: Check no valid value ranges


def test_Stock_entity_init():
    id = AssetId("SPY", AssetType.Stock, Currency.USDollar, None)
    stock = Stock(id)
    assert stock.id.code == "SPY"
    assert stock.id.asset_type == AssetType.Stock
    assert stock.id.currency == Currency.USDollar


def test_Stock_wrong_asset_type():
    id = AssetId("SPY", AssetType.Option, Currency.USDollar, None)
    with pytest.raises(ValueError):
        Stock(id)

