::--------------------------------------------------------------------------------------------
::                                                                                           |
::                                 == ODK SERVER MANAGER ==                                  |
::                                                                                           |
::     Leave this here. Symlink it to your preferred directory and launch it from there!     |
::--------------------------------------------------------------------------------------------
@echo off
IF %1.==. GOTO No1

set CONFIG=%~dpfn1
pipenv run python run.py "%CONFIG%"

GOTO End1

:No1
  ECHO.
  ECHO You tried to call this program directly :(
  ECHO You need to pass in a config file as first argument, either by cmd, batch file or dragging.
  ECHO.
  ECHO Bye!
  ECHO.

:End1
PAUSE