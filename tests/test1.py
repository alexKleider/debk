#!./venv/bin/python3
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8 :
#
# file: '../test1.py'
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
import sys
import csv
import json
import shutil
import unittest
import debk.src.entities as E
from debk.src.config import DEFAULTS as D
import debk.src.debk as debk

VERSION = "v0.0.1"

D['home'] = './tests/debk.d'  # for testing

CofA = os.path.join(D['home'], 
                    D['cofa_template'])
ENTITIES = ['EntityNoAccounts',
            'testentity',
            ]
entity_dirs = {entity: os.path.join(
                    D['home'], entity+'.d')
                            for entity in ENTITIES}

def testing_wrapper(collect, source=None):
    """
    """
    if source:
        ostdin = sys.stdin
        ostdout = sys.stdout
        src = open(source, 'r')
        sys.stdin = src
        out = open('/dev/null', 'w')  # Dump the prompts.
        sys.stdout = out
    
    ret = collect()

    if source:
        src.close()
        out.close()
        sys.stdin = ostdin
        sys.stdout = ostdout
    
    return ret

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

class none2float(unittest.TestCase):
    """test the global function none2float(n)"""

    def test_none(self):
        self.assertEqual(debk.none2float(None), 0.0)

    def test_False(self):
        self.assertEqual(debk.none2float(False), 0.0)

    def test_True(self):
        self.assertEqual(debk.none2float(True), 1.0)

    def test_45(self):
        self.assertEqual(debk.none2float(45), 45.0)

    def test_number_string(self):
        self.assertEqual(debk.none2float("45"), 45.0)

    def test_non_number_string_error(self):
        print("Expect logging critical re Not a number.")
        with self.assertRaises(ValueError):
            debk.none2float("Not a number")

class divider(unittest.TestCase):
    """test the global divider() function"""

    def test10by3(self):
        self.assertEqual(debk.divider(10, 3), [3.34, 3.33, 3.33])

    def test_minus10by3(self):
        # Handles negative dividend appropriately.
        self.assertEqual(debk.divider(-10, 3), [-3.33, -3.33, -3.34])

    def test_minus10by_minus3(self):
        print("Expect logging critical re -10 and -3")
        with self.assertRaises(AssertionError):
            debk.divider(-10, -3)

    def test10by_minus3(self):
        print("Expect logging critical re -3")
        with self.assertRaises(AssertionError):
            debk.divider(10, -3)

    def test_minus10by_0(self):
        print("Expect logging critical re -10 and div by 0")
        with self.assertRaises(ZeroDivisionError):
            debk.divider(-10, 0)

class ValidAccountType(unittest.TestCase):
    """Test global function valid_account_type(_type)."""
    def test_valid_account_types(self):
        testdata = [("Debit", True), ("Credit", True),
                    ("D", True), ("C", True),
                    ("debit", True), ("credit", True),
                    ('d', True), ('c', True),
                    ('junk string', False),
                    ('has debit & credit in it', False),
                    ({'debit': 'debit entry'}, False),
                    (0, False), ('', False), (None, False), ]
        for entry, result in testdata:
            with self.subTest(entry=entry, result=result):
                self.assertEqual(debk.valid_account_type(entry), result)

class AcntTypeFromCode(unittest.TestCase):
    """Test the acnt_type_from_code() function using a 'TestCase'.
    """
    def test_acnt_type_from_code(self):
        testdata = [
            ("1234", "Dr"),
            ("2341", "Cr"),
            ("3412", "Cr"),
            ("4123", "Cr"),
            ("5678", "Dr"),
            ("6789", None),
            ("0123", None),
            ("", None),
            ]
        print("\nExpect logging critical re 3 malformed codes.")
        for code, dr_cr in testdata:
            with self.subTest(code=code, dr_cr=dr_cr):
                self.assertEqual(debk.acnt_type_from_code(code), dr_cr)

