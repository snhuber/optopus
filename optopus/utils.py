# -*- coding: utf-8 -*-


def pdo(records):
    import pandas as pd
    if len(records) == 1:
        o = pd.Series(records[0])
    else:
        o = pd.DataFrame(records)
        o.set_index(['code'], inplace=True)
        o.sort_index(inplace=True)
    return o