::--------------------------------------------------------------------------------------------
::                                                                                           |
::                                 == ODK SERVER MANAGER ==                                  |
::                                                                                           |
::      Use this bat to launch the tool. Remember to pass in a config.ini file to it!        |
::--------------------------------------------------------------------------------------------
@echo off
IF %1.==. GOTO No1

:: If you move the ODKSM.bat remember to fill in ODKSM_ROOT_PATH: it should be the absolute path to the folder that
:: contains the run.py file
:: WARNING: remember that if the content of this file change with an update in the main program folder, you will need
:: to change every file like this you moved.
SET ODKSM_ROOT_PATH="."

:: Uncomment this if you want the tool to output a log when crashing
::SET "DEBUG=true"

:: Recover the config file absolute path
SET CONFIG=%~dpfn1

:: Save the pwd for later
SET LAUNCHING_DIR=%cd%

:: Move to the tool directory
cd "%ODKSM_ROOT_PATH%"

IF "%DEBUG%"=="true" (
    pipenv run python run.py --manage "%CONFIG%" --debug-logs-path "%LAUNCHING_DIR%"
) ELSE (
    pipenv run python run.py --manage "%CONFIG%"
)

GOTO End1

:No1
  ECHO.
  ECHO ======[ WELCOME TO ODKSM! ]======
  ECHO.
  ECHO [ERR] You tried to call this program directly :(
  ECHO You need to pass in a config file as first argument, either by cmd, batch file or drag^&drop.
  ECHO.
  ECHO Bye!
  ECHO.

:End1
PAUSE