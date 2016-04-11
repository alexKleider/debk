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
'verify_ledger.py' is a utility that accompanies the double entry
book keeping (debk) system.  Its purpose is to verify that a 
<entity>ChartOfAccounts file is valid.

Usage:
    ./verify_ledger.py <fleName>

"""

import os
import sys
import re
import CSV.debk.src.config as config

leading_white_space = r'^\s+'
p_object = re.compile(leading_white_space)

def check_line(line):
    """
    Given a line, checks its validity. If valid, does nothing.
    If invalid, a report (in the form of a string) is returned.
    """
    report_list = []
    m_object = p_object.match(line)
    if m_object == None:
        indent = 0
#       print("No indent discovered.")
    else:
        span = m_object.span()
        indent = span[1] - span[0]
        if indent%4: report_list.append("Indent%4!=0")
        indent = indent//4
#       print("Indent is {}.".format(indent))
    line = line.strip()
    parts = line.split(',')
    if len(parts) < config.N_COMPONENTS:
        report_list.append("Too few, no point continuing.")
    else:
        if '{}'.format(indent) != parts[1]:
            report_list.append("Indentation mismatch")
    return '; '.join(report_list)

def validate(file_object):
    """
    Given a file object, returns a report (in the form of a string) if
    validation fails; otherwise returns None.
    """
    report = ["Validation errors (Line # followed by description:)"]
    line_number = 0
    for line in file_object:
        line_number += 1
        if line_number == 1:
            parts = line.split(',')
            parts = [part.strip() for part in parts]
            assert(parts[:config.N_COMPONENTS] ==
                    config.CofA_HEADERS[:config.N_COMPONENTS])
        else:
            res = check_line(line)
            if res:
                report.append('{:>3d} {}'.format(line_number, res))
    if len(report) > 1:
        return '\n'.join(report)

def bad_ledger_file(file_name):
    with open(file_name, 'r') as file_object:
        if validate(file_object):
            return True

def main():
    if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
        print("'verify_ledger.py' must have a file name parameter.")
        sys.exit(1)
    else:
        ledger_file_name = sys.argv[1]
    with open(ledger_file_name, 'r') as file_object:
        error_report = validate(file_object)
    if error_report:
        output_file_name = input("""
Validation fails! Report will be sent to a file if provided,
to StdOut if not: """)
        if output_file_name:
            with open(output_file_name, 'w') as file_object:
                file_object.write(error_report)
        else:
            print(error_report)
    else:
        print("File '{}', validates."
            .format(ledger_file_name))

if __name__ == "__main__":
    main()
