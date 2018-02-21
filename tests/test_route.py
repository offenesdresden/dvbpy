import os
import unittest

from dvb.route import Route, RegularStop, Platform
from dvb.mot_type import MotType


class RouteTestCase(unittest.TestCase):
    # @unittest.skipUnless(os.getenv('TEST_LIVE_DATA'), 'route live tests')
    def test_gets_response(self):
        mup = 33000134
        alp = 33000013
        route_res = Route.get(mup, alp)
        self.assertGreater(len(route_res['routes']), 0)

    def test_subtype_deserialization(self):
        route = Route(dict(
            RouteId=0,
            MotChain=[dict(
                Type='Tram',
                Name='3',
                Diva=dict(
                    Network='voe'
                )
            )],
            PartialRoutes=[dict(
                PartialRouteId=0,
                Mot=dict(
                    Type='Tram',
                    Diva=dict(
                        Network='voe'
                    )
                ),
                RegularStops=[dict(
                    Name='Münchner Platz',
                    Type='Stop',
                    Platform=dict(
                        Name='1',
                        Type='Platform'
                    )
                )]
            )]
        ))

        self.assertEqual(route.route_id, 0)
        self.assertEqual(route.mot_chain[0].type, MotType.TRAM)
        self.assertEqual(route.mot_chain[0].name, '3')
        self.assertEqual(route.mot_chain[0].diva.network, 'voe')
        self.assertEqual(route.partial_routes[0].partial_route_id, 0)
        self.assertEqual(route.partial_routes[0].mot.type, MotType.TRAM)
        self.assertEqual(route.partial_routes[0].mot.diva.network, 'voe')
        self.assertEqual(route.partial_routes[0].regular_stops[0].name, 'Münchner Platz')
        self.assertEqual(route.partial_routes[0].regular_stops[0].type, RegularStop.Type.STOP)
        self.assertEqual(route.partial_routes[0].regular_stops[0].platform.name, '1')
        self.assertEqual(route.partial_routes[0].regular_stops[0].platform.type, Platform.Type.PLATFORM)

    def test_map_data_as_coords(self):
        route = Route(dict(MapData=['Footpath|5656398|4620868|5656399|4620867|',
                                    'Tram|5656388|4620895|5656402|4620920|5656534|4621144|5656555|4621180|']))
        self.assertEqual(route.map_data[0], 'Footpath|5656398|4620868|5656399|4620867|')
        self.assertEqual(route.map_data[1], 'Tram|5656388|4620895|5656402|4620920|5656534|4621144|5656555|4621180|')

        self.assertEqual(route.coord_chain[0][0], MotType.FOOTPATH)
        self.assertEqual(route.coord_chain[0][1][0], (51.03004245071804, 13.721491972240125))
        self.assertEqual(len(route.coord_chain[0][1]), 2)

        self.assertEqual(route.coord_chain[1][0], MotType.TRAM)
        self.assertEqual(route.coord_chain[1][1][0], (51.02994693147935, 13.721873343285964))
        self.assertEqual(len(route.coord_chain[1][1]), 4)

    def test_regular_stop_coords(self):
        stop = RegularStop(dict(
            Latitude=5656388,
            Longitude=4620895,
        ))
        self.assertEqual(stop.coordinates, (51.02994693147935, 13.721873343285964))
