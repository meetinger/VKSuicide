import json
import urllib.request
from urllib.parse import urlencode


def send_json(address, data):
    json_data = json.dumps(data).encode('utf-8')

    req = urllib.request.Request(address, data=json_data,
                                 headers={'Content-Type': 'application/json; charset=utf-8'})

    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))


def send_url(address, data):
    url_data = urlencode(data).encode('utf-8')

    req = urllib.request.Request(address, data=url_data, method='POST')

    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))
