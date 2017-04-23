#!/usr/bin/env python3

# File: money_test.py

"""
Tests src.money.get_currency_value function.
"""

import unittest
import src.money as money
import src.config as config
import tests.testdata4money as testdata

class test_get_currency_value(unittest.TestCase):
    def setUp(self):
        pass
    def test_without_symbol(self):
        for source, result in testdata:
            with self.subTest(source=source, result=result):
                self.assertEqual(
                    money.get_currency_value(source),
                    result)

if __name__ == "__main__":
    testdata = testdata.testdata[config.DEFAULT_CURRENCY]
    unittest.main()
