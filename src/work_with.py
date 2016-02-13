#!../../venv/bin/python
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8
#   File: /home/alex/Py/CSV/debk/src/work_with.py
"""
A second level menu model to work with a specific entity.
Part of the double entry book keeping project.
"""

from CSV.debk.src import entities as E

def work_with(entity):
    """
    Provides an interface stub for once an entity has been selected.
    Loads the entity's relevant files:

    """
    _ = input("Stub of code to work with '{}' entity goes here."
                    .format(entity))
    menu(entity)

def journal_entry(option):
    _ = input("Beginning journal entry.")
    pass

def add2journal(option):
    file_name = input(
        "Specify name of file from which to read journal entries")
    _ = input("Reading journal entries from file '{}'."
            .format(file_name))
    pass

def show_accounts(option):
    pass

def add_account(option):
    _ = input("Adding accounts not yet implemented- edit directly.")

def change_verbosity(option):
    _ = input("Verbosity not yet implemented")


def menu(entity):
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
Choice: """.format(entity))
        print("Main Menu choice: {}".format(option))
        if option in ('', '_', '0'):
            return
        try:
            option = int(option)
        except ValueError:
            print(
            "Invalid choice: {} (must be an integer 0...5,9.)"
                        .format(option))
            continue
        if option == 1:
            ret = journal_entry(option)
        elif option == 2:
            ret = add2journal(option)
        elif option == 3:
            ret = show_journal(option)
        elif option == 4:
            ret = show_accounts(option)
        elif option == 5:
            ret = add_account(option)
        elif option == 9:
            ret = change_verbosity(option)
        else:
            print("BAD CHOICE '{}'- try again....".format(option))

if __name__ == "__main__":
    from CSV.debk.src.config import DEFAULTS as D
    D['home'] = "/home/alex/Py/CSV/debk/tests/debk.d"
    menu(D)
