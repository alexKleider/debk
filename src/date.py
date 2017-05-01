#!./venv/bin/python

# file: 'src/date.py'

"""
This module provides:
    check_date(date_entry) which takes a string and
        attempts to return a string representing a date
        in the following format: "%b %d, %Y"
    date_object_from_entry(date_string): Takes a string
        representing a date in the "%b %d, %Y" format
        and returns a datetime.date instance.
        Returns None if the string is malformed.
"""

import re
import time
import datetime

try:
    import src.config as config
    DEFAULT_YEAR = config.DEFAULT_YEAR
    FISCAL_YEAR_BEGIN = config.FISCAL_YEAR_BEGIN 
    FISCAL_YEAR_END = config.FISCAL_YEAR_END 

    month_name_entry_format = config.month_name_entry_format 
    month_number_entry_format = config.month_number_entry_format 
    standard_display_format = config.standard_display_format 
except ImportError:
    DEFAULT_YEAR = time.localtime().tm_year
    FISCAL_YEAR_BEGIN = "Jan 1, {}".format(DEFAULT_YEAR)
    FISCAL_YEAR_END = "Dec 31, {}".format(DEFAULT_YEAR)

    month_name_entry_format = "%b %d, %Y"
    month_number_entry_format = "%m %d, %Y"
    standard_display_format = month_name_entry_format

three_letter_re = r"""[a-z,A-z]{3,3}?"""
three_letter_pattern = re.compile(three_letter_re)
number_re = r"""\d+"""
number_pattern = re.compile(number_re)


SHORT_MONTHS = {'Feb', 'Apr', 'Jun', 'Sep', 'Nov'}
MONTHS = (
    {'Jan', 'Mar', 'May', 'Jul', 'Aug', 'Oct', 'Dec'} | SHORT_MONTHS)

def check_date(date_entry):
    """
    Checks that something reasonable was provided as a date.
    Expects Month, Day, Year format.
    Month and Day can be without any separator between them.
    Returns standard Month, Day, Year (Mmm dd, yyy) formated
    string or None if uninterpretable.
    """
#   print("Checking '{}'...".format(date_entry))
    dt = None
    numbers = number_pattern.findall(date_entry)
#   print("\tgot {} numbers".format(numbers))
    res = three_letter_pattern.search(date_entry)
    if res:
        pass
#       print("\tgot month pattern: {}".format(res.group()))
    else:
#       print("\tgot no month pattern")
        pass
    if res and len(numbers) == 2:
        month = res.group().capitalize()
        day = int(numbers[0])
        year = int(numbers[1])
        if year < 100: year += 2000
        try:
            dt = datetime.datetime.strptime(
                "{} {:02}, {}".format(month, day, year),
                month_name_entry_format)
        except ValueError:
#           print("\tValueError with {}".format(date_entry))
            return
    elif res and len(numbers) == 1:
        month = res.group().capitalize()
        day = int(numbers[0])
        year = DEFAULT_YEAR
        try:
            dt = datetime.datetime.strptime(
                "{} {:02}, {}".format(month, day, year),
                month_name_entry_format)
        except ValueError:
#           print("\tValueError with {}".format(date_entry))
            return
    elif len(numbers) == 3:
        month = int(numbers[0])
        day = int(numbers[1])
        year = int(numbers[2])
        if year < 100: year += 2000
        try:
            dt = datetime.datetime.strptime(
                "{} {:02}, {}".format(month, day, year),
                month_number_entry_format)
        except ValueError:
#           print("\tValueError with {}".format(date_entry))
            return
    if dt:
#       print("\tReturning {}"
#           .format(dt.strftime(month_name_entry_format)))
        return dt.strftime(month_name_entry_format)

def date_object_from_entry(date_string):
    """
    Takes a string representing a date in the "%b %d, %Y"
    format and returns a datetime.date instance.
    Returns None if the string is malformed.
    """
    try:
        dt = datetime.datetime.strptime(
            date_string, month_name_entry_format)
    except ValueError:
        return
    return datetime.date(dt.year, dt.month, dt.day)

def string_from_date_object(date_object):
    """
    Takes a datetime.date object and returns a string
    representing a date in the "%b %d, %Y" format.
    Returns None if date_object is not a datetime.date.
    """
    if not isinstance(date_object, datetime.date):
        return
    return date_object.strftime(month_name_entry_format)

if __name__ == "__main__":
#   numbers = number_pattern.findall("66 88")
#   if numbers:
#       print("T: {}".format(numbers))
#   else:
#       print("T: No numbers")
#   month = three_letter_pattern.search(" 66 hello 20")
#   if month:
#       print("T: month returned {}".format(month.group()))
#   else:
#       print("T: mo month returned")

    import unittest
    
    testdata4check_date = (
        ("Sept14", "Sep 14, 2017"),
#       ("2 4 1918", "Feb 04, 1918"),
#       ("2 30 1918", None),
#       ("2Feb17", "Feb 02, 2017"),
#       ("2nomonth17", None),
    )

    testdata4string_from_date_object = (
        (datetime.date(1918, 2, 4), "Feb 04, 1918"),
        (datetime.date(2017, 2, 2), "Feb 02, 2017"),
        ("Wrong type!", None),
    )

    class Dates(unittest.TestCase):
        def setUp(self):
            pass
        def test_check_date(self):
            for entry, expected in testdata4check_date:
                with self.subTest(entry=entry, expected=expected):
                    self.assertEqual(
                        check_date(entry),
                        expected)
        def test_date_object_from_entry(self):
            self.assertEqual(
                date_object_from_entry("Feb 28, 2013"),
                datetime.date(2013, 2, 28))
        def test_string_from_date_object(self):
            for entry, expected in testdata4string_from_date_object:
                with self.subTest(entry=entry, expected=expected):
                    self.assertEqual(
                        string_from_date_object(entry),
                        expected)

    unittest.main()

    stamp = "%Y%m%d-%H:%M"
    now = datetime.datetime.now()
    time_stamp = now.strftime(stamp)
    print("{:<30}{}".format("My time stamp is:",time_stamp))
    d = datetime.datetime.strptime(time_stamp, stamp)
    print("{:<30}{}".format("The derived date object:", d))
    s = d.strftime(stamp)
    print("{:<30}{}".format("Time stamp from derived:", s))
    print("""a shortened version of
    {} should be
    {}""".format(now, d))
    print("config.check_date returns 'Feb 28, 2013'")

    notes = """
The following table demonstrates all of the formatting codes for
5:00PM January 13, 2016 in the US/Eastern time zone.
strptime/strftime format codes Symbol   Meaning     Example
%a  Abbreviated weekday name    'Wed'
%A  Full weekday name   'Wednesday'
%w  Weekday number – 0 (Sunday) through 6 (Saturday)    '3'
%d  Day of the month (zero padded)  '13'
%b  Abbreviated month name  'Jan'
%B  Full month name     'January'
%m  Month of the year   '01'
%y  Year without century    '16'
%Y  Year with century   '2016'
%H  Hour from 24-hour clock     '17'
%I  Hour from 12-hour clock     '05'
%p  AM/PM   'PM'
%M  Minutes     '00'
%S  Seconds     '00'
%f  Microseconds    '000000'
%z  UTC offset for time zone-aware objects  '-0500'
%Z  Time Zone name  'EST'
%j  Day of the year     '013'
%W  Week of the year    '02'
%c  Date and time representation for the current locale     'Wed Jan
%13 17:00:00 2016'
%x  Date representation for the current locale  '01/13/16'
%X  Time representation for the current locale  '17:00:00'
%%  A literal % character   '%'
"""

