import requests


class VKApiClient:
    def __init__(self, token: str):
        self._token = token
        self._user_id = None

    def execute_method(self, method, params):
        data = {'access_token': self._token, 'v': '5.131', **params}

        res = requests.post(url=f"https://api.vk.com/method/{method}", data=data)

        return res.json()

    @staticmethod
    def check_token(token):
        data = {'access_token': token, 'v': '5.131'}

        res = requests.post(url="https://api.vk.com/method/account.getAppPermissions", data=data)

        return res.json()

    @property
    def user_id(self):
        if self._user_id is None:
            res = self.execute_method('users.get', {'fields': 'id'})
            self._user_id = res['response'][0]['id']
        return self._user_id