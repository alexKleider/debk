#!./venv/bin/python
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8
#
# file: 'debk.py'
# Part of ___, ____.

# Copyright 2015 Alex Kleider
#   This program is free software: you can redistribute it and/or
#   modify #   it under the terms of the GNU General Public License
#   as published by the Free Software Foundation, either version 3
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.
#   If not, see <http://www.gnu.org/licenses/>.
#   Look for file named COPYING.
"""
       ******************   debk.py   *****************

       A module that supports double entry book keeping.

This project was inspired by and serves the special accounting
needs of the Kazan15 'group of 10.'[1]  Perhaps it might serve
other needs as well.

The current implementation is driven using the following command:
    ./src/menu.py
Run ./src/menu.py --help for further information.

Usage:
  ./src/debk.py
  ./src/debk.py -h | --help
  ./src/debk.py --version

Options:
  -h --help  Print usage statement.
  --version  Print version.

The first usage is only to run minor tests.
  """

# Clarification of some issues that might otherwise cause confusion:

# Attribute  Class(es)  Values / notes
# ---------  ---------  --------------
# acnt_type  Account    Dr | Cr | place_holder 
#                       / qualifies the account type as
#                       / (asset, income) vs (liab, equity, expense)
# category   Account    ASSETS, LIABILITIES, EQUITY, INCOME, EXPENSES.
# type_      Account    D | C / qualifies the balance attribute.
#            LineItem   / qualifies the amount attribute.
#            LineEntry  / ditto for JournalEntry LineEntrys.

import os
import sys
import csv
import json
import copy
#import shutil
import logging
#import datetime
import src.drcr as drcr
import src.date as date
import src.money as money
import src.config as config
from src.config import DEFAULTS as D

DEBUG = False

logging.basicConfig(level = config.LOGLEVEL)

INDENTATION_CONSTANT = ' ' * config.INDENTATION_MULTIPLIER  

N_ASSET_OWNERS = config.N_ASSET_OWNERS
                     #Must jive with 'split' values in CofAs.
                     #Only used for custom function adjust4assets()
# D = config.DEFAULTS
# Each entity will have its home directory in D['home'].
# create_entity, Journal.__init__ and ChartOfAccounts.__init__ all
# have a named default.dir=D['home'] paramter as a useful override
# when testing.  (See contents of tests/ directory.)

# A minimum of one file specified by D['cofa_template'] is
# expected to be in the D['home'] directory to serve as a template
# during entity creation although a different file can be used: see
# docstring for create_entity().
# D['entity']  - a file specified by this value may also be found in
# the D['home'] directory.  If so and if not an empty file, it 
# provides the name of the last entity accessed to serve as a
# default.

# D['cofa_name']         | These three files will be
# D['journal_name']      | in the home directory of
# D['metadata_name']     | each newly created entity.

NotesAboutAccountCodes = """
During development: Account codes each consisted of 4 digits,
with the first digit being one of the following:
1 for Asset
2 for Liability
3 for Equity
4 for Income, and 
5 for Expense accounts respectively.
The config.py is now structured in such a way that this can be
changed.  If you wish to change to a different code schema, the
global functions that are 'custom' for the Kazan15 entity
(adjust4assets, zero_expenses, check_equity_vs_bank) will not
work properly.  This is documented in each of these functions'
docstring.
"""

def convert2dict(an_object):
    """
    Returns a dictionary keyed by all attributes of an_object not
    prefaced with an underscore. (Uses the vars() built-in.)
    """
    return {key: vars(an_object)[key]
            for key in vars(an_object)
                if key[:1] != '_'}

def show_args(args, name = 'Arguments'):
    """                     [../tests/test1.py: global_show_args]
    Returns a string displaying args, which can be any iteration
    supporting collection including dictionary like objects (ones
    that implement an items() method.)
    """
    def show_l():
        return('  {}'.format(arg))
    def show():
        return('  {}: {}'.format(arg, args[arg]))
    try:
        args.items()  # See if it quacks like a dictionary.
    except AttributeError:
        show = show_l
    ret = ["{} are ...".format(name)]
    for arg in args:
        ret.append(show())
    ret.append('  ... end of report.\n')
    return '\n'.join(ret)

def none2float(n):
    """                     [../tests/test1.py: none2float.
    Solves the need to interpret a non-entry as zero.
    """
    if not n: return 0.0
    else: 
        try:
            return float(n)
        except ValueError:
            logging.critical(
                    "Attempting to create a float out of '{}'."
                        .format(n))
            raise

def divider(dollar_amount, split):
    """                                [../tests/test1.py: divider
    Attempts to divide 'dollar_amount' into 'split' equal parts.
    Returns a 'split' long list of floats.  Expects 'dollar_amount'
    to be a float, 'split' to be an int.  Works to the nearest penney.
    When equal amounts are not possible, if dollar_amount is positive,
    the first numbers in the list will be greater than the last by
    one; if negative, it's the ending numbers that are greater.
    An assertionError is raised if the sum of the list is not equal
    to 'dollar_amount'.  This occurs if split is negative.
    Behaves sensibly with negative dollar_ammount in wich case left
    over is added from end rather than beginning of resulting list.
    """
    try:   # money as float or string => pennies/int
        dollars = float(dollar_amount)  # Might come in as a string.
    except ValueError:
        logging.critical("Bad 1st param: divider({}, {})"
            .format(dollar_amount, split))
        raise
    dividend = round(dollars * 100)
    if split <=0:
        logging.critical(
        "Bad 2nd param (not a positive int): divider({}, {})"
            .format(dollar_amount, split))
    quotient, rem = divmod(dividend, split)
    ret = []  # Prepare to create a list with 'split' entries.
    for n in range(1, split + 1):
        if n > rem:  # Assign quotient (remainder 'used up.)
          ret.append(quotient/100.0)
        else:  # Still need to 'use up' remainder.
            ret.append((quotient + 1)/100.0)
    assert (abs(dollars)-abs(sum(ret)))<config.EPSILON  # Sanity chk.
    return ret

# The following two functions would be better placed in in
# src.config but are being kept here because they use the
# logging module.
def valid_account_type(type_):
    """     tested in tests/test1 class ValidAccountType
    Checks validity of an account type:
    i.e. checks that it is a string beginning with one of the
    letters in [DdCc]: interpretable as either Debit or Credit.
    NOTE: does not treat place_holder as a valid account type.
    See the docstring for src.config.
    """
#   print("\nCalling valid_account_type({})".format(type_))
    if (type_
    and isinstance(type_, str)
    and (type_[:1].upper() in "DC")):
#       print("Call to valid_account_type({}) returning True"
#           .format(type_))
        return True
