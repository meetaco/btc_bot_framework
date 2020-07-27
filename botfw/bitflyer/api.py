import ccxt
from ..base.api import ApiBase
from ..etc.util import decimal_add


class BitflyerApi(ApiBase, ccxt.bitflyer):
    _ccxt_class = ccxt.bitflyer

    def __init__(self, ccxt_config={}):
        ApiBase.__init__(self)
        ccxt.bitflyer.__init__(self, ccxt_config)
        self.rate_limit_manager = RateLimitManager()
        self.load_markets()

        # silence linter
        self.public_get_getboardstate = getattr(
            self, 'public_get_getboardstate')
        self.private_get_getpositions = getattr(
            self, 'private_get_getpositions')
        self.private_post_cancelallchildorders = getattr(
            self, 'private_post_cancelallchildorders')
        self.private_get_getcollateral = getattr(
            self, 'private_get_getcollateral')

    def fetch_status(self, params={'product_code': 'FX_BTC_JPY'}):
        res = self.public_get_getboardstate(params)
        status = 'ok' if res['state'] == 'RUNNING' else 'shutdown'
        return {
            'status': status,  # 'ok', 'shutdown', 'error', 'maintenance'
            'updated': None,
            'eta': None,
            'url': None,
        }

    def fetch_position(self, symbol):
        market_id = self.market_id(symbol)
        positions = self.private_get_getpositions({'product_code': market_id})
        total = 0
        for pos in positions:
            size = -pos['size'] if pos['side'] == 'SELL' else pos['size']
            total = decimal_add(total, size)
        return total

    def fetch_collateral(self):
        return self.private_get_getcollateral()

    def cancel_all_order(self, symbol):
        market_id = self.market_id(symbol)
        return self.private_post_cancelallchildorders(
            {'product_code': market_id})

    def request(self, path, api='public', method='GET', params={},
                headers=None, body=None):
        self.rate_limit_manager.add(path, api, params)
        return super().request(path, api, method, params, headers, body)


class RateLimitManager():
    def __init__(self):
        # import inside class due to:
        # https://qiita.com/puriketu99/items/a1347bf5200f095e486e
        from botutil.utils import TimeQueue
        self.time_queue = TimeQueue(5 * 60)

    def add(self, path, api, params):
        call = {}
        call['ip'] = True
        call['private'] = api == 'private'
        call['order'] = path in ['sendchildorder', 'sendparentorder', 'cancelallchildorders']
        call['small'] = 'size' in params and params['size'] <= 0.1
        self.time_queue.append(call)

    def stat(self):
        stat = {}
        elements = self.time_queue.get_elements()
        stat['ip'] = f"{len([x for x in elements if x['ip']])}/500 per 5m"
        stat['private'] = f"{len([x for x in elements if x['private']])}/500 per 5m"
        stat['order'] = f"{len([x for x in elements if x['order']])}/300 per 5m"
        stat['small'] = f"{len([x for x in self.time_queue.get_elements(60) if x['small']])}/100 per 1m"
        return str(stat)
