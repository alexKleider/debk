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
  debk.py new --entity=ENTITY
  debk.py show_accounts [--entity=ENTITY]
  debk.py show_journal [--entity=ENTITY]
  debk.py journal_entry [--entity=ENTITY]

Options:
  -h --help  Print usage statement.
  --version  Print version.
  --entity=ENTITY  Specify entity.

Commands:
  new creates a new set of books.
  show_accounts displays the chart of accounts.
  show_journal displays the journal entries.
  journal_entry provides for user entry.

Comments:
  The --entity=ENTITY option is mandatory with the 'mew' command.
  For the other commands, and attempt will be made to read the 

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
EPSILON = 0.01

DEFAULT_HOME = '/var/opt/debk.d'
# Each entity will have its home directory in DEFAULT_HOME.

# The following files are expected to be in the DEFAULT_HOME directory:
DEFAULT_CofA = "defaultChartOfAccounts"
# The default chart of accounts (place holders only.)
# A file of this name is kept in DEFAULT_HOME to serve as a template
# during entity creation although a different file can be used, see
# docstring for create_entity().
DEFAULT_Metadata = "defaultMetadata.json"
# A template used during entity creation.
DEFAULT_Entity = "defaultEntity"
# DEFAULT_Entity  - Keeps track of the last entity accessed and
# its content serves as the entity chosen if an entity is not
# specified on the command line.

CofA_name = 'CofA'               # These three files will appear
Journal_name = 'Journal.json'    # in the home directory 
Metadata_name = 'Metadata.json'  # of each entity.

with open(os.path.join(DEFAULT_HOME, DEFAULT_CofA), 'r') as f:
    reader = csv.reader(f)
    CSV_FIELD_NAMES = next(reader)
expected_field_names = ['code', 'type', 'full_name', 'name',
                            'notes', 'hidden', 'place_holder']
# print(CSV_FIELD_NAMES)
# print(expected_field_names)
assert CSV_FIELD_NAMES == expected_field_names
# global variables
# custom exception types
# private functions and classes
# public functions and classes
# main function

def none2float(n):
    """ Solves the need to interpret a non-entry as zero."""
    if not n: return 0
    else: return float(n)

def next_value(n=0):
    """ Used to assign numbers to journal entries.
    The value for 'n' will have to be kept in persistent storage
    (in metadata.)
    """
    while True:
        n += 1
        yield n

def create_entity(entity_name):
    """
    Establishes a new accounting system.

    Creates a new dirctory <entity_name> within DEFAULT_HOME.
    and populates it with a default start up chart of accounts.
    An attempt will be made to find a file name that is the 
    concatenation of the entity name and 'ChartOfAccounts'.
    If not found, the file specified by DEFAULT_CofA will be used.
    Reports error if:
        1. <entity_name> already exists, or
        2. not able to write to new directory.
    Also sets up an empty journal file. (contains only '{}'.)
    Returns <entity_name> if no errors are recognized.
    """
    cofa_source = os.path.join(  # Use a prepopulated chart of
                DEFAULT_HOME,    # accounts if it exists.
                entity_name + 'ChartOfAccounts')
#   print("#Looking for {}.#".format(cofa_source))
    if not os.path.isfile(cofa_source):
        cofa_source = os.path.join(DEFAULT_HOME, DEFAULT_CofA)
    new_dir = os.path.join(DEFAULT_HOME, entity_name+'.d')
    new_CofA_file_name = os.path.join(new_dir, CofA_name)
    new_Journal = os.path.join(new_dir, Journal_name)
    meta_source = os.path.join(DEFAULT_HOME, DEFAULT_Metadata)
    meta_dest = os.path.join(new_dir, Metadata_name)
    with open(meta_source, 'r') as meta_file:
        metadata = json.load(meta_file)
    metadata['entity_name'] = entity_name
    try:
        # The following keeps 
        with open(os.path.join(DEFAULT_HOME,
                    DEFAULT_Entity), 'w') as entity_file_object:
            entity_file_object.write(entity_name)
        os.mkdir(new_dir)
        shutil.copy(cofa_source, new_CofA_file_name)
        with open(new_Journal, 'w') as journal_file_object:
            journal_file_object.write('{"Journal": []}')
        with open(meta_dest, 'w') as json_file:
            json.dump(metadata, json_file)
    except FileExistsError:
        print("ERROR: Directory '{}' already exists"
                            .format(entity_name))
    except OSError:
        print("ERROR: Destination '{}' &/or '{}' may not be writeable."
                            .format(new_CofA_file_name, new_Journal))
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
        self.home = os.path.join(DEFAULT_HOME, entity_name+'.d')
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

