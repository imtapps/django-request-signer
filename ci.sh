#!/bin/bash

virtualenv test
. test/bin/activate

find . -name "*.pyc" -delete
pip install -e /Users/taylorhobbs/Projects/apysigner
pip install -e /Users/taylorhobbs/Projects/generic-request-signer
pip install -r requirements/test.txt

python manage.py test
