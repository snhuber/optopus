# -*- coding: utf-8 -*-
import datetime
from optopus.settings import BUY_COLOR, SELL_COLOR, UNDERLYING_COLOR

def pdo(records):
    import pandas as pd
    if len(records) == 1:
        o = pd.Series(records[0])
    else:
        o = pd.DataFrame(records)
        o.set_index(['code'], inplace=True)
        o.sort_index(inplace=True)
    return o



def plot_option_positions(positions, underlying_price: float):
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(12, 2.5))
    ax = fig.add_subplot(111)

    ax.set_frame_on(False)
    ax.get_yaxis().set_visible(False)

    x_min = 100000.0
    x_max = 0.0
    for pos in positions:
        x = pos['strike'] - 0.20
        color = SELL_COLOR if pos['ownership'] == 'SELL' else BUY_COLOR
        ax.annotate(pos['right'],
                    xy=(x, 0.6),
                    xycoords='data',
                    size=30,
                    color='white',
                    bbox=dict(boxstyle="round4", fc=color, ec=color))
        x_min = min(x_min, pos['strike'])
        x_max = max(x_max, pos['strike'])

    ax.set_xlim(x_min - 5, x_max + 5)
    ax.set_ylim(0, 5)

    ax.annotate("U",
                xy=(underlying_price-0.12, 0.4),
                xycoords="data",
                size=15,
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