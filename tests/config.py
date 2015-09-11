#!../venv/bin/python3
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8 :
#
# file: '../config.py'
# Part of testing suite regarding
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
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#   Look for file named COPYING.

"""
This version of config.py is specific for the testing suite.
It specifies a home directory that is under the tests directory
(rather than the default which is under /var/opt/.)
It lives under the tests directory along with the ./debk.d that
it specifies.  This ./debk.d directory includes the same default
files as well as a testentityChartOfAccounts file.
"""

# LOGLEVEL = "DEBUG"
# LOGLEVEL = "INFO"
LOGLEVEL = "WARNING"
# LOGLEVEL = "ERROR"
# LOGLEVEL = "CRITICAL"

MAXIMUM_VERBOSITY = 3
EPSILON = 0.01  # We want acuracy to the nearest $0.01.
INDENTATION_MULTIPLIER = 3  

N_ASSET_OWNERS = 8   # Specific to Kazan15
                     #Must jive with 'split' values in CofAs.
DEFAULT_DIR = './tests/debk.d'
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
