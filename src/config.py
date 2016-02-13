#!../venv/bin/python
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

"""
If editing this file, beaware that the testing suite uses its own
version of config.py which differs only in the home directory specified.
REMEMBER TO INCLUDE ANY CHANGES MADE TO THE OTHER VERSION.
"""
VERSION = "0.0.1"

# LOGLEVEL = "DEBUG"
# LOGLEVEL = "INFO"
LOGLEVEL = "WARNING"
# LOGLEVEL = "ERROR"
# LOGLEVEL = "CRITICAL"

ACCOUNT_CATEGORIES = dict(
    ASSETS= '1000',
    LIABILITY= '2000',
    EQUITY= '3000',
    INCOME= '4000',
    EXPENSES= '5000',
    )

def account_category(code):
    for category in ACCOUNT_CATEGORIES:
        if ACCOUNT_CATEGORIES[category][:1]  == code[:1]:
            return category

ACCOUNT_CODE_LENGTH = len(ACCOUNT_CATEGORIES['ASSETS'])

DR_ACCOUNTS = {'ASSETS', 'EXPENSES'}
CR_ACCOUNTS = {'LIABILITY', 'EQUITY', 'INCOME'}
DR_FIRSTS = {ACCOUNT_CATEGORIES[item][:1] for item in DR_ACCOUNTS}
CR_FIRSTS = {ACCOUNT_CATEGORIES[item][:1] for item in CR_ACCOUNTS}

def valid_account_code(account_code):
    if (account_code
    and type(account_code) == str
    and len(account_code) == ACCOUNT_CODE_LENGTH):
        return True

MAXIMUM_VERBOSITY = 3
EPSILON = 0.01  # We want acuracy to the nearest $0.01.
INDENTATION_MULTIPLIER = 3  

N_ASSET_OWNERS = 8   # Specific to Kazan15
                     #Must jive with 'split' values in CofAs.

DEFAULTS = dict(
home = '/var/opt/debk.d',  # for production
# home = "/home/alex/Py/CSV/debk/tutor/debk.d",  # for testing

# Files expected to be in the home directory:
cofa_template = "defaultChartOfAccounts",     # A file name.
# A default chart of accounts.  Used if a 'suffixed file' is absent.
cofa_suffix = 'ChartOfAccounts',  # Suffix used if another prepopulated
#           chart of accounts file is to be used for a specific entity.
metadata_template = "defaultMetadata.json",   # A file name.
# A template used during entity creation.
entity = "defaultEntity",            # A file name.
# Keeps track of the last entity accessed (the default.)

cofa_name = 'CofA',              #| These three files will appear in
journal_name = 'Journal.json',   #| the .d directory of each entity
metadata_name = 'Metadata.json', #| copied at time of creation from
                                 #| templates in the home directory.
#     | Not so for the journal_name file- it is created, not copied.
verbosity = 3,
indent = '',
)  # End of DEFAULTS dictionary.



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
    print("DR_FIRSTS are {}".format(DR_FIRSTS))
    print("CR_FIRSTS are {}".format(CR_FIRSTS))

def main():
    test_firsts()

if __name__ == '__main__':
    main()

