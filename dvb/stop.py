from .network import post
from .util.date import sap_date_to_datetime
from .util.geo import gk4_to_wgs, wgs_to_gk4


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
        if 'coord' in components[0]:
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

        out = dict()
        stops = [Stop.from_str(s) for s in res.get('Points')]
        stops = list(filter(lambda s: s is not None, stops))
        out['stops'] = stops
        out['status'] = res.get('PointStatus')
        out['expiration_time'] = sap_date_to_datetime(res.get('ExpirationTime'))
        return out

    @staticmethod
    def find_near(latitude: float, longitude: float, limit: int = None):
        limit = 0 if limit is None else limit

        (x, y) = wgs_to_gk4(latitude, longitude)

        res = post('https://webapi.vvo-online.de/tr/pointfinder', {
            'query': 'coord:{}:{}'.format(y, x),
            'limit': limit,
            'assignedstops': True,
        })

        out = dict()
        stops = [Stop.from_str(s) for s in res.get('Points')]
        stops = list(filter(lambda s: s is not None, stops))
        out['stops'] = stops
        out['status'] = res.get('PointStatus')
        out['expiration_time'] = sap_date_to_datetime(res.get('ExpirationTime'))
        return out
