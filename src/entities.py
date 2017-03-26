#!./venv/bin/python
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8
#   File: /home/alex/Py/CSV/debk/src/entities.py
"""
A module to keep track of the entities (and the default entity) as
part of the double entry book keeping system.
"""

import os
import sys
import shutil
import json
import logging

### Functions to deal with the file system. ###

def get_file_info(defaults):
    """
    Returns a tuple containing 
    1. a list of the names of all entities existing in
    the d['home'] file system (as a list,) 
    2. a string: the default entity (which may be the empty string.)
    Depends on defaults: typically config.DEFAULTS
    but for testing purposes, defaults['home'] can be changed.
    """
    home = defaults['home']
    default_file = os.path.join(home, defaults['last_entity'])
#   print("home dir: {}, entity file: {}"
#                   .format(home, default_file))
    try:
        assert os.path.isdir(home)
    except AssertionError:
        logging.critical(
        "Needed directory ('%s') doesn't exist." % (
            home))
        print("Unable to continue: missing vital 'home' directory.")
        sys.exit(1)
    lst = [file_name[:-2]
        for file_name in os.listdir(home)
        if file_name.endswith(".d")]
    try:
        with open(default_file, 'r') as f_object:
            default_entity = f_object.read()
    except OSError:
        default_entity = ''
        logging.warning(
    "Expected file (%s) could not be found by 'get_file_info()'." % default_file)
    if default_entity in lst:
        default = default_entity
    else:
        default = ''
    return (lst, default)

def create_entity(entity_name, defaults, set_default=True):
    """
    Establishes a new accounting system. 
    Indicates success by returning the entity_name.
    Returns None if unsuccessful.
    <entity_name> becomes the default unless set_default is False.
    Depends on <defaults>: typically config.DEFAULTS, a dict.

    Creates a new dirctory '<entity_name>.d' and populates it with
    a set of required files including a default start up chart of
    accounts.  An attempt will be made to find a file name that is
    the concatenation of the entity name and 'ChartOfAccounts'.
    If not found, the file specified by defaults['cofa'] will be used.
    Reports error if:
        1. <entity_name> already exists, or
        2. not able to write to new directory.
    Also sets up 
    1. an empty journal file, and
    2. a metadata file.
    The names of the above two files are defined in 
    src.config.defaults["metadata_name"] and
    src.config.defaults["journal_name"].
    """
#   print("Begin create_entity('{}')...".format(entity_name))
    home = defaults['home']
    cofa_source = os.path.join(  # | Use a prepopulated chart  |
                home,            # | of accounts if it exists. |
                entity_name + defaults['cofa_suffix'])
    if not os.path.isfile(cofa_source):  # Fall back on default.
        cofa_source = os.path.join(home,
                                    defaults['cofa_template'])
    new_dir = os.path.join(home, entity_name+'.d')
    new_CofA_file_name = os.path.join(new_dir, defaults['cofa_name'])
    new_Journal = os.path.join(new_dir, defaults['journal_name'])
    meta_dest = os.path.join(new_dir, defaults['metadata_name'])

    # Following provides the metadata content eliminating the need to
    # have a separate file as was done initially.
    metadata = ("""{{\n"entity_name": "{}",
"next_journal_entry_number": 1,
"last_closing": "unset"\n}}
""".format(entity_name))

    entity_file_path = os.path.join(home, defaults['last_entity'])
    try:
        os.mkdir(new_dir)
        shutil.copy(cofa_source, new_CofA_file_name)
        with open(new_Journal, 'w') as journal_file_object:
            journal_file_object.write('{"Journal": []}')
        with open(meta_dest, 'w') as json_file:
            json_file.write(metadata)
#       print("\tCreated and populated '{}'.".format(new_dir))
    except FileExistsError:
        logging.error("Directory %s already exists", new_dir)
        return
    except OSError:
        logging.error(
            "Destination %s &/or %s may not be writeable.",
                            new_CofA_file_name, new_Journal)
        return
    defaults['entity'] = entity_name
    if set_default:  # Keeps track of the last entity referenced.
        with open(entity_file_path, 'w') as entity_file_object:
            entity_file_object.write(entity_name)
#   print("...ending create_entity ?successfully?")
    return entity_name

