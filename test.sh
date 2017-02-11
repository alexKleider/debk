#!/bin/bash

# Runs all of the tests with all of the output going into a file
###     testresults    ###
# and then calls vim on that file for user inspection.
rm -f testresults
echo \
Notices of expected logging reports are NOT adjacent to reports themselves.\
> testresults
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
