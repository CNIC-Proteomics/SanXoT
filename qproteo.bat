@echo off

:: get current path
SET PWD=%~dp0
SET PWD=%PWD:~0,-1%

:: environment variables
SET VENV_HOME=%PWD%/venv_win
SET VENV_ACTIVE=%VENV_HOME%/Scripts/activate

:: constant parameters
SET NUM_CPUs=5

:: input arguments
REM SET PARAM_INFILE=%PWD%/utest/test1-in.xlsx
SET PARAM_INFILE=%PWD%/utest/test2-in.xlsx
SET PARAM_CFGFILE=%PWD%/utest/test2-conf.json
SET /p PARAM_INFILE="Enter the file with input data (in XLSX format): "
SET /p PARAM_CFGFILE="Enter the config file (in JSON format): "

:: execute workflow
CMD /k "%VENV_ACTIVE% && python %PWD%/qproteo.py -i %PARAM_INFILE% -c %PARAM_CFGFILE% -n %NUM_CPUs% -v"

SET /P DUMMY=Hit ENTER to continue...