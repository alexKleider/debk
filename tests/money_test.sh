#!/bin/bash

# File: tests/money_test.sh

# Runs .tests/money_test.py once for each currency symbol.
# This file will have to be changed if changes are made to
# the currency components of src/config.py- specifically:
#     src.config.CURRENCY_SYMBOLS and
#     src.config.DEFAULT_CURRENCY

./tests/money_test.py
sed -i 's/DEFAULT_CURRENCY = "dollar"/DEFAULT_CURRENCY = "pound"/g' src/config.py
./tests/money_test.py
sed -i 's/DEFAULT_CURRENCY = "pound"/DEFAULT_CURRENCY = "euro"/g' src/config.py
./tests/money_test.py
sed -i 's/DEFAULT_CURRENCY = "euro"/DEFAULT_CURRENCY = "yen"/g' src/config.py
./tests/money_test.py
sed -i 's/DEFAULT_CURRENCY = "yen"/DEFAULT_CURRENCY = "rupee"/g' src/config.py
./tests/money_test.py
sed -i 's/DEFAULT_CURRENCY = "rupee"/DEFAULT_CURRENCY = "Iceland krona"/g' src/config.py
./tests/money_test.py
sed -i 's/DEFAULT_CURRENCY = "Iceland krona"/DEFAULT_CURRENCY = "dollar"/g' src/config.py

