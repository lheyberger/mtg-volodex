#!/bin/bash

VIRTUAL_ENV=.venv
REQUIREMENTS=requirements.txt

cd "$( dirname "${BASH_SOURCE[0]}" )"

####
# Create virtualenv if needed
####
if [ ! -d ${VIRTUAL_ENV} ] ; then
    python3 -m venv ${VIRTUAL_ENV}
    ${VIRTUAL_ENV}/bin/python -m pip install --upgrade pip
fi

####
# Install or update dependencies
####
if [ -f ${REQUIREMENTS} ] ; then
    ${VIRTUAL_ENV}/bin/pip install --upgrade -r ${REQUIREMENTS}
fi