#   print("Call to valid_account_type({}) returning False"
#           .format(type_))
    logging.critical(
        "Invalid account type: '%s'", type_)
    return False

def acnt_type_from_code(account_code):
    """             [../tests/test1.py: AcntTypeFromCode]
    Attempts to return the account type, either 'Dr' or 'Cr' 
    determined by the account's code/number.
    Logs and returns None if code is malformed.
    Later processing may change an Account's type to
    'place_holder'.
    Used to set the Account attribute acnt_type.
    Depends on src.config to define account types.
    See the docstring for src.config.
    """
    first = account_code[:1]
    if first in config.DR_FIRSTS:    # Assets and Expenses
        return('Dr')
    elif first in config.CR_FIRSTS:  # Liability, Equity, Income
        return('Cr')
    logging.critical(
        "Malformed account code: '%s'", account_code)

#####  END OF HELPER FUNCTIONS  #####


## Ledger related classes:  LineItem, Account, ChartOfAccounts ##

class LineItem(object): 
    """                        [../tests/test1.py: LineItem] 
    Instances are collected from JournalEntry LineEntry objects and
    are used to populate the line_items array attribute of
    instances of the Account class.
    Each instance has the following attributes:
        number: a journal entry number: discoverable from Journal
        amount: monitary value   }|  Both discoverable from
        type_:  specify Dr or Cr }|  a JournalEntry instance.
    Do NOT confuse this class with Journal LineEntry entries.
    """
    
    def __init__(self, entry_number, type_, amount):
        """
        entry_number: journal entry number.
        type_: 'D'(ebit or 'C'(redit. 
        amount: float.
        """
#       print("\n Running LineItem({}, {}, {})"
#                   .format(entry_number, type_,amount))
#       print(
#       "Calling LineItem.__init__ with type_ '{}'".format(type_))
        if not (valid_account_type(type_)):
            logging.critical(
                "Calling LineItem.__init__ with bad type_: '{}'"
                .format(type_))
        self.entry_number = int(entry_number)
        self.amount = float(amount)
        self.type_ = type_[:1].upper()

    def show(self):
        """
        Returns a _one_line_ string representation of a LineItem
        instance.
        Any required indention can be handled by the client code.
        """
        if self.type_ == 'D': dr = '{:>12.2f}Dr'.format(self.amount)
        else: dr = '{:>14}'.format(' ')
        if self.type_ == 'C': cr = '{:>12.2f}Cr'.format(self.amount)
        else: cr = '{:>14}'.format(' ')
        return ("  je#{:0>3}{}{}"
                .format(self.entry_number, dr, cr))

    __str__ = show

class Account(object):
    """              [../tests/test1.py: CreateAccount,
                        Account_empty, Account_loaded
                        Account_signed_balance]
    Provides data type for values of the dict
    ChartOfAccounts.accounts which is keyed by account code.
    Attributes include: 
    1. from csv file:   code, indent, full_name, name, notes,
                        hidden, place_holder, split, 
    2. derived:   balance, line_items,
        s_balance, signed_balance,  
        (depending if place_holder, see below)
        type_: specifies if the balance is a D(ebit or C(redit,
                set to the empty string if there is no balance.
        acnt_type: 'Dr' if debits are positive,
                   'Cr' if credits are positive,
                or 'place_holder'.
    Place holder accounts will have the attribute s_balance (summed)
    depending on their acnt_type: 'D' totals in 'Cr' accounts
    and 'C' totals in 'Dr' accounts will be shown as negative.
    Non place_holder accounts have the signed_balance property to
    return the corresponding (signed) value.
    """

    def __init__(self, dict_from_csv):         # Account
        """                  [../tests/test1.py: CreateAccount]
        Accepts dict delivered by csv module as its parameter.
        code,indent,type,full_name,name,hidden,place_holder,split
        """
        dict_from_csv['code'] = dict_from_csv['code'].strip()
        self.code = dict_from_csv['code']
#       print("dict_from_csv => {}"  # debugging print
#                   .format(dict_from_csv))
        self.category = config.account_category(self.code)
        self.indent = INDENTATION_CONSTANT * int(
                                    dict_from_csv['indent'])
        self.full_name = dict_from_csv['full_name']
        self.name = dict_from_csv['name']