def delete_entity(entity2delete, defaults):
    """
    Removes the directory tree for specified entity
    and if successful returns the entity name.
    If not successful, logs and returns None.
    """
    entity_dir = os.path.join(defaults['home'], entity2delete+'.d')
    if os.path.isdir(entity_dir):
        shutil.rmtree(entity_dir)
        return entity2delete
    else:
        logging.error(
            "Attempting to delete an entity with no directory.")
                                                    
def write_default(default, defaults):
    """
    Writes the default entity to the file system.
    Depends on defaults: typically config.DEFAULTS.
    Returns the default if successful, else logs and returns None.
    """
    try:
        with open(defaults['last_entity'], 'w') as f_object:
            f_object.write(default)
    except OSError:
        logging.error("Unable to set default to '{}'.",default)
    else:
        return default


class Entities(object):
    """
    Keep track of the entities including a default.
    Expect only one instance which will be a global.
    The file system is handled by calls to global functions
    which in turn depend on defaults: typically config.DEFAULTS.
    <default_entity> will only be set if it exists in the data base.
    """

    def __init__(self, list_of_entities,  #| Unpack 2-tuple returned 
                        default_entity,   #|   by get_file_info().
                        defaults=None):   # Use defaults from config
        """
        Typically gets its parameters with the following call:
            entities = Entities(
                    *get_file_info(default_dir = DEFAULT_DIR,
                                default_file = DEFAULT_Entity)
                    defaults=config.DEFAULTS)
        """
        assert not defaults is None
        self.lst = list_of_entities
        self.default = default_entity
        self.D = defaults

    def reset_default(self, default=''):
        """
        Set the default attribute to default and returns it.
        Returns None (and issues a warning) if not a valid default.
        Note that the empty string is a valid default.
        Calls write_default (which logs failure) to deal with files.
        """
        if ((default==''
        or default in self.lst)
        and write_default(default, self.D)==default):
            self.default = default
            return default
        else:
            print("Unable to set default to '{}'."
                .format(default))

    def check_new_entity(self, entity):
        """
        Checks validity of entity- if it can be used for a new entity.
        """
        if (entity  # Insures we aren't passed an empty string.
        and not entity in self.lst
        and entity.isalnum()
        and entity[0:1].isalpha()):
            return True
        else:
            return False

    def add(self, new_entity, set_default=True):
        """
        If new_entity is valid, it is added and returned.
        Setting it as the default can be blocked.
        If new_entity is provided as an empty string:
        it is returned without any other action.
        If new_entity is not empty and not valid, 
        a warning is printed and None is returned.
        Calls create_entity() (which logs failure) to deal with files.
    """
        if new_entity == '':
            print("Aborting new entry creation- blank name.")
            return new_entity
        if (self.check_new_entity(new_entity)
        and create_entity(new_entity, self.D,
                            set_default) == new_entity):
            self.lst.append(new_entity)
            if set_default:
                self.default = new_entity
            return new_entity
        else:
            print("Failing to add an invalid entity: '{}'."
                        .format(new_entity))

    def remove(self, entity2remove):
        if not entity2remove in self.lst:
            print("Can't remove '{}': not in the list."
                        .format(entity2remove))
            return
        if delete_entity(entity2remove, self.D) == entity2remove:
            if entity2remove == self.default:
                self.reset_default()
            self.lst = [entity for entity in self.lst
                            if entity!=entity2remove]
        else: print(
                "Unsuccessful call to delete_entity() in remove().")

    def show_entities(self, numbered=False, indent=0):
        """
        Returns a string which, if there are entities, 
        consists of a sorted list of the entities,
        indented by indent spaces,
        and numbered if option is set to True.
        The default (if present) is indicated with an asterix.
        If there are no entities, the empty string is returned.
        """
        list_of_entities= sorted(self.lst)
        if not list_of_entities:
            return ''
        if numbered:
            return '\n'.join([" "*indent+"{}: {}  *default"
                                                .format(n, entity)
                        if entity==self.default 
                        else " "*indent+"{}: {}".format(n, entity)
                for (n, entity) in enumerate(list_of_entities, 1) ])
        else:
            return '\n'.join([' '*indent+entity+' *default'
                        if entity==self.default 
                        else ' '*indent+entity
                        for entity in list_of_entities ])

def main():
    print("Running entities.py which does nothing but print this.")

if __name__ == "__main__":
    main()
