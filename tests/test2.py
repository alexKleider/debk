#!./venv/bin/python3
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
from unittest import mock
from CSV.debk.src import debk
from CSV.debk.src import entities as E
from CSV.debk.src.config import DEFAULTS as D

VERSION = "v0.0.1"


class JournalEntryTests(unittest.TestCase):

    def test_ok(self):
        j = debk.JournalEntry.from_dict(
          dict(
            entry_number= 3,
            date_stamp= 'Sept 3, 2015',
            user= 'book keeper',
            description= 'dummy journal entry',
            line_items= [
                dict(account_code = '1234',
                    amount= 12.50,
                    type_= 'C'),
                dict(account_code = '2345',
                    type_= 'D',
                    amount= 12.50),
            ]))
        self.assertTrue(j.ok())

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
        acnt1p.code = '1110'
        acnt1p.balance = 1.5; acnt1p.type_ = 'D'
        testdata.append((acnt1p.signed_balance, 1.5))
        acnt1n = debk.Account(acnt_dict)
        acnt1n.balance = -2.5; acnt1n.type_ = 'D'
        testdata.append((acnt1n.signed_balance, -2.5))
        
        acnt2p = debk.Account(acnt_dict)
        acnt2p.code = '2110'
        acnt2p.balance = 3.5; acnt2p.type_ = 'C'
        testdata.append((acnt2p.signed_balance, 3.5))
        acnt2n = debk.Account(acnt_dict)
        acnt2n.code = '2110'
        acnt2n.balance = -4.5; acnt2n.type_ = 'C'
        testdata.append((acnt2n.signed_balance, -4.5))
        
        acnt3p = debk.Account(acnt_dict)
        acnt3p.code = '3110'
        acnt3p.balance = 5.5; acnt3p.type_ = 'C'
        testdata.append((acnt3p.signed_balance, 5.5))
        acnt3n = debk.Account(acnt_dict)
        acnt3n.code = '3110'
        acnt3n.balance = -6.5; acnt3n.type_ = 'C'
#       print(acnt3n.show_account())   # debugging print
        testdata.append((acnt3n.signed_balance, -6.5))
        
        acnt4p = debk.Account(acnt_dict)
        acnt4p.code = '4110'
        acnt4p.balance = 7.5; acnt4p.type_ = 'C'
        testdata.append((acnt4p.signed_balance, 7.5))
        acnt4n = debk.Account(acnt_dict)
        acnt4n.code = '4110'
        acnt4n.balance = -8.5; acnt4n.type_ = 'C'
        testdata.append((acnt4n.signed_balance, -8.5))
        
        acnt5p = debk.Account(acnt_dict)
        acnt5p.code = '5110'
        acnt5p.balance = 9.5; acnt5p.type_ = 'D'
        testdata.append((acnt5p.signed_balance, 9.5))
        acnt5n = debk.Account(acnt_dict)
        acnt5n.code = '5110'
        acnt5n.balance = -10.5; acnt5n.type_ = 'D'
        testdata.append((acnt5n.signed_balance, -10.5))

        n = 0
        for result, expected in testdata:
            with self.subTest(result=result, expected=expected):
                n += 1
#               print("testing #{}: {}  {}"   # debugging print
#                       .format(n, result, expected))
                self.assertEqual(result, expected)

if __name__ == '__main__':  # code block to run the application
    unittest.main()


