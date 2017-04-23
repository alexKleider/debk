#!/usr/bin/env python3
# File: drcr.py
"""
Provides drcr(a_string)
that returns either 'Dr' or 'Cr' or None,
depending on whether a debit or a credit is detected.
To return 'Dr', 'Dr' be at the end of the string
or surounded by at least one space.  Same for 'Cr'.
If neither of the above, None is returned.
"""

import re

drcr_esperimental_re = (r"""
(^[DC]r\s)
|
(\s[DC]r\s)
|
(\s[DC]r$)
|
([\d.][DC]r$)
|
([\d.][DC]r\s)
""")

drcr_re = (r"""
((?:^)[DC]r(?:\s))
|
((?:\s)[DC]r(?:\s))
|
((?:\s)[DC]r$)
|
((?:[\d.])[DC]r$)
|
((?:[\d.])[DC]r(?:\s))
""")

specific_re = (r"[DC]r")

catch_all_pattern = re.compile(drcr_re, re.VERBOSE)
specific_pattern = re.compile(specific_re)

def drcr(a_string):
    """
    Returns either 'Dr' or 'Cr' or None,
    depending on whether a debit or a credit is detected.
    To return 'Dr', 'Dr' be at the end of the string
    or surounded by at least one space.  Same for 'Cr'.
    If neither of the above, None is returned.
    """
    response = catch_all_pattern.search(a_string)
    if response:
        response = specific_pattern.search(response.group())
        if response:
            return response.group()

test_material = (
    ("Dr 1111 5000.00", 'Dr'),
    ("Dr 1111 5000.00", 'Dr'),
    ("3100 5000.00 Cr", 'Cr'),
    ("3100 5000.00Cr", 'Cr'),
    ("3100 5000.0Cr", 'Cr'),
    ("3100 5000.Cr", 'Cr'),
    ("3100 5000Cr", 'Cr'),
    ("1111 Cr 5000.00", 'Cr'),
    ("1511 Dr 5000.00", 'Dr'),
    ("no dr or cr found", None),
    )

if __name__ == "__main__":
    for source in test_material:
#       print("{}".format(drcr(source)))
        res = drcr(source[0])
        if res ==source[1]: report = "OK: "
        else: report = "WRONG: "
        print("{}{:>18} > '{}' Expected: {}"
            .format(report, source[0], res, source[1]))

