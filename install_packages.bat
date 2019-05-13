@ECHO OFF

:: sets the env. variables from input parameters ----------------------
ECHO **
ECHO **
ECHO ** sets the env. variables from input parameters:

ECHO **
SET  SRC_HOME="%~dp0"
SET  SRC_HOME=%SRC_HOME:"=%
SET  SRC_HOME=%SRC_HOME:~0,-1%

ECHO **
SET  LIB_VERSION=0.1
SET  LIB_PATH="%SRC_HOME%"

SET  LIB_HOME=%SRC_HOME%
ECHO %LIB_HOME%

SET PYTHON_VERSION=2.7.16

:: install the 'python' ----------------------
ECHO **
ECHO **
ECHO ** install the 'python'
CMD /C " "%SRC_HOME%/install/nuget.exe" install python2 -Version "%PYTHON_VERSION%" -OutputDirectory "%SRC_HOME%" "
ECHO **
ECHO **
ECHO ** install the 'pip'
CMD /C " "%SRC_HOME%/python2.%PYTHON_VERSION%/tools/python" "%SRC_HOME%/install/get-pip.py"  --no-warn-script-location "
ECHO **
ECHO **
ECHO ** install the 'python packages'
CMD /C " "%SRC_HOME%/python2.%PYTHON_VERSION%/tools/Scripts/pip.exe" install numpy matplotlib scipy pylab --no-warn-script-location "


GOTO :EndProcess



:: wait to Enter => Good installation
:EndProcess
  SET /P DUMMY=End of installation. Hit ENTER to continue...

