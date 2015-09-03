#!../venv/bin/python3
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
First test suite for debk.src.debk.py.
"""
import os
import json
import shutil
import unittest
import debk

VERSION = "v0.0.1"

CofA = os.path.join(debk.DEFAULT_DIR, 
                    debk.DEFAULT_CofA)
ENTITIES = ['EntityNoAccounts',
            'Kazan15',
            ]
entity_dirs = {entity: os.path.join(
                    debk.DEFAULT_DIR, entity+'.d')
                            for entity in ENTITIES}

class CreateEntity(unittest.TestCase):
    """Test creation of an accounting entity."""

    def setUp(self):
        """
        """
        for entity_dir in entity_dirs.values():
            if os.path.isdir(entity_dir):  # tearDown not executed
                shutil.rmtree(entity_dir)  # if previous run failed.
        for entity in ENTITIES:
            debk.create_entity(entity)

    def test_dir_creation(self):
        """
        Tests that new home directories are created for each entity.
        """
        for entity in ENTITIES:
            self.assertTrue(os.path.isdir(entity_dirs[entity]))

    def test_CofA_creation_0(self):
        """
        Tests creation of a non prepopulated CofA.
        """
        with open(os.path.join(debk.DEFAULT_DIR,
                        debk.DEFAULT_CofA), 'r') as f:
            original = f.read()
        with open(os.path.join(
                        debk.DEFAULT_DIR,
                        ENTITIES[0]+'.d',
                        debk.CofA_name), 'r') as f:
            new = f.read()
        self.assertEqual(original, new)

    def test_CofA_creation_1(self):
        """
        Tests creation of a prepopulated CofA.
        """
        with open(os.path.join(debk.DEFAULT_DIR,
                        'Kazan15ChartOfAccounts'),
                'r') as f:
            original = f.read()
        with open(os.path.join(
                        debk.DEFAULT_DIR,
                        ENTITIES[1]+'.d',
                        debk.CofA_name), 'r') as f:
            new = f.read()
#       print()
#       print(original)
#       print(new)
#       print()
        self.assertEqual(original, new)

    def test_JournalCreation(self):
        """
        Tests that an empty journal has been created.
        """
        for entity_dir in entity_dirs.values():
            with open(os.path.join(entity_dir, 'Journal.json'),
                    'r') as journal_file_obj:
                self.assertTrue(
                    journal_file_obj.read() == '{"Journal": []}') 

    def test_MetadataFileCreation(self):
        """
        Tests for a correclty set up json metadata file.
        """
        for entity in ENTITIES:
            match = {"next_journal_entry_number": 1,
                    "entity_name": entity}
            with open(os.path.join(entity_dirs[entity],
                        'Metadata.json'), 'r') as metadata_file_obj:
                metadata = json.load(metadata_file_obj)
#               print()
#               print(match)
#               print(metadata)
#               print(entity)
#               print()
                self.assertTrue(metadata == match) 

    def tearDown(self):
        """
        """
        for entity in ENTITIES:
            shutil.rmtree(entity_dirs[entity])

class global_show_args(unittest.TestCase):
    """test the global function show_args()"""

    def test_list(self):
        """test with a list"""
        ret = debk.show_args(
                    ['Aaron', 'Alex', 'Other people'],
                    'People')
        expect = """People are ...
  Aaron
  Alex
  Other people
  ... end of report.
"""
        self.assertEqual(ret, expect)

    def test_dict(self):
        """test with a dict"""
        ret = debk.show_args(dict(teacher= 'Aaron',
                            pupil= 'Alex',
                            ), 'People')
        expect1 = """People are ...
  teacher: Aaron
  pupil: Alex
  ... end of report.
"""
        expect2 = """People are ...
  pupil: Alex
  teacher: Aaron
  ... end of report.
