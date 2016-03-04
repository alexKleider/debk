#!../../venv/bin/python
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8
#   File: /home/alex/Py/CSV/debk/src/work_with.py
"""
A second level menu model to work with a specific entity.
Part of the double entry book keeping project.
"""

import os
from CSV.debk.src import debk

def setup_entity(defaults):
    """
    Assumes defaults['entity'] has already been assigned.
    """
    cofa = debk.ChartOfAccounts(defaults)
    journal = debk.Journal(defaults)
    cofa.load_journal_entries(journal.journal)
    return journal, cofa


def work_with(defaults):
    """
    Provides an interface stub for once an entity has been selected.
    Loads the entity's relevant files:
    """
    _ = input("Stub of code to work with '{}' entity goes here."
                    .format(defaults["entity"]))
    journal, cofa = setup_entity(defaults)
    menu(defaults, cofa, journal)

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
    _ = input("Beginning journal entry.")
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
    5. Add Another Account.
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
            ret = add_account(defaults, cofa)
        elif option == 9:
            ret = change_verbosity(defaults)
        else:
            print("BAD CHOICE '{}'- try again....".format(option))

if __name__ == "__main__":
    from CSV.debk.src.config import DEFAULTS as D
    D['home'] = "/home/alex/Py/CSV/debk/tests/debk.d"
    menu(D)
