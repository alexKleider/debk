#########################
Double Entry Book Keeping
#########################
``debk.py`` is a simple collection of utilities to facilitate double
entry book keeping.  It was inspired by Glen Jarvis who is working
on a (I suspect much more sophisticated) version of his own.

A major design decision (championed by Glen) is to keep all the data
files in text format (csv or json) to allow direct editing.
Large business entities (with so much data that it could not all be
held in memory at once) could not be accommodated.
Also note that it is **not** suitable for the naive user: assumed
is an understanding of what is meant by debit and credit and how
the significance differs depending on the account type.  Expressed
different way: this is only suitable for use by those who understand
the fundamentals of double entry book keeping.

Yet to be implemented is a method of 'closing the books,' that is to
say there is no accounting cycle concept as of yet.

************
Installation
************

The following is a suggested way of getting up and running.

Choose:
    #. An existing directory to serve as a parent for the project directory.
    #. A directory for the data files.
By default the latter will appear within the project directory.

Let's assume you've choosen your home directory (e.g. ``/home/user``)
to be the parent of your project directory.  Make it your working
directory, clone the repository thus creating the project directory
structure, and then make it your working directory::

    cd /home/user 
    git clone https://github.com/alexKleider/debk.git
    cd debk

The ``debk`` project directory tree will contain all needed
files and subdirectories including a ``debk.d`` directory for
persistent storage.

All of what follows assumes that you have the project directory
as your current working directory.  Although not likely to be
necessary, if experiencing difficulties:
Check that all the ``.py`` files have the execution bits set::

    chmod 755 */*.py

The directory in which the data files are kept is specified in the
``debk/src/config.py`` file. If you wish to change the default value
(``~/debk/debk.d``) you'll have to edit ``~/debk/src/config.py``
and change the value of ``DEFAULTS['home']``.  Be sure to set
ownership and permissions appropriately.  (This will not be necessary
if you stick to the defaults.)

Still from within your project directory, prepare your environment,
activate it and bring in dependencies as follows::

    virtualenv -p python3 venv
    source venv/bin/activate
    pip install -r requirements.txt

Not now, but when it's time to exit the environment, you can do so
with the following command::

    deactivate   #... but don't do it now!

Another requirement is to add your project directory to the
``PYTHONPATH`` environment variable.  Provided is ``path.sh``,
a shell script, which can be sourced to accomplish this::

    source ./path.sh


*****
Usage
*****

Use of the program requires familiarity with the 
``DefaultChartOfAccounts`` file which can be edited to suit
your purposes.  Rather than editing it, you might want instead
to create copies for specific entities and customize each as
described further down.

To begin using the program::

    ./src/menu.py

*****************
Explanatory Notes
*****************

Most of the functionality is found in ``src/debk.py`` although entity
creation is handled by ``src/entities.py``.  A menu driven user
interface is provided by the ``src/menu.py`` module.  The next level
down menu driven interface is provided by ``src/workwith.py``. 
``src/money.py`` provides regex support for reading money values. 
There is also a ``src/config.py`` dependency.  A test suite is found
under the ``tests`` directory.

``debk.d/defaultChartOfAccounts`` provides a suggested chart of
accounts (aka ledger) which can be edited to suit your own needs.
Indentation is for readability only.  Comments are not permitted.
A copy must exist in the ``debk.d`` directory discussed in the next
paragraph.  A leading white space stripped version of this file is
treated as a CSV file so apart from the leading white space, it must
conform to the format of a CSV file.  

******************
Persistent Storage
******************

The system depends on the existence of a ``debk.d`` directory to
provide a 'home' for the project's data.   It is  specified within
``src/config.py`` as the value of ``config.DEFAULTS['home']``.  By
default this is set to ``~/debk/debk.d``.  This directory must (at a
bare minimum) contain a ``defaultChartOfAccounts`` file.

********
Entities
********

The system allows management of more than one set of books, each
representing a named entity.  Entity creation, selection and deletion
are handled through the menu interface which relies on
``src/entities.py``.

Entity names must consist only of letters, no dashes or underscores.
Before creating a new entity, ``testentity`` for example, you might
like to first create a custom chart of accounts.  Be sure its format
matches the ``defaultChartOfAccounts`` file and then place it in the
'home' directory naming it ``testentityChartOfAccounts`` (a
concatenation of the name of the entity and ``ChartOfAccounts``.)
``debk/tests/debk.d/ManeroChartOfAccounts`` and
``debk/debk.d/defaultChartOfAccounts`` serve as examples.
New entity creation wil result in a new sub-directory ``testentity.d``
populated with the following files:
    * ``CofA``
    * ``Journal.json``
    * ``Metadata.json``
If you experience difficulties, verify that read/write privileges
are appropriate.


*************
Journal Entry
*************

Journal entry can be done individually by the user responding to
prompts, or, more conveniently, by means of a previously created
input file, as described in the file ``how2input``. It is suggested
that you create a ``Pvt`` directory and keep journal input files there
with file names such as ``MyEntity16`` (containing 2016 entries for
MyEntity.)


***********
Back Ground
***********

The project was inspired by the book keeping needs of a group
(Kazan15) taking a wilderness canoe trip on the Kazan River in
Nunavit, Canada. The software includes several 'custom' features
specialized for this group.  These custom features probably do not
work in the current version since their support has been neglected as
the project has evolved.  Support may reappear in a later version.


***********
Disclaimers
***********

There is still, as of ``src/config.VERSION`` no support for adding
accounts except by editing the entity's CofA file.  Deleting accounts
will likely create havoc!

To use this software, the user must have a clear idea of the meaning
of 'debit' and 'credit' in the context of double entry book keeping.
Familiarity with the command line, text editing, file manipulation
and Python's virtualenv is also assumed.

-------
TESTING
-------

The script ``test.sh`` runs the whole test suite redirecting all
output to ``testresults`` which is then opened with ``vim``.

*******
Finally
*******

Correspondence with the author is welcome whether it be criticism,
suggestions for improvement, offer to collaborate, or anything else.

**alex at kleider dot ca**

