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
# Note: The date formats in the previous two lines must
# match that provided by <standard_display_format> 3 lines down.
month_name_entry_format = "%b %d, %Y"
month_number_entry_format = "%m %d, %Y"
standard_display_format = month_name_entry_format

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
# be modified- for this reason, we are in the process of
# putting all of the test data at the end of this file.

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
            and 0 < int(account_code[:1]) < 6
            and len(account_code) == ACCOUNT_CODE_LENGTH):
        return True

def account_category(code):
    """
    Depending on code provided, returns one of the following
    "ASSET", "LIABILITY", "EQUITY", "INCOME", "EXPENSE"
    account categories.
    Returns None if not a valid code!
    """
    if not valid_account_code(code):
        return
    for category in ACCOUNT_CATEGORIES:
        if ((not category.startswith("LAST")) and
            (ACCOUNT_CATEGORIES[category][:1] == code[:1])):
            return category

    # The following are used by the tests in tests/config_test.py
    # and will have to be modified if the account numbering system
    # is changed.

test_data4get_list_of_accounts = (
    ("no account here", None),
    ("1011 Cr 4.5", ["1011",]),
    ("1011 4.5 Cr", ["1011",]),
    ("Cr 1011 4.5", ["1011",]),
    ("Cr 4.5 1011", ["1011",]),
    ("4.5 1011 Cr", ["1011",]),
    ("4.5 Cr 1011", ["1011",]),
    ("Dr 2010 360.9", ["2010"]),
    ("Dr 2010,2011,2012 360.34", ["2010", "2011", "2012"]),
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

test_data4get_type = (# The account codes here don't matter.
    ("Dr 2010 360.9", "Dr"),
    ("2010 Dr 360.9", "Dr"),
    ("2010 360.9 Dr", "Dr"),
    ("cr 2010,2011,2012 360.34", "Cr"),
    ("2010,2011,2012 cr 360.34", "Cr"),
    ("2010,2011,2012 360.34 cr", "Cr"),
    ("no account here", None),
    ("no date here", None),
)

test_data4account_category = (
    ("1010", "ASSET"),
    ("1000", "ASSET"),
    ("1100", "ASSET"),
    ("1110", "ASSET"),
    ("1500", "ASSET"),
    ("1511", "ASSET"),
    ("1512", "ASSET"),
    ("1513", "ASSET"),
    ("1514", "ASSET"),
    ("2000", "LIABILITY"),
    ("2001", "LIABILITY"),
    ("2002", "LIABILITY"),
    ("2003", "LIABILITY"),
    ("2004", "LIABILITY"),
    ("2005", "LIABILITY"),
    ("2006", "LIABILITY"),
    ("2007", "LIABILITY"),
    ("2008", "LIABILITY"),
    ("2009", "LIABILITY"),
    ("2010", "LIABILITY"),
    ("3000", "EQUITY"),
    ("3001", "EQUITY"),
    ("3002", "EQUITY"),
    ("3003", "EQUITY"),
    ("3004", "EQUITY"),
    ("3005", "EQUITY"),
    ("3006", "EQUITY"),
    ("3007", "EQUITY"),
    ("3008", "EQUITY"),
    ("3009", "EQUITY"),
    ("3010", "EQUITY"),
    ("4000", "INCOME"),
    ("4001", "INCOME"),
    ("5000", "EXPENSE"),
    ("5001", "EXPENSE"),
    ("5002", "EXPENSE"),
    ("5020", "EXPENSE"),
    ("5021", "EXPENSE"),
    ("5030", "EXPENSE"),
    ("5031", "EXPENSE"),
    ("5041", "EXPENSE"),
    ("5051", "EXPENSE"),
    ("5310", "EXPENSE"),
    ("5320", "EXPENSE"),
    ("5400", "EXPENSE"),
    ("5401", "EXPENSE"),
    ("5500", "EXPENSE"),
    ("5501", "EXPENSE"),
    ("5502", "EXPENSE"),
)

test_data4valid_account_code = (
    ("1010", True),
    ("1000", True),
    ("1010", True),
    ("1000", True),
    ("1100", True),
    ("1110", True),
    ("1500", True),
    ("1511", True),
    ("1512", True),
    ("1513", True),
    ("1514", True),
    ("2000", True),
    ("2001", True),
    ("2002", True),
    ("2003", True),
    ("2004", True),
    ("2005", True),
    ("2006", True),
    ("2007", True),
    ("2008", True),
    ("2009", True),
    ("2010", True),
    ("3000", True),
    ("3001", True),
    ("3002", True),
    ("3003", True),
    ("3004", True),
    ("3005", True),
    ("3006", True),
    ("3007", True),
    ("3008", True),
    ("3009", True),
    ("3010", True),
    ("4000", True),
    ("4001", True),
    ("5000", True),
    ("5001", True),
    ("5002", True),
    ("5020", True),
    ("5021", True),
    ("5030", True),
    ("5031", True),
    ("5041", True),
    ("5051", True),
    ("5310", True),
    ("5320", True),
    ("5400", True),
    ("5401", True),
    ("5500", True),
    ("5501", True),
    ("5502", True),
)