class CreateEntity(unittest.TestCase):
    """Test creation of an accounting entity."""

    def setUp(self):
        """
        """
        for entity_dir in entity_dirs.values():
            if os.path.isdir(entity_dir):  # tearDown not executed
                shutil.rmtree(entity_dir)  # if previous run failed.
        for entity in ENTITIES:
            E.create_entity(entity, D)

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
        with open(os.path.join(D['home'],
                        D['cofa_template']), 'r') as f:
            original = f.read()
        with open(os.path.join(
                        D['home'],
                        ENTITIES[0]+'.d',
                        D['cofa_name']), 'r') as f:
            new = f.read()
        self.assertEqual(original, new)

    def test_CofA_creation_1(self):
        """
        Tests creation of a prepopulated CofA.
        """
        with open(os.path.join(D['home'],
                        'testentityChartOfAccounts'),
                'r') as f:
            original = f.read()
        with open(os.path.join(
                        D['home'],
                        ENTITIES[1]+'.d',
                        D['cofa_name']), 'r') as f:
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

class LineEntry(unittest.TestCase):
    """Test LineEntry class"""

    def test_init_and_str(self):
        testdata = [
            ((2, 'D', 12.30),   "  je#002       12.30Dr              "),
            ((3, 'C', 12.30),   "  je#003                     12.30Cr"),
            ]
        for params, show in testdata:
            with self.subTest(params=params, show=show):
                self.assertEqual(
                    debk.LineEntry(*params).show(),show)

    def test_str_error(self):
        print(
"Expect logging critical re LineEntry.__init__ with bad type_: '0'")
        with self.assertRaises(ValueError):
            debk.LineEntry("12.30", '0', 5).show()

class CreateAccount(unittest.TestCase):
    """Test account creation.
    code,indent,full_name,name,notes,hidden,place_holder,split
    """

    def setUp(self):
        self.acnt = debk.Account(
            dict(code= '1020', indent= 3,
                full_name= 'Full Name', name= 'Account Name',
                hidden= 'F', place_holder= 'F', split= 0)
                )

    def test_place_holder(self):
        self.assertFalse(self.acnt.place_holder)

    def test_s_balance_dr_cr(self):
        self.acnt.balance = 4.40
        self.acnt.acnt_type = 'Cr'
        self.assertEqual(self.acnt.signed_balance,
                        -self.acnt.balance)

    def test_s_balance_dr_cr_0(self):
        self.acnt.balance = 0
        self.acnt.acnt_type = 'Cr'
        self.assertEqual(self.acnt.signed_balance,
                        self.acnt.balance)

    def test_s_balance_dr_dr_neg(self):
        self.acnt.balance = -4.40
        self.acnt.dr_cr = 'Dr'
        self.assertEqual(self.acnt.signed_balance,
                        self.acnt.balance)

    def test_s_balance_cr_dr(self):
        self.acnt.code = '2050'
        self.acnt.balance = 4.40
        self.acnt.dr_cr = 'Dr'
        self.assertEqual(self.acnt.signed_balance,
                        -self.acnt.balance)

    def test_s_balance_cr_dr_0(self):
        self.acnt.code = '2050'
        self.acnt.balance = 0
        self.acnt.dr_cr = 'Dr'
        self.assertEqual(self.acnt.signed_balance,
                        self.acnt.balance)

    def test_s_balance_cr_cr_neg(self):
        self.acnt.code = '2050'
        self.acnt.balance = -4.40
        self.acnt.dr_cr = 'Cr'
        self.assertEqual(self.acnt.signed_balance,
                        self.acnt.balance)


class Account_empty(unittest.TestCase):
    """Test Account class
    Tests only the opening of a file and presentation
    of a few accounts but with no journal entries.
    Will test further under ChartOfAccounts."""
    
    def setUp(self):
        self.cofa = []
        with open("./tests/debk.d/testentityChartOfAccounts",
                'r') as cofa_file_object:
            reader = csv.DictReader(cofa_file_object)
            for row in reader:  # Collects a CofAs without entries.
                self.cofa.append(debk.Account(row))
#               print(debk.Account(row))  #debugging print


    def test_init_and_str(self):
        testdata = [
    (19, 'Acnt#3000 EQUITY  Title_Account- subtotal: 0.00'),
    (50, '      Acnt#5501 Petrol          (/10) Total:      0.00'),
            ]
        for n, show in testdata:
            with self.subTest(n=n, show=show):
