#!./venv/bin/python
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8 :
#
# file: 'src/config.py'

# Copyright 2015 Alex Kleider
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see
#   <http://www.gnu.org/licenses/>.
#   Look for file named COPYING.

"""
MODULE debk.src.config

Part of the Double Entry Book Keeping package.

Serves as a configuration file:
 1. Holds global configurable constants
    and values derived from them.
 2. Provides some functions having to do with globals:
        get_list_of_accounts(a_string)
        account_category(code)
        valid_account_code(account_code)
        check_date(entry)

Verbosity Levels Explained:
 0: Show all the accounts without any accounting data.
 1: Show accounts and their balances but only if there is a
    balance.
 2: Show accounts along with each contributing journal entry
    but only for accounts that have at least one journal entry.
 3: Show everything; that is to say, all the accounts, devoid of
    activity or not, along with all the relevant journal entries.

Clarification of account attributes, specifically type or category:
    The attribute 'type_' refers to the account's associated balance
    and can be only Debit or Credit. (It can not be 'place_holder'.)
    The 'acnt_type' attribute refers to whether it is a debit,
    credit (or 'place_holder') account.
    The accounts 'category' refers to asset, liability, equity,
    income or expense.
"""

import os
import re
import time

VERSION = "0.1.0-beta"

DEFAULT_VERBOSITY = 2
DEFAULT_USER = "Book Keeper"
DEFAULT_YEAR = time.localtime().tm_year
FISCAL_YEAR_BEGIN = "Jan 1, {}".format(DEFAULT_YEAR)
FISCAL_YEAR_END = "Dec 31, {}".format(DEFAULT_YEAR)

SHORT_MONTHS = {'Feb', 'Apr', 'Jun', 'Sep', 'Nov'}
MONTHS = (
    {'Jan', 'Mar', 'May', 'Jul', 'Aug', 'Oct', 'Dec'} | SHORT_MONTHS)

# If any changes are made to either of the next two constants,
# the file tests/money_test.sh will have to be edited to suit.
CURRENCY_SYMBOLS = {  # These will be used in a RegEx:
    "dollar": "[$]",  # Since the dollar sign must be escaped
    "pound": "[£]",   # all are being escaped (made into a 
    "euro": "[€]",    # character class, or a sequence there of)
    "yen": "[¥]",     # to make processing simpler.
    "rupee": "[₹]",   
    "Iceland krona": "[k][r]",
    }
DEFAULT_CURRENCY = "dollar"
DEFAULT_CURRENCY_SYMBOL = CURRENCY_SYMBOLS[DEFAULT_CURRENCY]

# LOGLEVEL = "DEBUG"
# LOGLEVEL = "INFO"
LOGLEVEL = "WARNING"
# LOGLEVEL = "ERROR"
# LOGLEVEL = "CRITICAL"

ACCOUNT_RANGE_INDICATOR = ':'  # Would probably make more sense
    # to  make this a '-' but want to test before changing.
CofA_HEADERS = ['code', 'indent', 'full_name', 'name', #{
                'hidden', 'place_holder', 'split']     #{not used?
N_COMPONENTS = len(CofA_HEADERS) -1                    #{
INCOME_TRANSFER2EQUITY_DESCRIPTOR = (
    "End of Period: Move net income into owner equity")

# Untested is the possibility of changing the length of account
# numbers.  If one does so, the following will have to be changed
# to maintain consistency.  This also will involve changing
# account numbers in the defaultChartOfAccounts.
# Even more importantly: much of the test suite will have to
# be modified- specifically the test data
ACCOUNT_NUMBER_LENGTH = 4
ACCOUNT_CATEGORIES = dict(
    ASSET='1000',     LAST_ASSET='1999',
    LIABILITY='2000', LAST_LIABILITY='2999',
    EQUITY='3000',    LAST_EQUITY='3999',
    INCOME='4000',    LAST_INCOME='4999',
    EXPENSE='5000',   LAST_EXPENSE='5999')
NET_INCOME_ACCOUNT = "4999"
EQUITY4INCOME_ACCOUNT = "3100"
# End of account length dependent constants.

BALANCE_SHEET_ACCOUNTS = {"ASSET", "LIABILITY", "EQUITY"}
INCOME_STATEMENT_ACCOUNTS = {"INCOME", "EXPENSE"}

