::--------------------------------------------------------------------------------------------
::                                                                                           |
::                                 == ODK SERVER MANAGER ==                                  |
::                                                                                           |
:: Use this bat to start creating a new instance! Remember you still have work to do inside  |
:: the newly created folder instance after this.                                             |
::--------------------------------------------------------------------------------------------
@echo off

:: If you move the ODKSM.bat remember to fill in ODKSM_FOLDER_PATH: it should be the absolute path to the folder that
:: contains the run.py file
:: WARNING: remember that if the content of this file change with an update in the main program folder, you will need
:: to change every file like this you moved.
SET ODKSM_FOLDER_PATH="."

:: This is the ini file that contains the [bootstrap] section and default fields for a new instance
SET DEFAULT_CONFIG="bootstrap.ini"

:: Uncomment this if you want the tool to output a log when crashing
::SET "DEBUG=true"

:: Recover the config file absolute path
CALL :NORMALIZEPATH %DEFAULT_CONFIG%
SET DEFAULT_CONFIG=%RETVAL%

:: Save the pwd for later
SET LAUNCHING_DIR=%cd%

:: Move to the tool directory
cd "%ODKSM_FOLDER_PATH%"

IF "%DEBUG%"=="true" (
    pipenv run python run.py --bootstrap "%DEFAULT_CONFIG%" --debug-logs-path "%LAUNCHING_DIR%"
) ELSE (
    pipenv run python run.py --bootstrap "%DEFAULT_CONFIG%"
)

PAUSE

:: ------------- Functions

:NORMALIZEPATH
    SET RETVAL=%~dpfn1
    EXIT /B
