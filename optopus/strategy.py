import datetime
from money import Money
from order_manager import OrderManager
from data_manager import DataManager, DataSeriesType, DataSource, DataSeries
from signal import Signal, RightType, ActionType
from security import SecurityType
from settings import p_currency


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
        self.SPX = DataSeries('SPX',
                              DataSeriesType.Index,
                              None,
                              DataSource.IB)
        self.SPX_OPT = DataSeries('SPX',
                                  DataSeriesType.Option,
                                  DataSeriesType.Index,
                                  DataSource.IB)
    def calculate_signals2():
        s = Signal('DummyStrategy')
        s.add_item('SPX',
                    SecurityType.Option,
                    datetime.datetime.strptime('20/12/2018','%d/%m/%Y').date(),
                    2700,
                    RightType.Call,
                    ActionType.Buy,
                    1,
                    Money('170', p_currency))

    def calculate_signals(self):
        self._data_manager.ticket(self.SPX)
        self._data_manager.ticket(self.SPX_OPT)