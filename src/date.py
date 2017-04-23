#!./venv/bin/python

# file: 'date.py'

"""
This module is still in development-
currently the dates are 'free form'.
This module is intended to provide the ability to
convert date entries to a form that can be used
to do date arithmetic and enforce chronological
ordering.
"""

import datetime

stamp = "%Y%m%d-%H:%M"
now = datetime.datetime.now()
time_stamp = now.strftime(stamp)
print("{:<30}{}".format("My time stamp is:",time_stamp))
d = datetime.datetime.strptime(time_stamp, stamp)
print("{:<30}{}".format("The derived date object:", d))
s = d.strftime(stamp)
print("{:<30}{}".format("Time stamp from derived:", s))
print("""a shortened version of
{} should be
{}""".format(now, d))
