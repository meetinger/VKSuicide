import time
import requests
import multiprocessing as mp
from multiprocessing.synchronize import Lock
from typing import Optional

try:
    from vk_captcha import VkCaptchaSolver
    CAPTCHA_SOLVER = True
except ImportError:
    VkCaptchaSolver = None
    CAPTCHA_SOLVER = False


class VKApiClient:
    def __init__(self, token: str, rate_limit: int = 3):
        self._token = token
        self._user_id = None
        self.rate_limit = rate_limit
        self.time_window = 1

        self.rate_limit_lock: Optional[Lock] = None
        self.captcha_lock: Optional[Lock] = None
        self.request_timestamps: Optional[list] = None
        self.captcha_params: dict = {}
        self.wait_until: mp.Value = mp.Value('d', time.time())

        self.logger = None

    def set_shared_state(self, rate_limit_lock: Lock, captcha_lock: Lock, timestamps: list, captcha_params: dict, wait_until: float = 0):
        self.rate_limit_lock = rate_limit_lock
        self.captcha_lock = captcha_lock
        self.request_timestamps = timestamps
        self.captcha_params = captcha_params
        self.wait_until = wait_until

        self.logger = None

    def _rate_limit_check(self):
        with self.rate_limit_lock:
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
        self.logger.info(f"data: {data}")
        res = requests.post(url=f"https://api.vk.com/method/{method}", data=data).json()
        return res

    def execute_method(self, method: str, params: dict, max_retries: int = 5):
        attempts = 0

        while True:
            attempts += 1
            res = self._execute_method(method, params)
            err_code = res.get('error', {}).get('error_code', 0)

            if err_code not in (14, 9, 6):
                break

            if attempts >= max_retries:
                self.logger.error(f"Max retries reached for {method} with params {params}")
                break

            if err_code == 14:
                error_data = res['error']
                captcha_sid = error_data['captcha_sid']
                captcha_img_url = error_data['captcha_img']

                with self.captcha_lock:
                    if (self.captcha_params.get('captcha_sid') == captcha_sid and
                            'captcha_key' in self.captcha_params):
                        self.logger.info(f"Captcha already solved by another worker (sid={captcha_sid})")
                        continue

                    if not CAPTCHA_SOLVER:
                        self.logger.error("CAPTCHA_SOLVER not available")
                        raise Exception("Captcha needed, but no solver available")

                    self.logger.info("Captcha Needed, locking workers")
                    self.logger.info(f'RES: {res}')

                    captcha_solver = VkCaptchaSolver()
                    captcha_key, accuracy = captcha_solver.solve(
                        captcha_img_url,
                        minimum_accuracy=0.7,
                        repeat_count=5
                    )

                    if accuracy < 0.8:
                        self.logger.warning(f"Captcha accuracy too low ({accuracy:.3f}), skipping attempt")
                        self._set_delay(5)
                        continue

                    self.captcha_params['captcha_sid'] = captcha_sid
                    self.captcha_params['captcha_key'] = captcha_key

                    self.logger.info(f"Captcha solved:\n"
                                     f"captcha_img_url={captcha_img_url}\n"
                                     f"captcha_sid={captcha_sid}\n"
                                     f"captcha_key={captcha_key}\n"
                                     f"accuracy={accuracy:.3f}")
                    continue

            else:
                self.logger.info(f"Error code: {err_code}, retrying in 10 seconds")
                self._set_delay(10)
                continue

        if 'error' in res:
            raise Exception(res['error'])

        self.captcha_params.pop('captcha_sid', None)
        self.captcha_params.pop('captcha_key', None)

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
