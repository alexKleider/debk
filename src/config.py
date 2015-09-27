#!../venv/bin/python3
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

# LOGLEVEL = "DEBUG"
# LOGLEVEL = "INFO"
LOGLEVEL = "WARNING"
# LOGLEVEL = "ERROR"
# LOGLEVEL = "CRITICAL"

ACCOUNT_CLASSES = dict(
    ASSETS= '1000',
    LIABILITY= '2000',
    EQUITY= '3000',
    INCOME= '4000',
    EXPENSES= '5000',
    )

ACCOUNT_CODE_LENGTH = len(ACCOUNT_CLASSES[ASSETS])

DR_ACCOUNTS = {'ASSETS', 'EXPENSES'}
CR_ACCOUNTS = {'LIABILITY', 'EQUITY', 'INCOME'}
DR_FIRSTS = {ACCOUNT_CLASSES[item][:1] for item in DR_ACCOUNTS}
CR_FIRSTS = {ACCOUNT_CLASSES[item][:1] for item in CR_ACCOUNTS}

MAXIMUM_VERBOSITY = 3
EPSILON = 0.01  # We want acuracy to the nearest $0.01.
INDENTATION_MULTIPLIER = 3  

N_ASSET_OWNERS = 8   # Specific to Kazan15
                     #Must jive with 'split' values in CofAs.
DEFAULT_DIR = '/var/opt/debk.d'
# Each entity will have its home directory in DEFAULT_DIR.

# The following files are expected to be in the DEFAULT_DIR directory:
DEFAULT_CofA = "defaultChartOfAccounts"     # A file name.
# The default chart of accounts. (For now: place holders only.)
# A file of this name is kept in DEFAULT_DIR to serve as a template
# during entity creation although a different file can be used, see
# docstring for create_entity().
DEFAULT_Metadata = "defaultMetadata.json"   # A file name.
# A template used during entity creation.
DEFAULT_Entity = "defaultEntity"            # A file name.
# DEFAULT_Entity  - Keeps track of the last entity accessed.
# Its content serves as a default if an entity is required but
# not specified on the command line.

CofA_name = 'CofA'               #| These three files will appear
Journal_name = 'Journal.json'    #| in the home directory of
Metadata_name = 'Metadata.json'  #| each newly created entity.

def test_firsts():
    print("DR_FIRSTS are {}".format(DR_FIRSTS))
    print("CR_FIRSTS are {}".format(CR_FIRSTS))

def main():
    test_firsts()

if __name__ == '__main__':
    main()