INCOME_RANGE = "{}{}{}".format(ACCOUNT_CATEGORIES["INCOME"],
                               ACCOUNT_RANGE_INDICATOR,
                               ACCOUNT_CATEGORIES["LAST_INCOME"])
EXPENSE_RANGE = "{}{}{}".format(ACCOUNT_CATEGORIES["EXPENSE"],
                                ACCOUNT_RANGE_INDICATOR,
                                ACCOUNT_CATEGORIES["LAST_EXPENSE"])

DIGITS = r"[\d]" * ACCOUNT_NUMBER_LENGTH 
acnt_pattern = re.compile(r"""
\b  # beginning of a 'word'
{0:}  # requisite number of digits
(
,{0:} # ditto
)*  # 0 or more (comma separated) acnt numbers
\b  # end of a 'word'
""".format(DIGITS), re.VERBOSE)

debit_or_credit_pattern = re.compile(r"""
\b[DdCc]r\b
""", re.VERBOSE)

ACCOUNT_CODE_LENGTH = len(ACCOUNT_CATEGORIES['ASSET'])

DR_ACCOUNTS = {'ASSET', 'EXPENSE'}
CR_ACCOUNTS = {'LIABILITY', 'EQUITY', 'INCOME'}
DR_FIRSTS = {ACCOUNT_CATEGORIES[key][:1] for key in DR_ACCOUNTS}
CR_FIRSTS = {ACCOUNT_CATEGORIES[key][:1] for key in CR_ACCOUNTS}

EPSILON = 0.001  # We want acuracy to the nearest $0.001.
INDENTATION_MULTIPLIER = 3   # Might want to move this into DEFAULTS.

N_ASSET_OWNERS = 8   # Specific to Kazan15
                     # Must jive with 'split' values in CofAs.
                     # Will try to move this out of here and into a
                     # special use module.

DEFAULTS = dict(        # DEFAULTS, often imported "as D".  ####
    home=os.path.join(os.getcwd(), 'debk.d'), # home of data files
    # If changing the above, be sure permissions are set properly.
    # DEFAULTS["home"] is reset to './tests/debk.d' for tests.
    cofa_template="defaultChartOfAccounts",     # A file name.
    # A file by this name and consisting of a default chart of
    # accounts is expected to be in the "home" directory to be
    # used if there is no 'suffixed file'.
    cofa_suffix='ChartOfAccounts',  # Suffix used to indicate which
    # file to use rather than falling back on the default.
    last_entity="defaultEntity",            # A file name.
    # Keeps track of the last entity accessed (the default.)
    # May be empty or non existent (if there is no default set.)
    cofa_name='CofA',              #| These three files will appear
    metadata_name='Metadata.json', #| in the .d directory of each
    journal_name='Journal.json',   #| entity at the time of its
        # creation . The first one is copied from a template in the
        # home directory; the other two are created.
    currency=DEFAULT_CURRENCY,
    verbosity=DEFAULT_VERBOSITY,
    # Plan to make verbosity a bit map:
#   indentation='',
#   indentation_multiplier=3,

)   #### End of DEFAULTS dictionary.  ####


# The following is no longer necessary: code is written to accept
# these items in any order.
LineEntry_input_order = dict(account_code=0, #| Determines order in
                             _type=1,      #| which LineItem textual
                             amount=2)     #| input will be accepted.
# The above no longer need match the following prompt:
LineEntry_input_format = "{}Enter AccntNum cr/dr Amount: "
LineEntry_input_prompt = (
"an account number, D(ebit or or C(redit specifier, and n.n amount")

def get_list_of_accounts(a_string):
    """
    Uses regex to find valid account numbers (comma separated
    if more than one) in a_string.
    Returns a list of account numbers or None if none are found.
    "Validity" has to do with their consisting of the correct 
    number of digits; there is no guarantee that all returned
    accounts exist in the currently used chart of accounts.
    """
    ret = acnt_pattern.search(a_string)
    if ret:
        return ret.group().split(',')

def get_type(a_string):
    """
    Uses regex to determine if debit or credit entry.
    Returns None if unsuccessful.
    """
    ret = debit_or_credit_pattern.search(a_string)
    if ret:
        ret = ret.group()
        return ret.capitalize()

