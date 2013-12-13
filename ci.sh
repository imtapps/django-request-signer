#!/bin/bash

if [ -z "$1" ]; then
    echo "usage: $0 virtual_env_name"
    exit
fi
VIRTUALENV_NAME=$1

virtualenv $VIRTUALENV_NAME
. $VIRTUALENV_NAME/bin/activate
rm -rf .tox
pip install tox flake8

tox
TOX_EXIT=$?

flake8 request_signer --max-line-length=120 --max-complexity=5 | grep -Pv '(base|__init__).py:\d+:\d+:\sF401' > flake8.txt
FLAKE8_EXIT=`cat flake8.txt | wc -l`

EXIT=`expr $TOX_EXIT + $FLAKE8_EXIT`
if [ $EXIT -gt 1 ]; then
    echo "Tox exit status:" $TOX_EXIT
    echo "FLAKE8 exit status:" $FLAKE8_EXIT
    echo "Exiting Build with status:" $EXIT
    exit $EXIT
fi