#               print("\n{}\n".format(self.cofa[n].__str__()))
                self.assertEqual(
                    self.cofa[n].__str__(), show)

class Account_signed_balance(unittest.TestCase):
    """
    Creates (debk.Account())  and then
    populates some values into instances of Account.
    """
    def test_signed_balance_Dr_accounts(self):
        acnt_dict = dict(code= '1110', indent= 0,
                full_name= 'Full Name', name= 'Account Name',
                notes= 'Some notes about the account.',
                hidden= 'F', place_holder= 'F')
        testdata = []

        acnt1p = debk.Account(acnt_dict)
        acnt1p.balance = 2.5; acnt1p.type_ = 'D'
        testdata.append((acnt1p.signed_balance, 2.5))
        acnt1n = debk.Account(acnt_dict)
        acnt1n.balance = -2.5; acnt1n.type_ = 'D'
        testdata.append((acnt1n.signed_balance, -2.5))
        
        acnt2p = debk.Account(acnt_dict)
        acnt2p.code = '2110'
        acnt2p.balance = 2.5; acnt2p.type_ = 'C'
        testdata.append((acnt2p.signed_balance, 2.5))
        acnt2n = debk.Account(acnt_dict)
        acnt2n.code = '2110'
        acnt2n.balance = -2.5; acnt2n.type_ = 'C'
        testdata.append((acnt2n.signed_balance, -2.5))
        
        acnt3p = debk.Account(acnt_dict)
        acnt3p.code = '3110'
        acnt3p.balance = 2.5; acnt3p.type_ = 'C'
        testdata.append((acnt3p.signed_balance, 2.5))
        acnt3n = debk.Account(acnt_dict)
        acnt3n.code = '3110'
        acnt3n.balance = -2.5; acnt3n.type_ = 'C'
        testdata.append((acnt3n.signed_balance, -2.5))
        
        acnt4p = debk.Account(acnt_dict)
        acnt4p.code = '4110'
        acnt4p.balance = 2.5; acnt4p.type_ = 'C'
        testdata.append((acnt4p.signed_balance, 2.5))
        acnt4n = debk.Account(acnt_dict)
        acnt4n.code = '4110'
        acnt4n.balance = -2.5; acnt4n.type_ = 'C'
        testdata.append((acnt4n.signed_balance, -2.5))
        
        acnt5p = debk.Account(acnt_dict)
        acnt5p.code = '5110'
        acnt5p.balance = 2.5; acnt5p.type_ = 'D'
        testdata.append((acnt5p.signed_balance, 2.5))
        acnt5n = debk.Account(acnt_dict)
        acnt5n.code = '5110'
        acnt5n.balance = -2.5; acnt5n.type_ = 'D'
        testdata.append((acnt5n.signed_balance, -2.5))

        for result, expected in testdata:
            with self.subTest(result=result, expected=expected):
                self.assertEqual(result, expected)

class Account_loaded(unittest.TestCase):
    """Test Account class
    I think this can more easily be done once we have 
    a chart of accounts."""
    def setUp(self):
        pass

problem = """
ERROR: test_sum_accounts2 (__main__.Ledger)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "./tests/test1.py", line 523, in setUp
    self.cofa = debk.ChartOfAccounts(D)
  File "/home/alex/Py/CSV/debk/src/debk.py", line 502, in __init__
    self.entity = defaults['entity']
KeyError: 'entity'
"""

