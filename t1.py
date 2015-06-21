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

class CreateEntity(unittest.TestCase):
    """Test creation of an accounting entity."""

    entity = debk.ENTITIES['testEntity']
    entity_dir = os.path.join(debk.DEFAULT_HOME, entity)
    CofA = os.path.join(debk.DEFAULT_HOME,
                        debk.DEFAULT_CofA)

    def setUp(self):
        """
        """
        if os.path.isdir(self.entity_dir):  # tearDown not executed
            shutil.rmtree(self.entity_dir)  # if previous run failed.
        debk.create_entity(self.entity)

    def test_dir_creation(self):
        self.assertTrue(os.path.isdir(self.entity_dir))

    def test_CofA_creation(self):
        with open(os.path.join(debk.DEFAULT_HOME,
                                debk.DEFAULT_CofA), 'r') as f:
            original = f.read()
        with open(os.path.join(self.entity_dir,
                                debk.CofA_name), 'r') as f:
            new = f.read()
        self.assertEqual(original, new)

    def tearDown(self):
        """
        """
        shutil.rmtree(self.entity_dir)

class CreateAccount(unittest.TestCase):
    """Test account creation.
    """
    pass

if __name__ == '__main__':  # code block to run the application
    unittest.main()


