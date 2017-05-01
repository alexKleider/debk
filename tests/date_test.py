#!/usr/bin/env python3

# File: tests/date_test.py

import src.date as date

testdata4check_date = (
    ("january 32", None),
    ("Feb30", None),
    ("Feb 30", None),
    ("dECEMBERl 32", None),
    ("fEBRUARY 28 13", "Feb 28, 2013"),
    ("december-31/16 ", "Dec 31, 2016"),
    ("Oct 20, 2014", "Oct 20, 2014"),
    ("Nov 2, 2015", "Nov 02, 2015"),
    ("June 23, 2015", "Jun 23, 2015"),
    ("March 8, 2016", "Mar 08, 2016"),
    ("March 9, 2016", "Mar 09, 2016"),
    ("Aug 17, 2015", "Aug 17, 2015"),
    ("Aug 20, 15", "Aug 20, 2015"),
    ("Aug 32, 2015", None),
    ("Sept 04, 2015", "Sep 04, 2015"),
    ("Sept 8, 15", "Sep 08, 2015"),
    ("March 0, 2015", None),
    ("May 10, 2015", "May 10, 2015"),
    ("April 14, 2015", "Apr 14, 2015"),
    ("June 31, 2015", None),
    ("May 20, 2015", "May 20, 2015"),
    ("July 4, 2015", "Jul 04, 2015"),
    ("August 3, 2015", "Aug 03, 2015"),
    ("Septe4, 2015", "Sep 04, 2015"),
    ("Sept14", "Sep 14, 2017"),
# The above will fail with each new year! Change 2017 to 2018 when the time comes.
    ("Sept 4, 2015", "Sep 04, 2015"),
    ("january31, 2015", "Jan 31, 2015"),
    ("january 31, 2015", "Jan 31, 2015"),
    ("january 32, 2015", None),
    ("january32, 2015", None),
    ("february28, 2015", "Feb 28, 2015"),
    ("february 0, 2015", None),
    ("March 0, 2015", None),
    ("March32, 2015", None),
    ("april31, 2015", None),
    ("april 31, 2015", None),
    ("april30, 2015", "Apr 30, 2015"),
    ("may32, 2015", None),
    ("may31, 2015", "May 31, 2015"),
    ("june 0, 2015", None),
    ("july 0, 2015", None),
    ("august32, 2015", None),
    ("september31, 2015", None),
    ("october32, 2015", None),
    ("november31, 2015", None),
    ("december32, 2015", None),
            )

class DateStamp(unittest.TestCase):
    """Test the check_date function of src/date.py."""
    def test_check_date(self):
        for input_string, result in testdata4check_date:
            with self.subTest(input_string=input_string,
                                    result=result):
                self.assertEqual(date.check_date(input_string),
                                    result)
