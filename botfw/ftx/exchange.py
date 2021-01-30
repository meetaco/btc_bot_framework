from ..base.exchange import ExchangeBase
from .websocket import FtxWebsocket
from .trade import FtxTrade
from .orderbook import FtxOrderbook
from .order import FtxOrderManager, FtxOrderGroupManager
from .api import FtxApi


class Ftx(ExchangeBase):
    Api = FtxApi
    Websocket = FtxWebsocket
    OrderManager = FtxOrderManager
    OrderGroupManager = FtxOrderGroupManager
    Trade = FtxTrade
    Orderbook = FtxOrderbook
