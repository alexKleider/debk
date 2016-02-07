#!../../venv/bin/python
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8
#   File: /home/alex/Py/CSV/debk/src/menu.py
"""
A simple menu model to be used as a front end for the doble entry book
keeping project.
"""

from CSV.debk.src import entities as E

def choose_entity(entities, indent=0):
    """
    Queries the user to choose an entity.
    If no entities are available, this is reported and None returned.
    Loops continuously until a valid choice is made and returned,
    or the user chooses to exit in which case None is returned.
    If a valid choice is made, it is set to be the default.
    Entry of empty string or underscore picks the default (if it
    exists,) or is considered an invalid option if it doesn't.
    Invalid entry/options are reported before the loop is restarted.
    """
    if not entities.lst:
        print("No entities from which to choose!")
        return
    else:
        entity_list = sorted(entities.lst)
    while True:
        option = input(
"""{0:}Choose one of the following:
{1:}
{0:}0: to exit.
{0:}Pick an entity: """.format(" "*indent,
                entities.show_entities(numbered=True, indent=indent)))
        default = entities.default
        if (option=='' or option=='_') and default:
            return default
        try:
            option = int(option)
        except ValueError:
            print("Invalid option: {}! (It must be an integer.)"
                    .format(option))
            continue
        if option in range(1, len(entity_list) + 1):
            chosen_entity = entity_list[option - 1]
            entities.reset_default(chosen_entity)
            return chosen_entity 
        elif option == 0:
            return None
        else:
            print("Invalid entry- try again ('0' to quit.)")

def choose_existing(option, entities):
    """
    A main menu response function.
    A wrapper for choose_entity().
    """
    print("Picked '{}. Choose an existing entity.'".format(option))
    chosen_entity = choose_entity(entities, 4)
    if chosen_entity:
        work_with(chosen_entity)

def create_new(option, entities):
    """
    A main menu response function.
    """
    print("Picked '{}. Create a new entity.'".format(option))
    while True:
        entity = input("Pick name for new entity: ")
        if (entities.check_new_entity(entity)
        and entities.add(entity) == entity):
            print(
            "Entity '{}' successfully created (and set as default.)"
                .format(entity))
#           print("Entity listing is now: {}".format(entities.lst))
            work_with(entity)
            return
        elif not entity:
            print("Aborting entity creation.")
            return
        else:
            print("Invalid entity name, try again or Enter to exit.")

def delete_option(option, entities):
    """
    A main menu response function.
    """
    print("Picked '{}. Delete an existing entity.'".format(option))
    while True:
        entity = choose_entity(entities, 4)
        if not entity: 
            print("Entity deletion aborted.")
            return
        y_n = input("About to delete entity '{}', ARE YOU SURE? "
                .format(entity))
        if y_n and y_n[0] in 'Yy':
            print("Deleting entity '{}'.".format(entity))
            entities.remove(entity)
        else:
            print("No deletion being done.")
        break

def work_with(entity):
    """
    Provides an interface stub for once an entity has been selected.
    """
    _ = input("Stub of code to work with '{}' entity goes here."
                    .format(entity))

def menu(defaults):
    """
    Provides the top level user interface.
    """
    entities = E.Entities(*E.get_file_info(defaults),
                            defaults=defaults)
#   print("'entities' is of type '{}'.".format(type(entities)))
#   print("Initializing 'entities' with the following values:")
#   print("\t", entities.lst)
#   print("\t", entities.default)
    while True:
        listing = entities.show_entities(indent=4)
        if listing:
            listing = (
"""\n(Currently existing entities are:\n{}          )"""
                    .format(listing))
        else: listing = "(No entities currently exist.)"
        option = input("""
Main Menu:{}
    1. Create a new entity.
    2. Choose an existing entity.
    9. Delete an entity.
    0. Exit
Choice: """
                        .format(listing))
        print("Main Menu choice: {}".format(option))
        if option in ('', '_', '0'):
            return
        try:
            option = int(option)
        except ValueError:
            print(
                "Invalid main menu choice: {} (must be an integer.)"
                        .format(option))
            continue
        if option == 1:
            entity = create_new(option, entities)
        elif option == 2:
            entity = choose_existing(option, entities)
        elif option == 9:
            delete_option(option, entities)
            entity = ''
        else:
            print("BAD CHOICE '{}'- try again....".format(option))
            entity = None
        if entity:
            work_with(entity)

if __name__ == "__main__":
    from CSV.debk.src.config import DEFAULTS as D
    D['home'] = "/home/alex/Py/CSV/debk/tutor/debk.d"
    menu(D)