"""
        comparison = (ret == expect1) or (ret == expect2)
#       print()
#       print('\n'.join((ret, expect1, expect2)))
        self.assertTrue(comparison)

class global_dr_or_cr(unittest.TestCase):
    """Test the dr_or_cr() function using a 'TestCase'.
    """
    def test_dr_or_cr(self):
        testdata = [
            ("1234", "DR"),
            ("2341", "CR"),
            ("3412", "CR"),
            ("4123", "CR"),
            ("5678", "DR"),
            ("6789", None),
            ("0123", None),
            ("", None),
            ]
        for code, dr_cr in testdata:
            with self.subTest(code=code, dr_cr=dr_cr):
                self.assertEqual(debk.dr_or_cr(code), dr_cr)


class CreateAccount(unittest.TestCase):
    """Test account creation.
    """
    def setUp(self):
        self.acnt = debk.Account(
            dict(code= '1020',
                indent= 3,
                split= 0,
                place_holder= 'F',
                ))

    def test_place_holder(self):
        self.assertFalse(self.acnt.place_holder)

    def test_s_balance_dr_cr(self):
        self.acnt.balance = 4.40
        self.acnt.dr_cr = 'CR'
        self.assertEqual(self.acnt.signed_balance(),
                        -self.acnt.balance)

    def test_s_balance_dr_cr_0(self):
        self.acnt.balance = 0
        self.acnt.dr_cr = 'CR'
        self.assertEqual(self.acnt.signed_balance(),
                        self.acnt.balance)

    def test_s_balance_dr_dr_neg(self):
        self.acnt.balance = -4.40
        self.acnt.dr_cr = 'DR'
        self.assertEqual(self.acnt.signed_balance(),
                        self.acnt.balance)

    def test_s_balance_cr_dr(self):
        self.acnt.code = '2050'
        self.acnt.balance = 4.40
        self.acnt.dr_cr = 'DR'
        self.assertEqual(self.acnt.signed_balance(),
                        -self.acnt.balance)

    def test_s_balance_cr_dr_0(self):
        self.acnt.code = '2050'
        self.acnt.balance = 0
        self.acnt.dr_cr = 'DR'
        self.assertEqual(self.acnt.signed_balance(),
                        self.acnt.balance)

    def test_s_balance_cr_cr_neg(self):
        self.acnt.code = '2050'
        self.acnt.balance = -4.40
        self.acnt.dr_cr = 'CR'
        self.assertEqual(self.acnt.signed_balance(),
                        self.acnt.balance)
class JournalClass(unittest.TestCase):

    def setUp(self):
        debk.create_entity("Kazan15")

    def test_load(self):
        self.maxDiff = None
        journal = debk.Journal({"--entity": 'Kazan15'})
        journal.load(
"""August 26, 2015
book keeper
Reflect ownership of fixed assets.
3001,3002,3003,3004,3005,3006,3007,3008 Dr 2100.50
2001,2002,2003,2004,2005,2006,2007,2008 Cr 2100.50

""")
        report = journal.show()
        expected = (
"""
JOURNAL ENTRIES:......           Entity: 'Kazan15'

  #001 on August 26, 2015 by book keeper.
    Reflect ownership of fixed assets.
    3001:    262.57          
    3002:    262.57          
    3003:    262.56          
    3004:    262.56          
    3005:    262.56          
    3006:    262.56          
    3007:    262.56          
    3008:    262.56          
    2001:              262.57
    2002:              262.57
    2003:              262.56
    2004:              262.56
    2005:              262.56
    2006:              262.56
    2007:              262.56
    2008:              262.56""")
        print("Expected is:\n{}".format(expected))
        print("report is:\n{}".format(report))
        self.assertEqual(report, expected)

    def tearDown(self):
        try:
            shutil.rmtree('/var/opt/debk/Kazan15.d')
        except FileNotFoundError:
            print(
        "'/var/opt/debk/Kazan15.d' doesn't exist; can't delete.")


if __name__ == '__main__':  # code block to run the application
    unittest.main()


