import os
import unittest
from datetime import datetime

from dvb.monitor import Departure


class MonitorTestCase(unittest.TestCase):
    @unittest.skipUnless(os.getenv('TEST_LIVE_DATA'), 'not testing live data')
    def test_gets_response(self):
        response = Departure.fetch(33000013)
        self.assertGreater(len(response['departures']), 0)
        self.assert_('name' in response)
        self.assert_('place' in response)
        self.assert_('expiration_time' in response)

    def test_departure_etas(self):
        departure = Departure({'ScheduledTime': '/Date(1518807600000+0100)/',
                               'RealTime': '/Date(1518807780000+0100)/',
                               'LineName': '85',
                               'Direction': 'Löbtau Süd'})
        now = datetime.fromtimestamp(1518807600)

        self.assertEqual(departure.scheduled_eta(from_date=now), 0)
        self.assertEqual(departure.eta(from_date=now), 3)
        self.assertEqual(departure.fancy_eta(from_date=now), '0+3')
