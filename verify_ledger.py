#!./venv/bin/python
# -*- coding: utf-8 -*-
# vim: set file encoding=utf-8
#
# file: 'verify_ledger.py'
# Part of ___, ____.

# Copyright 2015 Alex Kleider
#   This program is free software: you can redistribute it and/or
#   modify #   it under the terms of the GNU General Public License
#   as published by the Free Software Foundation, either version 3
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.
#   If not, see <http://www.gnu.org/licenses/>.
#   Look for file named COPYING.
"""
'verify_ledger.py' is a utility that accompanies the double entry book
keeping system.
Its purpose is to verify that a <entity>ChartOfAccounts file is valid.
Usage:
    ./verify_ledger.py <fleName>
"""

import os
import sys

def check_line(line, report):
    """
    Given a line, checks its validity. If valid, does nothing.
    If it is invalid, an entry is appended to report_array.
    """
    pass

def validate(file_object):
    """
    Given a file object, result will be a tuple consisting of 
    (0, '') if successful, or
    (1, <error report>) if not.
    """
    report = ["Validation errors:"]
    line_number = 1
    for line in file_object:
        line_report = check_line(line, report)
    if len(report) > 1:
        return (0, '')
    else:
        return (1, '\n'.join(report))

def main()
    if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
        print("'verify_ledger.py' must have a file name parameter."
        sys.exit(1)
    else:
        ledger_file_name = sys.argv[1]
    with open(ledger_file_name, 'r') as file_object:
        exit_status, error_report = validate(file_object)
    if exit_status:
        output_file_name = ("""
Validation fails! Report will be sent to a file if provided,
to StdOut if not: """)
        if output_file_name:
            with open(output_file_name, 'w') as file_object:
                file_object.write(error_report)
        else:
            print(error_report)
    else:
        assert(exit_status == 0)
        assert(error_report = '')
        print("The file '{}', validates successfully."
            .format(ledger_file_name))

if __name__ == "__main__":
    main()
