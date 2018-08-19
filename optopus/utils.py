# -*- coding: utf-8 -*-
import datetime

def pdo(records):
    import pandas as pd
    if len(records) == 1:
        o = pd.Series(records[0])
    else:
        o = pd.DataFrame(records)
        o.set_index(['code'], inplace=True)
        o.sort_index(inplace=True)
    return o


nan = float('nan')


def is_nan(x: float) -> bool:
    """
    Not a number test.
    """
    return x != x


def parse_ib_date(s: str) -> datetime.date:
    if len(s) == 8:
        # YYYYmmdd
        y = int(s[0:4])
        m = int(s[4:6])
        d = int(s[6:8])
        dt = datetime.date(y, m, d)
    return dt


def format_ib_date(d: datetime.date) -> str:
    return d.strftime('%Y%m%d')