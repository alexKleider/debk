# Double Entry Book Keeping

**debk.py** is a simple collection of utilities to facilitate double
entry book keeping.  It was inspired by Glen Jarvis who is working
on a (I suspect much more sophisticated) version of his own.

A major design decision (championed by Glen) is to keep all the data
files in text format (csv or json) to allow direct editing.
Large business entities (with so much data that it could not all be
held in memory at once) could not be accommodated.
Also note that it is **not** suitable for the naive user: assumed
is an understanding of what is meant by debit and credit and how
the significance differs depending on the account type.

## Installation

The following is a suggested way of getting up and running.

Choose (1.) a directory within which you want the project directory to
reside and (2.) a directory for the data files.  They can both be the
same directory; the latter can be within the former; they can be in
disparate locations of your choosing.

Let's assume you choose _/home/user/python_ to be the parent of your
project directory.  Make it your working directory and then execute
the following command:
_prompt>_ **git pull https://github.com/alexKleider/debk.git**
which will create a _debk_ directory tree containing the source
files.  Check that all the _.py_ files have the execution bits set.
_prompt>_ **chmod 755 .py**

The directory in which the data files are kept is specified in 
the _debk/src/config.py_ file. If you wish to change the default
value (_/var/opt/debk.d_) you'll have to edit _debk/src/config.py_
and change the value of DEFAULTS['home'].  Be sure to set ownership
and permissions appropriately.  You will need to use root privileges
to create and change ownership if you use the default.
_prompt>_ **sudo mkdir /var/opt/debk.d**
_prompt>_ **sudo chown alex:alex /var/opt/debk.d**
You must of course use your own user name (rather than 'alex'.)

Another requirement is to add your project directory to the
PYTHONPATH environment variable.  Provided is _path.sh_, a shell
script, which can be sourced, perhaps after editing to suit local
needs:
_prompt>_ **bash path.sh**
This script assumes that you've chosen your home directory into
which to clone the _debk_ project.  If not, edit to suit.

Finally, set up an environment: from within the project directory:
_prompt>_ **virtualenv -p python3 venv
_prompt>_ **source venv/bin/activate
To exit the environment (when done) the command to use is simply:
_prompt>_ **deactivate**


Usage:

The following is no longer implemented:
_prompt>_ **./src/python3 debk.py -h**
Instead use
_prompt>_ **./src/menu.py**

Most of the functionality is found in _src/debk.py_ although entity
creation is handled by _src/entities.py_.  A menu driven user
interface is provided by the _src/menu.py_ module.  The next level
down menu driven interface is provided by _src/workwith.py_.  There
is also a _src/config.py_ dependency.  A test suite is found under
the _tests_ directory.  _debk.d/defaultChartOfAccounts_ provides a 
suggested chart of accounts (aka ledger) which can be edited to 
suit your own needs.  Indentation is for readability only. Comments
are not permitted.  A copy must be placed in the _debk.d_ directory
discussed in the next paragraph.
_prompt>_ **cp debk.d/defaultChartOfAccounts**  \
                        **/var/opt/debk.d/defaultChartOfAccounts**
A leading white space stripped version of this file is treated as a
CSV file so apart from the leading white space, it must conform to
the format of a CSV file.

## Persistent Storage

The system depends on the existence of a debk.d directory found under
a 'home' directory specified by config.DEFAULTS['home'] by default
set to _/var/opt_. It must be populated with appropriate content
which at a minimum must include a _defaultChartOfAccounts_ file, an
example of which can be copied from _debk/debk.d/_.

## Entities

The system allows management of more than one set of books, each
representing a named entity.  Entity creation, selection and deletion
are handled through the menu interface which relies on entities.py.

Entity names must consist only of letters, no dashes or underscores.
Before creating a new entity, _testentity_ for example, you might like
to first create a testentityChartOfAccounts (a concatenation of the name
of the entity and 'ChartOfAccounts') and edit it to suit.
_debk/tests/debk.d/ManeroChartOfAccounts_ and
_debk/debk.d/defaultChartOfAccounts_ serve as examples.
New entity creation wil result in a new sub-directory **testentity.d**
populated it with the following files:
    CofA
    Journal.json
    Metadata.json
Any user must of course have read/write privileges.


## Journal Entry

Journal entry can be done individually by the user responding to
prompts, or, more conveniently, by means of a previously created
input file, as described in the file **how2input**.


## Back Ground

The project was inspired by the book keeping needs of a group
(Kazan15) taking a wilderness canoe trip on the Kazan River in
Nunavit, Canada. The soft ware includes several 'custom' features
specialized for this group. 


## Disclaimers

There is still, as of this version (0.0.1,) no support for adding
accounts except to create and then use a custom chart of accounts
prior to account creation as described in the create_entity()
docstring.  Although not tested, it should be possible after entity
creation to add accounts by simply editing the entity's CofA file.
Deleting accounts will likely create havoc!

To use this software, the user must have a clear idea of the meaning
of 'debit' and 'credit' in the context of double entry book keeping.
Familiarity with the command line, text editing, file manipulation
and Python's virtualenv is also assumed.
