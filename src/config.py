#!./venv/bin/python
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8 :
#
# file: 'src/config.py'
# Part of debk module.
# 'debk.py', Double Entry Book Keeping module.

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

verbosity_levels_explained = """
0: Show all the accounts without any accounting data.
1: Show accounts and their balances but only if there is a balance.
2: Show accounts along with each contributing journal entry
but only for accounts that have at least one journal entry.
3: Show everything; that is to say, all the accounts, devoid of
activity or not, along with all the relevant journal entries..
"""

VERSION = "0.0.2"

import os
import time

DEFAULT_YEAR = time.localtime().tm_year
Short_Months = {'Feb', 'Apr', 'Jun', 'Sep', 'Nov'}
Months = (
{'Jan', 'Mar', 'May', 'Jul', 'Aug', 'Oct', 'Dec'} | Short_Months)

DEFAULT_CURRENCY = 'dollar'
currency_signs = {
    "dollar": "\u0024",
    "pound": "\u00a3",
    "yuan": "\u00a5",
    "yen": "\u00a5",
    "euro": "\u20ac",
    }
DEFAULT_CURRENCY_SIGN = currency_signs[DEFAULT_CURRENCY]
def assign_money_regex(currency_sign=DEFAULT_CURRENCY):
    if currency_sign == 'dollar':
        return r"\${0,1}\d{0,}\.\d{0,2}"
    else:
        return (
            "(?:{})".format(currency_signs[currency_sign]) +
                r"{0,1}\d{0,}\.\d{0,2}")
MONEY_REGEX = assign_money_regex()

# LOGLEVEL = "DEBUG"
# LOGLEVEL = "INFO"
LOGLEVEL = "WARNING"
# LOGLEVEL = "ERROR"
# LOGLEVEL = "CRITICAL"
DEFAULT_CURRENCY_SIGN = '$'
CofA_HEADERS = ['code', 'indent', 'full_name', 'name',
                    'hidden', 'place_holder', 'split']
N_COMPONENTS = len(CofA_HEADERS) -1

ACCOUNT_CATEGORIES = dict(
    ASSET= '1000',
    LIABILITY= '2000',
    EQUITY= '3000',
    INCOME= '4000',
    EXPENSE= '5000',
    )

def account_category(code):
    """
    Depending on code provided, returns one of the following
    ASSETS, LIABILITY, EQUITY, INCOME, EXPENSE
    ACCOUNT_CATEGORIES.
    """
    for category in ACCOUNT_CATEGORIES:
        if ACCOUNT_CATEGORIES[category][:1]  == code[:1]:
            return category

ACCOUNT_CODE_LENGTH = len(ACCOUNT_CATEGORIES['ASSET'])

DR_ACCOUNTS = {'ASSET', 'EXPENSE'}
CR_ACCOUNTS = {'LIABILITY', 'EQUITY', 'INCOME'}
DR_FIRSTS = {ACCOUNT_CATEGORIES[item][:1] for item in DR_ACCOUNTS}
CR_FIRSTS = {ACCOUNT_CATEGORIES[item][:1] for item in CR_ACCOUNTS}

def valid_account_code(account_code):
    if (account_code
    and type(account_code) == str
    and len(account_code) == ACCOUNT_CODE_LENGTH):
        return True

DEFAULT_VERBOSITY = 2
EPSILON = 0.001  # We want acuracy to the nearest $0.001.
INDENTATION_MULTIPLIER = 3   # Might want to move this into DEFAULTS.

N_ASSET_OWNERS = 8   # Specific to Kazan15
                     # Must jive with 'split' values in CofAs.
                     # Will try to move this out of here and into a
                     # special use module.

