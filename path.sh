# Sets PYTHONPATH to suit my needs.
# Can easily add another path using the 'formula' implemented below.
# The first line clears what was in PYTHONPATH previously.
# If it's commented out, the lines that follow will add to what's
# already there.

unset PYTHONPATH
myPyDir='Py'
PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}${HOME}/$myPyDir"
myPyDir='some/other/project'
PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}${HOME}/$myPyDir"
myPyDir='debk'
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}${HOME}/$myPyDir"

# Only the last two lines are needed for a project that lives in
# ~/debk but the rest is provided to illustrate how you could set
# it up so several projects would be included in your PYTHONPATH.
