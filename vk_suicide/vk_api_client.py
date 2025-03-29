import functools
import random
import time

import requests

CAPTCHA_SOLVER = True
try:
    import vk_captchasolver as vk_solver
    CAPTCHA_SOLVER = True
except ImportError as e:
    vk_solver = None
    CAPTCHA_SOLVER = False

def vk_limit_solver(func):

    @functools.wraps(func)
    def wrapper(method: str, params: dict, *args, **kwargs):
        res = func(method, params, *args, **kwargs)
        err_code = res.get('error', {'error_code': 0}).get('error_code', 0)

        while err_code in (14, 9):
            if err_code == 14 and CAPTCHA_SOLVER:
                captcha_sid = res['error']['captcha_sid']
                captcha_key = vk_solver.solve(sid=captcha_sid, s=1)

                params.update({'captcha_sid': captcha_sid, 'captcha_key': captcha_key})

                res = func(method, params, *args, **kwargs)
                err_code = res.get('error', {'error_code': 0}).get('error_code', 0)
            elif err_code == 9 or err_code == 14 and not CAPTCHA_SOLVER:
                time.sleep(random.randint(1,5))
                res = func(method, params, *args, **kwargs)
                err_code = res.get('error', {'error_code': 0}).get('error_code', 0)

    return wrapper

class VKApiClient:
    def __init__(self, token: str):
        self._token = token
        self._user_id = None

    @vk_limit_solver
    def execute_method(self, method: str, params: dict):
        data = {'access_token': self._token, 'v': '5.131', **params}

        res = requests.post(url=f"https://api.vk.com/method/{method}", data=data)

        return res.json()

    @staticmethod
    # @vk_limit_solver
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