DEFAULTS = dict(        # DEFAULTS, often imported "as D".  ####
    home = os.path.expanduser('~/debk/debk.d'),
    # If changing the above, be sure permissions are set properly.
    # DEFAULTS["home"] is reset to './tests/debk.d' for tests.

    cofa_template = "defaultChartOfAccounts",     # A file name.
    # A file by this name and consisting of a default chart of
    # accounts is expected to be in the "home" directory to be
    # used if there is no 'suffixed file'.
    cofa_suffix = 'ChartOfAccounts',  # Suffix used to indicate which
    # file to use rather than falling back on the default.
    last_entity = "defaultEntity",            # A file name.
    # Keeps track of the last entity accessed (the default.)
    # May be empty or non existent (until file if there is no default set.

    cofa_name = 'CofA',              #| These three files will appear
    metadata_name = 'Metadata.json', #| in the .d directory of each
    journal_name = 'Journal.json',   #| entity at the time of its
        # creation . The first one is copied from a template in the
        # home directory; the other two are created.
    verbosity = DEFAULT_VERBOSITY,
    # Plan to make verbosity a bit map:
#   indentation = '',
#   indentation_multiplier = 3,

)   #### End of DEFAULTS dictionary.  ####


# The following is no longer necessary: code is written to accept
# these items in any order.
LineEntry_input_order = dict(account_code= 0, #| Determines order in
                            _type= 1,      #| which LineItem textual
                            amount= 2)     #| input will be accepted.
# The above no longer need match the following prompt:
LineEntry_input_format = "{}Enter AccntNum cr/dr Amount: "
LineEntry_input_prompt = (
"an account number, D(ebit or or C(redit specifier, and n.n amount")
                            
def valid_account_code_length(account_code):
    """
    Checks the validity of an account code:
    i.e. checks that has the correct number of digits.
    Note: it does NOT check that such an account exists.
    """
    if (len(account_code) == ACCOUNT_CODE_LENGTH 
    and account_code.isdigit()):
        return True

def test_firsts():
    print("DR_FIRSTS are {}".format(sorted(list(DR_FIRSTS))))
    print("CR_FIRSTS are {}".format(sorted(list(CR_FIRSTS))))

def split_month_day(date):
    i = 0
    letters = []
    numbers = []
    while i<len(date):
        if date[i].isalpha():
            letters.append(date[i])
            i+=1
        else:
            break
    while i<len(date):
        if date[i].isdigit():
            numbers.append(date[i])
            i+=1
        else:
            break
    return [''.join(letters), ''.join(numbers)]

def check_date(entry):
    """
    Checks that something reasonable was provided as a date.
    Expects Month, Day, Year format.
    Month and Day can be without any separator between them.
    Returns standard Month, Day, Year formated string
    or None if uninterpretable.
    """
    parts = entry.translate(str.maketrans(',.-/-','     ')).split()
    if parts and parts[0][:1].isalpha() and parts[0][-1:].isdigit():
        parts = split_month_day(parts[0]) + (parts[1:])
    if len(parts) == 2:
        parts.append(DEFAULT_YEAR)
    if (len(parts) != 3) or (not parts[0].isalpha()):
        return
    parts[0] = parts[0].capitalize()[:3]
    if not parts[0] in Months:
        return
    try:
        day = int(parts[1])
        year = int(parts[2])
    except ValueError:
        return
    if ( (day > 31) or (day < 1) or
         (day == 31 and parts[0] in Short_Months) or
         ( parts[0] == 'Feb' and day > 29)):
        return
    if year < 100:
        year += 2000
    return "{} {:0>2d}, {}".format(parts[0], day, year)

def normalizeValue(val):
    """
    Provides for parens as an alternative to minus
    and eliminates currency sign if present.
    If both are used, the currency sign is expected
    to be with in the parens.
    """
    if amt.startswith('(') and amt.endswith(')'):
       amt = '-' + amt[1:-1]
    return amt.replace(DEFAULT_CURRENCY_SIGN,'')

if __name__ == '__main__':
    print("DEFAULT_YEAR is '{}'.".format(DEFAULT_YEAR))
    while True:
        print("Type 'end' to end date testing.")
        date = input("Date: ")
        if date == "end":
            break
        date = check_date(date)
        if date:
            print("Valid date: '{}'.".format(date))
        else:
            print("Invalid date.")

