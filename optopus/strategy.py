import datetime
from money import Money
from order_manager import OrderManager
from data_manager import (DataManager, DataSeriesType, DataSource,
                          DataSeriesIndex, DataSeriesOption)
from signal import Signal, RightType, ActionType
from security import SecurityType
from settings import CURRENCY


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
        self.SPX = DataSeriesIndex('SPX',
                                   DataSource.IB)
        self.SPX_OPT = DataSeriesOption(self.SPX)
    def calculate_signals2():
        s = Signal('DummyStrategy')
        s.add_item('SPX',
                    SecurityType.Option,
                    datetime.datetime.strptime('20/12/2018','%d/%m/%Y').date(),
                    2700,
                    RightType.Call,
                    ActionType.Buy,
                    1,
                    Money('170', CURRENCY))

    def calculate_signals(self):
        dl = self._data_manager.data(self.SPX)
        if dl:
             print(self.SPX.data_series_id)
             print(dl[-1].time)
             print('Last: ', dl[-1].last)
             print('Midpoint: ', dl[-1].midpoint())
             print('Market price', dl[-1].market_price())
        else:
            print('dl is empty')
        #print('SPX OPTION!!!!!')
        #self._data_manager.ticket(self.SPX_OPT)
        #dl = self._data_manager.data(self.SPX_OPT)