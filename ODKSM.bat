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
set ODKSM_ROOT_PATH="."

:: Recover the config file absolute path
set CONFIG=%~dpfn1

cd "%ODKSM_ROOT_PATH%"
pipenv run python run.py "%CONFIG%"

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