#       self.notes = dict_from_csv['notes']  # removed from csv
        self.hidden = dict_from_csv['hidden']
        if dict_from_csv['place_holder'] in 'Tt':
            self.place_holder = True 
            self.header = 'Header'
            self.acnt_type = 'header'
        elif dict_from_csv['place_holder'] in 'Ff':
            self.place_holder = False 
            self.header = ''
            self.acnt_type = acnt_type_from_code(self.code)  #'Dr''Cr'
        else:
            self.place_holder = None
            logging.critical(
                    "Problem with Acnt %s: Place holder or not??",
                            self.code)
        #> 'split' value exists only for custom needs.
        split = dict_from_csv.setdefault('split', 0)
        if split:  # 'split' was specified.
            self.split = int(split)
            self.split_as_str = "(/{})".format(self.split)
        else:  # 'split' was not specified, already set to 0.
            self.split_as_str = ''
        # End of attributes derived from dict_from_csv.
        #self.line_items = []  # list of LineItem objects.
        self.balance = 0
        self.type_ = ''  # Set to empty string if balance is 0.
                        # Specifies if the balance is 'D' or 'C'
        self.s_balance = 0  # This attribute is populated by the
                            # _set_place_holder_signed_balances method
                            # of the ChartOfAccounts class and
                            # applies only to place_holder accounts.
        self.line_items = []

    @property
    def signed_balance(self):
        """                [../tests/test1.py: Account_signed_balance]
        Checks (based on its code) if an account's balance is positive
        or negative and returns the balance appropriately signed.
        REFACTOR TO USE category INSTEAD OF code ATTRIBUTE.
        """
        #  If nothing in account, not to worry:
        if (self.balance < config.EPSILON or 
        #  Asset and Expense accounts are Debit accounts:
        (self.code[:1] in config.DR_FIRSTS and self.type_ == 'D')
        #  Liability, Equity and Income accounts are Credit accounts:
        or (self.code[:1] in config.CR_FIRSTS and self.type_ == 'C')
        ):
            logging.debug(
                "Accnt %s%s has the appropriate Dr/Cr balance: %.2f",
                    self.code, self.type_, self.balance)
            return self.balance  # As it should be.
        else:
            logging.debug(
                "Accnt %s%s has a NEGATIVE Dr/Cr balance:      %.2f",
                    self.code, self.type_, self.balance)
            return self.balance * -1

    @property
    def _dict(self):
        """
        Returns a dictionary representation of an Account.
        It is used to format output for reports and
        to create json files.
        Could use global function convert2dict() but for now choosing
        not to because it would include a lot that is not needed.
        """
        return dict(code= self.code,
                    indent= self.indent,
                    full_name= self.full_name,
                    name= self.name,
#                   notes= self.notes,
                    header= self.header,

                    balance= self.balance,
                    type_= self.type_,
                    s_balance= self.s_balance,  # Place holders only!
                    acnt_type= self.acnt_type,
                    category= self.category,

                    split= self.split,
                    split_as_string = self.split_as_str,
                    )

    def show_account(self, verbosity = config.DEFAULT_VERBOSITY):
        """   Indirectly tested in tests/test1 class Ledger.setUp-
                            must examine TestReport.
        Returns a string representation of an account.
        Assigned to __str__.
        What is shown depends on verbosity which is determined
        by the value of /src/config.DEFAULTS['verbosity'] which 
        defaults to 2 but can be can be set by the CLI and within
        the src/menu.py menu.
        See src/config.py for details of what each verbosity level
        means.
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
        # Assign 2nd part of first line- depending if place_holder:
        has_balance = False
        if self.place_holder:
            if self.s_balance:
                has_balance = True
            ret.append(
                "{} {} (Title_Account) subtotal: {:.2f}".
                format(
                    self.full_name.upper(),
                    self.split_as_str,
                    self.s_balance))
        else: 
            if self.balance:
                has_balance = True
                type_ = self.type_ + 'r'
            else:
                type_ = ''
            ret.append("{:<15} {} Total:{:>10.2f}{}"
                    .format(
                            self.name,
                            self.split_as_str,
                            self.balance,
                            type_))
        # Join the two parts to complete the first (header) line:
        ret = [' '.join(ret)]

        if verbosity > 1: # Add the line entries:
            for line_item in self.line_items:
                ret.append('{}{}'.format(self.indent,
                                        line_item.show()))

        # Put it all together and return it:
        if (verbosity > 3) or (has_balance):
            return '\n'.join(ret)
        else:
            return ''

    __str__ = show_account


    def update_balance(self):
        """
        Traverses line_items to populate the balance and type_
        attributes.  Accounts (all the place holder accounts for
        sure) with no entries will continue to have their
        type_ attribute set to the empty string.  (It is only for
        display purposes that place holders have a balance assigned,
        and this is done by the show method of ChartOfAccounts.)
        Note: the line_items themselves are populated by the
        ChartOfAccounts load_journal_entries method.
        """
        if self.place_holder == 'T':
            return  # Defaults have already been set.
        totals = dict(D= 0, C= 0)
        for line_item in self.line_items:
            if line_item.amount:
                totals[line_item.type_] += line_item.amount
        if (totals['D'] - totals['C']) > config.EPSILON:
            self.balance = totals['D'] - totals['C']
            self.type_ = 'D'
        elif (totals['C'] - totals['D']) > config.EPSILON:
            self.balance = totals['C'] - totals['D']
            self.type_ = 'C'
        else:  
            assert self.balance == 0.0
            self.type_ = ''

class ChartOfAccounts(object):
    """
    A class to manage an entity's chart of accounts (AKA the Ledger.)
    Instantiation loads a CSV file without any accounting information.
    The load_journal_entries method populates the accounts.
    The 'show' method returns text displaying the accounts in a way
    determined by the 'verbosity' parameter:
        0: Listing if the accounts only.
        1: Accounts with totals.
        2: Accounts with all entries affecting each account.
    Zeroing out of the temporary (Expenses and Income) accounts is for
    now being left for the user to do using journal entries.
    """

    # The following is used only by zero_temporaries, one of the
    # custom functions and therefore should be moved there unless
    # used elsewhere.
    format_line = "{}{:>10}{:^10}{:^10}{}{}"
#                                        ^
#                  ^ Journal entry number

    def __init__(self, defaults=D):
        """
        Loads the chart of accounts belonging to a specified entity.
        The accounts attribute is a dict keyed by account codes and
        values are instances of the Account class.
        No accounting information comes in with instantiation.
        Use the load_journal_entries method after instatiation in
        order to populate the accounting information.
        """
        self.defaults = defaults
        self.entity = defaults['entity']
        self.verbosity = defaults['verbosity']
        self.home = os.path.join(D['home'], self.entity  + '.d')
        self.cofa_file = os.path.join(self.home, D['cofa_name'])
        self.csv_dict = {}  # Keyed by account number ('code'.)
        self.code_set = set()
        try:
            with open(self.cofa_file, 'r') as cofa_file_object:
                reader = csv.DictReader(cofa_file_object)
                for row in reader:
#                   logging.debug(
#                       show_args(row, 'CofA input line values'))
                    row['code'] = row['code'].strip()
                    if row['code'] in self.code_set:
#                       print(   # debugging print
#               "Duplicate account code:{}; Fix before rerunning.."
#                               .format(row['code']))
                        logging.error(
                "Duplicate account code:%s; Fix before rerunning..",
                                row['code'])
                        sys.exit()
                    self.code_set.add(row['code'])
                    self.csv_dict[row['code']] = row
        except FileNotFoundError:
            logging.critical("%s\n%s '%s' %s",
                "File not found attempting to initialize a Ledger.",
                "Perhaps entity", self.entity,
                "has not yet been created.")
            sys.exit(1)
        self.ordered_codes = sorted([key for key in self.code_set])
#       logging.debug(self.ordered_codes)
        self.accounts = {key:
                Account(self.csv_dict[key]) for key in self.code_set}
        # The accounts attribute is not fully populated until if and
        # when needed.  This is done using the load_journal_entries()
        # method.

    def _dict(self):
        """
        Returns a dictionary with one key ("ledger") value pair:
        The value is an ordered (by account code) list of all the
        Account instances in the ledger
        """
        list_of_accounts = [self.accounts[key]
                    for key in self.ordered_codes]
        return {"ledger": [self.accounts[key]
                    for key in self.ordered_codes]
            }
              
    def balance_sheet_account_codes(self):
        """
        Returns a tuple of two ordered lists of account codes.
        The first contains the income account codes, and
        the second contains the expense account codes.
        """
        return dict(
        income= [code for code in self.ordered_codes if code[:1]
                    == config.ACCOUNT_CATEGORIES["INCOME"][:1]],
        expense= [code for code in self.ordered_codes if code[:1]
                    == config.ACCOUNT_CATEGORIES["EXPENSE"][:1]],
        )

    def _set_place_holder_signed_balances(self):
        """
        Iterates through the accounts setting the signed_balance
        attribute for each of the place_holder accounts.
        A private method used only by load_journal_entries method.
        """
#       print("Running _set_place_holder_signed_balances...")
        I = len(self.ordered_codes)  # Don't index here or beyond.
        for code in self.ordered_codes:
            acnt = self.accounts[code]
            if acnt.place_holder:
#               print("..Considering account code: {}"
#                       .format(code))
                indent = acnt.indent
                acnt.s_balance = 0
                i = self.ordered_codes.index(code) + 1
                while True:
                    if (i >= I
                    or (self.accounts[self.ordered_codes[i]].indent
                                                    <= indent)):
                        break  # out of while loop.
                    sub_acnt = self.accounts[self.ordered_codes[i]]
#                   print("....Checking #{}"
#                           .format(self.ordered_codes[i]))
                    if not sub_acnt.place_holder:
#                       print("....it is a place holder so adding {}"
#                               .format(sub_acnt.signed_balance))
                        acnt.s_balance += sub_acnt.signed_balance
                    i += 1

    def load_journal_entries(self, list_of_journal_entries): 
        """
        LineItem => LineEntrys
        Posts journal entries to the ledger.
        """
        # Populate accounts with entries...
        for je in list_of_journal_entries:
            for line_entry in je.line_entries:
                if line_entry.account_code not in self.code_set:
                    logging.error(
                    "Journal entry #%s: unrecognized AcntCode '%s'.",
                        je.entry_number, line_entry.account_code)
                else:
                    self.accounts[
                    line_entry.account_code].line_items.append(
                            LineItem(je.entry_number,
                                        line_entry.type_,
                                            line_entry.amount,
                                    )                         )
        # All jounal entries have now been posted but
        # the ledger still needs to be 'cleaned up.'
        totals = dict(d= 0, c= 0)
        for code in self.ordered_codes:
            # Populate the accounts with balances, specify Dr or Cr,
            # and do a running total to check that all is in balance.
            account = self.accounts[code]
            account.update_balance()  # Ignores place holder accounts.
            if (account.acnt_type != 'place_holder'
            and account.type_
            and account.type_ in 'dc'):
                totals[account.type_] += account.balance
        imbalance = totals['d'] - totals['c']
        if abs(imbalance)>config.EPSILON:
            logging.critical(
                "Balance sheet out of balance: Dr - Cr = %.2f.",
                        imbalance)
        self._set_place_holder_signed_balances()

    def sum_accounts(self, account_codes):
        """        -test: see class Ledger in tests/test1.py
        Parameter can be a list of account_codes (as numbers or
        strings) or a string with two account codes separated by a
        dash (-) representing a range of accounts.
        Returns the sum of all the non place holder balances.
        Cr values are considered negative if in a Debit account and
        Dr values are considered negative if in a Credit account.
        self.sum_accounts(4000-5999) will return Net Income.
        """
#       print("Calling ChartOfAccounts.sum_accounts({})."
#                   .format(account_codes))
        if isinstance(account_codes, str):
            split = account_codes.split(
                            config.ACCOUNT_RANGE_INDICATOR)
            codes = []
            if len(split) != 2:
                logging.critical(
            "ChartOfAccounts.sum_accounts({}): bad parameter."
                        .format(account_codes))
                return 0
            first = int(split[0])
            last = int(split[1])
            for code in self.ordered_codes:
              if int(code) >= first and int(code) <= last:
                  codes.append(code)
        elif isinstance(account_codes, list):
            codes = account_codes
        else:
            logging.critical(
            "ChartOfAccounts.sum_accounts({}): bad parameter."
                        .format(account_codes))
        ret = 0
        for code in codes:
            acnt = self.accounts[str(code)]
            if not acnt.place_holder:
                ret += acnt.signed_balance
#               print("Adding balance for acnt#{}: {:.2f}"
        return ret

    def get_net_income(self):
        return  (self.sum_accounts(config.INCOME_RANGE)
                - self.sum_accounts(config.EXPENSE_RANGE))

    def show_accounts(self):
        """Returns a string representation of the Ledger.
        """
        ret = ["\nLEDGER/CHART of ACCOUNTS:......  Entity: '{}'\n"
            .format(self.entity)]
        for code in self.ordered_codes:
            text2show = (
                    self.accounts[code].show_account(self.verbosity))
            if text2show: ret.append(text2show)
#           logging.debug("Signed balance Acnt %s: %.2f",
#               code, self.accounts[code].signed_balance)
        ret.append("\nNET INCOME: ${:.2f}"
                .format(self.get_net_income()))
        return '\n'.join(ret)

    def show_balance_sheet(self, date):
        """Returns the balance sheet as a string.
        """
        ret = ["{:^60}".format(self.entity),
               "{:^60}".format("Balance Sheet"),
               "{:^60}".format(date),
            ]
        for code in self.ordered_codes:
            if account_category(code) in config.BALANCE_SHEET_ACCOUNT:
                text2show = (
                        self.accounts[code].show_account(self.verbosity))
                if text2show: ret.append(text2show)
    #           logging.debug("Signed balance Acnt %s: %.2f",
    #               code, self.accounts[code].signed_balance)
        return '\n'.join(ret)

    def show_income_statement(self,
                              begin = config.FISCAL_YEAR_BEGIN,
                                end = config.FISCAL_YEAR_END):
        """Returns the income statement as a string.
        """
        fiscal_period = "For Fiscal Period {} to {}".format(
                                                begin, end),
        ret = ["{:^60}".format(self.entity),
               "{:^60}".format("Income Statement"),
               "{:^60}".format(fiscal_period),
            ]
        for code in self.ordered_codes:
            if account_category(code) in config.INCOME_STATEMENT_ACCOUNT:
                text2show = (
                        self.accounts[code].show_account(self.verbosity))
                if text2show: ret.append(text2show)
    #           logging.debug("Signed balance Acnt %s: %.2f",
    #               code, self.accounts[code].signed_balance)
        return '\n'.join(ret)
        return ret

def total_reversal(self, account_category, total):
    """
    Returns a list of <LineEntry>s to zero out all 
    account_category accounts and adds the balance of 
    each to total.  << A SIDE EFFECT!!
    """
    line_entries = []
    for code in self.balance_sheet_account_codes[account_category]:
        acnt = self[code]
        balance = acnt.balance
        if (acnt.type_[:1] in 'DC') and (balance):
            total += balance
            line_entries.append(LineEntry(code, drcr, balance))
    return line_entries


#The following classes pertain to the journal:

class LineEntry(object):
    """
    ineEntry: the individual line_entries of each JournalEntry.
    Attributes are account_code, type_ (dr or cr), and amount.
    type_ is converted to 'D' or 'C'.
    Provides the following methods:
    _dict: @property- returns a dict (for json compatibility.)
    show == __str__
    list_from_text: a class method, returns a list of instances
    get_LineEntry: a class method, interactively returns an instance.
    balanced_LineEntry_list: a class method, returns True or False.
    """

    def __init__(self, account_code, type_, amount):
        """
        Does validity checking.
        """
        assert config.valid_account_code(account_code)
        self.account_code = account_code
        self.type_ = type_[:1].upper()
        assert self.type_ in 'DC'
        try:
            self.amount = float(amount)
        except ValueError:
            logging.warning("LineEntry({}, {}, {}), bad last param."
                .format(account_code, type_, amount))
            raise

    def __eq__(self, other):
        return (self.account_code == other.account_code
            and self.type_ == other.type_
            and self.amount == other.amount)

    @classmethod     # LineEntry
    def old_list_from_text(cls, line):
        """     
        Accepts a string with the following three white space
        separated components: account_code, type_, & amount.
        The <account_code> component may be a comma separated
        (no whitespace) list of <account_code>s. (For example
        "1010,1011,1012 Cr 4.50") in which case the the currency
        amount is divided (as evenly as possible) between the
        accounts listed.
        The components can appear in any order.
        Returns a list of LineEntry instances (or None if parsing
        is unsuccessful.)
        """
        if not line: return
        ret = []
        money_pull = pull_money(line,
                currency_name = D["currency"],
                debug=False)
        if money_pull is None:
            logging.warning(
        """Malformed LineEntry entry line- 1st test: no dollar amount.
