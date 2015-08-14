# Double Entry Book Keeping

**debk.py** is a simple collection of utilities to facilitate double entry
book keeping.  It was inspired by Glen Jarvis who is is working on a
much more sophisticated version.

A major design decision (championed by Glen) is to keep all the data
files in text format (csv or json) to allow direct editing.  It is
**not** suitable for the naive user.

_prompt>_ python3 debk.py -h

## Persistent Storage

**debk.py** depends on the existence of a /var/opt/debk.d directory
with appropriate content which at a minimum must include: 
    defaultChartOfAccounts
    defaultMetadata.json
Before creating a new entity, _TestEntity_ for example, you might like
to first create a TestEntityChartOfAccounts (a concatenation of the name
of the entity and 'ChartOfAccounts') and edit it to suit.
'Kazan15ChartOfAccounts' serves as an example.
**./debk.py new --entity=TestEntity**
will create a directory **TestEntity.d** and populate it with the
following files:
    CofA
    Journal.json
    Metadata.json
Any user of **debk.py** must of course have read/write privileges.
A **debk.d** directory is provided for use as a template.

Journal entry can be automated using redirection or, more conveniently,
an input file, as described in the file **how2input**.  Further
automation can be done using a bash script as demonstrated in **k15.sh**.

The project was inspired by the book keeping needs of a group (Kazan15)
taking a wilderness canoe trip on the Kazan River, Nunavit, Canada. The
soft ware includes facilities specialized for this group.  The
accompanying 'explanation' file provides details.
