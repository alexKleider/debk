#!../venv/bin/python3
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8 :
#
# file: '../t2.py'
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
Second test suite for debk.src.debk.py.
"""
import os
import csv
import json
import shutil
import unittest
import CSV.debk.src.debk as debk

VERSION = "v0.0.1"

DEFAULT_DIR = debk.DEFAULT_DIR

CofA = os.path.join(DEFAULT_DIR, 
                    debk.DEFAULT_CofA)

class JournalEntryTests(unittest.TestCase):
    def setUp(self):
        debk.create_entity('testentity')

    def test_ok(self):
        j = debk.JournalEntry(
          dict(
            number= "{:0>3}".format(3),
            date= 'Sept 3, 2015',
            user= 'book keeper',
            description= 'dummy journal entry',
            line_entries= [
                dict(acnt = '1234',
                    DR= 12.50,
                    CR= 0),
                dict(acnt = '2345',
                    DR= 0,
                    CR= 12.50),
            ]))
        self.assertTrue(j.ok())
 
    def tearDown(self):
        entity_dir = './tests/debk.d/testentity.d'
        if os.path.isdir(entity_dir):
            shutil.rmtree(entity_dir)
if __name__ == '__main__':  # code block to run the application
    unittest.main()


