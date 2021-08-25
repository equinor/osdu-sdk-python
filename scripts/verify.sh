#!/bin/bash

# Basic script used by bash and local to verify all tests

function launch_pylint()
{
    $(which pylint) $1 --msg-template='{path}({line}): [{msg_id}{obj}] {msg}' --load-plugins=scripts.license_verify_pylint
}

function launch_unit_tests()
{
    nose2 -v --with-coverage --coverage src
}

if [[ $1 == "local" ]]
    then
        launch_unit_tests && launch_pylint ./src && launch_pylint ./tests && launch_pylint ./scripts/license_verify_pylint && launch_pylint ./scripts/license_verify
elif [[ $1 == "test" ]]
    then
        launch_unit_tests
elif [[ $1 == "lint" ]]
    then
        echo "Linting src..."
        launch_pylint ./src
        r1=$?
        echo "Linting tests..."
        launch_pylint ./tests
        r2=$?
        echo "Linting Checker..."
        launch_pylint ./scripts/license_verify_pylint
        r3=$?
        launch_pylint ./scripts/license_verify
        r4=$?
        exit $((r1 + r2 + r3 + r4))
fi
