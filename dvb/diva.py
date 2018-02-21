from dvb.JSONBase import JSONBase


class Diva(JSONBase):
    def __repr__(self):
        return f'{self.network} {self.number}'

    @property
    def number(self) -> str:
        return self._get('Number')

    @property
    def network(self) -> str:
        return self._get('Network')
