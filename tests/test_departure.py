import os
import unittest
from datetime import datetime

from dvb.departure import Departure
from dvb.mode import Mode


class MonitorTestCase(unittest.TestCase):
    @unittest.skipUnless(os.getenv('TEST_LIVE_DATA'), 'monitor live tests')
    def test_gets_response(self):
        albert_platz = 33000013
        response = Departure.for_stop(albert_platz)
        self.assertGreater(len(response['departures']), 0)
        self.assertTrue('name' in response)
        self.assertTrue('place' in response)
        self.assertTrue('expiration_time' in response)

    def test_departure_etas(self):
        departure = Departure({'ScheduledTime': '/Date(1518807600000+0100)/',
                               'RealTime': '/Date(1518807780000+0100)/'})

        twenty = datetime.fromtimestamp(1518807600)  # 16.02.18 20:00
        self.assertEqual(departure.scheduled_eta(from_date=twenty), 0)
        self.assertEqual(departure.eta(from_date=twenty), 3)
        self.assertEqual(departure.fancy_eta(from_date=twenty), '0+3')

        eighteen_thirty = datetime.fromtimestamp(1518802200)  # 16.02.18 18:30
        self.assertEqual(departure.fancy_eta(from_date=eighteen_thirty), '1:30+3')

        eighteen_fifty_eight = datetime.fromtimestamp(1518803880)  # 16.02.18 18:58
        self.assertEqual(departure.fancy_eta(from_date=eighteen_fifty_eight), '1:02+3')

        twenty_one = datetime.fromtimestamp(1518894060)  # 16.02.18 20:01
        self.assertEqual(departure.fancy_eta(from_date=twenty_one), '-1+3')

    def test_departure_properties(self):
        departure = Departure({'Mot': 'Tram',
                               'LineName': '3',
                               'Direction': 'Wilder Mann',
                               'Platform': {
                                   'Name': '3',
                                   'Type': 'Platform'
                               },
                               'State': 'InTime'})
        self.assertEqual(departure.mode, Mode.TRAM)
        self.assertEqual(departure.line_name, '3')
        self.assertEqual(departure.direction, 'Wilder Mann')
        self.assertEqual(departure.platform, {'Name': '3', 'Type': 'Platform'})
        self.assertEqual(departure.state, Departure.State.IN_TIME)
