import unittest

from dvb.util.date import *


class DateTestCase(unittest.TestCase):
    def test_sap_date_conversion(self):
        d1 = sap_date_to_datetime('/Date(1518787726000+0100)/')
        self.assertEqual(d1.year, 2018)
        self.assertEqual(d1.month, 2)
        self.assertEqual(d1.day, 16)
        self.assertEqual(d1.hour, 14)
        self.assertEqual(d1.minute, 28)

        d2 = sap_date_to_datetime('/Date(1518804840000+0100)/')
        self.assertEqual(1518804840, d2.timestamp())

        d3 = sap_date_to_datetime('/Date(1518804720000+0100)/')
        self.assertEqual(1518804720, d3.timestamp())

        d4 = sap_date_to_datetime('/Date(1518805500000+0100)/')
        self.assertEqual(1518805500, d4.timestamp())

        from_timestamp = datetime.fromtimestamp(1518807600)
        self.assertEqual('/Date(1518807600000+0100)/', datetime_to_sap_date(from_timestamp))
