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

The directory in which the data files are kept is specified in 
the _debk/src/config.py_ file. If you wish to change the default
value (_/var/opt/debk.d_) you'll have to edit _debk/src/config.py_
and change the value of DEFAULTS['home'].  Be sure to set ownership
and permissions appropriately.  You will need to use root privileges
to create and change ownership if you use the default.

Another requirement is to add your project directory to the
PYTHONPATH environment variable.  Provided is _path.sh_, a shell
script, which can be sourced, perhaps after editing to suit local
needs:
_prompt>_ **bash path.sh**
This assumes that you've chosen your
home directory into which to clone the _debk_ project.

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
interface is provided in _src/menu.py_ module.  The next level down
menu driven interface is provided by _src/workwith.py_.  There is
also a _src/config.py_ dependency.  A test suite is found under the
_tests_ directory.  _debk.d/defaultChartOfAccounts_ provides a 

## Persistent Storage

The system depends on the existence of a debk.d directory found under
a 'home' directory specified by config.DEFAULTS['home'] by default set
to /var/opt. It must be populated with appropriate content which at a
minimum must include a _defaultChartOfAccounts_ file, an example of
which can be copied from _debk/debk.d/_.

## Entities

The system allows management of more than one set of books, each
representing a named entity.  Entity creation, selection and deletion
are handled through the menu interface which relies on entities.py.

Before creating a new entity, _testentity_ for example, you might like
to first create a testentityChartOfAccounts (a concatenation of the name
of the entity and 'ChartOfAccounts') and edit it to suit.
_debk/tests/debk.d/ManeroChartOfAccounts_ and
_debk/debk.d/defaultChartOfAccounts_ serves as examples.
New entity creation wil result in a new sub-directory **testentity.d**
and populate it with the following files:
    CofA
    Journal.json
    Metadata.json
Any user must of course have read/write privileges.
A **debk.d** directory is provided for use as a template under tests.

## Journal Entry

Journal entry can be automated using redirection or, more conveniently,
an input file, as described in the file **how2input**.  Further
automation can be done using a bash script as demonstrated in **k15.sh**.

## Back Ground

The project was inspired by the book keeping needs of a group (Kazan15)
taking a wilderness canoe trip on the Kazan River, Nunavit, Canada. The
soft ware includes 'custom' facilities specialized for this group.  The
accompanying 'explanation' file provides details.

## Disclaimers

There is still, as of this version (0.0.1,) no support for adding
accounts except to create and then use a custom chart of accounts
prior to account creation as described in the create_entity()
docstring.  Although not tested, it should be possible after entity
creation to add accounts by simply editing the entity's CofA file.
Deleting accounts will likely create havoc!

To use this software, the user must have a clear idea of the meaning of
'debit' and 'credit' in the context of double entry book keeping.
Familiarity with text editing and file manipulation and redirection is
also assumed.
