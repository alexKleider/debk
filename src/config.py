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

import os

VERSION = "0.0.2"

# LOGLEVEL = "DEBUG"
# LOGLEVEL = "INFO"
LOGLEVEL = "WARNING"
# LOGLEVEL = "ERROR"
# LOGLEVEL = "CRITICAL"

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

MAXIMUM_VERBOSITY = 3
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
    verbosity = 3,
    # Plan to make verbosity a bit map:
    #   Names only
    #   Names and totals only
    #   Names, journal entries (brief), and totals.
    #   Names, journal entries with descriptions, and totals.
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

def main():
    test_firsts()

if __name__ == '__main__':
    main()