...line was: {}""".format(line))
            return
        value, span = money_pull
        remaining_line = line[:span[0]] + line[span[1]:]
        parts = remaining_line.split()
        if len(parts) != 2:
            logging.warning(
        """Malformed LineEntry entry line- $ OK but wrong # of params.
...line was: {}""".format(line))
#           print("'parts' consisted of {}"
#               .format(parts))
            return
#-----------------------------------------------------------
        if valid_account_type(parts[0]):
            type_part = parts[0]
            codes_part = parts[1]
        elif valid_account_type(parts[1]):
            code_part = parts[0]
            type_part = parts[1]
#-----------------------------------------------------------
        else:
            logging.warning(
    """Malformed LineEntry entry line- bad type (not Dr or CR.)
...line was: {}""".format(line))
            return

        code_parts = code_part.split(',')
        amnt_parts = divider(value, len(code_parts))
        for (code_part, amnt_part) in zip(code_parts, amnt_parts):
            ret.append(LineEntry(code_part, type_part, amnt_part))
        return ret

    @classmethod     # LineEntry
    def list_from_text(cls, line):
        """     
        Accepts a string with the following three white space
        separated components: account_code, type_, & amount.
        The <account_code> component may be a comma separated
        (no whitespace) list of <account_code>s. (For example
        "1010,1011,1012 Cr 4.50") in which case the the currency
        amount is divided (as evenly as possible) between the
        accounts listed.
        All three compoenets are identified using RegEx.
        The components can appear in any order.
        Returns a list of LineEntry instances (or None if parsing
        is unsuccessful.)
        """
        if not line: return
        abort = False
        ret = []
        value = money.get_currency_value(line,
                debug=DEBUG)
        accounts = config.get_list_of_accounts(line)
        type_ = drcr.drcr(line)
        for item, report in (
                (value, "no dollar amount"),
                (accounts, "no account(s) entered"),
                (type_, "no 'Dr' or 'Cr' given"),
                ):
            if item is None:
                logging.warning(
"""Malformed LineEntry entry line- ({}).
...line has {}""".format(line, report))
                abort = True
        if abort == True:
            return
        
        values = divider(value, len(accounts))
        for (account, value) in zip(accounts, values):
            ret.append(LineEntry(account, type_, value))
        return ret

    @property       # LineEntry
    def _dict(self):
        """
        Returns a dictionary representation of a LineEntry.
        """
        return dict(account_code=self.account_code,
                    amount=self.amount,
                    type_=self.type_)

    def show(self):
        """
        Returns a string version of a LineEntry instance.
        Output format puts account type_ at end.
        """
        if self.type_ == 'D': spacer = 12
        if self.type_ == 'C': spacer = 26
        format_string = "      {{}}:{{:>{}.2f}}{{}}r".format(spacer)
        return format_string .format(self.account_code,
                                    self.amount,
                                    self.type_)
    def __str__(self):
        return self.show()

    def get_LineEntrys(indent=0):
        """
        Interactively prompts the user for a LineEntry.
        Returns a list of instances (usually only one),
        None if unsuccessful.
        Returns a list to allow for possibility of multi-account 
        input format.
        """
        return LineEntry.list_from_text(input(
            config.LineItem_input_format
                    .format(" " * indent)))

    @classmethod       # LineEntry
    def balanced_LineEntry_list(cls, list_of_LineEntrys):
        """
        Returns True if list_of_LineEntrys is balanced.
        i.e. if Debits equal Credits.  Else returns False.
        Used for sanity checking.
        """
        totals = dict(D= 0,
                      C= 0)
        for line_entry in list_of_LineEntrys:
#           print(             # debugging print
#               "line_entry is type '{}': '{}'"
#               .format(type(line_entry), line_entry))
            totals[line_entry.type_] += line_entry.amount
        return (totals['D'] - totals['C']) < config.EPSILON

class JournalEntry(object):
    """
    JournalEntry objects have the following attributes:
            entry_number: int but displayed as a formatted string.
            date_stamp: date_stamp,  # string- any format
            user: name,  # person making the journal entry
            description: explanation, # string with imbedded '\n's.
            line_entries: list of LineEntry objects
                (need conversion to dict to fit json format)
    We use the _dict property to convert to json format.
    Provides the following methods:
    _dict: @property- returns a dict (for json compatibility.)
    from_dict: converse of _dict- takes dict, returns instance.
    show == __str__
    get_JournalEntry: interactive class method, returns an instance.
    """
    
    def __init__(self,  entry_number,
                        date_stamp,
                        user,
                        description,
                        line_entries  # list of LineEntry instances
                        ):
        """
        Creates a JournalEntry instance from its 5 parameters.
        """
        self.entry_number = int(entry_number)
        self.date_stamp = date_stamp
        self.user = user
        self.description = description
        self.line_entries = line_entries

    def show(self):
        """
        Presents a printable version of a journal entry.
        """
        _dict = self._dict
        ret = []
        ret.append(
            "  #{entry_number:0>3} on {date_stamp:<12} by {user}."
            .format(**_dict))

        description_lines = _dict["description"].split('\n')
        for line in description_lines:
            ret.append("    {}".format(line))
        for line_entry in _dict["line_entries"]:
            ret.append(LineEntry(**line_entry).show())
        return '\n'.join(ret)

    def __str__(self):
        return self.show()

    @property       # JournalEntry
    def _dict(self):
        """
        Returns a dictionary representation of a JournalEntry.
        """
        return dict(entry_number=self.entry_number,
                    date_stamp=self.date_stamp,
                    user=self.user,
                    description=self.description,
                    line_entries=[
                        item._dict for item in self.line_entries],
                    )

    @classmethod       # JournalEntry
    def from_dict(cls, _dict):
        """      a classmethod
        Takes the dict version and returns an instance.
        Need this because list of LineEntry objects must
        also be converted from corresponding dicts.
        """
#       print("Calling JournalEntry.from_dict(_dict) on:\n{}"
#               .format(_dict))
        dict_copy = copy.deepcopy(_dict)
        # Make a copy to prevent side effect.
        dict_copy["line_entries"] = [
                LineEntry(**item) for item in _dict["line_entries"]]
        return JournalEntry(**dict_copy)

    @classmethod       # JournalEntry
    def get_JournalEntry(cls):
        """
        An interactive class method: prompts the user for and returns
        a JournalEntry instance (with entry_number set to 0.)
        Returns None if unsuccessful.   (a UI controller in the mvc
        model?)
        Usage:
        Empty 'date_stamp' line terminates (None is returned.)
        Two empty account number entries in the face of an imbalance
        will also terminate (None is returned.) 
        A valid entry is returned following a single blank line_entry
        so long as debits and credits balance (else None is returned.)
        """
        print("""
    A journal entry must include a date, a user ID, a transaction
    description (more than one line is OK, an empty line terminates
    description entry) and a list of line items each consisting of the
    following three white space separated values: 
    {}.
    Debit and credit values must balance. Empty line terminates.""" 
                        .format(config.LineItem_input_prompt))
        while True:
            date_stamp = input("""
        Date (Month, day, year format please): """)
            if not date_stamp:  # Empty 'date_stamp' line terminates
                print()
                return
            date = date.check_date(date_stamp)
            if date:
                date_stamp = date
                break
            else:
                print("!!!! Invalid date entry- please try again.")

        user = input("        Your ID: ")
        description_array = []
        while True:  # Allow multiline transaction description.
            description_line = input("        Description: ")
            if not description_line: break
            description_array.append(description_line)
        description = '\n'.join(description_array)
        line_entries = []
        blanks = 0   # Keep track of blank entries.
        while True:  # Allow multiple account entries, all balanced.
            line_entry_s = LineEntry.get_LineEntrys(indent=8)
            if line_entry_s is None:
                blanks += 1
            else:
                line_entries.extend(line_entry_s)
                blanks = 0
            if (blanks >= 1 
            and LineEntry.balanced_LineEntry_list(line_entries)):
                return JournalEntry(**dict(
                            entry_number= 0,
                            date_stamp= date_stamp,
                            user= user,
                            description= description,
                            line_entries= line_entries))
            if blanks >= 2:
                return
 
    @classmethod    # JournalEntry
    def load(cls, text_or_filename):
        """     
        Accepts properly formatted text or the name of a file
        containing such text. (A batch controller in the mvc model?)
        IF SUCCESSFUL: Returns a list of JournalEntry instances
        all with their <entry_number>s set to zero.
        (<entry_number>s will be set appropriately when the list
        is appended to the Journal instance.)
        The text must be in a specific format described in
        'how2input' and exemplified in 
        'debk/tests/debk.d/testEntityJournal_input0'.
        NB: There is noo user approval mechanism for this form of
        journal entry.
        """

        def initialize():                                  # Helper
#           print(  # debugging print                      # func.
#               "Initializing a new journal_entry dict.")  #
            return  dict(entry_number= 0,                  #
                        date_stamp= '',                    #
                        user= '',                          #
                        description = [],                  #
                        line_entries = [],                    #
                        )                                  #

        if os.path.isfile(text_or_filename):               # collect
            with open(text_or_filename, 'r') as f:         # text
                raw_data = f.read()                        # i.e.
        else:                                              # raw
            raw_data = text_or_filename                    # data
        data = raw_data.split('\n')                        #

        ret = []   # To collect journal_entries.

        # Initialize what will potentially be the first entry...
        new_dict = initialize()

        for line in data:
            line = line.strip()
            if not line:  # Blank line.
                # Assume have collected a journal entry so ...
                # save the description & then save the entry:
#               print(  # debugging print
# "Empty line being processed: assume an entry has been collected...")
                new_dict['description'] = (
                    '\n'.join(new_dict['description']))
                new_je = JournalEntry(**new_dict)
#               print(  # debugging print
#                   "\nEntry being considered: ".format(new_je))
                if new_je.ok():
#                   print(  # debugging print
#                       "JE passed: {}".format(new_je.show()))
                    ret.append(new_je)
                else:
                    pass
#                   print(  # debugging print
#                   "Expect to fail after last JE is collected.")
                new_dict = initialize()
                continue
            # Not a blank line.
            if not new_dict['date_stamp']:
#               print(  # debugging print
#                  "setting date_stamp to '{}'".format(line))
                new_dict['date_stamp'] = date.check_date(line)
            elif not new_dict['user']:
#               print(   # debugging print
#                  "setting user to '{}'".format(line))
                new_dict['user'] = line
            elif not drcr.drcr(line):
#               print(  # debugging print
#                  "Appending description: '{}'".format(line))
                new_dict['description'].append(line)
            else:  # Parse LineEntry
                # Note: might be of the form 1010,1011,1012 Cr 4.50
#               print("DEBUG: line: '{}'.".format(line))
#               print(LineEntry.list_from_text(line).show())
                for line_entry in LineEntry.list_from_text(line):
#                   print("DEBUG: line OK: '{}'.".format(line))
                    if isinstance(line_entry, LineEntry):
#                       print( # debugging pr
#                           "Got a LineEntry: '{}'".format(line_entry))
                        new_dict['line_entries'].append(line_entry)
                    else:
                        pass
#                       print(   # debugging print
#               "Expect to fail after last line_entry is collected.")
#       if not ret:   # next 6 lines debugging print
#           print("\nJournalEntry.load on '{}' => {} (nothing!)"
#                   .format(text_or_filename, ret))
#       else:
#           for journal_entry in ret:
#               print("\n{}".format(journal_entry.show()))
        return ret

    def ok(self):
        """             Tested in ./tests/test2.py JournalEntryTests
        A rigorous self check of a JournalEntry instance.
        """
#       print(show_args(self._dict, 'JournalEntry.ok()'))
        if (isinstance(self.entry_number, int)
        and isinstance(self.date_stamp, str)
        and self.date_stamp
        and isinstance(self.user, str)
        and self.user
        and isinstance(self.description, str)
        and self.description
        and self.line_entries
        and LineEntry.balanced_LineEntry_list(self.line_entries)):
            return True
        else:
            print("""Rejecting journal entry:
{}
^^^^^^^^^^ Some rejections are OK (i.e. blank entries.) ^^^^^^^^^^"""
                .format(self.show()))
            return False

class Journal(object):
    """
    Deals with the whole journal, providing methods for retrieving it
    from persistent storage (__init__,) adding to it either
    interactively (get,) or from file/text (load,) and sending it back
    to be stored (save) along with convenience functions unlikely to
    be used publicly (append, extend.)
    It keeps track of journal entry numbers, the next one of which is
    kept in persistent storage as part of the metadata for an entity.
    See docstring for __init__ method.
    Attributes include:
        entity: comes from args: args[--entity].
        journal_file: name of the json file (persistent storage.)
        metadata_file: name of file where next_entry is discovered.
        next_entry: discoverd from metadata & incrimented as needed.
        journal: a list of dicts
            In persistent storage it is a json file consisting of 
            a dict with only one entry keyed by "Journal" with a 
            value that is a list of dicts. The journal attribute
            becomes this list.  Each item of this list is the dict
            version of a JournalEntry instance.
        metadata: the info sourced from metadata_file
    Public methods include:
        __init__() - loads data from persistent storage.
        show() - assigned to __str__.
        get() - get new entries from user
        load()- load new entries from text, either a string or text
        collected from a file.
        save()- save new entries to persistent storage.
    NOTE: this class's get_entry and show methods rely on 
    JournalEntry methods get_entry and show.
    """

    def __init__(self, defaults=D):
        """
        Loads (from persistent storage) an entity's metadata
        and all journal entries to date in preparation for
        further journal entries or to populate the Ledger.
        In future, may well load only journal entries created
        since last end of year close out of the books.
        As of yet have not dealt with end of year.
        Also consider collecting new entries and not even loading
        those in persistent storage until user decides to save.
        """
        self.changed = False
        self.defaults = defaults
        self.entity = defaults["entity"]
        self.infiles_loaded = False
        dir_name = os.path.join(D['home'], self.entity + '.d')
        self.metadata_file = os.path.join(dir_name,
                                        defaults['metadata_name'])
        self.journal_file = os.path.join(dir_name,
                                        defaults['journal_name'])
        # The json file consists of a dict with only one entry
        # keyed by "journal" and its value is a list of dicts,
        # each corresponding to a JournalEntry instance.
        with open(self.journal_file, 'r') as f_object:
            persistent_dict = json.load(f_object)
#           logging.debug(persistent_dict)
#           print("persistent journal_dict: {}"
#                       .format(persistent_dict))
            self.journal = [JournalEntry.from_dict(_dict) for
                            _dict in persistent_dict["Journal"]]
        with open(self.metadata_file, 'r') as f_object:
            self.metadata = json.load(f_object)
        self.next_entry = self.metadata['next_journal_entry_number']

    def append(self, journal_entry):
        """
        Appends the journal_entry while giving it the correct
        entry_number and updating self.next_entry.
        """
        journal_entry.entry_number = self.next_entry
        self.next_entry += 1
        self.journal.append(journal_entry)
        self.changed = True

    def extend(self, journal_entries):
        for journal_entry in journal_entries:
            self.append(journal_entry)
        self.changed = True

    def show(self):
        """
        Returns a string representation of the journal attribute.
        """

        ret = ["\nJOURNAL ENTRIES:......           Entity: '{}'\n"
            .format(self.entity)]
        for je in self.journal:
            ret.append(je.show())
        return '\n'.join(ret)

    def __str__(self):
        """
        Implemented as self.show()
        """
        return self.show()

    def save(self):
        """
        Saves journal to persistent storage.
        Replaces, rather than adds to, what was previously in
        persistent storage.  What was previously stored is loaded
        when a Journal is instantiated so data will not be lost.
        Returns an error string if unsuccessfull.
        """
        if not self.changed:
            return "No entries to save."
        persistent_dict = {"Journal":
                                [je._dict for je in self.journal]}
        self.metadata['next_journal_entry_number'] = self.next_entry
        try:
            with open(self.journal_file,
                            'w', newline='') as f_object:
                json.dump(persistent_dict, f_object)
            with open(self.metadata_file, 'w') as f_object:
                json.dump(self.metadata, f_object)
        except IOError:
            return "Encountered an IOError; journal NOT saved."

#   def _get_entry(self):
#       """Used by the get method to add an entry to the the journal.
#       Instantiates a JournalEntry and, if it passes its ok method,
#       saves its data atribute to the Journal (self.)
#       The next_number attribute is updated each time.
#       If successful, the JournalEntry instance is returned;
#       otherwise None is returned
#       """
#       new_entry = (
#           JournalEntry(self.next_entry))
#       if new_entry.ok():
#           self.next_entry += 1
#           self.journal.append(new_entry.data)
#           return new_entry
#       # else returns None

    def extend(self, JournalEntry_list):
        """                     [test: JournalClass - test_load()]
        Takes a list of JournalEntry instances and appends this list
        to the journal.  The append method takes care of setting the
        entry_number(s).
        """
        for journal_entry in JournalEntry_list:
            self.append(journal_entry)  # Takes care of updating 

    def get(self):
        """Interactively collects journal entries from the user and,
        if well formed and validated by the user, appends each one to
        the Journal.  An empty or malformed entry terminates.
        A client of JournalEntry.get_JournalEntry ; a ui controller?
        """
        while True:
            journal_entry = JournalEntry.get_JournalEntry()
            if journal_entry != None:
                print(
                    "You have submitted the following journal entry:")
                print(journal_entry)
                answer = input(
                    "Do you want it added to the journal (Yes/No)? ")
                if answer and answer[:1] in 'Yy':
                    self.append(journal_entry)
                else:
                    break
            else:
                break

    def load(self, text_or_filename):
        """
        Accepts properly formatted text or the name of a file
        containing such text and adds the JournalEntries specified
        in that text to those already existing.
        See docstring for JournalEntry.load.
        A client of JournalEntry.load ; a batch controller?
        """
        for journal_entry in JournalEntry.load(text_or_filename): 
            self.append(journal_entry)


