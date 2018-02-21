import json

import requests


def post(url: str, params: dict = None) -> dict:
    r = requests.post(url, params=params, headers={'Content-Type': 'application/json;charset=UTF-8'})
    return json.loads(r.text)
