class JSONBase:
    def __init__(self, _dict):
        self._dict = _dict

    def _get(self, key: str):
        return self._dict.get(key)
