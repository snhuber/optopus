# -*- coding: utf-8 -*-
from optopus.common import AssetDefinition, AssetType


# TODO: load the wath list from a json
WATCH_LIST = {
    "DIA": AssetType.ETF,
    "EEM": AssetType.ETF,
    "EFA": AssetType.ETF,
    "EWZ": AssetType.ETF,
    # 'FEZ': AssetType.ETF, not enough historic data
    "FXI": AssetType.ETF,
    "GDX": AssetType.ETF,
    "GDXJ": AssetType.ETF,
    "GLD": AssetType.ETF,
    "IWM": AssetType.ETF,
    "IYR": AssetType.ETF,
    "KRE": AssetType.ETF,
    "OIH": AssetType.ETF,
    # 'QQQ': AssetType.ETF,
    "SLV": AssetType.ETF,
    "SPY": AssetType.ETF,
    "TLT": AssetType.ETF,
    "XBI": AssetType.ETF,
    "XLB": AssetType.ETF,
    "XLE": AssetType.ETF,
    "XLF": AssetType.ETF,
    "XLI": AssetType.ETF,
    "XLK": AssetType.ETF,
    "XLP": AssetType.ETF,
    "XLU": AssetType.ETF,
    "XME": AssetType.ETF,
    "XOP": AssetType.ETF,
    "XRT": AssetType.ETF,
}

WATCH_LIST = {
    "SPY": AssetType.ETF,
    "XOP": AssetType.ETF,
    "XLI": AssetType.ETF,
    "XLE": AssetType.ETF,
    "OIH": AssetType.ETF,
}

WATCH_LIST = {"SPY": AssetType.ETF, "AD-NYSE": AssetType.Index}

WATCH_LIST = (
    AssetDefinition("SPY", AssetType.ETF),
    AssetDefinition("TRIN-NYSE", AssetType.Index, exchange="NYSE"),
)


# https://groups.io/g/twsapi/topic/market_breadth_symbols_at_ib/11899195?p=,,,20,0,0,0::recentpostdate%2Fsticky,,,20,2,0,11899195