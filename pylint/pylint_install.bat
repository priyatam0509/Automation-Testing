@echo off
REM Set the configuration file (pylintrc) and the pre-commit hook to the correct Path


echo =================================================================
echo Installing pylint
pip install pylint
IF ERRORLEVEL 1 (
    echo "Failed installing pylint."
    GOTO FAILED
    
)

echo =================================================================
echo Installing git-pylint-commit-hook
pip install git-pylint-commit-hook
IF ERRORLEVEL 1 (
    echo "Failed installing git-pylint-commit-hook."
    GOTO FAILED
)

echo =================================================================
echo Copying: pylintrc to ..\
copy "pylintrc" "..\"
if %ERRORLEVEL% NEQ 0 GOTO FAILED

echo Creating dir: ../hooks
mkdir "../hooks"
if %ERRORLEVEL% NEQ 0 GOTO FAILED

echo Copying: pre-commit to ../hooks/
copy "pre-commit" "..\hooks\"
if %ERRORLEVEL% NEQ 0 GOTO FAILED

echo Configuring ../hooks like the Hooks path folder.
git config --local core.hooksPath ../hooks
if %ERRORLEVEL% NEQ 0 GOTO FAILED

echo Pylint was correctly installed.
GOTO END

:FAILED
echo FAILED
EXIT

:END
EXIT
