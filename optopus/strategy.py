import datetime
from money import Money
from signal import Signal, RightType, ActionType
from security import SecurityType
from settings import p_currency


class Strategy():
    def calculate_signals() -> None:
        raise(NotImplementedError)

    def manage_positions() -> None:
        raise(NotImplementedError)

    
class DummyStrategy(Strategy):
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

    def calculate_signals():
        print('BIP.')