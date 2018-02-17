from .network import post
from .util.date import sap_date_to_datetime
from .util.geo import gk4_to_wgs


class Stop:
    def __init__(self, ident: int, place: str, name: str, latitude: float, longitude: float):
        self.id = ident
        self.place = place
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return '{} {}'.format(self.name, self.place)

    @staticmethod
    def from_str(val: str):
        components = val.split('|')
        if len(components) != 9:
            return None
        ident = int(components[0])
        place = components[2] if components[2] != '' else 'Dresden'
        name = components[3]
        x_gk4 = int(components[4])
        y_gk4 = int(components[5])
        (lat, lng) = gk4_to_wgs(x_gk4, y_gk4)
        return Stop(ident, place, name, lat, lng)

    @staticmethod
    def find(query: str, limit: int = None):
        limit = 0 if limit is None else limit

        res = post('https://webapi.vvo-online.de/tr/pointfinder', {
            'query': query,
            'limit': limit,
            'stopsOnly': True,
            'dvb': True
        })
        res['points'] = [Stop.from_str(s) for s in res['points']]
        res['expiration_time'] = sap_date_to_datetime(res['expiration_time'])
        return res
