import requests


def post(url: str, params: dict = None) -> str:
    r = requests.post(url, params=params)
    return r.text
