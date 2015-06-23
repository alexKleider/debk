#!venv/bin/python3
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8 :
#
# file: '../t1.py'
# Part of debk, Double Entry Book Keeping module.

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
First test suite for debk module.
"""
import os
import shutil
import unittest
import src.debk as debk

VERSION = "v0.0.1"

ENTITIES = ['EntityNoAccounts',
            'EntityPrepopulatedAccounts',
            ]
entity_dirs = [os.path.join(debk.DEFAULT_HOME, entity)
                            for entity in ENTITIES]
CofA = os.path.join(debk.DEFAULT_HOME, debk.DEFAULT_CofA)

class CreateEntity(unittest.TestCase):
    """Test creation of an accounting entity."""

    def setUp(self):
        """
        """
        for entity_dir in entity_dirs:
            if os.path.isdir(entity_dir):  # tearDown not executed
                shutil.rmtree(entity_dir)  # if previous run failed.
        for entity in ENTITIES:
            debk.create_entity(entity)

    def test_dir_creation(self):
        for entity_dir in entity_dirs:
            self.assertTrue(os.path.isdir(entity_dir))

    def test_CofA_creation0(self):
        with open(os.path.join(debk.DEFAULT_HOME,
                                debk.DEFAULT_CofA), 'r') as f:
            original = f.read()
        with open(os.path.join(debk.DEFAULT_HOME,
                                ENTITIES[0],
                                debk.CofA_name), 'r') as f:
            new = f.read()
        self.assertEqual(original, new)

    def test_CofA_creation1(self):
        with open(os.path.join(debk.DEFAULT_HOME,
                                'kazan15ChartOfAccounts'), 'r') as f:
            original = f.read()
        with open(os.path.join(debk.DEFAULT_HOME,
                                ENTITIES[1],
                                debk.CofA_name), 'r') as f:
            new = f.read()
        self.assertEqual(original, new)

    def tearDown(self):
        """
        """
        for entity_dir in entity_dirs:
            shutil.rmtree(entity_dir)

class CreateAccount(unittest.TestCase):
    """Test account creation.
    """
    pass

if __name__ == '__main__':  # code block to run the application
    unittest.main()


