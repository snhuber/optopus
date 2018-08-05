# -*- coding: utf-8 -*-

from optopus.account import Account


def test_create_a_account():
    a = Account(id = 'IDACCOUNT')
    assert a.id == 'IDACCOUNT'