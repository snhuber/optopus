# -*- coding: utf-8 -*-
import pytest
from optopus.account import Account, AccountItem


def test_assign_account_id():
    a = Account()
    i = AccountItem('ACCOUNT1', 'id', 'ACCOUNTID', None)

    a.update_item_value(i)

    assert a.id == 'ACCOUNTID'


def test_not_update_account_id_value():
    a = Account()
    i = AccountItem('ACCOUNT1', 'id', 'ACCOUNTID', None)

    a.update_item_value(i)

    i2 = AccountItem('ACCOUNT1', 'id', 'ACCOUNTID2', None)

    a.update_item_value(i2)

    assert a.id == 'ACCOUNTID'


def test_account_attribute_not_exists():
    a = Account()
    i = AccountItem('ACCOUNT1', 'unknown', 'VALUE', None)

    with pytest.raises(AttributeError):
        a.update_item_value(i)
