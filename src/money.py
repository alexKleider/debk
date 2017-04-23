#!./venv/bin/python3

# File: tmoney.py

import re
import src.config as config

wo_symbol_re = r"""
[-]?
(?P<d1>[0-9]*)
[.]  # If no currency symbol, must have a decimal point.
(?P<c1>[0-9]{0,2})?
[.]?  # Want to know if there is a second_decimal!
"""

before_symbol_re = r"""
[-]?
{}
[-]?
(?P<d1>\d+)
([.](?P<c1>\d{{0,2}}))?
[.]?
"""

with_symbol = before_symbol_re.format(
    config.DEFAULT_CURRENCY_SYMBOL)

pat_w_symbol = re.compile(with_symbol, re.VERBOSE)
pat_wo_symbol = re.compile(wo_symbol_re, re.VERBOSE)

def get_currency_value(string,
                    pat_w_symbol=pat_w_symbol,
                    debug=False):
    """
    Uses regex to find a currency value within the string.
    Depends on the expressions precompiled in this module.
    Those expressions in turn depend on the currency symbol
    set in src.config.DEFAULT_CURRENCY_SYMBOL
    Returns a float if successful, None if not.
    """
    value = cents = ''
    negative = False
    res = pat_w_symbol.search(string)
    if not res:
        if debug: print("failed w symbol")
        res = pat_wo_symbol.search(string)
    if res:
        match = res.group()
        if debug:
            print("got a match: {}".format(match))
        if match.count('.') > 1:
            if debug:
                print("failing: >1 decimal")
            return
        if match.count("-"):
            if debug:
                print("negative sign found")
            negative = True
        value = res.group("d1")
        if debug: print("value is {}".format(value))
        if not value:
            if debug:
                print("no dollar value. => '0'")
            value = "0"
        value = float(value)
        cents = res.group("c1")
        if debug: print("cents is {}".format(cents))
        if not cents:
            if debug: print("no cents. => '0'")
            cents = "0"
        if len(cents) == 1: cents += "0"
        cents = float(cents)
        if debug: print("final cents: {}".format(cents))
        value += cents / 100
        if negative: value = -value
        if value != 0:
            return value

data2test = (
    ("nothing here", "None"),
    ("-45", "None"),
    ("45", "None"),
    ("cost is -45", "None"),
    ("-45 is the price", "None"),

    ("-45.", "-45.00"),
    ("45.", "45.00"),
    ("cost is -45.", "-45.00"),
    ("-45. is the price", "-45.00"),

    ("-45.2", "-45.20"),
    ("45.2", "45.20"),
    ("cost is -45.2", "-45.20"),
    ("cost is 45.2", "45.20"),
    ("-45.2 is the price", "-45.20"),
    ("45.2 is the price", "45.20"),

    ("-45.33", "-45.33"),
    ("45.33", "45.33"),
    ("cost is -45.33", "-45.33"),
    ("-45.33 is the price", "-45.33"),
    ("cost is 45.33", "45.33"),
    ("45.33 is the price", "45.33"),

    ("-45.33.", "None"),
    ("45.33.2", "None"),
    ("cost is -45.33.78", "None"),
    ("-45.33. is the price", "None"),
    ("cost is 45.33.2", "None"),
    ("45.33.2 is the price", "None"),

    ("nothing here", "None"),
    ("-$45", "-45.00"),
    ("$-45", "-45.00"),
    ("cost is -45", "None"),
    ("$-45 is the price", "-45.00"),

    ("-$45.", "-45.00"),
    ("$-45.", "-45.00"),
    ("cost is -$45.", "-45.00"),
    ("$-45. is the price", "-45.00"),

    ("-$45.2", "-45.20"),
    ("$-45.2", "-45.20"),
    ("cost is -$45.2", "-45.20"),
    ("$-45.2 is the price", "-45.20"),

    ("-$45.33", "-45.33"),
    ("$-45.33", "-45.33"),
    ("cost is -$45.33", "-45.33"),
    ("$-45.33 is the price", "-45.33"),

    ("-$45.33.", "None"),
    ("$-45.33.9", "None"),
    ("cost is -$45.33.99", "None"),
    ("$-45.33.99 is the price", "None"),

      ("Dr 1111 5000.00", '5000.00'),
      ("Dr 1111 5000.00", '5000.00'),
      ("3100 5000.00 Cr", '5000.00'),
       ("3100 5000.00Cr", '5000.00'),
        ("3100 5000.0Cr", '5000.00'),
         ("3100 5000.Cr", '5000.00'),
          ("3100 5000Cr", "None"),
      ("1111 Cr 5000.00", '5000.00'),
      ("1511 Dr 5000.00", '5000.00'),
    ("no dr or cr found", "None"),

)

def test_data(list_of_2_tuples,
            symbol=config.DEFAULT_CURRENCY_SYMBOL,
            debug=False):
#           debug=True):
    """
    Each of the (2) tuples in the first paramter consists of a
    string which when passed to the get_currency function should
    result it its returning the second component of the tuple.
    Returned is a (3) tuple each component of which is a list:
    The first of these lists represents successes, the second 
    represents failures in that there was a match but the returned
    value was not that specified, and the third lists the cases
    where there was no match.
    """
    successes = []
    wrong_match = []
    no_match = []
    for subject, expected in list_of_2_tuples:
        res = get_currency_value(subject,
                                debug=False)
#                               debug=True)
        if res:
            if "{:.2f}".format(res) == expected:
                successes.append("{:>32}  {:.2f}  {}"
                                   .format(subject, res, expected))
            else:
                wrong_match.append("{:>32}  {:.2f}  {}"
                                   .format(subject, res, expected))
        else:
            no_match.append("{:>32} => no match - expect {}"
                                        .format(subject, expected))
    return (successes, wrong_match, no_match)

def populate(successes, wrong_match, no_match, res):
    """
    Assumes that res is a (3) tuple as returned by test_data.
    The three lists of res are appended to the first three params
    as appropriate.
    """
    successes.extend(res[0])
    wrong_match.extend(res[1])
    no_match.extend(res[2])

def test_foreign_currencies(dict_of_lists):
    successes = []
    wrong_match = []
    no_match = []
    for key in config.CURRENCY_SYMBOLS.keys():
        data = dict_of_lists[key]
        res = test_data(data)
        populate(successes, wrong_match, no_match, res)
    return (successes, wrong_match, no_match)

def display(successes, wrong_match, no_match):
    print("Successes:")
    print("\n".join(successes))
    print("Matched but wrong:")
    print("\n".join(wrong_match))
    print("No match:")
    print("\n".join(no_match))

if __name__ == "__main__":
#   test(after_symbol, test_data_with_sign)
#   test(wo_symbol_re, test_data_without_sign)

    double_symbol=config.CURRENCY_SYMBOLS["Iceland krona"]

    successes = []
    wrong_match = []
    no_match = []

    populate(successes, wrong_match, no_match,
            test_data(data2test,
#                   config.CURRENCY_SYMBOLS["Iceland krona"],
#                   debug = True))
                    debug = False))

    display(successes, wrong_match, no_match)

