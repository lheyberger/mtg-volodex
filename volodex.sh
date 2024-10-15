#!/bin/bash

VIRTUAL_ENV=.venv
FILENAME=$(basename "$0")
SHORTNAME="${FILENAME%.*}"
SCRIPT="${SHORTNAME}.py"

cd "$( dirname "${BASH_SOURCE[0]}" )"

####
# Set environment variables if any
####
for file in .env*; do
    if [ -f ${file} ] ; then
        source ${file}
    fi
done

####
# Invoke script
####
${VIRTUAL_ENV}/bin/python -B $SCRIPT $@
