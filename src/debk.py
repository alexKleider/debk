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

       ******************   debk.py   *****************

       A module that supports double entry book keeping.

This project was inspired by and serves the special accounting
needs of the Kazan15 'group of 10.'[1]  Perhaps it might serve
other needs as well.

Usage:
  debk.py -h | --version
  debk.py new --entity=ENTITY
  debk.py journal_entry [<infiles>...] [--entity=ENTITY]
  debk.py show_journal [--entity=ENTITY]
  debk.py [-v ...] show_accounts [--entity=ENTITY]
  debk.py [-v ...] custom [<infiles>...] [--entity=ENTITY]
  debk.py [-v ...] test [--entity=ENTITY]


Options:
  -h --help  Print usage statement.
  --version  Print version.
  -v --verbosity  How much info to show (>2 = 2)
  --entity=ENTITY  Specify entity.

Commands:
  <new> creates a new set of books.
  <show_accounts> displays the chart of accounts.
  <show_journal> displays the journal entries.
  <journal_entry> provides for user entry.
  <custom> serves the specialized needs of Kazan15:
    prompt> ./src/debk.py -vvv custom ./debk.d/kazan_journal --entity=Kazan15
    Then look for a file 'Report'.
    To make the above work, the following files are provided:
      ./debk.d/kazan_journal
      /var/opt/debk.d/KazanChartOfAccounts

Comments:
  The --entity=ENTITY option is mandatory with the 'new' command.
  In the case of other commands: when not provided, it defaults to the
  last entity referenced.

[1] canoetripping.info:5380
"""

import os
import sys
import csv
import json
import shutil

import docopt

VERSION = "0.0.1"

MAXIMUM_VERBOSITY = 3
EPSILON = 0.01  # We want acuracy to the nearest penney only.
INDENTATION_MULTIPLIER = 3  
INDENTATION_CONSTANT = ' ' * INDENTATION_MULTIPLIER  

N_ASSET_OWNERS = 8  # Must jive with 'split' values in CofAs.
                    # This is specific to Kazan15.

DEFAULT_HOME = '/var/opt/debk.d'
# Each entity will have its home directory in DEFAULT_HOME.

# The following files are expected to be in the DEFAULT_HOME directory:
DEFAULT_CofA = "defaultChartOfAccounts"     # A file name.
# The default chart of accounts. (For now: place holders only.)
# A file of this name is kept in DEFAULT_HOME to serve as a template
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

NotesAboutAccountCodes = """
Account codes are assumed to consist of 4 digits each,
with the first digit being one of the following:
1 for Assets
2 for Liabilities
3 for Equity
4 for Income, and 
5 for Expenses.
If you wish to adapt the code for a different scheme, corresponding
changes will have to be made in the following:
The global function dr_or_cr
Account class methods signed_balance, show_balance
Global functions that are 'custom' for the Kazan15 entity:
    adjust4assets, zero_expenses, check_equity_vs_bank.
