#!/usr/bin/env python3

# File: tests/config_test.py

"""
So far this file serves to only to test
src.config.get_list_of_accounts.
"""

import unittest
import re
import src.config as config

test_data = (
    ("1011 Cr 4.5", ["1011",]),
    ("1011 4.5 Cr", ["1011",]),
    ("Cr 1011 4.5", ["1011",]),
    ("Cr 4.5 1011", ["1011",]),
    ("4.5 1011 Cr", ["1011",]),
    ("4.5 Cr 1011", ["1011",]),
    ("1011,1050,1260 Cr 4.5", ["1011", "1050", "1260"]),
    ("1011,1050,1260 4.5 Cr", ["1011", "1050", "1260"]),
    ("Cr 1011,1050,1260 4.5", ["1011", "1050", "1260"]),
    ("Cr 4.5 1011,1050,1260", ["1011", "1050", "1260"]),
    ("4.5 1011,1050,1260 Cr", ["1011", "1050", "1260"]),
    ("4.5 Cr 1011,1050,1260", ["1011", "1050", "1260"]),
    ("1011Cr 4.5", None),
    ("Cr1011 4.5", None),
    ("Cr 10114.5", None),
    ("Cr10114.5", None),
    ("4.5 Cr1011", None),
    )

class Config(unittest.TestCase):
    def setUp(self):
        pass
    def test_get_acnt(self):
        for source, expected in test_data:
            with self.subTest(source=source, expected=expected):
                self.assertEqual(
                    config.get_list_of_accounts(source),
                    expected)

if __name__ == "__main__":
    unittest.main()

    old = """
    no_match = []
    wrong = []
    success = []
    for source, should_be in test_data:
        result = config.get_list_of_accounts(source)
        if not result:
            no_match.append("{} => {}=={}"
                        .format(source, result, should_be))
        elif result == should_be:
            success.append("{} => {}".format(source, should_be))
        else:
            wrong.append("{} !=> {}".format(source, should_be))
    print("Successes:")
    print("\n".join(success))
    print("Failures:")
    print("\n".join(wrong))
    print("No Match:")
    print("\n".join(no_match))
"""
