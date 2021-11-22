from requests_utils import send_json, send_url


class VKApi:
    token = ""

    def __init__(self, token: str):
        self.token = token

    def execute_method(self, method, params):
        data = {'access_token': self.token, 'v': '5.131'}

        data.update(params)

        return send_url("https://api.vk.com/method/" + method, data)

    @staticmethod
    def check_token(token):
        data = {'access_token': token, 'v': '5.131'}

        res = send_url("https://api.vk.com/method/account.getAppPermissions", data)

        return res