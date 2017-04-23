#!./venv/bin/python
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8
#   File: /home/alex/Py/CSV/debk/src/menu.py
"""
A simple menu model to be used as a front end for the
double entry book keeping project.

Usage:
    ./src/menu.py
    ./src/menu.py -h | --help
    ./src/menu.py --version
    ./src/menu.py <data_directory>

Options:
  -h --help  Print usage statement.
  --version  Print version.

A single positional parameter, if provided, specifies a
directory which will replace that specified by DEFAULTS['home']
in ./src/config.py
"""

import docopt
import src.work_with as work_with
import src.entities as entities
import src.config as config

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
{0:}Pick an entity: """
            .format(" "*indent,
                    entities.show_entities(numbered=True,
                                           indent=indent)))
        default = entities.default
        if (option == '' or option == '_') and default:
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

def choose_existing(defaults, entities):
    """
    A main menu response function.
    A wrapper for choose_entity().
    """
    print("Picked 'Choose an existing entity.'")
    chosen_entity = choose_entity(entities, 4)
    if chosen_entity:
        defaults['entity'] = chosen_entity
        work_with.work_with(defaults)

def create_new(entities):
    """
    A main menu response function.
    """
    print("Picked 'Create a new entity.'")
    while True:
        entity = input("Pick name for new entity: ")
        if (entities.check_new_entity(entity)
                and entities.add(entity) == entity):
            print(
            "Entity '{}' successfully created (and set as default.)"
                .format(entity))
#           print("Entity listing is now: {}".format(entities.lst))
            return entity
        elif not entity:
            print("Aborting entity creation.")
            return
        else:
            print("Invalid entity name, try again or Enter to exit.")

def delete_option(defaults, entities):
    """
    A main menu response function.
    """
    print("Picked 'Delete an existing entity.'")
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
            defaults['entity'] = ''
        else:
            print("No deletion being done.")
        break

def change_args_option(defaults):
    """
    Moving away from debk.py command line arguments so verbosity
    defaults['verbosity']
    (and prossibly indentation) defaults['indentation']
    might have to be modifiable here.
    """
    _ = input("Changing options has not yet been implemented.")

def menu(defaults):
    """
    Provides the top level user interface.
    Prompts for what to do and then calls the appropriate
    function or method.
    Creating a new entity or choosing an existing one, if successful,
    begins the accounting process with that entity.
    """
    entities_ = entities.Entities(
        *entities.get_file_info(defaults),
        defaults=defaults)
#   print("'entities_' is of type '{}'.".format(type(entities_)))
#   print("Initializing 'entities_' with the following values:")
#   print("\t", entities_.lst)
#   print("\t", entities._default)
    while True:
        listing = entities_.show_entities(indent=8)
        if listing:
            listing = (
"""\n    (Currently existing entities_ are:\n{}          )"""
                .format(listing))
        else: listing = "\n    (No entities_ currently exist.)"
#       print("listing is '{}'.".format(listing))
        option = input("""
Main Menu:
    [Working dir: {}]{}
    1. Create a new entity.
    2. Choose an existing entity.
    3. Delete an entity.
    9. Change arguments.
    0. Exit
Choice: """.format(defaults['home'], listing))
        print("You've chosen: '{}'.".format(option))
        if option in ('', '_', '0'):
            break
        try:
            option = int(option)
        except ValueError:
            print(
                "Invalid main menu choice: {} (must be an integer.)"
                .format(option))
            continue
        if option == 1:
            entity = create_new(entities_)
        elif option == 2:
            entity = choose_existing(defaults, entities_)
        elif option == 3:
            delete_option(defaults, entities_)
            entity = ''
        elif option == 9:
            change_args_option(defaults)
        else:
            print("BAD CHOICE '{}'- try again....".format(option))
            entity = None
        if entity:
            defaults["entity"] = entity
            work_with.work_with(defaults)

if __name__ == "__main__":
    args = docopt.docopt(__doc__, version=config.VERSION)
#   print(args)
    if args['<data_directory>']:
        config.DEFAULTS['home'] = args["<data_directory>"]
    menu(config.DEFAULTS)