######################################################################
# The following 3 global functions are specific to the Kazan15 entity.

def adjust4assets(chart_of_accounts):
    """This is one of several 'custom' procedures specific to the
    needs of Kazan15.  It 'auto-dates.'
    Returns a string that can be provided as a parameter to the load
    method of a Journal instance.  Such an entry adjusts the equity
    and liability accounts to reflect the fact that the 'group of 8'
    own the fixed assets but that ownership comes at a cost to them:
    hence the Dr entries against their equity accounts.  See file
    'explanation'.
    Note: this function will NOT adapt to a change in the account
    code schema as defined in config.py.
    """
    print("Begin running custom function adjust4assets")
    total_assets_2split = 0
    asset_codes2check = [code for code in
                                chart_of_accounts.ordered_codes
                                        if (code[:2] == '15') ]
    asset_codes = []
    for asset_code in asset_codes2check:
        acnt = chart_of_accounts.accounts[asset_code]
        if (not acnt.place_holder
        and hasattr(acnt, 'split')):
            assert acnt.split == N_ASSET_OWNERS
            total_assets_2split += acnt.signed_balance
            asset_codes.append(asset_code)
    ret = "\n".join([
                "{:%b %d, %Y}".format(datetime.date.today()),
                'book keeper',
                'Adjust equity and liability accounts to reflect',
                "ownership of assets by the 'group of 8'.",
                ("2001,2002,2003,2004,2005,2006,2007,2008 Cr {}"
                .format(total_assets_2split)),
                ("3001,3002,3003,3004,3005,3006,3007,3008 Dr {}"
                .format(total_assets_2split)),
                '\n'  # ...to satisfy journal entry requirements.
                ])
    print(
    "Finished running custom function adjust4assets: returning:")
    print(ret)
    return ret
    
