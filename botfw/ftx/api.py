import ccxt
from ..base.api import ApiBase


class FtxApi(ApiBase, ccxt.ftx):
    _ccxt_class = ccxt.ftx

    def __init__(self, ccxt_config={}):
        ApiBase.__init__(self)
        ccxt.ftx.__init__(self, ccxt_config)
        self.load_markets()

        # silence linter
        self.private_get_positions = getattr(
            self, 'private_get_positions')

    def fetch_position(self, symbol):
        positions = self.private_get_positions()['result']
        for p in positions:
            if p['future'] == symbol:  # 現物は？
                return p['netSize']
        raise Exception('symbol not found')
