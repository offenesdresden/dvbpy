import os
import unittest

from dvb.stop import Stop


class StopTestCase(unittest.TestCase):
    @unittest.skipUnless(os.getenv('TEST_LIVE_DATA'), 'stopfinder live tests')
    def test_gets_response(self):
        res = Stop.find('albertplatz')
        self.assertGreater(len(res['points']), 0)