def zero_temporaries(chart_of_accounts):
    """This is one of several 'custom' procedures specific to the
    needs of Kazan15.
    It's parameter is expected to be a journal populated instance of
    the ChartOfAccounts class.
    It returns text (representing journal entries) that conforms to
    the format expected by the journal.extend() method. These
    additional entries preform one of the 'custom' requirements
    described in the accompanying 'explanation' file.
    This zero_expenses method depends on the final (otherwise
    optional) 'split' field of the expense account.
    Typical usage would be as follows:  load a ChartOfAccounts with
    all the journal entries and run this function with it as the
    parameter. Then load the returned value to the journal and
    populate another chartofaccounts with this updated journal. 
    Note: this function will NOT adapt to a change in the account
    code schema as defined in config.py.
    """

    def zero_out(preamble, # date, user, descr text (can be more than
                           # one line,) and zeroing entry: as a list
                           # of strings.
                format_line, # format string used for balancing entries.
                split_list): # returned by divider()
        """                           [Not subjected to unittest.]
        Sets up text that can be read as a journal entry.
        Assumes that numerically sequential accounts are being
        affected and that the sequence begins with 1 (or 01, or 001
        ... depending on the format_line.
        """
        ret = preamble
        for i in range(len(split_list)):
            ret.append(format_line.format(i + 1, split_list[i]))
        ret.append('\n')  # Journal entry depends on this trailing CR
        return '\n'.join(ret)

    print("Begin running custom function zero_temporaries")
    entries = []
    expenses = {}      # Dict of totals keyed by 'split'
    income = {}
    for code in chart_of_accounts.ordered_codes:
        acnt = chart_of_accounts.accounts[code]
        if (code[:1] == '5') and (not
                    acnt.place_holder):
        # if expense account that isn't a place holder:
            _value = expenses.setdefault(
                        acnt.split, 0)
            expenses[acnt.split] += acnt.signed_balance
    # expenses[9]: Cr 5001  Dr 3001..3009
        if (code[:1] == '4') and (not
                    acnt.place_holder):
        # if income account that isn't a place holder:
            _value = income.setdefault(
                        acnt.split, 0)
            income[acnt.split] += acnt.signed_balance
