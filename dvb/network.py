import json
import os

import requests


def post(url: str, params: dict = None) -> dict:
    if os.getenv('TEST_LIVE_DATA') is not None:
        print(url, json.dumps(params))
    r = requests.post(url, json=params, headers={
        'Content-Type': 'application/json; charset=UTF-8'
    })
    return json.loads(r.text)
