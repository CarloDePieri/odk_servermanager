::--------------------------------------------------------------------------------------------
::                                                                                           |
::                                 == ODK SERVER MANAGER ==                                  |
::                                                                                           |
:: This is a generated file! DO NOT EDIT IT BY HAND. Use server instance configuration file. |
::--------------------------------------------------------------------------------------------
@echo off
color 0b
title ODK Training Server Monitor
:ServerStart
echo .
echo ..
echo ...
echo Launching Server %date% %time%
C:
cd "C:\Program Files (x86)\Steam\steamapps\common\Arma 3"
echo ODK Training Server Monitor... Active !
start "Arma3" /min /wait arma3server_x64.exe -port=2202 -config=serverTraining.cfg -cfg=Arma3Training.cfg -maxMem=8192 -filePatching -autoinit -enableHT -mod="!Mods_linked/@ace;!Mods_copied/@CBA_A3;!Mods_linked/@ODKAI;" -servermod="!Mods_linked/@AdvProp;!Mods_linked/@ODKMIN;"
ping 127.0.0.1 -n 15 >NUL
echo ODK Training Server Shutdown ... Restarting!
ping 127.0.0.1 -n 5 >NUL
cls
goto ServerStart

:StartupError
echo Configuration files error at startup!
ping 127.0.0.1 -n 15 >NUL
echo ODK Training Server down ... retry!
ping 127.0.0.1 -n 5 >NUL
goto ServerStart