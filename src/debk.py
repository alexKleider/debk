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
  debk.py [-v|-vv|-vvv] show_account_balances [--entity=ENTITY]
  debk.py show_journal [--entity=ENTITY]
  debk.py journal_entry [--entity=ENTITY]

Options:
  -h --help  Print usage statement.
  --version  Print version.
  -v --verbosity  How much info to show [default: 0]
  --entity=ENTITY  Specify entity.

Commands:
  new creates a new set of books.
  show_accounts displays the chart of accounts.
  show_journal displays the journal entries.
  journal_entry provides for user entry.

Comments:
  The --entity=ENTITY option is mandatory with the 'new' command.
  For the other commands, an attempt will be made to set the entity to
  the last one used (and persistently stored in
  DEFULT_HOME/DEFAULT_Entity.
"""

import os
import sys
import shutil
import json
import csv

import docopt

VERSION = "0.0.0"

EPSILON = 0.01
INDENTATION_MULTIPLIER = 2  

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

def dr_or_cr(code):
    """
    Returns the account type, either 'DR' or 'CR' 
    determined by the account's code/number.
    Later processing may change an Accounts type to
    'place_holder'.
    """
    number = int(code)
    if  number  <= 1999: return('DR')   # Assets
#   elif number <= 3999: return('CR')   # Liabilities and Equity
    elif number <= 4999: return('CR')   # Income
    elif number <= 5999: return('DR')   # Expenses

def set_indentation(indentation_level, 
                    previous_place_holder_value,
                    current_place_holder_value,
                    account_code):
    """Uses the account's place_holder value to algorithmicly change
    indentation_level. The first two parameters are both changed.
    Tried to use a generator but didn't work."""
    assert current_place_holder_value in {'T', 'F'}
    if account_code in {'1000', '2000', '3000', '4000', '5000'}:
        return(0, 'T')
#   print("PREVIOUS AND CURRENT: {}, {}"
#       .format(previous_place_holder_value,
#               current_place_holder_value))
    if previous_place_holder_value == 'T':
        indentation_level += 1
    elif (previous_place_holder_value == 'F' and 
            current_place_holder_value == 'T'):
        indentation_level -= 1
    previous_place_holder_value = current_place_holder_value
#   print("PREVIOUS AND CURRENT: {}, {}"
#       .format(previous_place_holder_value,
#               current_place_holder_value))
#   print("INDENT SET TO {}.".format(indentation_level))
    return (indentation_level, previous_place_holder_value)


def create_entity(entity_name):
    """
    Establishes a new accounting system.

    Creates a new dirctory '<entity_name>.d' within DEFAULT_HOME
    and populates it with a set of required files including a
    default start up chart of accounts.
    An attempt will be made to find a file name that is the 
    concatenation of the entity name and 'ChartOfAccounts'.
    If not found, the file specified by DEFAULT_CofA will be used.
    Reports error if:
        1. <entity_name> already exists, or
        2. not able to write to new directory.
    Also sets up an empty journal file and a metadata file.
    Reports success if no errors are recognized.
    """
    cofa_source = os.path.join(  # Use a prepopulated chart of
                DEFAULT_HOME,    # accounts if it exists.
                entity_name + 'ChartOfAccounts')
    print("#Looking for {}.#".format(cofa_source))
    if not os.path.isfile(cofa_source):
        print("Could not find file '{}'.."
            .format(cofa_source))
        cofa_source = os.path.join(DEFAULT_HOME, DEFAULT_CofA)
        print("... so default '{}' is being used"
            .format(cofa_source))
    new_dir = os.path.join(DEFAULT_HOME, entity_name+'.d')
    print("new_dir is {}.".format(new_dir))
    new_CofA_file_name = os.path.join(new_dir, CofA_name)
    print("new_CofA_file_name is {}.".format(new_CofA_file_name))
    new_Journal = os.path.join(new_dir, Journal_name)
    meta_source = os.path.join(DEFAULT_HOME, DEFAULT_Metadata)
    meta_dest = os.path.join(new_dir, Metadata_name)
    with open(meta_source, 'r') as meta_file:
        metadata = json.load(meta_file)
    metadata['entity_name'] = entity_name
    entity_file_path = os.path.join(DEFAULT_HOME, DEFAULT_Entity)
    try:
        # The following keeps track of the last entity referenced.
        with open(entity_file_path, 'w') as entity_file_object:
            entity_file_object.write(entity_name)
        print("Wrote entity name to {}.".format(entity_file_path))
        os.mkdir(new_dir)
        print("Created new directory {}.".format(new_dir))
        shutil.copy(cofa_source, new_CofA_file_name)
        print("Copied {} to {}.".format(cofa_source,
        new_CofA_file_name))
        with open(new_Journal, 'w') as journal_file_object:
            journal_file_object.write('{"Journal": []}')
        print("Wrote to {}.".format(new_Journal))
        with open(meta_dest, 'w') as json_file:
            json.dump(metadata, json_file)
        print("Dumped to {}.".format(meta_dest))
    except FileExistsError:
        print("ERROR: Directory '{}' already exists"
                            .format(new_dir))
    except OSError:
        print("ERROR: Destination '{}' &/or '{}' may not be writeable."
                            .format(new_CofA_file_name, new_Journal))
    else:
        return entity_name

class LineEntry(object): 
    """
    Serves as a line entry for ledger accounts. 
    Do NOT confuse this class with journal line entries which
    have NOT been given their own class.
    Each instance has the following attributes:
        num    a journal entry number
        DR     a debit amount
        CR     a credit amount
    An instance of one of the line_entries of a Journal instance
    can be used to populate the DR and CR keys but the num key value
    (the Journal instance's number) must be known as well.
    Instances of LineEntry are used to populate the line_entries
    attribute of instances of the Account class which is in turn used
    by the ChartOfAccounts class.
    """
    
    def __init__(self, dr, cr, entry_number):
        self.entry_number = entry_number
        self.DR = dr
        self.CR = cr

    def show(self):
        if self.DR: dr = '{:>10.2f}Dr'.format(self.DR)
        else: dr = '{:>10}'.format(' ')
        if self.CR: cr = '{:>10.2f}Cr'.format(self.CR)
        else: cr = '{:>10}'.format(' ')
        return ("  {}  {}   {}"
                .format(self.entry_number, dr, cr))

class Account(object):
    """Provides data type for values of the dict
    ChartOfAccounts.accounts keyed by account code.
    Attributes include csv, code, balance, dr_cr, place_holder,
    acnt_type, split
    """

    def __init__(self, csv):
        self.csv = csv
        self.code = csv['code']
#       print('Dealing with account code {}'.format(self.code))
        if csv['split']:
            self.split = int(csv['split'])
        else:
            self.split = 0
        self.line_entries = []  # list of LineEntry objects.
        self.balance = 0
        self.dr_cr = ''  # Specifies if the balance is 'DR' or 'CR'
#       print("csv['place_holder'] for Acnt {} is {}."
#           .format(self.code, csv['place_holder']))
        if csv['place_holder'] in 'Tt':
            self.place_holder = True 
            self.acnt_type = 'place_holder'
        elif csv['place_holder'] in 'Ff':
            self.place_holder = False 
            self.acnt_type = dr_or_cr(self.code)  # Specifies account type.
                # Possible values: 'DR', 'CR', 'place_holder'
        else:
            self.place_holder = None
            print("Problem with Acnt {}: Place holder or not??"
                    .format(self.code))

    def dump(self):
        """ A 'quick and dirty' way to show an account.
        Expect to only use it during development.
        """
        if self.split: split = "{}".format(self.split)
        else: split = ''
        ret = ['Acnt#{}'.format(self.code)]
        if self.split:
            split = self.split
        else:
            split = ''
        if self.place_holder: ret.append(
                "{}  < place holder{}".
                format(self.csv['full_name'].upper(),
                    split))
        else: 
            ret.append("{:<15}{:>10.2f}{} <TOTAL {}"
                    .format(self.csv['name'],
                            self.balance,
                            self.dr_cr,
                            split))
        ret = [' '.join(ret)]
        for line_entry in self.line_entries:
            ret.append(line_entry.show())
        return '\n'.join(ret)

    def update_balance(self):
        """
        Traverses line_entries to populate the balance and dr_cr
        attributes.  Accounts (all the place holder accounts for sure)
        with no entries will continue to have their dr_cr attribute set
        to the empty string.
        Note: the line_entries themselves are populated by the
        ChartOfAccounts load_journal method.
        """
        if self.csv['place_holder'] == 'T':
            return  # Defaults have already been set.
        dr = cr = 0
        for line_entry in self.line_entries:
            dr += line_entry.DR
            cr += line_entry.CR
        if dr > cr:
            self.balance = dr - cr
            self.dr_cr = 'DR'
        elif dr < cr:
            self.balance = cr - dr
            self.dr_cr = 'CR'
        else:  
            assert self.balance == 0
#           self.dr_cr = ' '
            self.dr_cr = ''

    def show_balance(self, indent = 0):
        """Returns a string representation of an account's balance
        formatted to serve as a last line.  Use strip method if you want
        just the value.
        ########  CURRENTLY SEEMS NOT TO WORK  ##################
        """
        if self.dr_cr == 'DR':
            dr_cr_type = 'Dr'
        elif self.dr_cr == 'CR':
            dr_cr_type = 'Cr'
        else:
            dr_cr_type = 'Unspecified'
        return(ChartOfAccounts.format_line
            .format("{}".format(' '*INDENTATION_MULTIPLIER*indent),
                    ' ', ' ', ' ',
                    '{:.2f}'.format(self.balance),
                    dr_cr_type))


    def show(self, args, indent = 0, place_holder = 0):
        """
        Returns a string representation of itself (an account.)
        The 'place_holder' parameter is used to control indentation.
        """
        print("Calling the show method on an account. (verbosity is {})"
                .format(args['--verbosity']))
        ret = []
        assert type(self.place_holder) == type(True) 
        if self.place_holder is True:
            header_choice = 'full_name'
        elif self.place_holder is False:
            header_choice = 'name'
        else: 
            print("ERROR Condition: place holder neither T nor F")
        indent, place_holder = (
                set_indentation(indent,   # { These two parameters
                        place_holder,     # {    are modified.
                        self.csv['place_holder'],
                        self.code))
        header_line =("{}{:<5}{}"
            .format("{}".format(' '*INDENTATION_MULTIPLIER*indent),
                self.code,
                self.csv[header_choice]))
        if args['--verbosity'] == 1:
            print('--verbosity is only 1')
            return header_line + ('{:>6.2f}{}'
                                .format(self.balance, self.dr_cr))
        ret = [header_line]
        if args['--verbosity'] > 1:
            print('--verbosity is > 1')
            if self.line_entries:
                print("There are entries for this account ({})"
                        .format(self.code))
                ret.append(ChartOfAccounts.format_line
                    .format("{}".format(' '*INDENTATION_MULTIPLIER*indent),
                            "Entry#", 'Debits', 'Credits', 'Balance', ' '))
                for line_entry in (self.line_entries):
                    if line_entry.DR:
                        new_line = (ChartOfAccounts.format_line
                            .format("{}"
                                .format(' '*INDENTATION_MULTIPLIER*indent),
                                        line_entry.entry_number,
                                        line_entry.DR, ' ', ' ', ' '))
                    if line_entry.CR:
                        cr_check += line_entry.DR
                        new_line = (ChartOfAccounts.format_line
                            .format("{}".format(' '*i_mult*indent),
                                    line_entry.entry_number,
                                    ' ', line_entry.CR, ' ', ' '))
                    if line_entry.DR and line_entry.CR:
                        new_line = (ChartOfAccounts.format_line
                            .format("{}".format(' '*i_mult*indent),
                                    line_entry.entry_number,
                                    line_entry.DR, line_entry.CR,
                                    ' ', ' '))
                    ret.append(new_line)
                if account.dr_cr == 'DR':
                    dr_cr_type = 'Dr'
                else: dr_cr_type = 'Cr'
                ret.append(ChartOfAccounts.format_line
                    .format("{}".format(' '*i_mult*indent),
                            ' ', ' ', ' ',
                            '{:.2f}'.format(account.balance),
                            dr_cr_type))
            else:
                print("There are no entries for this account!!!")
        return '\n'.join(ret)



class ChartOfAccounts(object):
    """
    A class to manage an entity's chart of accounts.
    Instantiation loads such a chart from a file 
    but this includes only what's in the CSV file,
    NOT any accounting information. When accounting
    information is required, it is calculated on the fly.  
    The 'show' method returns text displaying the accounts
    in a way determined by the 'verbosity' parameter:
        0: Listing if the accounts only.
        1: Accounts with totals.
        2: Accounts with all entries affecting each account.
    Zeroing out of the temporary (Expenses and Income) accounts is for
    now being left for the user to do using journal entries.
    """

    format_line = "{}{:>10}{:^10}{:^10}{}{}"

    def __init__(self, entity_name):
        """
        Loads the chart of accounts belonging to a specified entity.
        The accounts attribute is a dict keyed by account codes and
        values are instances of the Account class.
        """
        self.entity_name = entity_name  # Used by self.load_journal().
        self.home = os.path.join(DEFAULT_HOME, entity_name+'.d')
        self.cofa_file = os.path.join(self.home, CofA_name)
        self.csv_dict = {}  # Keyed by account number ('code'.)
        self.code_set = set()
        with open(self.cofa_file, 'r') as cofa_file_object:
            reader = csv.DictReader(cofa_file_object)
            for row in reader:
#               print(row)
                if row['code'] in self.code_set:
                    print("Error Condition: Duplicate account code:{}."
                            .format(row['code']))
                    print("Fix before rerunning the script.")
                    sys.exit()
                self.code_set.add(row['code'])
                self.csv_dict[row['code']] = row
        self.ordered_codes = sorted([key for key in self.code_set])
#       print(self.ordered_codes)
        self.accounts = {key:
                Account(self.csv_dict[key]) for key in self.code_set}
        # The accounts attribute is not fully populated until if and
        # when needed.  This is done using the load_journal() method.

    def load_journal(self):
        """
        Posts the journal to the ledger.
        Returns a tuple: (expenses, fixed_assets)
            This is for my convenience- it's NOT std accounting
            proceedure!
        """
        journal = Journal(self.entity_name)
#       print("Journal Contains the following......................")
#       print(journal.journal)
#       print("....................................................")
        for je in journal.journal:  # Populate accounts with entries.
            for le in je["line_entries"]:
                if le['acnt'] not in self.code_set:
                    print(
                    "Error Condition: AcntCode {} is not recognized."
                        .format(le['acnt']))
                line_entry = LineEntry(le['DR'],
                                        le['CR'],
                                        je['number'])
#               print("   {}      {}"
#                                   .format(line_entry.show(),
#                                           le['acnt']))

                self.accounts[le['acnt']].line_entries.append(
                                                line_entry)
        fixed_assets = expenses = 0  # Keep running totals of these.
        dr_check = cr_check = 0  # To check totals balance.
        print("\nACCOUNTS FOR SPECIAL TREATMENT:")
        for code in self.ordered_codes:
            # Populate the accounts with balances, specify Dr or Cr, and
            # do a running total to check that all is in balance.
            # I'm also keeping a running total of fixed assets and
            # expenses (a custom requirement. -Not part of standard
            # accounting practices.
            self.accounts[code].update_balance()
            balance = self.accounts[code].balance

            if self.accounts[code].dr_cr == 'DR':
                dr_check += balance
#               print("For {} dr_cr is 'DR' {:,.2f}"
#                   .format(code, balance))
            elif self.accounts[code].dr_cr == 'CR':
                cr_check += balance
#               print("For {} dr_cr is 'CR' {:,.2f}"
#                   .format(code, balance))
            else:
                pass
#               print("For {} no dr_cr entry {:,.2f}"
#                       .format(code, balance))
            ##############################################
            if (code[:1] == '5') and (not
                        self.accounts[code].place_holder):
                expenses += balance
                print("Expense {}: ${:.2f}  /by {}"
                    .format(code, balance, self.accounts[code].split))
            if (code[:2] == '15') and (not
                        self.accounts[code].place_holder):
                fixed_assets += balance
                print("FixedAsset {}: ${:.2f}  /by {}"
                    .format(code, balance, self.accounts[code].split))
        print("\nEND OF ACCOUNTS FOR SPECIAL TREATMENT:\n")
            ##############################################
        imbalance = dr_check - cr_check
        if abs(imbalance) > EPSILON:
            print("MAJOR ERROR! Balance sheet doesn't balance!")
            print(" Debits - Credits = {:,.2f}.".format(imbalance))
        return (expenses, fixed_assets)

    def show(self, args):
        """
        Return a string representation of the Ledger.
        Parameter args('--verbosity') determines how much
        information is displayed.
        """
        indent = 0  # Keep track of indentation level.
        place_holder = ''  # Used by indentation mechanism.
        header = "Account Balances"
        ret = [header, "-"*len(header)]
        for account_code in self.ordered_codes:
            account = Account(self.csv_dict[account_code])
            ret.append(account.show(args, indent, place_holder))
        return '\n'.join(ret)


class JournalEntry(object):
    """
    Each journal entry (self.data) is 
    a dictionary: dict(
            number: "{:0>3}".format(entry_number),
            date: date_stamp,
            user: name,
            description: explanation,
            line_entries: list of {'acnt', 'DR', 'CR' keyed values},
            )
    (We use 'data' rather than individual attributes to allow persistent
    storage in a json file.
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
        line_entries = []
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
                    print('Imbalance! Dr - Cr = {:,.2f}. (Entry #{})'
                                .format(imbalance, entry_number))
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
#           print('Dr & Cr values are of type {} and {}.'
#                       .format(type(dr), type(cr)))
            line_entries.append(dict(acnt= number, DR= dr, CR= cr))
        print("Captured entry # {}.".format (entry_number))
        return dict(
            number= "{:0>3}".format(entry_number),
            date= date_stamp,
            user= name,
            description= explanation,
            line_entries= line_entries
            )

    def ok(self):
        """
        Checks that a journal entry was actually created.
        """
        return hasattr(self, 'data')

    def show_line_entry(line_entry):
        """
        Parameter is expected to be a dict with following keys:
        'accnt' (type str,) 'DR', 'CR' (both type float.)
        Note: don't confuse this line entry in the journal
        whith line entries in Chart of Accounts.
        """
        ret = dict(acnt= '{:>8}'.format(line_entry['acnt']),)
        if line_entry['DR']:
            ret['DR'] = '{:>10,.2f}'.format(line_entry['DR'])
        else:
            ret['DR'] = '{:>10}'.format(' ')
        if line_entry['CR']:
            ret['CR'] = '{:>10,.2f}'.format(line_entry['CR'])
        else:
            ret['CR'] = '{:>10}'.format(' ')
        return ('{acnt:>8}:{DR}{CR}'
                            .format(**ret))

    def show(self):
        """Presents a printable version of a journal entry, more
        specifically, a representation of its only attribute: data which
        is a dictionary.
        Returns None if parameter is False in a Boolean context.
        """
        if not self.ok(): return  # Check for data attribute.
        data = self.data
        ret = []
        ret.append("  #{:>3} on {:<12} by {}."
            .format(data['number'], data['date'], data['user']))

        description_lines = data["description"].split('\n')
#       print(description_lines)
        for line in description_lines:
            ret.append("    {}".format(line))

        for line_entry in data["line_entries"]:
            ret.append(JournalEntry.show_line_entry(line_entry)) 

        return '\n'.join(ret)

class Journal(object):
    """
    peals with the whole journal, loading it from persistent storage,
    adding to it, and then sending it back to be stored.
    It keeps track of journal entry numbers, the next one of which is
    kept in persistent storage as part of the metadata for an entity.
    See docstring for __init__ method.
    NOTE: this class's get_entry and show methods rely on 
    JournalEntry methods get_entry and show.
    """

    def __init__(self, entity_name):
        """
        Loads an entity's metadata and all journal entries to date:
        in preparation for further journal entries.
        Attributes include:
            entity_name:
            journal_file:
            metadata_file:
            next_entry
            journal: a list of dicts
                In persistent storage it is a json file consisting of 
                a dict with only one entry keyed by "Journal" with a 
                value that is a list of dicts. The journal attribute
                becomes this list.  Each item of this list is a dict and
                corresponds to the data attribute of instances of the
                class JournalEntry.
            metadata:
        In future, may well load only journal entries created
        since last end of year close out of the books.
        As of yet have not dealt with end of year.
        Also consider collecting new entries and not even loading
        those in persistent storage until user decides to save.
        """
        self.entity_name = entity_name
        dir_name = os.path.join(DEFAULT_HOME, entity_name+'.d')
        self.journal_file = os.path.join(dir_name, Journal_name)
        self.metadata_file = os.path.join(dir_name, Metadata_name) 
        with open(self.journal_file, 'r') as f_object:
            journal_dict = json.load(f_object)
#           print(journal_dict)
            self.journal = journal_dict["Journal"]
            # The json file consists of a dict with only one entry keyed
            # by "journal" and its value is a list of dicts, each
            # corresponding to the data attribute of the JournalEntry
            # class.
        with open(self.metadata_file, 'r') as f_object:
            self.metadata = json.load(f_object)
        self.next_entry = self.metadata['next_journal_entry_number']

    def show(self):
        """
        Returns a string representation of the journal attribute.
        """
        journal = self.journal

        ret = ["Journal Entries:......"]
        for je in self.journal:
            entry = JournalEntry(je)
            ret.append(entry.show())
        return '\n'.join(ret)

    def save(self):
        """Saves journal to persistent storage.
        Only called after entries have been made and approved."""
        self.metadata['next_journal_entry_number'] = self.next_entry
        with open(self.journal_file, 'w', newline='') as f_object:
            json.dump({"Journal": self.journal}, f_object)
        with open(self.metadata_file, 'w') as f_object:
            json.dump(self.metadata, f_object)

    def get_entry(self):
        """Used by the get method do add an entry to the the journal
        attribute of 'self', an instance of the Journal class.
        The next_number attribute is updated each time.
        Each entry is a dict corresponding to the data attribute of
        an instance of the JournalEntry class.
        An instance of the JournalEntry class is returned.
        """
#       print("\na journal entry is of type {}\n"
#                   .format(type(self.journal)))
        new_entry = (
            JournalEntry(self.next_entry))
        if new_entry.ok():
            self.next_entry += 1
            self.journal.append(new_entry.data)
            return new_entry
        # else returns None

    def get(self):
        """Gets journal entries from the user.
        Does this using the get_entry method.
        Once user input is completed, checks the next_number attribute
        to see if entries have been made, and if so, confirms with user
        before calling the save method to save them.
        """
        while True:
#           print("Beginning journal entry.")
            entry = self.get_entry()
            if not entry:
#               print("Breaking out of journal entry.")
                break
#           else: print(entry.show())
        print('next numbers are self {} and metadata {}.'
                .format(self.next_entry,
                self.metadata['next_journal_entry_number']))
        if self.next_entry > self.metadata[
                            'next_journal_entry_number']:
            # Entries have been made; will probably want to save.
            journal_dict = {'Journal': self.journal}
#           print("journal_dict (to be stored) is:")
#           print(journal_dict)
            answer = input("Would you like to save the entries?: ")
            if answer and (answer[0] in 'yY'):
                self.save()
                print('Answer was affirmative.  Journal content:')
                print(self.show())
                print(
                "Journal content as it appears above, has been saved.")
#       print("Should now be all over.")


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
    
    if args['journal_entry']:
        journal = Journal(args['--entity'])
        journal.get()

    if args['show_journal']:
        journal = Journal(args['--entity'])
        print(journal.show())

    if args['show_accounts']:
        cofa = ChartOfAccounts(args['--entity'])
        print(cofa.show(args))


    if args['show_account_balances']:
        cofa = ChartOfAccounts(args['--entity'])
        expenses, fixed_assets = cofa.load_journal()
        for key in cofa.ordered_codes:
            print(cofa.accounts[key].dump())


#       print(cofa.show(args))
        print("\nAssets total: ${:.2f}".format(fixed_assets))
        print("\nExpenses total: ${:.2f}".format(expenses))

if __name__ == '__main__':  # code block to run the application
    main()

