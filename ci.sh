#!/bin/bash

# verify user provided a name for the virtualenv
if [ -z "$1" ]; then
    echo "usage: $0 virtual_env_name"
    exit
fi

VIRTUALENV_NAME=$1

virtualenv $VIRTUALENV_NAME
. $VIRTUALENV_NAME/bin/activate

find . -name "*.pyc" -delete

pip install tox
pip install flake8

tox

TEST_EXIT=$?
rm -rf jenkins_reports
mkdir jenkins_reports
flake8 request_signer --max-complexity=5 --max-line-length=120 --exclude=base.py,"*/client/generic/__init__.py" > jenkins_reports/flake8.txt
FLAKE8_EXIT=$?

# cleanup virtualenv
deactivate
rm -rf $VIRTUALENV_NAME

let JENKINS_EXIT="$TEST_EXIT + $FLAKE8_EXIT"
if [ $JENKINS_EXIT -gt 2 ]; then
    echo "Test exit status:" $TEST_EXIT
    echo "Flake8 exit status:" $FLAKE8_EXIT
    echo "Exiting Build with status:" $EXIT
    exit $JENKINS_EXIT
fi