class JournalClass(unittest.TestCase):

    def setUp(self):
        if os.path.isdir('./tests/debk.d/testentity.d'):
            print("Deleting '{}'- shouldn't exist."
                .format('./tests/debk.d/testentity.d'))
            shutil.rmtree('./tests/debk.d/testentity.d')
        E.create_entity("testentity", D)

    def test_load(self):
        self.maxDiff = None
        journal = debk.Journal(D)
        journal.extend(debk.JournalEntry.load(
"""July 3, 2015
Alex Kleider
Pay for some food.
5310 304.20 Dr
3009 Cr 304.20

August 26, 2015
book keeper
Reflect ownership of fixed assets.
3001,3002,3003,3004,3005,3006,3007,3008 Dr 2100.50
2001,2002,2003,2004,2005,2006,2007,2008 Cr 2100.50

"""))
        report = journal.show()
        expected = (
"""
JOURNAL ENTRIES:......           Entity: 'testentity'

  #001 on July 3, 2015 by Alex Kleider.
    Pay for some food.
      5310:      304.20Dr
      3009:                    304.20Cr
  #002 on August 26, 2015 by book keeper.
    Reflect ownership of fixed assets.
      3001:      262.57Dr
      3002:      262.57Dr
      3003:      262.56Dr
      3004:      262.56Dr
      3005:      262.56Dr
      3006:      262.56Dr
      3007:      262.56Dr
      3008:      262.56Dr
      2001:                    262.57Cr
      2002:                    262.57Cr
      2003:                    262.56Cr
      2004:                    262.56Cr
      2005:                    262.56Cr
      2006:                    262.56Cr
      2007:                    262.56Cr
      2008:                    262.56Cr""")
#       print("Expected is:\n{}".format(expected))
#       print("report is:\n{}".format(report))
        self.assertEqual(report, expected)

    def tearDown(self):
        try:
            shutil.rmtree('./tests/debk.d/testentity.d')
        except FileNotFoundError:
            print(
        "'./tests/debk.d/testentity.d' doesn't exist; can't delete.")

class Ledger(unittest.TestCase):
    """Test ChartOfAccounts and Account classes."""
    def setUp(self):
        entity_dir = './tests/debk.d/Manero.d'
        if os.path.isdir(entity_dir):
            shutil.rmtree(entity_dir)
            print(
"Shouldn't need to delete entity dir '{}'".format(entity_dir))
        self.test_entity = "Manero"
        self.test_journal_input = (
            '/home/alex/Py/CSV/debk/tests/debk.d/Manero_input0')
        self.entity = E.create_entity(self.test_entity, D)
        self.cofa = debk.ChartOfAccounts(D)
        self.journal = debk.Journal(D)
        self.journal.load(self.test_journal_input)
        print("\ntest1-Ledger setUP:\n".       # debugging print
                format(self.journal.show()))
        self.journal.save()
        self.cofa.load_journal_entries(self.journal.journal)
        with open('TestReport', 'w') as file_object:  # debugging pr
            file_object.write(self.cofa.show_accounts())

    def test_init(self):
        self.assertEqual(self.test_entity, self.entity)

    def test_sum_accounts0(self):
        """This test will break if the account code schema changes."""
        testdata = [
            (self.cofa.sum_accounts("1000:1999"), 22600.00), 
            (self.cofa.sum_accounts("2000:2999"), 7000.00),  # 0
            (self.cofa.sum_accounts("3000:3999"), 15000.00), # 
            (self.cofa.sum_accounts("4000:4999"), 600.00),  
            (self.cofa.sum_accounts("5000:5999"), 00.00),  #
                    ]
        for acnt_sum, amount in testdata:
            with self.subTest(acnt_sum=acnt_sum, amount=amount):
                self.assertEqual("{:.2f}".format(acnt_sum),
                                "{:.2f}".format(amount))
#       total_Dr = (
#               self.cofa.sum_accounts("1000:1999") +
#               self.cofa.sum_accounts("5000:5999")
#               )
#       total_Cr = (
#               self.cofa.sum_accounts("2000:2999") +
#               self.cofa.sum_accounts("3000:3999") +
#               self.cofa.sum_accounts("4000:4999")
#               )
#       self.assertEqual("{:.2f}".format(total_Dr - total_Cr),
#                       "{:.2f}".format(0))

    def test_sum_accounts1(self):
        self.assertEqual('{:.2f}'.format(
                            self.cofa.sum_accounts([1210, 1311])),
                        '{:.2f}'.format(7000))
    def test_sum_accounts2(self):
        total = '{:.2f}'.format(
                self.cofa.sum_accounts("2000:3999"))
        self.assertEqual(total, '{:.2f}'.format(22000))

    def tearDown(self):
        return
        entity_dir = './tests/debk.d/testentity.d'
        if os.path.isdir(entity_dir):
            shutil.rmtree(entity_dir)

if __name__ == '__main__':  # code block to run the application
    unittest.main()


