#!./venv/bin/python

# File: test_debk.py

import unittest
import src.debk as debk

testdata = (
          ("Dr 1111 5000.00", [debk.LineEntry('1111','D',5000.00),]),
          ("3100 5000.00 Cr", [debk.LineEntry('3100','C',5000.00),]),
           ("3100 5000.00Cr", [debk.LineEntry('3100','C',5000.00),]),
            ("3100 5000.0Cr", [debk.LineEntry('3100','C',5000.00),]),
             ("3100 5000.Cr", [debk.LineEntry('3100','C',5000.00),]),
              ("3100 5000Cr", None),
          ("1111 Cr 5000.00", [debk.LineEntry('1111','C',5000.00),]),
          ("1511 Dr 5000.00", [debk.LineEntry('1511','D',5000.00),]),
        ("no dr or cr found", None),

         ("Dr 1111 $5000.00", [debk.LineEntry('1111','D',5000.00),]),
         ("3100 $5000.00 Cr", [debk.LineEntry('3100','C',5000.00),]),
          ("3100 $5000.00Cr", [debk.LineEntry('3100','C',5000.00),]),
           ("3100 $5000.0Cr", [debk.LineEntry('3100','C',5000.00),]),
            ("3100 $5000.Cr", [debk.LineEntry('3100','C',5000.00),]),
             ("3100 $5000Cr", [debk.LineEntry('3100','C',5000.00),]),
         ("1111 Cr $5000.00", [debk.LineEntry('1111','C',5000.00),]),
         ("1511 Dr $5000.00", [debk.LineEntry('1511','D',5000.00),]),
    )

class TestDebk(unittest.TestCase):
    def test_list_from_text(self):
        for source, expected in testdata:
            with self.subTest(source=source, expected=expected):
                self.assertEqual(
                    debk.LineEntry.list_from_text(source),
                    expected)
if __name__ == "__main__":
    unittest.main()
