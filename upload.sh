#!/bin/bash
#
# Requires the .pypirc file
# The pypi server index can be overridden on the commandline, default is "internal"
#
index=${1:-internal}
echo $index
rm -r dist/ hoops.egg-info/
python setup.py sdist upload -r $index
rm -r dist/ hoops.egg-info/
