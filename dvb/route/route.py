from datetime import datetime

from dvb.JSONBase import JSONBase
from dvb.mot_type import MotType
from dvb.network import post
from dvb.stop import Stop
from dvb.util.geo import gk4_to_wgs
from .mot import Mot
from .partial_route import PartialRoute
from .request_attrs import MobilitySettings, StandardSettings


class Route(JSONBase):
    def __repr__(self):
        return f'Route {self.route_id} {self.duration}m'

    @staticmethod
    def get_for_stop_names(origin_name: str, destination_name: str, *args, **kwargs):
        """Find a route given two stop names. Warning: This sends two stopfinder requests first!"""
        origin_res = Stop.find(origin_name)
        assert (len(origin_res['stops']) > 0)
        destination_res = Stop.find(destination_name)
        assert (len(destination_res['stops']) > 0)

        return Route.get(origin_res['stops'][0].id, destination_res['stops'][0].id, *args, **kwargs)

    @staticmethod
    def get(origin_id: int, destination_id: int, time: datetime = None, is_arrival: bool = None,
            allow_short_term_changes: bool = None, mobility_settings: dict = None,
            standard_settings: StandardSettings = None) -> dict:
        """Find a route matching the given parameters"""

        time = datetime.now() if time is None else time
        is_arrival = False if is_arrival is None else is_arrival
        allow_short_term_changes = True if allow_short_term_changes is None else allow_short_term_changes
        mobility_settings = MobilitySettings.no_restriction() if mobility_settings is None else mobility_settings
        standard_settings = StandardSettings() if standard_settings is None else standard_settings

        res = post('https://webapi.vvo-online.de/tr/trips', dict(
            origin=str(origin_id),
            destination=str(destination_id),
            time=time.isoformat(),
            isarrivaltime=is_arrival,
            shorttermchanges=allow_short_term_changes,
            mobilitySettings=mobility_settings,
            standardSettings=standard_settings._dict,
        ))

        out = dict()
        routes = res.get('Routes') if res.get('Routes') is not None else []
        out['routes'] = [Route(r) for r in routes]
        out['session_id'] = res.get('SessionId')
        return out

    @property
    def price_level(self) -> int:
        return self._get('PriceLevel')

    @property
    def price(self) -> str:
        return self._get('Price')

    @property
    def duration(self) -> int:
        return self._get('Duration')

    @property
    def interchanges(self) -> int:
        return self._get('Interchanges')

    @property
    def mot_chain(self) -> [Mot]:
        mot_chain = [Mot(m) for m in self._get('MotChain')]
        return mot_chain

    @property
    def farezone_origin(self) -> int:
        return self._get('FareZoneOrigin')

    @property
    def farezone_destination(self) -> int:
        return self._get('FareZoneDestination')

    @property
    def map_pdf_id(self) -> str:
        return self._get('MapPdfId')

    @property
    def route_id(self) -> int:
        return self._get('RouteId')

    @property
    def partial_routes(self) -> [PartialRoute]:
        partial_routes = [PartialRoute(pr) for pr in self._get('PartialRoutes')]
        return partial_routes

    @property
    def map_data(self) -> [str]:
        """This is the raw map_data str as returned by the API. You might be looking for route.coord_chain instead."""
        return self._get('MapData')

    @property
    def coord_chain(self) -> [(MotType, [(float, float)])]:
        # example: [`Tram|5656388|4620895|[...]|5660124|4622534|`]
        chains = []
        for chain in self.map_data:
            values = chain.split('|')
            mot_type = values[0]
            gk4_coords = []
            for val in values:
                try:
                    gk4_coords.append(int(val))
                except ValueError:
                    pass
            xs = gk4_coords[::2]
            ys = gk4_coords[1::2]
            coords = [gk4_to_wgs(lat, lng) for lat, lng in zip(xs, ys)]
            chains.append((mot_type, coords))
        return chains
