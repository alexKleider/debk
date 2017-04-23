#!../../venv/bin/python
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8
#   File: /home/alex/Py/CSV/debk/src/work_with.py
"""
A second level menu model to work with a specific entity.
Part of the double entry book keeping project.

If called rather than imported, it attempts to 'work_with' a
defaultentity which probably doesn't exist and so will print a warning
and exit.
"""

import os
from src import debk
from src import config

def setup_entity(defaults):
    """
    Assumes defaults['entity'] has already been assigned.
    Returns a tuple: chart of accounts for the entity,
    and the journal for the entity.
    """
    cofa = debk.ChartOfAccounts(defaults)
    journal = debk.Journal(defaults)
    cofa.load_journal_entries(journal.journal)
    return cofa, journal


def work_with(defaults):
    """
    Provides an interface stub for once an entity has been selected.
    Loads the entity's relevant files:
    """
    _ = input("Stub of code to work with '{}' entity goes here."
                    .format(defaults["entity"]))
    menu(defaults, *setup_entity(defaults))

def save_work(journal):
    error_string = journal.save()
    if error_string:
        print(error_string)
    else:
        print('Journal saved successfully.')

def deal_w_new_entries(new_entries, cofa, journal):
    if new_entries:
        journal.extend(new_entries)
        cofa.load_journal_entries(new_entries)


def journal_entry(cofa, journal):
    _ = input("Enter to begin journal entry: ")
    new_entries = []
    while True:
        entry = debk.JournalEntry.get_JournalEntry()
        if entry:
            new_entries.append(entry)
        else:
            break
    if new_entries:
        deal_w_new_entries(new_entries, cofa, journal)

def load2journal(cofa, journal):
    file_name = input(
        "File with journal entries: ")
    _ = input("Reading journal entries from file '{}'."
            .format(file_name))
    if not os.path.isfile(file_name):
        return "Unable to find file '{}'".format(file_name)
    new_entries = debk.JournalEntry.load(file_name)
    if new_entries:
        deal_w_new_entries(new_entries, cofa, journal)

def show_journal(journal):
    file_name = input("Enter a file name (blank if to screen): ")
    if not file_name:
        print(journal.show())
    else:
        try:
            with open(file_name, 'w') as file_obj:
                file_obj.write(journal.show())
        except IOError:
            print("Unable to write journal to file '{}'."
                .format(file_name))
        else:
            print("Journal written to file '{}'."
                .format(file_name))

def show_accounts(cofa):
    file_name = input("Enter a file name (blank if to screen): ")
    if not file_name:
        print(cofa.show_accounts())
    else:
        try:
            with open(file_name, 'w') as file_obj:
                file_obj.write(cofa.show_accounts())
        except IOError:
            print("Unable to write cofa to file '{}'."
                .format(file_name))
        else:
            print("cofa written to file '{}'."
                .format(file_name))

def close_fiscal_period(cofa, journal):
    """
    Closes the fiscal period:
    a. Zero out all the temporary accounts (income and
    expenses) with adjustment entries putting net income
    into the config.EQUITY4INCOME_ACCOUNT.
    b. Create a new JournalEntry that would populate a virgin
    chart of accounts with starting balances as in the newly
    created balance sheet.  (Adjust the metadata file accordingly.)
    c. Archive the Journal as a time stamped file.  (Log this in
    the metadata file.)

    Returns two strings as a tuple:
        1. an income statement (before zeroing of the temporary
        accounts,) and
        2. a balance sheet (with net income already moved
        to owner equity (config.EQUITY4INCOME_ACCOUNT.))
    """
    print("Beginning and ending dates of fiscal period-")
    begin_date = input("First date of fiscal period ({}): "
                        .format(src.config.FISCAL_YEAR_BEGIN))
    closing_date = input("Last date of fiscal period ({}): "
                        .format(src.config.FISCAL_YEAR_END))
    if not begin_date:
        begin_date = src.config.FISCAL_YEAR_BEGIN
    if not closing_date:
        closing_date = src.config.FISCAL_YEAR_END
    net_income = cofa.get_net_income()
    print("Net Income at closing is: ${}"
            .format(net_income))
    income_statement = cofa.show_balance_sheet(closing_date)
    closing_entry = JournalEntry( 0, date, user,
        [config.INCOME_TRANSFER2EQUITY_DESCRIPTOR],
        [LineEntry(config.NET_INCOME_ACCOUNT, "Dr", net_income),
         LineEntry(config.EQUITY4INCOME_ACCOUNT, "Cr", net_income)])
    journal.append(closing_entry)
    cofa.load_journal_entries([closing_entry])
    balance_sheet = cofa.show_income_statement(
                                    begin_date, closing_date)
    income_total = 0
    expense_total = 0
    line_entries = cofa.total_reversal("INCOME", income_total)
    line_entries.append(
                cofa.total_reversal("EXPENSE", expense_total))
    pass

def add_account(defaults, cofa):
    """
    This will be tricky: must add the account to the data base AND
    to the current cofa instance.
    """
    _ = input("Adding accounts not yet implemented- edit directly.")

def change_verbosity(defaults):
    _ = input("Verbosity not yet implemented")


def menu(defaults, cofa, journal):
    """
    Provides the 'work_with' user interface.
    """
    while True:
        option = input("""==========================
Working with {}:
    1. Journal Entry.
    2. Load Journal Entries from file.
    3. Show Journal.
    4. Show Accounts.
    5. Close Fiscal Period
    6. Add Another Account.
    9. Change Verbosity.
    0. Exit
Choice: """.format(defaults["entity"]))
        print("You've chosen: {}".format(option))
        if option in ('', '_', '0'):
            ret = save_work(journal)
            if ret:
                print(ret)
            else: 
                print("Successfully saved work.")
                return
        try:
            option = int(option)
        except ValueError:
            print(
            "Invalid choice: {} (must be an integer 0...5,9.)"
                        .format(option))
            continue
        if option == 1:
            ret = journal_entry(cofa, journal)
        elif option == 2:
            ret = load2journal(cofa, journal)
        elif option == 3:
            ret = show_journal(journal)
        elif option == 4:
            ret = show_accounts(cofa)
        elif option == 5:
            ret = close_fiscal_period(cofa, journal)
        elif option == 8:
            ret = add_account(defaults, cofa)
        elif option == 9:
            ret = change_verbosity(defaults)
        else:
            print("BAD CHOICE '{}'- try again....".format(option))
        if ret:
            _input = input(ret)

if __name__ == "__main__":
    from CSV.debk.src.config import DEFAULTS as D
    D['home'] = "tests/debk.d"
    _ = D.setdefault('entity', 'defaultentity')
    menu(D, *setup_entity(D))

