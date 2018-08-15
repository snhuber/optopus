# -*- coding: utf-8 -*-


def pdo(records):
    import pandas as pd
    if len(records) == 1:
        o = pd.Series(records[0])
    else:
        o = pd.DataFrame(records)

        # Adding a index
        # If the assets are options
        if 'code' in o.columns:
            if ('strike' in o.columns) and ('expiration' in o.columns) and ('right' in o.columns):
                o.set_index(['code', 'expiration', 'strike', 'right'], inplace=True)
            else:
                o.set_index(['code'], inplace=True)
        
        o.sort_index(inplace=True)
    return o