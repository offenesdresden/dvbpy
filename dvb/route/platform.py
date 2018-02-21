from dvb.JSONBase import JSONBase


class Platform(JSONBase):
    class Type:
        """Non-exhaustive list of known Platform.Type values"""
        PLATFORM = 'Platform'
        RAILTRACK = 'Railtrack'

    @property
    def name(self) -> str:
        return self._get('Name')

    @property
    def type(self) -> Type:
        return self._get('Type')
