import datetime
from optopus.money import Money
from optopus.order_manager import OrderManager
from optopus.data_manager import DataManager
from optopus.data_objects import DataSource, IndexAsset
from optopus.signal import Signal, RightType, ActionType
from optopus.data_objects import AssetType
from optopus.settings import CURRENCY


class Strategy():
    def __init__(self, data_manager: DataManager):
        self._data_manager = data_manager

    def calculate_signals() -> None:
        raise(NotImplementedError)

    def manage_positions() -> None:
        raise(NotImplementedError)


class DummyStrategy(Strategy):
    def __init__(self, data_manager: DataManager) -> None:
        super().__init__(data_manager)
        self.SPX = AssetIndex('SPX',
                                   DataSource.IB)
        self.SPX_OPT = AssetOption(self.SPX)
    def calculate_signals2():
        s = Signal('DummyStrategy')
        s.add_item('SPX',
                    AssetType.Option,
                    datetime.datetime.strptime('20/12/2018','%d/%m/%Y').date(),
                    2700,
                    RightType.Call,
                    ActionType.Buy,
                    1,
                    Money('170', CURRENCY))

    def calculate_signals(self):
        f = ['high', 'low', 'close', 'bid', 'bid_size', 'ask', 'ask_size',
             'last', 'last_size', 'time', 'midpoint', 'market_price']
        d = self._data_manager.current(self.SPX, f)
        if d:
            print(d)
        else:
            print('dl is empty')
        #print('SPX OPTION!!!!!')
        #self._data_manager.ticket(self.SPX_OPT)
        #dl = self._data_manager.data(self.SPX_OPT)
        #if dl:
        #    print(dl._data)
        #    print(dl.values)