"""

def none2float(n):
    """ Solves the need to interpret a non-entry as zero."""
    if not n: return 0
    else: return float(n)

def divider(dollar_amount, split):
    """Attempts to divide 'dollar_amount' into 'split' equal parts.
    Returns a 'split' list of floats.  Expects 'dollar_amount' to be
    a float, 'split' to be an int.  Works to the nearest penney.
    When equal amounts are not possible, the first numbers in
    the list will be greater than the last by one.
    An assertionError is raised if the sum of the list is not equal
    to 'dollar_amount'.
    """
    ret = []
    dividend = int(dollar_amount * 100)  # money/float => pennies/int
    quotient, rem = divmod(dividend, split)
    for split in range(1, split + 1):
        if split > rem:
          ret.append(quotient/100.0)
        else: ret.append((quotient + 1)/100.0)
    assert (sum(ret) - dollar_amount) < EPSILON
    return ret

def zero_out(preamble,
            format_line,
            split_list):
    """Sets up text that can be read as a journal entry from an input
    file.
    'preamble' is a list of strings representing date, user,
    descriptive text (which can be more than one line/string,)
    and the single zeroing entry.
    'format_line' is the format string used for the balancing entries.
    'split_list' is expected to be the output from a call to divider().
    """
    ret = preamble
    for i in range(len(split_list)):
        ret.append(format_line.format(i + 1, split_list[i]))
    ret.append('\n')  # Journal entry depends on this trailing CR
    return '\n'.join(ret)

def dr_or_cr(code):
    """
    Returns the account type, either 'DR' or 'CR' 
    determined by the account's code/number.
    Later processing may change an Accounts type to
    'place_holder'.
    Used to set the Account attribute acnt_type.
    """
    first = code[:1]
    if first in ('1', '5'):          # Assets and Expenses
        return('DR')
    elif first in ('2',  '3', '4'):  # Liabilities, Equity, Income
        return('CR')
    else:
        print(
        "WARNING: malformed account code: '{}'.  Unable to continue."
                    .format(code))
        sys.exit(2)

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
    Leaves a record of the entity_name to serve as a default for future
    commands.
    """
    cofa_source = os.path.join(  # Use a prepopulated chart of
                DEFAULT_HOME,    # accounts if it exists.
                entity_name + 'ChartOfAccounts')
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
    entity_file_path = os.path.join(DEFAULT_HOME, DEFAULT_Entity)
    try:
        # The following keeps track of the last entity referenced.
        with open(entity_file_path, 'w') as entity_file_object:
            entity_file_object.write(entity_name)
        os.mkdir(new_dir)
        shutil.copy(cofa_source, new_CofA_file_name)
        with open(new_Journal, 'w') as journal_file_object:
            journal_file_object.write('{"Journal": []}')
        with open(meta_dest, 'w') as json_file:
            json.dump(metadata, json_file)
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
    A single line entry of a Journal instance can be used to populate
    the DR and CR attributes (one of them is generally 0) but the num
    attribute (the Journal instance's number) must be known as well.
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
        return ("  je#{:0>3}  {}   {}"
                .format(self.entry_number, dr, cr))

class Account(object):
    """Provides data type for values of the dict
    ChartOfAccounts.accounts keyed by account code.
    Attributes include: csv, code, balance,
    dr_cr (specifies if the balance is a debit or credit,)
    place_holder, split, indent,
    acnt_type (DR if debits are positive,
               CR if credits are positive,
               or 'place_holder'.)
    Place holder accounts will have the attribute s_balance
    depending on their acnt_type: Dr totals in Cr accounts
    and Cr totals in Dr accounts will be shown as negative.
    Non place_holder accounts have the signed_balance method to return
    the corresponding (signed) value.
    """

    def __init__(self, csv):
        self.csv = csv
        self.code = csv['code']
        self.indent = INDENTATION_CONSTANT * int(csv['indent'])
        if csv['split']:
            self.split = int(csv['split'])
            self.split_as_str = "(\{})".format(self.split)
        else:
            self.split = 0
            self.split_as_str = ''
        self.line_entries = []  # list of LineEntry objects.
        self.balance = 0
        self.dr_cr = ''  # Specifies if the balance is 'DR' or 'CR'
        self.s_balance = 0  # This attribute is populated by the
                            # set_place_holder_signed_balances method
                            # of the ChartOfAccounts class and
                            # applies only to place_holder accounts.
        if csv['place_holder'] in 'Tt':
            self.place_holder = True 
            self.acnt_type = 'header'
            self.header_str = 'Header'
        elif csv['place_holder'] in 'Ff':
            self.place_holder = False 
            self.acnt_type = dr_or_cr(self.code)  # Dr, Cr, or 'header'
            self.header_str = ''
        else:
            self.place_holder = None
            print("Problem with Acnt {}: Place holder or not??"
                    .format(self.code))

    def signed_balance(self):
        """Checks (based on its code) if an account's balance is positive
        or negative and returns the balance appropriately signed.
        """
        if (self.balance < EPSILON or 
        (self.code[:1] in '15' and self.dr_cr == 'DR')
        #  Asset and Expense accounts are Debit accounts.
        or (self.code[:1] in '234' and self.dr_cr == 'CR')
        #  Liability, Equity and Income accounts are Credit accounts.
        ):
#           print("Accnt {}{} has the appropriate Dr/Cr balance: {:.2f}"
#               .format(self.code, self.dr_cr, self.balance))
            return self.balance  # As it should be.
        else:
#           print("Accnt {}{} has a NEGATIVE Dr/Cr balance:      {:.2f}"
#               .format(self.code, self.dr_cr, self.balance))
            return self.balance * -1

    def acnt_dict(self):
        """Returns a dict that can be used to format output for reports.
        """
        return dict(code= self.code,
                    balance= self.balance,
                    s_balance= self.s_balance,
                    _type= self.acnt_type,
                    category= self.csv['type'],
                    full_name= self.csv['full_name'],
                    name= self.csv['name'],
                    notes= self.csv['notes'],
                    indent= self.indent,
                    split= self.split_as_str,
                    header= self.header_str
                    )

    def dump(self, verbosity = MAXIMUM_VERBOSITY):
        """ A 'quick and dirty' way to show an account.
        Expect to only use it during development.
        Verbosity defaults to the maximum.
        """
        if not verbosity:    # Just show the account metadata.
            ret = []
            if self.place_holder:
                ret.append(
                '{indent}{code}: {header}: {category}- {notes}'
                    .format(**self.acnt_dict()))
            else:
                ret.append('{indent}{code}: {name}{split}'
                    .format(**self.acnt_dict()))
            return '\n'.join(ret)        # That's all.

        # Assign first part of first line:
        ret = ['{}Acnt#{}'.format(self.indent, self.code)]
        # Assign second part of first line- depending if place_holder:
        if self.place_holder: ret.append(
#               "{}{}  < {} place holder subtotal: {:.2f}".
                "{}{} {} Title_Account- subtotal: {:.2f}".
                format(self.indent,
                    self.csv['full_name'].upper(),
                    self.split_as_str,
                    self.s_balance))
        else: 
            ret.append("{}{:<15} {} Total:{:>10.2f}{}"
                    .format(self.indent,
                            self.csv['name'],
                            self.split_as_str,
                            self.balance,
                            self.dr_cr))
        # Join the two parts to complete the first (header) line:
        ret = [' '.join(ret)]

        if verbosity > 1: # Add the line entries:
            for line_entry in self.line_entries:
                ret.append('{}{}'.format(self.indent,
                                        line_entry.show()))

        # Put it all together and return it:
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
            self.dr_cr = ''

    def show_balance(self, indent = 0):
        """Returns a string representation of an account's balance
        formatted to serve as a last line.  Use strip method if you want
        just the value.
        ########  CURRENTLY SEEMS NOT TO WORK  ##################
        ########  CURRENTLY USING dump METHOD  ##################
        Thinking of using an extra 'indent' parameter in the CofA csv
        file to solve the indentation problem.
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

class ChartOfAccounts(object):
    """
    A class to manage an entity's chart of accounts (AKA the Ledger.)
    Instantiation loads such a chart from a file 
    but this includes only what's in the CSV file,
    NOT any accounting information. When accounting
    information is required, it is calculated on the fly by loading the
    journal.
    The 'show' method returns text displaying the accounts
    in a way determined by the 'verbosity' parameter:
        0: Listing if the accounts only.
        1: Accounts with totals.
        2: Accounts with all entries affecting each account.
    Zeroing out of the temporary (Expenses and Income) accounts is for
    now being left for the user to do using journal entries.
    """

    format_line = "{}{:>10}{:^10}{:^10}{}{}"

    def __init__(self, args):
        """
        Loads the chart of accounts belonging to a specified entity.
        The accounts attribute is a dict keyed by account codes and
        values are instances of the Account class.
        """
        self.entity = args['--entity']
        self.home = os.path.join(DEFAULT_HOME, self.entity  + '.d')
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
        self.journal_loaded = False
        # The accounts attribute is not fully populated until if and
        # when needed.  This is done using the load_journal() method.

    def set_place_holder_signed_balances(self):
        """
        Iterates through the accounts setting the signed_balance
        attribute for each of the place_holder accounts.
        """
        I = len(self.ordered_codes)
        for code in self.ordered_codes:
            acnt = self.accounts[code]
            if acnt.place_holder:
                indent = acnt.indent
                balance = 0
                i = self.ordered_codes.index(code) + 1
                while True:
                    if (i >= I
                    or (self.accounts[self.ordered_codes[i]].indent
                                                    <= indent)):
                        self.accounts[code].s_balance = balance
                        break
                    sub_acnt = self.accounts[self.ordered_codes[i]]
                    if not sub_acnt.place_holder:
                        balance += sub_acnt.signed_balance()
                    i += 1

    def load_journal(self, args):
        """
        Posts the journal to the ledger.
        """
        journal = Journal(args)
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
                self.accounts[le['acnt']].line_entries.append(
                                                line_entry)
        dr_check = cr_check = 0  # To check totals balance.
        for code in self.ordered_codes:
            # Populate the accounts with balances, specify Dr or Cr, and
            # do a running total to check that all is in balance.
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
        imbalance = dr_check - cr_check
        if abs(imbalance) > EPSILON:
            print("MAJOR ERROR! Balance sheet doesn't balance!")
            print(" Debits - Credits = {:,.2f}.".format(imbalance))
        self.set_place_holder_signed_balances()
        self.journal_loaded = True

    def show_accounts(self, args):
        """This is the show method currently being used.
        """
        if args['--verbosity'] and not self.journal_loaded:
            self.load_journal(args)
        ret = ["\nLEDGER/CHART of ACCOUNTS:......  Entity: '{}'\n"
            .format(self.entity)]
        for code in self.ordered_codes:
            ret.append(self.accounts[code].dump(args['--verbosity']))
#           print("Signed balance Acnt {}: {:.2f}"
#               .format(code, self.accounts[code].signed_balance()))
        return '\n'.join(ret)

    def show(self, args):
        """
        Return a string representation of the Ledger.
        Parameter args('--verbosity') determines how much
        information is displayed.
        ##############  NOT BEING USED  ################
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
            description: explanation, (a string with imbedded CRs
            line_entries: list of {'acnt', 'DR', 'CR' keyed values},
            )
    We use 'data' (a dict) rather than individual attributes to
    allow persistent storage in a json file.
    """
    
    def __init__(self, entry):
        """
        An instance can be instantiated by providing the dictionary
        directly or by providing an entry number (as a string.)
        In the later case, the user is prompted for data entry.
        """
        if not (type(entry) is dict):   # Not a dict so assume
                                        # it's an entry number
                                        # and turn it into a dict.
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
                    print('Imbalance! Dr - Cr = {:,.2f}. (Entry #{:0>3})'
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
            line_entries.append(dict(acnt= number, DR= dr, CR= cr))
        print("Captured entry # {:0>3}.".format (entry_number))
        return dict(
            number= "{:0>3}".format(entry_number),
            date= date_stamp,
            user= name,
            description= explanation,
            line_entries= line_entries
            )

    def ok(self):
        """
        Checks that a journal entry was actually created and has
        substance.
        """
        return (hasattr(self, 'data')
                and
                self.data['line_entries'])

    def show_line_entry(line_entry):
        """
        Parameter is expected to be a dict with following keys:
        'accnt' (type str,) 'DR', 'CR' (both type float.)
        Note: don't confuse this line entry in the journal
        whith line entries in Chart of Accounts.
        """
        ret = dict(acnt= '{:>8}'.format(line_entry['acnt']),)
        if line_entry['DR']:
            ret['DR'] = '{:>10,.2f}'.format(float(line_entry['DR']))
        else:
            ret['DR'] = '{:>10}'.format(' ')
        if line_entry['CR']:
            ret['CR'] = '{:>10,.2f}'.format(float(line_entry['CR']))
        else:
            ret['CR'] = '{:>10}'.format(' ')
        return ('{acnt:>8}:{DR}{CR}'
                            .format(**ret))

    def show(self):
        """Presents a printable version of a journal entry, more
        specifically, a representation of its only attribute: data which
        is a dictionary.
        Returns None if fails the ok method.
        """
        if not self.ok(): return  # No data atribute or it is empty.
        data = self.data
        ret = []
        ret.append("  #{:0>3} on {:<12} by {}."
            .format(data['number'], data['date'], data['user']))

        description_lines = data["description"].split('\n')
        for line in description_lines:
            ret.append("    {}".format(line))
        for line_entry in data["line_entries"]:
            ret.append(JournalEntry.show_line_entry(line_entry)) 
        return '\n'.join(ret)

class Journal(object):
    """
    Deals with the whole journal, providing methods for loading it from
    persistent storage (__init__,) adding to it (get, load,) and sending
    it back to be stored (save.)
    It keeps track of journal entry numbers, the next one of which is
    kept in persistent storage as part of the metadata for an entity.
    See docstring for __init__ method.
    NOTE: this class's get_entry and show methods rely on 
    JournalEntry methods get_entry and show.
    """

    def __init__(self, args):
        """
        Loads from persistent storage an entity's metadata and
        all journal entries to date in preparation for
        further journal entries or to populate the Ledger.
        The entity comes from args: args[--entity].
        Attributes include:
            entity:
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
        self.entity = args["--entity"]
        dir_name = os.path.join(DEFAULT_HOME, self.entity + '.d')
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

        ret = ["\nJOURNAL ENTRIES:......           Entity: '{}'\n"
#       ret = ["\nJOURNAL ENTRIES:......      Entity: '{}'\n"
            .format(self.entity)]
        for je in self.journal:
            entry = JournalEntry(je)
            ret.append(entry.show())
        return '\n'.join(ret)

    def save(self):
        """Saves journal to persistent storage.
        """
        self.metadata['next_journal_entry_number'] = self.next_entry
        with open(self.journal_file, 'w', newline='') as f_object:
            json.dump({"Journal": self.journal}, f_object)
        with open(self.metadata_file, 'w') as f_object:
            json.dump(self.metadata, f_object)

    def add(self, journal_entry):
        """Adds an instance of JournalEntry to the journal (self.)
        Incriments the next_number attribute at the same time."""
        if journal_entry.ok():
            self.journal.append(journal_entry.data)
            self.next_entry += 1

    def get_entry(self):
        """Used by the get method do add an entry to the the journal.
        Instanciates a JournalEntry and, if it passes its ok method,
        saves its data atribute to the Journal (self.)
        The next_number attribute is updated each time.
        If successful, the JournalEntry instance is returned;
        otherwise None is returned
        """
        new_entry = (
            JournalEntry(self.next_entry))
        if new_entry.ok():
            self.next_entry += 1
            self.journal.append(new_entry.data)
            return new_entry
        # else returns None

    def load(self, text_or_file):
        """<text_or_file> can be either text suitable for journal entry
        or a file name containing such text.  The text must be in the
        same format as in the accompanying files in0, in1, ...
        JournalEntry instances are created and _added_ to the (already
        existing) Journal.
        Note: No user approval mechanism for this form of journal entry.
        """

        def initialize():
            start_new_entry = True
            new_entry =  dict(number= self.next_entry,
                                date= '',
                                user= '',
                                description = [],
                                line_entries= [],
                                )
            return (start_new_entry, new_entry)

        def parse_DrCr_amnt(line):
            part = line.split()
            code = part[0]
            if part[1] == 'Dr':
                dr = float(part[2])
                cr = 0
            elif part[1] == 'Cr':
                dr = 0
                cr = float(part[2])
            else:
                print("Something is wrong!: bad format in {}?"
                        .format(infile))
            return dict(acnt= code,
                        DR= dr,
                        CR= cr)

        journal_entries = []
        start_new_entry, new_entry = initialize()
        if os.path.isfile(text_or_file):
            with open(text_or_file, 'r') as f:
                raw_data = f.read()
        else:
            raw_data = text_or_file
        data = raw_data.split('\n')
        for line in data:
            line = line.strip()
            if not line:
                # Save the description & then save the current entry:
                new_entry['description'] = (
                    '\n'.join(new_entry['description']))
                new_je = JournalEntry(new_entry)
                if new_je.ok():
                    self.add(new_je)
                start_new_entry, new_entry = initialize()
                continue
            if not new_entry['date']: new_entry['date'] = line
            elif not new_entry['user']: new_entry['user'] = line
            elif (not 'Dr' in line) and (not 'Cr' in line):
                new_entry['description'].append(line)
            else:  # Parse acnt Dr/Cr amnt
                new_entry['line_entries'].append(
                                            parse_DrCr_amnt(line))

    def get(self):
        """Gets journal entries from the user.
        Does this using the get_entry method.
        Once user input is completed, checks the next_number attribute
        to see if entries have been made, and if so, confirms with user
        before calling the save method to save them.
        """
        while True:
            entry = self.get_entry()
            if not entry:
                break
        print('next numbers are self {} and metadata {}.'
                .format(self.next_entry,
                self.metadata['next_journal_entry_number']))
        if self.next_entry > self.metadata[
                            'next_journal_entry_number']:
            # Entries have been made; will probably want to save.
            journal_dict = {'Journal': self.journal}
            answer = input("Would you like to save the entries?: ")
            if answer and (answer[0] in 'yY'):
                self.save()
                print('Answer was affirmative.  Journal content:')
                print(self.show())
                print(
                "Journal content as it appears above, has been saved.")


## The following 3 global functions are specific to the Kazan15 entity.

def adjust4assets(chart_of_accounts):
    """This is one of several 'custom' procedures specific to the
    needs of Kazan15.
    Returns a string that can be provided as a parameter to the load
    method of a Journal instance.  Such an entry adjusts the equity and
    liability accounts to reflect the fact that the 'group of 8' own the
    fixed assets but that ownership comes as a cost to them: hence the
    Dr entries against their equity accounts.  See file 'explanation'.
    """
    total2split = 0
    codes2check = [ code for code in chart_of_accounts.ordered_codes
            if (code[:2] == '15') ]
    for code in codes2check:
        acnt = chart_of_accounts.accounts[code]
        if (not acnt.place_holder
        and hasattr(acnt, 'split')):
            assert acnt.split == N_ASSET_OWNERS
            total2split += acnt.signed_balance()
    entries = divider(total2split, 8)
    journal_input = ['August 10, 2015', 'book keeper',
                    'Adjust equity and liability accounts to reflect',
                    "ownership of assets by the 'group of 8'."
                    ]
    for i in range(N_ASSET_OWNERS):
        journal_input.append(
            '20{:0>2} Cr {:.2f}'.format(i + 1, entries[i]))
        journal_input.append(
            '30{:0>2} Dr {:.2f}'.format(i + 1, entries[i]))
    journal_input.append('\n')
    # Need the above CR to satisfy journal entry requirements.
    return '\n'.join(journal_input)
    
def zero_expenses(chart_of_accounts):
    """This is one of several 'custom' procedures specific to the
    needs of Kazan15.
    It's parameter is expected to be a journal populated instance of
    the ChartOfAccounts class.
    It returns text (representing journal entries) that can then be
    added to the journal (using its load method.)  These additional
    entries preform one of the 'custom' requirements described in the
    accompanying 'explanation' file.
    This zero_expenses method depends on the final (otherwise optional)
    'split' field of the expence account.
    Typical usage would be as follows:  load a ChartOfAccounts with
    all the journal entries and run this function with it as the
    parameter. Then load the returned value to the journal and populate
    another chartofaccounts with this updated journal. 
    """
    expenses = {}      # Dict of totals keyed by 'split'
    for code in chart_of_accounts.ordered_codes:
        acnt = chart_of_accounts.accounts[code]
        if (code[:1] == '5') and (not
                    acnt.place_holder):
        # if expense account that isn't a place holder:
            _value = expenses.setdefault(
                        acnt.split, 0)
            expenses[acnt.split] += acnt.signed_balance()
    # expenses[9]: Cr 5001  Dr 3001..3009
    journal_input_ex9 = zero_out(
            ['August 10, 2015', 'book keeper',
            'Distribute expenses among 9 participants.',
            '5001 Cr {:.2f}'.format(expenses[9])],
            '30{:0>2} Dr {:.2f}',
            divider(expenses[9], 9))
    # expenses[10]: Cr 5002  Dr  3001..3010
    journal_input_ex10 = zero_out(
            ['August 10, 2015', 'book keeper',
            'Distribute expenses among 10 participants.',
            '5002 Cr {:.2f}'.format(expenses[10])],
            '30{:0>2} Dr {:.2f}',
            divider(expenses[10], 10))
    # Note: the following join method is used on the empty string rather
    # than a CR because a CR was added to each string in the list by the
    # zero_out method (because journal reading depends on it.
    return ''.join([journal_input_ex9,
                    journal_input_ex10 ])

def check_equity_vs_bank(chart_of_accounts):
    """This is one of several 'custom' procedures specific to the
    needs of Kazan15.
    Checks that the sum of the equity accounts balances against liquid
    assets, in our case, just the bank account.
    Returns a string.
    """
    assets = 0
    codes2check = [ code for code in chart_of_accounts.ordered_codes
            if (code[:2] == '30') ]  # Equity accounts
    for code in codes2check:
        acnt = chart_of_accounts.accounts[code]
        if not acnt.place_holder:
            assets += acnt.signed_balance()
    ret = ["Total assets of participants:  {:.2f}"
                .format(assets)]
    ret.append(
        "...which balances nicely against the total liquid assets...")
    ret.append("... remaining in bank account: {:.2f}"
        .format(chart_of_accounts.accounts['1110'].signed_balance()))
    return '\n'.join(ret)
## End of Kazan15 'custom' functions.


def main():
    args = docopt.docopt(__doc__, version=VERSION)
#   print("Args are:")
#   for arg in args:
#       print("{}: {}"
#           .format(arg, args[arg]))
#   print()
    if args['new']:
        if args['--entity'] == create_entity(args['--entity']):
            print(
        "An accounting system for '{}' has been successfully created."
                        .format(args['--entity']))
    if not args['--entity']:
        with open(os.path.join(DEFAULT_HOME,
                    DEFAULT_Entity), 'r') as entity_file_object:
            args['--entity'] = entity_file_object.read()
    
    if args['test']:
        print("Args are:")
        for arg in args:
            print("{}: {}"
                .format(arg, args[arg]))
        print()
        cofa = ChartOfAccounts(args)
        print(cofa.show_accounts(args))
    
    if args['journal_entry']:
        journal = Journal(args)
        journal.get()

    if args['show_journal']:
        journal = Journal(args)
        print(journal.show())

    if args['show_accounts']:
        cofa = ChartOfAccounts(args)
        cofa.load_journal(args)
        print(cofa.show_accounts(args))

    if args['custom']:
        ret = []
        entity = create_entity(args['--entity'])
        assert args["--entity"] == entity
        journal = Journal(args)  # Loaded from persistent storage.
        for infile in args["<infiles>"]:
            journal.load(infile)
        journal.save()  # Sends journal to persistent storage.

        cofa = ChartOfAccounts(args)
        cofa.load_journal(args)  # Gets journal from persistent storage.

        expense_adjustment = zero_expenses(cofa)
        asset_adjustment = adjust4assets(cofa)

        journal = Journal(args)  # ?unnecessary retrieval?
        journal.load(expense_adjustment)
        journal.load(asset_adjustment)
        cofa = ChartOfAccounts(args)  # A virgin ledger.
        journal.save()

        ret.append(journal.show())

        cofa.load_journal(args)
        ret.append("\n")
        ret.append(cofa.show_accounts(args))
        ret.append('\n')
        ret.append(check_equity_vs_bank(cofa))

        with open("Report", 'w') as report_file:
            report_file.write('\n'.join(ret))

if __name__ == '__main__':  # code block to run the application
    main()

