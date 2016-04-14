#!/bin/bash

python manage.py test --with-xunit --with-xcover --cover-package=request_signer
TEST_EXIT=$?

echo "Flake8 Results"
flake8 request_signer --max-complexity=5 --max-line-length=120 --exclude=base.py,"*/client/generic/__init__.py" > flake8.txt
cat ./flake8.txt
FLAKE8_EXIT=`cat ./flake8.txt | wc -l`

let JENKINS_EXIT="$TEST_EXIT + $FLAKE8_EXIT"
if [ $JENKINS_EXIT -gt 0 ]; then
    echo "Test exit status:" $TEST_EXIT
    echo "Flake8 exit status:" $FLAKE8_EXIT
    echo "Exiting Build with status:" $JENKINS_EXIT
    exit $JENKINS_EXIT
fi

