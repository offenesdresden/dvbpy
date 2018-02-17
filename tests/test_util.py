import unittest

from dvb.util import *


class UtilitesTestCase(unittest.TestCase):
    def test_convert_to_snakecase(self):
        self.assertEqual('camel_case', convert_to_snake_case('CamelCase'))
        self.assertEqual('camel_case', convert_to_snake_case('camelCase'))
        self.assertEqual('camelcase', convert_to_snake_case('camelcase'))
