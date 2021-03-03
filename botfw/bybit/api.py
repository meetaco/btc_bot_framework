import ccxt
from ..base.api import ApiBase


class BybitApi(ApiBase, ccxt.bybit):
    _ccxt_class = ccxt.bybit

    def __init__(self, ccxt_config={}):
        ApiBase.__init__(self)
        ccxt.bybit.__init__(self, ccxt_config)
        self.load_markets()

        # silence linter
        self.private_get_position_list = getattr(
            self, 'v2_private_get_position_list')

    def fetch_position(self, symbol):
        market_id = self.market_id(symbol)
        res = self.private_get_position_list({'symbol': market_id})['result']
        return -res['size'] if res['side'] == 'Sell' else res['size']

    def fetch_orders(self, symbol=None, since=None, limit=None, params={}):
        return self.fetch_orders_in_real_time(symbol=symbol, since=since, limit=limit, params=params)

    # Calls /v2/private/order instead of /v2/private/order/list
    # The former has no delay.
    # See https://twitter.com/sen_axis/status/1364218923068002304
    def fetch_orders_in_real_time(self, symbol=None, since=None, limit=None, params={}):
        self.load_markets()
        request = {
            # 'order_id': 'string'
            # 'order_link_id': 'string',  # unique client order id, max 36 characters
            # 'symbol': market['id'],  # default BTCUSD
            # 'order': 'desc',  # asc
            # 'page': 1,
            # 'limit': 20,  # max 50
            # 'order_status': 'Created,New'
            # conditional orders ---------------------------------------------
            # 'stop_order_id': 'string',
            # 'stop_order_status': 'Untriggered',
        }
        market = None
        if symbol is not None:
            market = self.market(symbol)
            request['symbol'] = market['id']
        options = self.safe_value(self.options, 'fetchOrders', {})
        marketTypes = self.safe_value(self.options, 'marketTypes', {})
        marketType = self.safe_string(marketTypes, symbol)
        defaultMethod = 'privateLinearGetOrderQuery' if (marketType == 'linear') else 'v2PrivateGetOrder'
        query = params
        method = self.safe_string(options, 'method', defaultMethod)
        response = getattr(self, method)(self.extend(request, query))
        result = self.safe_value(response, 'result', {})
        return self.parse_orders(result, market, since, limit)
