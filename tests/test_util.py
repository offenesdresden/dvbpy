import unittest

from dvb.util import *


class UtilitesTestCase(unittest.TestCase):
    def test_sap_date_conversion(self):
        d1 = sap_date_to_datetime('/Date(1518787726000+0100)/')
        self.assertEqual(d1.year, 2018)
        self.assertEqual(d1.month, 2)
        self.assertEqual(d1.day, 16)
        self.assertEqual(d1.hour, 14)
        self.assertEqual(d1.minute, 28)

        d2 = datetime.fromtimestamp(1518807600)
        self.assertEqual('/Date(1518807600000+0100)/', datetime_to_sap_date(d2))

    def test_convert_to_snakecase(self):
        self.assertEqual('camel_case', convert_to_snake_case('CamelCase'))
        self.assertEqual('camel_case', convert_to_snake_case('camelCase'))
        self.assertEqual('camelcase', convert_to_snake_case('camelcase'))
