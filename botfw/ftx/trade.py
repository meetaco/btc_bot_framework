from ..base.trade import TradeBase
from .websocket import FtxWebsocket
from .api import FtxApi
from ..etc.util import unix_time_from_ISO8601Z


class FtxTrade(TradeBase):
    def __init__(self, symbol, ws=None):
        super().__init__()
        self.symbol = symbol
        self.ws = ws or FtxWebsocket()

        market_id = FtxApi.ccxt_instance().market_id(self.symbol)
        self.ws.subscribe(f'trades.{market_id}', self.__on_message)

    def __on_message(self, msg):
        if 'data' not in msg:
            return

        for t in msg['data']:
            ts = unix_time_from_ISO8601Z(t['time'])
            price = t['price']
            size = t['size']
            if t['side'] == 'Sell':
                size *= -1
            self.ltp = price
            self._trigger_callback(ts, price, size)