class JournalEntry(object):
    """
    Each journal entry (self.data) is a dictionary as defined at the end
    of the JournalEntry.get_entry method declaration.)
    """
    
    def __init__(self, entry):
        """
        An instance can be instantiated by providing the dictionary
        directly or by providing an entry number (as a string.)
        In the later case, the user is prompted for data entry.
        """
        if not (type(entry) is dict):
            entry = JournalEntry.get_entry(entry)
        if entry: self.data = entry
        else: return

    def get_entry(entry_number):
        """
        Attempts to return a journal entry in the
        form of a dictionary which can be appended to the array
        kept in the Journal json file inside its single dictionary keyed
        by 'Journal'.
        Empty 'date' line terminates (None is returned.)
        Two empty account number entries in the face of an imbalance will
        also terminate (None is returned.) 
        """
        date_stamp = input("""
    Each entry must include a date, your name, a transaction description
    (more than one line is OK, an empty line terminates description entry)
    and a list of acnts with debits and credits. (Empty line terminates.)
        Date: """)
        if not date_stamp:
            print()
            return
        name = input("    Name: ")
        description_array = []
        while True:  # Allow multiline transaction description.
            description_line = input("    Description: ")
            if not description_line:
                break
            description_array.append(description_line)
        explanation = '\n'.join(description_array)
        account_list = []
        sum_dr = sum_cr = 0
        tries = 0   # Keep track of blank entries.
        while True:  # Allow multiple account entries that must balance.
            print(
        "  Enter an account number with debit &/or credit. (<--' to quit)")
            number = input("    Acnt#: ")
            if not number:  # User is finished?
                # Not allowed to leave imbalance.
                imbalance = sum_dr - sum_cr
                if abs(imbalance) > EPSILON:
                    print('Imbalance! Dr - Cr = {:,.2f}.'
                                .format(imbalance))
                    if tries > 0:  # Two empty entries in a row
                        return
                    else:
                        tries += 1
                        continue
                else: break
            else: tries = 0  # It's only two in a row that aborts entry.
            dr = none2float(input("    DR: "))
            sum_dr += dr
            cr = none2float(input("    CR: "))
            sum_cr += cr
            print('Dr & Cr values are of type {} and {}.'
                        .format(type(dr), type(cr)))
            account_list.append({"acnt":number, "DR":dr, "CR":cr})
        return {
            "number":"{:0>4}".format(entry_number),
            "date":date_stamp,
            "user":name,
            "description":explanation,
            "accounts":account_list
        }

    def ok(self):
        """
        Checks that a journal entry was actually created.
        """
        return hasattr(self, 'data')

    def show(self):
        """Presents a printable version of a journal entry (self.)
        Returns None if parameter is False in a Boolean context.
        """
        if not self.ok(): return
        ret0 = ["Entry {number:0>4} created {date} by {user}"]
        ret0.append('  {description}')
        ret1 = ('\n'.join(ret0)).format(**self.data)

        ret2 = ['{0:>16}{1:>10}'.format("DR", "CR")]
        print(self.data["accounts"])
        for account in self.data["accounts"]:
            ret2.append('{acnt:>6}:{DR:>10,.2f}{CR:>10,.2f}'
                            .format(**account))
        ret3 = '\n'.join(ret2)
        return '\n'.join([ret1, ret3])

