import os
import unittest

from dvb.stop import Stop


class StopTestCase(unittest.TestCase):
    @unittest.skipUnless(os.getenv('TEST_LIVE_DATA'), 'stopfinder query live tests')
    def test_find(self):
        res = Stop.find('albertplatz')
        self.assertGreater(len(res['stops']), 0)

    @unittest.skipUnless(os.getenv('TEST_LIVE_DATA'), 'stopfinder coord live tests')
    def test_find_near(self):
        lat = 51.0647899
        lng = 13.7489767
        res = Stop.find_near(lat, lng)
        self.assertGreater(len(res['stops']), 0)
