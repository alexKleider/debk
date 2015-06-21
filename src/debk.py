#!./venv/bin/python3
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8 :
#
# file: 'debk.py'
# Part of ___, ____.

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
debk.py is a module that supports double entry book keeping.

Usage:
  debk.py -h | --version
  debk.py ( new | show_accounts | show_journal )  --entity=ENTITY

Options:
  -h --help  Print usage statement.
  --version  Print version.
  --entity=ENTITY  Specify entity.

Commands:
  new creates a new set of books.
  show_accounts displays the chart of accounts.
  show_journal displays the journal entries.
"""
#
# hash-bang line
# encoding cookie
# licence
# doc string explaining what the module does
# from __future__ imports
# import standard library modules
import os
import sys
import shutil
import json
import csv

# import custom modules
import docopt

# metadata such as version number
VERSION = "0.0.0"

# other constants
DEFAULT_HOME = '/var/opt/debk.d'
ENTITIES = dict(
            kazan15 = 'Kazan15',
            testEntity = 'TestEntity',
            )
DEFAULT_CofA = "defaultChartOfAccounts"
DEFAULT_Metadata = "defaultMetadata.json"
# Expect there to be DEFAULT_CofA and DEFAULT_Metadata
# files in DEFAULT_HOME.
CofA_name = 'CofA'               # These three files will appear
Journal_name = 'Journal.json'         # in the home directory
Metadata_name = 'Metadata.json'  # of each entity.

# Each entity will have its home directory in debk.d.

# global variables
# custom exception types
# private functions and classes
# public functions and classes
# main function

def create_entity(entity_name):
    """
    Establishes a new accounting system.

    Creates a new dirctory <entity_name> within DEFAULT_HOME.
    and populates it with a default start up chart of accounts.
    An attempt will be made to find a file name that is the 
    concatenation of the entity name and 'ChartOfAccounts'.
    If not found, the 'defaultChartOfAccounts' will be used.
    Reports error if:
        1. <entity_name> already exists, or
        2. not able to write to new directory.
    Also sets up an empty journal file. (contains only '{}'.)
    Returns <entity_name> if no errors are recognized.
    """
    cofa_source = os.path.join(
                DEFAULT_HOME,
                entity_name + 'ChartOfAccounts')
    if not os.path.isfile(cofa_source):
        cofa_source = os.path.join(DEFAULT_HOME, DEFAULT_CofA)
    new_dir = os.path.join(DEFAULT_HOME, entity_name)
    new_CofA = os.path.join(new_dir, CofA_name)
    new_Journal = os.path.join(new_dir, Journal_name)
    meta_source = os.path.join(DEFAULT_HOME, DEFAULT_Metadata)
    meta_dest = os.path.join(new_dir, Metadata_name)
    with open(meta_source, 'r') as json_file:
        metadata = json.load(json_file)
    metadata['entity_name'] = entity_name
    try:
        os.mkdir(new_dir)
        shutil.copy(cofa_source, new_CofA)
        with open(new_Journal, 'w') as journal_file_object:
            journal_file_object.write('{}')
        with open(meta_dest, 'w') as json_file:
            json.dump(metadata, json_file)
    except FileExistsError:
        print("ERROR: Directory '{}' already exists"
                            .format(entity_name))
    except OSError:
        print("ERROR: Destination '{}' &/or '{}' may not be writeable."
                            .format(new_CofA, new_Journal))
    else:
        return entity_name

class ChartOfAccounts(object):
    """
    A class to manage an entity's chart of accounts.
    Instantiation loads such a chart from a file.
    Methods are planned to show the accounts in various way.
    I expect that there'll be a method to create journal entries 
    and have them posted to the relevant accounts.
    """

    def __init__(self, entity_name):
        """
        Loads the chart of accounts belonging to a specified entity.
        """
        self.entity = entity_name
        self.home = os.path.join(DEFAULT_HOME, entity_name)
        self.cofa_file = os.path.join(self.home, CofA_name)
        self.cofa_dict = {}  # Keyed by account number ('code'.)
        self.code_set = set()
        with open(self.cofa_file, 'r') as cofa_file_object:
            reader = csv.DictReader(cofa_file_object)
            for row in reader:
#               print(row)
                if row['code'] in self.code_set:
                    print("Error Condition: Duplicate account code.")
                    print("Fix before rerunning the script.")
                    sys.exit()
                self.code_set.add(row['code'])
                self.cofa_dict[row['code']] = row

    def show(self):
        """
        """
        acnt_codes = sorted(self.cofa_dict)
#       print(acnt_codes)
        ret = ['{} Chart of Accounts'.format(self.entity)]
        for code in acnt_codes:
#           print("'code' is '{}, value is '{}'."
#               format(code, self.cofa_dict[code]))
            if 'T' in self.cofa_dict[code]['place_holder']:
                place_holder_indicator = ' --'
            else:
                place_holder_indicator = ''
            ret.append("{code:<5}{full_name}"
                                .format(**self.cofa_dict[code])
                        + place_holder_indicator)
        return '\n'.join(ret)

class Journal(object):
    """
    """
    # code being tested in temp.py

    def __init__(self, entity_name):
        """
        """
        self.entity = entity_name
        self.cofa = ChartOfAccounts(entity_name)
        journal_file = os.path.join(
                self.cofa.home,
                Journal_name)
        with open("journal_file", 'r') as f_object:
            self.data = json.load(f_object)

    def show_entry(entry):
        pass


    def show(self):
        """
        """
        ret = ['{}  Journal Entries'.format(self.entity)]
        for entry in self.data:
            ret.append(show_entry(entry))
        return '\n  '.join(ret)


def main():
    args = docopt.docopt(__doc__, version=VERSION)
#   print(args)
    if args['show_accounts']:
        cofa = ChartOfAccounts(args['--entity'])
        print(cofa.show())
#       for key in cofa.cofa_dict:
#           print("{:<6}{}".format(key, cofa.cofa_dict[key]))
    if args['show_journal']:
        cofa = ChartOfAccounts(args['--entity'])
        journal = Journal(args['--entity'])
        print(cofa.show())
    if args['new']:
        if args['--entity'] == create_entity(args['--entity']):
            print(
        "An accounting system for '{}' has been successfully created."
                        .format(args['--entity']))
        

if __name__ == '__main__':  # code block to run the application
    main()

