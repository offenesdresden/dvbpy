from dvb.JSONBase import JSONBase
from .platform import Platform
from dvb.util.date import sap_date_to_datetime
from dvb.util.geo import gk4_to_wgs


class RegularStop(JSONBase):
    class Type:
        """Non-exhaustive list of known RegularStop.Type values"""
        STOP = 'Stop'

    @property
    def arrival_time(self) -> str:
        return sap_date_to_datetime(self._get('ArrivalTime'))

    @property
    def departure_time(self) -> str:
        return sap_date_to_datetime(self._get('DepartureTime'))

    @property
    def place(self) -> str:
        return self._get('Place')

    @property
    def name(self) -> str:
        return self._get('Name')

    @property
    def type(self) -> Type:
        return self._get('Type')

    @property
    def data_id(self) -> str:
        return self._get('DataId')

    @property
    def coordinates(self) -> (float, float):
        return gk4_to_wgs(self._get('Latitude'), self._get('Longitude'))

    @property
    def map_pdf_id(self) -> str:
        return self._get('MapPdfId')

    @property
    def platform(self) -> Platform:
        return Platform(self._get('Platform'))
