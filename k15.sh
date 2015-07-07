./src/debk.py new --entity=Kazan15
./src/debk.py journal_entry < input
echo '
EXPLANATION:
Journal entries appear in the first half of this file, 
followed in the second half by the ledger: a listing of entries
and balances for each account.
Place holder accounts are simply listed without any corresponding
entries or balances (except for 5000- explained below.)

The value of canoes and other 'fixed assets' has been moved from the
equity to the liability accounts of the 'group of 8' who are now owners
of the canoes, and other things bought.  Do not be alarmed by the word
"liability."  This does not mean a liability born by you.  It means 
that the "trip entity" owes you the value of those assets.
The equity accounts reflect how much of your initial investment
remains (or, if negative, how much you owe.)

The total of the expense accounts has been balanced against the equity
accounts of all the participants:
The amount in account 5000 is meant to equal the sum of all the other
expense (5000) accounts and has been divided up and subtracted from the
participant equity accounts.
' > output
./src/debk.py show_journal >> output
echo '
Ledger follows:
' >> output
./src/debk.py -vv show_account_balances >> output
rm -r /var/opt/debk.d/Kazan15.d
cp output output.dos
todos output.dos
vim output

