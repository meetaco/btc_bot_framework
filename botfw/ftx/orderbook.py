from sortedcontainers import SortedDict

from ..base.orderbook import OrderbookBase
from .websocket import FtxWebsocket
from .api import FtxApi


class FtxOrderbook(OrderbookBase):

    def __init__(self, symbol, ws=None):
        super().__init__()
        self.symbol = symbol
        self.ws = ws or FtxWebsocket()

        market_id = FtxApi.ccxt_instance().market_id(self.symbol)
        self.ws.subscribe(f'orderbook.{market_id}', self.__on_message)

    def __on_message(self, msg):
        if 'data' not in msg:
            return

        d = msg['data']
        action = d['action']

        if action == 'partial':
            bids, asks = SortedDict(), SortedDict()
            self.__update(bids, d['bids'], -1)
            self.__update(asks, d['asks'], 1)
            self.sd_bids, self.sd_asks = bids, asks
        elif action == 'update':
            self.__update(self.sd_bids, d['bids'], -1)
            self.__update(self.sd_asks, d['asks'], 1)

        self._trigger_callback()

    def __update(self, sd, d, sign):
        for i in d:
            p, s = float(i[0]), float(i[1])
            if s == 0:
                sd.pop(p * sign, None)
            else:
                sd[p * sign] = [p, s]
