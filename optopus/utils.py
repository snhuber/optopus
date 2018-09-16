from collections import OrderedDict
import datetime
from enum import Enum
from typing import List
from urllib import request, parse
#tfrom optopus.settings import BUY_COLOR, SELL_COLOR, UNDERLYING_COLOR
import pandas as pd
from pandas import DataFrame

def to_df(items: List[object]) -> DataFrame:
    rows = []
    for i in items:
        d = OrderedDict()
        for attr, value in vars(i).items():
            if not any([isinstance(value, list),
                        isinstance(value, dict)]):
                d[attr] = value.value if isinstance(value, Enum) else value
        rows.append(d)
    return pd.DataFrame(rows)

def plot_option_positions(positions, underlying_price: float):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(12, 2))
    ax = fig.add_subplot(111)

    #ax.set_frame_on(False)
    #ax.get_yaxis().set_visible(False)

    x_min = underlying_price
    x_max = underlying_price
    for pos in positions:
        x = pos['strike']
        y = -2 if pos['ownership'] == 'SELL' else 0.7
        color = SELL_COLOR if pos['ownership'] == 'SELL' else BUY_COLOR
        
        ax.annotate('   ' + pos['right'] + '\n' + str(pos['strike']),
                    xy=(x, y),
                    xycoords='data',
                    size=10,
                    color=color,
                    bbox=dict(boxstyle="round4", fc='white', ec=color))

        x_min = min(x_min, pos['strike'])
        x_max = max(x_max, pos['strike'])

    ax.set_xlim(x_min - 2, x_max + 2)
    ax.set_ylim(-3, 3)

    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_position('center')
    ax.spines['bottom'].set_color('gray')
    ax.yaxis.set_visible(False)
    ax.xaxis.set_visible(False)

    ax.annotate(str(underlying_price),
                xy=(underlying_price, 0),
                xycoords="data",
                size=10,
                color='white',
                bbox=dict(boxstyle="circle", fc=UNDERLYING_COLOR, ec=UNDERLYING_COLOR))

    plt.plot([], [])


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


def notify(event: str, value1: str = None, value2: str = None, value3: str = None):
    data = {'value1': value1, 'value2': value2, 'value3': value3}  
    data = parse.urlencode(data).encode()
    url = f'https://maker.ifttt.com/trigger/{event}/with/key/cy0nEe3pY7MJjeLakJNeL-'
    
    req = request.Request(url, data=data)
    resp = request.urlopen(req)
    print(resp.read())
