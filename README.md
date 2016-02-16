# Double Entry Book Keeping

**debk.py** is a simple collection of utilities to facilitate double
entry book keeping.  It was inspired by Glen Jarvis who is is working
on a much more sophisticated version.

A major design decision (championed by Glen) is to keep all the data
files in text format (csv or json) to allow direct editing.  It is
**not** suitable for the naive user.  A clear understanding of what is
ment by debit and credit entries and how the significance differs
depending on the account type is assumed.

_prompt>_ **python3 debk.py -h**

A menu driven user interface is provided in the menu.py module.  The
next level down menu driven interface is provided by work_with.py.
There is also a config.py dependency.  These are all found under the
src directory.  A test suite is found under the tests directory.

## Persistent Storage

The system depends on the existence of a debk.d directory found under
a 'home' directory specified by config.DEFAULTS['home'] by default set
to /var/opt. It must be populated with appropriate content which at a
minimum must include: 
    defaultChartOfAccounts
    defaultMetadata.json

## Entities

The system allows management of more than one set of books, each
representing a named entity.  Entity creation, selection and deletion
are handled through the menu interface which relies on entities.py.

Before creating a new entity, _testentity_ for example, you might like
to first create a testentityChartOfAccounts (a concatenation of the name
of the entity and 'ChartOfAccounts') and edit it to suit.
'debk/tests/debk.d/ChartOfAccounts' serves as an example.
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
