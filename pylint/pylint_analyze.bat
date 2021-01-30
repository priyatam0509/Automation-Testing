@echo off
REM Do a Pylint analysis

if "%1"=="" goto usage
if "%2"=="" goto usage

REM Set the PULL REQUEST Number to be analyzed
set PR_NO=%1
REM Set the LOCAL BRANCH
set LOCAL_BRANCH=%2
goto process

:usage
echo =========================================================
echo USEAGE: 
echo    pylint_analyze [pr_no] [local_branch]
echo         pr_no - set the PULL REQUEST NUMBER to be analyzed
echo         local_branch - set the local branch name to be checkouted
echo EXAMPLE: pylint_analyze 634 Temp01
echo =========================================================
exit

:process
echo =================================================================
echo Doing ... git fetch origin refs/pull-requests/%PR_NO%/from:%LOCAL_BRANCH% ...

git fetch origin refs/pull-requests/%PR_NO%/from:%LOCAL_BRANCH%

IF ERRORLEVEL 1 (
    echo Failed doing git fetch.
    exit
)

echo =================================================================
echo Doing ... git checkout %LOCAL_BRANCH% ...
git checkout %LOCAL_BRANCH%
IF ERRORLEVEL 1 (
    echo Failed doing git checkout.
    exit
) 

echo =================================================================
echo Analyzing differences (only .py files) ...
for /f %%f in ('git diff origin/development... --name-only') do (
    REM Analyzing only .py files extension
    if "%%~xf"==".py" ( 
        echo =================================================================
        echo Doing ... pylint %%f  ...
        pylint %%f
    )
)

echo Anlysis finished

