#!/usr/bin/env python3

# File: tests/config_test.py

"""
So far this file serves to only to test
src.config.get_list_of_accounts.
"""

import unittest
import re
import time
import src.config as config

class Config(unittest.TestCase):
    def setUp(self):
        pass
    def test_DEFAULT_YEAR(self):
        self.assertEqual(
            config.DEFAULT_YEAR,
            time.localtime().tm_year)

    def test_get_list_of_accounts(self):
        for source, expected in test_data4get_list_of_accounts:
            with self.subTest(source=source, expected=expected):
                self.assertEqual(
                    config.get_list_of_accounts(source),
                    expected)
    def test_get_type(self):
        for entry, expected in test_data4get_type:
            with self.subTest(entry=entry, expected=expected):
                self.assertEqual(
                    config.get_type(entry),
                    expected)
    def test_valid_account_code(self):
        for entry, expected in test_data4valid_account_code:
            with self.subTest(entry=entry, expected=expected):
                self.assertEqual(
                    config.valid_account_code(entry),
                    expected)
    def test_account_category(self):
        for entry, expected in test_data4account_category:
            with self.subTest(entry=entry, expected=expected):
                self.assertEqual(
                    config.account_category(entry),
                    expected)

test_data4get_list_of_accounts = (
    config.test_data4get_list_of_accounts)

test_data4get_type = (
    config.test_data4get_type)

test_data4valid_account_code = (
    config.test_data4valid_account_code)

test_data4account_category = (
    config.test_data4account_category)

if __name__ == "__main__":
    
    unittest.main()

