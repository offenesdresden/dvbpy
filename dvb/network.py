import json

import requests

from .util.other import convert_to_snake_case


def post(url: str, params: dict = None) -> dict:
    r = requests.post(url, params=params)
    js = json.loads(r.text)
    res = dict()
    for key, val in js.items():
        # convert root keys in JSON response to snake_case
        res[convert_to_snake_case(key)] = val
    return res
