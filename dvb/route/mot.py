from dvb.JSONBase import JSONBase
from dvb.diva import Diva
from dvb.mot_type import MotType


class Mot(JSONBase):
    def __repr__(self):
        return f'{self.type} {self.name} {self.direction}'

    @property
    def type(self) -> MotType:
        return self._get('Type')

    @property
    def name(self) -> str:
        return self._get('Name')

    @property
    def diva(self) -> Diva:
        return Diva(self._get('Diva'))

    @property
    def direction(self) -> str:
        direction = self._get('Direction')
        return direction.strip() if direction is not None else direction

    @property
    def changes(self) -> [str]:
        return self._get('Changes')
