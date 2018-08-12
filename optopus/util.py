# -*- coding: utf-8 -*-


def df(data):
    import itertools
    import pandas as pd
    records = [e.values for e in data]
    records = list(itertools.chain.from_iterable(records))
    print(records)
    return pd.DataFrame(data=[r.values for r in records])
