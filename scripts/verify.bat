:: Note: this script does not return an error code because it's meant for manual use only.
@echo off

SETLOCAL

IF %1 == local CALL :lint_func & CALL :test_func

IF %1 == lint CALL :lint_func

IF %1 == test CALL :test_func

IF %1 == format CALL :format_func

EXIT /B 0

:: define function to run linter
:lint_func
pylint.exe src --msg-template="{path}({line}): [{msg_id}{obj}] {msg}" --load-plugins=scripts.license_verify_pylint --rcfile=pylintrc -r n
echo pylint tests
pylint tests --msg-template="{path}({line}): [{msg_id}{obj}] {msg}" --load-plugins=scripts.license_verify_pylint --rcfile=pylintrc -r n
echo pylint licenses
pylint scripts/license_verify_pylint.py --msg-template="{path}({line}): [{msg_id}{obj}] {msg}" --load-plugins=scripts.license_verify_pylint --rcfile=pylintrc -r n
pylint scripts/license_verify.py --msg-template="{path}({line}): [{msg_id}{obj}] {msg}" --load-plugins=scripts.license_verify_pylint --rcfile=pylintrc -r n
echo flake8 src
flake8 --statistics --append-config=.flake8 src
echo flake8 tests
flake8 --statistics --append-config=.flake8 tests
EXIT /B 0

:: define function to launch tests
:test_func
echo testing
nose2 -v --with-coverage --coverage src
EXIT /B 0

:: format
:format_func
echo isort src
isort src --profile black
echo isort tests
isort tests --profile black
echo isort scripts
isort tests --profile black
echo isort examples
isort tests --profile black
echo black src
black src --line-length 100
echo black tests
black tests --line-length 100
echo black scripts
black tests --line-length 100
echo black examples
black tests --line-length 100
EXIT /B 0

ENDLOCAL

@echo on



