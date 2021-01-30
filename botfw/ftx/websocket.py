import time

from ..base.websocket import WebsocketBase
from ..etc.util import hmac_sha256
from ..etc.util import run_forever_nonblocking


class FtxWebsocket(WebsocketBase):
    ENDPOINT = 'wss://ftx.com/ws'

    def command(self, op, channel=None, market=None, args=None, cb=None):
        msg = {'op': op}
        if channel:
            msg['channel'] = channel
        if market:
            msg['market'] = market
        if args:
            msg['args'] = args
        self._request_table[self._request_id] = (msg, cb)
        self._request_id += 1
        self.send(msg)

    def _subscribe(self, ch):
        if '.' in ch:
            self.command('subscribe', channel=ch[:ch.find('.')], market=ch[ch.find('.') + 1:])
        else:
            self.command('subscribe', args={'channel': ch})

    def _authenticate(self):
        now = int(time.time() * 1000)
        sign = hmac_sha256(self.secret, f'{now}websocket_login')

        self.command('login', args={
            'key': self.key,
            'sign': sign,
            'time': now},
            cb=lambda msg: self._set_auth_result('result' in msg))

        self._set_auth_result(True)  # authに成功しても何も返ってこない（仕様？）のでcallbackにまかせず手動でauth完了とする

    def _handle_message(self, msg):
        self.log.info(msg)
        channel = msg.get('channel')
        market = msg.get('market')
        if channel and market:
            ch = f'{channel}.{market}'
            self._ch_cb[ch](msg)
        else:
            self.log.info(f'recv: {msg}')
            if 'id' in msg:
                req, cb = self._request_table[msg['id']]
                if 'result' in msg:
                    res = msg['result']
                    self.log.info(f'{req} => {res}')
                elif 'error' in msg:
                    err = msg['error']
                    code, message = err.get('code'), err.get('message')
                    self.log.error(f'{req} => {code}, {message}')

                if cb:
                    cb(msg)
            else:
                self.log.warning(f'Unknown message: {msg}')


class FtxWebsocketPrivate(WebsocketBase):
    ENDPOINT = 'wss://ftx.com/ws'

    def __init__(self, api):
        self.__api = api  # _on_init() may be called in super().__init__()
        self.__cb = []
        self.__key = None  # websocket_key (listenKey)
        super().__init__(None)
        run_forever_nonblocking(self.__worker, self.log, 60 * 30)

    def add_callback(self, cb):
        self.__cb.append(cb)

    def _on_init(self):
        res = self.__api.websocket_key()
        self.__key = res['listenKey']
        self.url = f'{self.ENDPOINT}/{self.__key}'

    def _on_open(self):
        super()._on_open()
        self._set_auth_result(True)

    def _handle_message(self, msg):
        self._run_callbacks(self.__cb, msg)

    def __worker(self):
        if self.__key:
            self.__api.websocket_key('PUT', self.__key)  # keep alive
