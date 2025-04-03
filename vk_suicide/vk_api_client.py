import time
import requests
import multiprocessing as mp

from multiprocessing.synchronize import Lock
from typing import Optional


try:
    import vk_captchasolver as vk_solver
    CAPTCHA_SOLVER = True
except ImportError:
    vk_solver = None
    CAPTCHA_SOLVER = False


class VKApiClient:
    def __init__(self, token: str, rate_limit: int = 1):
        self._token = token
        self._user_id = None
        self.rate_limit = rate_limit
        self.time_window = 1

        self.request_lock: Optional[Lock] = None
        self.request_timestamps: Optional[list] = None
        self.captcha_params: dict = {}
        self.wait_until: mp.Value = mp.Value('d', time.time())

    def set_shared_state(self, lock: Lock, timestamps: list, captcha_params: dict, wait_until: float = 0):
        self.request_lock = lock
        self.request_timestamps = timestamps
        self.captcha_params = captcha_params
        self.wait_until = wait_until

    def _rate_limit_check(self):
        with self.request_lock:
            now = time.time()
            ts = self.request_timestamps

            while ts and now - ts[0] > self.time_window:
                del ts[0]

            if len(ts) >= self.rate_limit:
                sleep_time = self.time_window - (now - ts[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                del ts[0]

            ts.append(time.time())

    def _wait_if_needed(self):
        now = time.time()
        if now < self.wait_until.value:
            time.sleep(self.wait_until.value - now)

    def _set_delay(self, seconds: int):
        self.wait_until.value = time.time() + seconds

    def _execute_method(self, method: str, params: dict):
        self._wait_if_needed()
        self._rate_limit_check()
        data = {'access_token': self._token, 'v': '5.131', **params, **self.captcha_params}
        print('data:', data)
        res = requests.post(url=f"https://api.vk.com/method/{method}", data=data).json()
        print('res:', res)
        return res

    def execute_method(self, method: str, params: dict):
        res = self._execute_method(method, params)
        err_code = res.get('error', {}).get('error_code', 0)

        while err_code in (14, 9, 6):
            if err_code == 14 and CAPTCHA_SOLVER:
                print('CAPTCHA')
                self.request_lock.acquire()
                captcha_sid = res['error']['captcha_sid']
                captcha_key = vk_solver.solve(sid=captcha_sid, s=1)
                self.captcha_params['captcha_sid'] = captcha_sid
                self.captcha_params['captcha_key'] = captcha_key
                print(self.captcha_params)
                res = self._execute_method(method, params)
                self.request_lock.release()
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

    def __str__(self):
        return f"VKApiClient(user_id={self.user_id})"