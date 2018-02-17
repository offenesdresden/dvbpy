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

    def test_init_from_str(self):
        test_cases = [
            ('33000013|||Albertplatz|5660140|4622550|0||', 33000013, 'Albertplatz'),
            ('33000451||Oberwartha|Albertplatz|5662035|4613040|0||', 33000451, 'Albertplatz'),
            ('30202000||Plauen (Vogtl)|Am Albertplatz|5596300|4509657|0||', 30202000, 'Am Albertplatz'),
            ('33000732|||Mommsenstraße|5656128|4621560|2||', 33000732, 'Mommsenstraße'),
            ('33000727|||Technische Universität (Fr.-Foerster-Platz)|5656360|4621515|233||', 33000727,
             'Technische Universität (Fr.-Foerster-Platz)'),
            ('33000742|||Helmholtzstraße|5655904|4621157|565||', 33000742, 'Helmholtzstraße'),
            ('33000728|||Staats- und Universitätsbibliothek|5656331|4621972|600||', 33000728,
             'Staats- und Universitätsbibliothek'),
            ('33000512|||Stadtgutstraße|5655763|4621918|623||', 33000512, 'Stadtgutstraße'),
        ]

        for test in test_cases:
            stop = Stop.from_str(test[0])
            self.assertEqual(stop.id, test[1])
            self.assertEqual(stop.name, test[2])
