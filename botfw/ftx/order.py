from ..base import order as od
from .api import FtxApi
from ..etc.util import decimal_add


class FtxOrderManager(od.OrderManagerBase):
    def __init__(self, api, ws=None, retention=60):
        super().__init__(api, ws, retention)
        self.ws.subscribe('orders', self.__on_events, True)
        self.ws.subscribe('fills', self.__on_events, True)

    def _generate_order_object(self, e):
        info = e.info
        if info['event_type'] != 'ORDER':
            self.log.warning(f'event for unknown order: {e}')
            return None

        api = FtxApi.ccxt_instance()
        symbol = api.markets_by_id[info['product_code']]['symbol']
        return od.Order(
            symbol, info['child_order_type'].lower(), info['side'].lower(),
            info['size'], info['price'])

    def __on_events(self, msg):
        print('__on_events')
        print(msg)
        # e = msg['data']
        # oe = od.OrderEvent()
        # oe.info = e
        # oe.id = e['id']
        # oe.ts = time.time()
        # oe.price = e['price']
        # oe.size = -e['size'] if e['side'] == 'SELL' else e['size']

        # t = e['event_type']
        # if t == 'EXECUTION':
        #     oe.type = od.EVENT_EXECUTION
        #     oe.price = e['price']
        #     oe.size = -e['size'] if e['side'] == 'SELL' else e['size']
        #     oe.fee = oe.price * e['commission']
        #     # fee is in "base" currency
        # elif t == 'ORDER':
        #     oe.type = od.EVENT_OPEN
        # elif t in ['CANCEL', 'EXPIRE']:
        #     oe.type = od.EVENT_CANCEL
        # elif t == 'ORDER_FAILED':
        #     oe.type = od.EVENT_OPEN_FAILED
        #     oe.message = e['reason']
        # elif t == 'CANCEL_FAILED':
        #     oe.type = od.EVENT_CANCEL_FAILED

        # self._handle_order_event(oe)


class FtxPositionGroup(od.PositionGroupBase):
    def __init__(self):
        super().__init__()

    def update(self, price, size, fee=0, info=None):
        super().update(price, size, fee)
        if info:
            self.position = decimal_add(self.position, -info['commission'])


class FtxOrderGroup(od.OrderGroupBase):
    PositionGroup = FtxPositionGroup


class FtxOrderGroupManager(od.OrderGroupManagerBase):
    OrderGroup = FtxOrderGroup
