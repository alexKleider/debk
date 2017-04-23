#!/bin/bash

# File: debk/test.sh

# Runs all of the tests with all of the output going into a file
###     testresults    ###
# and then calls vim on that file for user inspection.

echo Notices of expected logging reports are > testresults
echo NOT adjacent to reports themselves. >> testresults
echo  >> testresults

# NOTE: debk.money is tested with tests/money_test.sh (NOT '.py')
# See that file for explanations.
echo Running tests/money_test.sh..................... >> testresults
tests/money_test.sh >> testresults 2>&1

echo  >> testresults
echo Running tests/config_test.py >> testresults
tests/config_test.py >> testresults 2>&1

echo  >> testresults
echo Running tests/test_0.py......................... >> testresults
tests/test_0.py >> testresults 2>&1

echo  >> testresults
echo Running tests/test_1.py......................... >> testresults
tests/test_1.py >> testresults 2>&1

echo  >> testresults
echo Running tests/test_2.py......................... >> testresults
tests/test_2.py >> testresults 2>&1

echo  >> testresults
echo Running tests/test_3.py......................... >> testresults
tests/test_3.py >> testresults 2>&1

vim testresults