#           print('Adding ${:.2f} (in Acnt:{}) to income totals.'
#                       .format(acnt.signed_balance,
#                       code))
    if expenses[9]:
        entries.append(zero_out(
            ['Sept 27, 2015', 'book keeper',
            'Distribute expenses among 9 participants.',
            '5001 Cr {:.2f}'.format(expenses[9])],
            '30{:0>2} Dr {:.2f}',
            divider(expenses[9], 9)))
    # expenses[10]: Cr 5002  Dr  3001..3010
    if expenses[10]:
        entries.append(zero_out(
            ['Sept 27, 2015', 'book keeper',
            'Distribute expenses among 10 participants.',
            '5002 Cr {:.2f}'.format(expenses[10])],
            '30{:0>2} Dr {:.2f}',
            divider(expenses[10], 10)))
#   print("'income9' contains {:.2f}"
#                   .format(income[9]))
    if income[9]:
        entries.append(zero_out(
            ['Sept 27, 2015', 'book keeper',
            'Distribute income among 9 participants.',
            '4001 Dr {:.2f}'.format(income[9])],
            '30{:0>2} Cr {:.2f}',
            divider(income[9], 9)))
    # expenses[10]: Cr 5002  Dr  3001..3010
    if income[10]:
        entries.append(zero_out(
            ['Sept 27, 2015', 'book keeper',
            'Distribute income among 10 participants.',
            '4002 Dr {:.2f}'.format(income[10])],
            '30{:0>2} Cr {:.2f}',
            divider(income[10], 10)))
    # Note: the following join method is used on the empty string
    # rather than a CR because a CR was added to each string in the
    # list by the zero_out method (because journal reading depends
    # on it.)
    ret = ''.join(entries)
    print(
    "Finished running custom function zero_temporaries: returning:")
    print(ret)
    return ret

