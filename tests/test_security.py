# -*- coding: utf-8 -*-
from optopus.security import Security, SecurityType


def test_create_a_security():
    sec = Security('SPX', 'S&P 500', SecurityType.Index)
    assert sec.symbol == 'SPX'
    assert sec.name == 'S&P 500'
    assert sec.security_type == SecurityType.Index