def account_category(code):
    """
    Depending on code provided, returns one of the following
    ASSETS, LIABILITY, EQUITY, INCOME, EXPENSE
    account categories.
    """
    for category in ACCOUNT_CATEGORIES:
        if ACCOUNT_CATEGORIES[category][:1] == code[:1]:
            return category

def valid_account_code(account_code):
    """
    Checks the validity of an account code:
    i.e. checks that has the correct number of digits.
    Note: it does NOT check that such an account exists.
    (Used only once: in src.debk.LineEntry.__init__().)
    """
    if (account_code
            and isinstance(account_code, str)
            and account_code.isdigit()
            and len(account_code) == ACCOUNT_CODE_LENGTH):
        return True

def test_firsts():
    """
    A testing function.
    """
    print("DR_FIRSTS are {}".format(sorted(list(DR_FIRSTS))))
    print("CR_FIRSTS are {}".format(sorted(list(CR_FIRSTS))))

def check_date(entry):
    """
    Checks that something reasonable was provided as a date.
    Expects Month, Day, Year format.
    Month and Day can be without any separator between them.
    Returns standard Month, Day, Year formated string
    or None if uninterpretable.
    """

    def day_of_month_out_of_range(day):
        """
        Checks that day is >=1 and <=31
        returning True if it's not.
        """
        return (day > 31) or (day < 1)

    def split_month_day(date):
        """
        Takes a string and tries to return a tuple of 2 strings:
        (<name of month>, <date>)
        """
        i = 0
        letters = []
        numbers = []
        while i < len(date):
            if date[i].isalpha():
                letters.append(date[i])
                i += 1
            else:
                break
        while i < len(date):
            if date[i].isdigit():
                numbers.append(date[i])
                i += 1
            else:
                break
        return [''.join(letters), ''.join(numbers)]

    parts = entry.translate(str.maketrans(',.-/-', '     ')).split()
#   print(parts)
    if parts and parts[0][:1].isalpha() and parts[0][-1:].isdigit():
        parts = split_month_day(parts[0]) + (parts[1:])
    if len(parts) == 2:
        parts.append(DEFAULT_YEAR)
#   print(parts)
    if (len(parts) != 3) or (not parts[0].isalpha()):
        return
    parts[0] = parts[0].capitalize()[:3]
#   print(parts)
    if not parts[0] in MONTHS:
#       print("{} not in MONTHS".format(parts[0]))
        return
    try:
        day = int(parts[1])
        year = int(parts[2])
    except ValueError:
#       print("day&year: {} {}".format(day, year))
        return
    if (day_of_month_out_of_range(day) or
            (day == 31 and parts[0] in SHORT_MONTHS) or
            (parts[0] == 'Feb' and day > 29)):
#       print("out of range")
        return
    if year < 100:
        year += 2000
#   print(parts)
    return "{} {:0>2d}, {}".format(parts[0], day, year)

def test_data(func, data):
    for datum, desired in data:
        res = func(datum)
        if res is None:
            res = "None"
        if ((func == get_list_of_accounts)
                and(res != "None")):
            desired = desired.split(',')
        if res == desired: ok = "OK"
        else: ok = "WRONG"
        print("{} {} => {}  SHOULD BE {}".format(
            ok, datum, res, desired))

if __name__ == '__main__':
    print("DEFAULT_YEAR is '{}'.".format(DEFAULT_YEAR))

    date_test_data = (
        ("no date here", "None"),
        ("July 3 1945", "Jul 03, 1945"),
        ("august 30", "Aug 30, 2017"),
    )

    account_test_data = (
        ("Dr 2010 360.9", "2010"),
        ("Dr 2010,2011,2012 360.34", "2010,2011,2012"),
        ("no account here", "None"),
    )

    type_test_data = (
        ("Dr 2010 360.9", "Dr"),
        ("2010 Dr 360.9", "Dr"),
        ("2010 360.9 Dr", "Dr"),
        ("cr 2010,2011,2012 360.34", "Cr"),
        ("2010,2011,2012 cr 360.34", "Cr"),
        ("2010,2011,2012 360.34 cr", "Cr"),
        ("no account here", "None"),
        ("no date here", "None"),
    )

    print("Testing date input:")
    test_data(check_date, date_test_data)

    print("Testing account input:")
    test_data(get_list_of_accounts, account_test_data)

    print("Testing type input:")
    test_data(get_type, type_test_data)


