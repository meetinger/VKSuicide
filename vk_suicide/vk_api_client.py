import requests


class VKApiClient:
    def __init__(self, token: str):
        self.token = token

    def execute_method(self, method, params):
        data = {'access_token': self.token, 'v': '5.131', **params}

        res = requests.post(url=f"https://api.vk.com/method/{method}", data=data)

        return res.json()

    @staticmethod
    def check_token(token):
        data = {'access_token': token, 'v': '5.131'}

        res = requests.post(url="https://api.vk.com/method/account.getAppPermissions", data=data)

        return res.json()
