import time
import requests
from collections import deque

import vk_captchasolver as vk_solver

CAPTCHA_SOLVER = True
try:
    CAPTCHA_SOLVER = True
except ImportError as e:
    vk_solver = None
    CAPTCHA_SOLVER = False

class VKApiClient:
    def __init__(self, token: str, shared_data: dict = None, rate_limit: int = 3):
        self._token = token
        self._user_id = None
        self.shared_data = shared_data or {}
        self.rate_limit = rate_limit
        self.time_window = 1
        self.request_timestamps = deque()

    def _rate_limit_check(self):
        now = time.time()
        while self.request_timestamps and now - self.request_timestamps[0] > self.time_window:
            self.request_timestamps.popleft()
        if len(self.request_timestamps) >= self.rate_limit:
            sleep_time = self.time_window - (now - self.request_timestamps[0])
            time.sleep(sleep_time)
            self.request_timestamps.popleft()

        self.request_timestamps.append(time.time())
        print(self.request_timestamps)

    def _wait_if_needed(self):
        now = time.time()
        if now < self.wait_until:
            delay = self.wait_until - now
            time.sleep(delay)

    def _set_delay(self, seconds: int):
        self.wait_until = time.time() + seconds

    def _execute_method(self, method: str, params: dict):
        self._wait_if_needed()
        self._rate_limit_check()

        data = {'access_token': self._token, 'v': '5.131', **params, **self.captcha_params}

        res = requests.post(url=f"https://api.vk.com/method/{method}", data=data).json()
        print('res:', res)
        return res

    def execute_method(self, method: str, params: dict):
        res = self._execute_method(method, params)
        err_code = res.get('error', {}).get('error_code', 0)

        while err_code in (14, 9, 6):
            if err_code == 14 and CAPTCHA_SOLVER:
                captcha_sid = res['error']['captcha_sid']
                captcha_key = vk_solver.solve(sid=captcha_sid, s=1)
                self.captcha_params = {'captcha_sid': captcha_sid, 'captcha_key': captcha_key}
                res = self._execute_method(method, params)
                err_code = res.get('error', {}).get('error_code', 0)
            else:
                self._set_delay(1)
                res = self._execute_method(method, params)
                err_code = res.get('error', {}).get('error_code', 0)

        return res

    @staticmethod
    def is_token_valid(token: str) -> bool:
        data = {'access_token': token, 'v': '5.131'}
        res = requests.post(url="https://api.vk.com/method/account.getAppPermissions", data=data)
        return 'error' not in res.json()

    @property
    def user_id(self):
        if self._user_id is None:
            res = self.execute_method('users.get', {'fields': 'id'})
            self._user_id = res['response'][0]['id']
        return self._user_id

    @property
    def captcha_params(self):
        return self.shared_data.get('captcha_params', {})

    @captcha_params.setter
    def captcha_params(self, value):
        self.shared_data['captcha_params'] = value

    @property
    def wait_until(self):
        return self.shared_data.get('wait_until', time.time())

    @wait_until.setter
    def wait_until(self, value):
        self.shared_data['wait_until'] = value

    @property
    def request_timestamps(self):
        return self.shared_data.get('request_timestamps')

    @request_timestamps.setter
    def request_timestamps(self, value):
        self.shared_data['request_timestamps'] = value

    def __str__(self):
        return f"VKApiClient(user_id={self.user_id})"