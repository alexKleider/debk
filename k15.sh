#!/user/bin/bash
./src/debk.py new --entity=Kazan15
./src/debk.py journal_entry < input
cat explanation > output
printf "\n\f" >> output
./src/debk.py show_journal >> output
echo '
Ledger follows:
' >> output
printf "\f" >> output
echo 'Account balances for Kazan15 entity.
' >> output
./src/debk.py -vv show_account_balances >> output
rm -r /var/opt/debk.d/Kazan15.d
cp output output.dos
todos output.dos
mv output.dos ~/Sask/Kazan15/
vim output