class Journal(object):
    """
    Deals with the whole journal, loading it from persistent storage ,
    adding to it and then sending it back to be stored.
    See docstring for __init__ method.
    NOTE: this class's get_entry and show methods rely on 
    JournalEntry methods get_entry and show_entry methods.
    """

    def show_entry(entry):
        journal_entry = JournalEntry(entry)
        return journal_entry.show()

    # code was developed in journal.py

    def __init__(self, entity_name):
        """
        Loads an entity's metadata, chart of accounts, and 
        all journal entries to date in preparation for further
        journal entries.
        In future, may well load only journal entries created
        since last last end of year close out of the books.
        As of yet have not dealt with end of year.
        Also consider collecting new entries and not even loading
        those in persistent storage until user decides to save.

        Attributes include:
            cofa: chart of accounts
            journal:
            metadata:
            cofa_file:
            journal_file:
            metadata_file:
        """
        dir_name = os.path.join(DEFAULT_HOME, entity_name+'.d')
        self.cofa_file = os.path.join(dir_name, CofA_name)
        self.journal_file = os.path.join(dir_name, Journal_name)
        self.metadata_file = os.path.join(dir_name, Metadata_name) 
        with open(self.cofa_file, 'r') as f_object:
            self.cofa = [row for row in csv.DictReader(f_object)]
        with open(self.journal_file, 'r') as f_object:
            journal_dict = json.load(f_object)
            print(journal_dict)
            self.journal = journal_dict["Journal"]
            # The json file consists of a dict with only one entry keyed
            # by "journal" and its value is a list of journal entries.
        with open(self.metadata_file, 'r') as f_object:
            self.metadata = json.load(f_object)
        self.last_number = self.metadata['last_journal_entry_number']
        self.entity_name = entity_name

    def save(self):
#       with open(self.cofa_file, 'w') as f_object:
#           writer = csv.DictWriter(f_object)
#           self.cofa = csv.DictWriter(f_object)
#       May in the future allow adding accounts during journal entry.
        with open(self.journal_file, 'w', newline='') as f_object:
            json.dump({"Journal": self.journal}, f_object)
        with open(self.metadata_file, 'w') as f_object:
            json.dump(self.metadata, f_object)

    def get_entry(self):
#       print("\na journal entry is of type {}\n"
#                   .format(type(self.journal)))
        new_entry = (
            JournalEntry(self.metadata['last_journal_entry_number']))
        if new_entry.ok():
            self.metadata['last_journal_entry_number'] += 1
            self.journal.append(new_entry.data)
            return new_entry
        # else returns None

    def show(self):
        """
        """
        ret = ['{}  Journal Entries'
            .format(self.entity_name)]
        for entry in self.journal:
#           if entry:
                ret.append(Journal.show_entry(entry))
        return '\n  '.join(ret)


def main():
    args = docopt.docopt(__doc__, version=VERSION)
#   print(args)
    if args['new']:
        if args['--entity'] == create_entity(args['--entity']):
            print(
        "An accounting system for '{}' has been successfully created."
                        .format(args['--entity']))
    if not args['--entity']:
        with open(os.path.join(DEFAULT_HOME,
                    DEFAULT_Entity), 'r') as entity_file_object:
            args['--entity'] = entity_file_object.read()
    if args['show_accounts']:
        cofa = ChartOfAccounts(args['--entity'])
        print(cofa.show())
#       for key in cofa.cofa_dict:
#           print("{:<6}{}".format(key, cofa.cofa_dict[key]))
    if args['show_journal']:
        cofa = ChartOfAccounts(args['--entity'])
        journal = Journal(args['--entity'])
        print(journal.show())
    if args['journal_entry']:
        journal = Journal(args['--entity'])
        while True:
            print("Beginning a journal entry.")
            entry = journal.get_entry()
            if not entry:
                print("Breaking out of journal entry.")
                break
            else: print(entry.show())
        if journal.last_number < journal.metadata[
                                    'last_journal_entry_number']:
            journal_dict = {'Journal': journal.journal}
            print("journal_dict (to be stored) is:")
            print(journal_dict)
            answer = input("Would you like to save the entries?: ")
            if answer and (answer[0] in 'yY'):
                print('Answer was affirmative.  Journal content:')
                print(journal.show())
                print("Journal content should have been printed.")
                with open(journal.journal_file, 'w') as f_object:
                    json.dump(journal_dict, f_object)
                with open(journal.metadata_file, 'w') as f_object:
                    json.dump(journal.metadata, f_object)
        print("Should now be all over.")
        

if __name__ == '__main__':  # code block to run the application
    main()

