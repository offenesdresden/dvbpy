import json

import requests


def post(url: str, params: dict = None) -> dict:
    r = requests.post(url, params=params)
    return json.loads(r.text)
