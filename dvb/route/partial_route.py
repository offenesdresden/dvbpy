from dvb.JSONBase import JSONBase
from .mot import Mot
from .regular_stop import RegularStop


class PartialRoute(JSONBase):
    @property
    def duration(self) -> int:
        return self._get('Duration')

    @property
    def mot(self) -> Mot:
        return Mot(self._get('Mot'))

    @property
    def map_data_index(self) -> int:
        return self._get('MapDataIndex')

    @property
    def shift(self) -> str:
        return self._get('Shift')

    @property
    def regular_stops(self) -> [RegularStop]:
        regular_stops = [RegularStop(rs) for rs in self._get('RegularStops')]
        return regular_stops

    @property
    def partial_route_id(self) -> int:
        return self._get('PartialRouteId')