def check_equity_vs_bank(chart_of_accounts):
    """This is one of several 'custom' procedures specific to the
    needs of Kazan15.
    Checks that the sum of the equity accounts balances against liquid
    assets, in our case, just the bank account.
    Returns a string.
    Note: this function will NOT adapt to a change in the account code
    schema as defined in config.py.
    """
    print("Running custom function check_equity_vs_bank")
    assets = 0
    codes2check = [ code for code in chart_of_accounts.ordered_codes
            if (code[:2] == '30') ]  # Equity accounts
    for code in codes2check:
        acnt = chart_of_accounts.accounts[code]
        if not acnt.place_holder:
            assets += acnt.signed_balance
    ret = ["Total assets of participants:  {:.2f}"
                .format(assets)]
    ret.append(
        "...which balances nicely against the total liquid assets...")
    ret.append("... remaining in bank account: {:.2f}"
        .format(chart_of_accounts.accounts['1110'].signed_balance))
    return '\n'.join(ret)
    print("Finished running custom function check_equity_vs_bank")

## End of Kazan15 'custom' functions.
######################################################################

#### The menu framework is in menu.py and work_with.py

if __name__ == '__main__':  # code block to run the application
    from docopt import docopt
    args = docopt(__doc__, version=config.VERSION)
    print(
    'Running src/debk.py which does nothing but print its args:')
    print(args)

