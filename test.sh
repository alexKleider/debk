#!/bin/bash
rm -f testresults
echo \
Notices of expected logging reports are NOT adjacent to reports themselves.\
> testresults
tests/test_0.py >> testresults 2>&1
tests/test_1.py >> testresults 2>&1
tests/test_2.py >> testresults 2>&1
tests/test_3.py >> testresults 2>&1
less testresults
