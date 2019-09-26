# Necessary for allowing modules to import sibling modules
NANOPATH="$( dirname "$(readlink -f -- "$0")" )" #dirname $THISPATH`
echo "Prepending PYTHONPATH with $NANOPATH"
export PYTHONPATH=$NANOPATH:$PYTHONPATH
