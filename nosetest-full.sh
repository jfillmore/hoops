#!/bin/bash -u

PYTHON=`which python`
NOSETESTS=`which nosetests`

usage() {
    cat <<EOI
------------------------
Test Suit launcher
------------------------
Usage:
Fulltest:               $0
File test:              $0 /path/to/test/file.py
Module Test:            $0 test.module
Module Method Test:     $0 another.test:TestCase.test_method
Module TestCase Test:   $0 a.test:TestCase
EOI
}

while getopts ":h" opt; do
    case $opt in
        h)
            usage
            exit 1
            ;;

    esac
done

clear_pyc() {
    find ./ -name \*.pyc -print0 | xargs -0 rm -f
}


clear_pyc
$NOSETESTS \
    --with-coverage \
    --with-progressive \
    --detailed-errors \
    --logging-level=ERROR \
    --cover-package=hoops \
    --cover-branches \
    --cover-erase \
    $@
clear_pyc

