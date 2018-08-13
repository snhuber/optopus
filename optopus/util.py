# -*- coding: utf-8 -*-


def df(records):
    import pandas as pd
    print('Type: ', type(records))
    if type(records) != list:
        records = [records]
    return pd.DataFrame(data=records)
