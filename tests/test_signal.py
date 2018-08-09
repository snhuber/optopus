import datetime
import pytest
from optopus.signal import ItemSignal, Signal
from optopus.security import SecurityType
from optopus.signal import RightType, ActionType
from optopus.money import Money
from optopus.settings import p_currency


def test_create_item_signal():
    isig = ItemSignal('SPX',
                      SecurityType.Option,
                      datetime.datetime.now().date(),
                      100,
                      RightType.Call,
                      ActionType.Buy,
                      8,
                      Money('1.5', p_currency))

    assert isig.symbol == 'SPX'


def test_create_item_signal_strike_not_positive_value():
    with pytest.raises(ValueError):
        ItemSignal('SPX',
                   SecurityType.Option,
                   datetime.datetime.now().date(),
                   -1,
                   RightType.Call,
                   ActionType.Buy,
                   8,
                   Money('1.5', p_currency))


def test_create_item_signal_quantity_not_positive_value():
    with pytest.raises(ValueError):
        ItemSignal('SPX',
                   SecurityType.Option,
                   datetime.datetime.now().date(),
                   100,
                   RightType.Call,
                   ActionType.Buy,
                   0,
                   Money('1.5', p_currency))


def test_create_item_signal_limit_not_positive_value():
    with pytest.raises(ValueError):
        ItemSignal('SPX',
                   SecurityType.Option,
                   datetime.datetime.now().date(),
                   100,
                   RightType.Call,
                   ActionType.Buy,
                   1,
                   Money('-4.0', p_currency))


def test_create_signal():
    i = [ItemSignal('SPX',
                    SecurityType.Option,
                    datetime.datetime.now().date(),
                    100,
                    RightType.Call,
                    ActionType.Buy,
                    8,
                    Money('1.5', p_currency))]
    s = Signal(i)
    assert len(s.items) == 1


def test_create_signal_empty_items_signal_list():
    i = []
    with pytest.raises(ValueError):
        Signal(i)
