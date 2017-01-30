# Sets PYTHONPATH to suit my needs.
# Can easily add another path using the 'formula' implemented below.
# The first line clears what was in PYTHONPATH previously.
# -- You may not want to do that but only add to it- hence it's
# commented out.

#unset PYTHONPATH
myPyDir=$(pwd)  # this is where you put the path you want added.
PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}$myPyDir"
#myPyDir='some/other/project'
#PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}${HOME}/$myPyDir"
#myPyDir='debk'
#PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}${HOME}/$myPyDir"
export PYTHONPATH

# The uncommented lines add '~/debk' to the PYTHONPATH environment
# variable. If you are in your home directory when you clone the
# repo, it will be cloned into '~/debk' 
# Some of the commented lines are provided to illustrate how you
# might want to add other paths so several projects could be
# included in your PYTHONPATH.
