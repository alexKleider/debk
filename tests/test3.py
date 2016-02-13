#!../../venv/bin/python
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8
#   File: /home/alex/Py/CSV/debk/tests/test3.py
"""
Testing of entities module (imported as E) and menu module.
"""
import os
import shutil
import unittest
from unittest import mock
from CSV.debk.src import entities as E
from CSV.debk.src import menu
from CSV.debk.src.config import DEFAULTS as D

D['home'] = "./tests/debk.d"

class EntitiesAddDefaultTests(unittest.TestCase):

    def setUp(self):
        """
        Effectively tests get_file_info and create_entity.
        """
        self.new_entity = 'newEntity'
        self.invalid_entity = 'invalid_entity'
        self.ent_w_default = "entwdefault"
        self.ent_wo_default = "entwodefault"
        self.starting_list = ['ent1', 'ent2', 'ent3']
        for entity in self.starting_list:
            E.create_entity(entity, defaults=D)
        self.entities = E.Entities(*E.get_file_info(D), defaults=D)

    def test_setUp_list(self):
        self.assertEqual(self.starting_list.sort(),
                        self.entities.lst.sort())

    def test_setUp_default(self):
        self.assertEqual(self.starting_list[-1],
                        self.entities.default)

    def test_add_new_entity(self):
        entity_returned = self.entities.add(self.new_entity)
        self.assertTrue(
            entity_returned == self.new_entity
            and self.new_entity == self.entities.default
            and entity_returned in self.entities.lst
            )

    def test_add_faulty(self):
        entity_returned = self.entities.add(self.invalid_entity)
        self.assertTrue(
            not (self.invalid_entity in self.entities.lst)
            and self.invalid_entity != self.entities.default
            and self.entities.default == self.starting_list[-1]
            )

    def test_add_w_default(self):
        added_entity = self.entities.add(self.ent_w_default)
        self.assertTrue(
            added_entity == self.ent_w_default
            and self.entities.default == self.ent_w_default
            and self.ent_w_default == self.entities.lst[-1]
            )

    def test_add_wo_default(self):
        self.entities.add(self.ent_wo_default, set_default=False)
        self.assertTrue(
            self.entities.default != self.ent_wo_default
            and self.starting_list[-1] == self.entities.default
            and self.ent_wo_default in self.entities.lst
            )

    def test_empty_reset_default(self):
        default = self.entities.reset_default('')
        self.assertTrue(self.entities.default == '')

    def test_ent1_reset_default(self):
        default = self.entities.reset_default('ent1')
        self.assertTrue(self.entities.default == 'ent1')

    def test_invalid_reset_default(self):
        invalid_default = 'invalid_default'
        returned_default = self.entities.reset_default(
                        invalid_default)
        self.assertTrue(
            self.entities.default == self.starting_list[-1]
            and returned_default is None
            )

    def test_remove(self):

        for entity in self.entities.lst:
            self.entities.remove(entity)
        should_be_empty = (
                    [entity_dir for entity_dir in 
                            os.listdir(D['home'])
                            if entity_dir.endswith('.d')])
#       print("should_be_empty: {}".format(should_be_empty))
        self.assertTrue(self.entities.lst == []
                    and self.entities.default == ''
                    and not should_be_empty
                            )

    def test_menu_create_abort(self):
        with mock.patch("builtins.input",
                            side_effect=["1", "", "0"]):
            menu.menu(D)
            self.entities = E.Entities(  # Must reassign because
                            # menu.menu sets up its own 'entities'.
                        *E.get_file_info(D), defaults=D)
            self.assertEqual(self.starting_list.sort(),
                            self.entities.lst.sort())

    def test_menu_create_invalid_entity(self):
        with mock.patch("builtins.input",
                    side_effect=["1", self.invalid_entity, '', "0"]):
            menu.menu(D)
            self.entities = E.Entities(  # Must reassign because
                            # menu.menu sets up its own 'entities'.
                        *E.get_file_info(D), defaults=D)
            self.assertEqual(self.starting_list.sort(),
                            self.entities.lst.sort())

    def test_menu_create_newEntity(self):
        with mock.patch("builtins.input",
                        side_effect=["1", self.new_entity, '',
                        '', '']):
            menu.menu(D)
            self.entities = E.Entities(  # Must reassign because
                            # menu.menu sets up its own 'entities'.
                        *E.get_file_info(D), defaults=D)
            expected_list = self.starting_list[:]
            expected_list.append(self.new_entity)
            self.assertTrue((sorted(self.entities.lst)
                                        == sorted(expected_list)) and
                        (self.entities.default == self.new_entity))

    def tearDown(self):
        for entity in self.entities.lst:
            entity_dir = os.path.join(
                D['home'], entity+'.d')
            if os.path.isdir(entity_dir):
                shutil.rmtree(entity_dir)

"""
Main Menu:(No entities currently exist.)
    1. Create a new entity.
    2. Choose an existing entity.
    9. Delete an entity.
    0. Exit
Choice: 

Main Menu choice: 1
Picked '1. Create a new entity.'
Pick name for new entity: 
Aborting entity creation.

Choice: 1
Main Menu choice: 1
Picked '1. Create a new entity.'
Pick name for new entity: new_entity
Invalid entity name, try again or Enter to exit.
Pick name for new entity: newentity
Entity 'newentity' successfully created (and set as default.)
Stub of code to work with 'newentity' entity goes here.

"""



if __name__ == '__main__':  # code block to run the application
    unittest.main()
