import datetime
from dataclasses import dataclass
from optopus.asset import Asset, AssetId
from optopus.common import AssetType, Direction


class Stock(Asset):
    def __init__(self, id: AssetId):
        if not id.asset_type == AssetType.Stock:
            raise ValueError("Wrong AssetType for stock asset")
        super().__init__(id)
