@echo off
setlocal enableextensions
title Tokey

REM --- Find a Python launcher: prefer the py launcher, fall back to python ---
set "PYCMD="
where py     >nul 2>nul && set "PYCMD=py"
if defined PYCMD goto py_ok
where python >nul 2>nul && set "PYCMD=python"
:py_ok
if not defined PYCMD goto no_python

REM Run via -m so this never depends on PATH. Any arguments are passed through,
REM e.g.  run-tokey.bat cc   (account usage)   or   run-tokey.bat --no-mood
%PYCMD% -m cc_token_tracker.roster %*
if errorlevel 1 goto failed

echo.
echo Tokey closed. You can close this window.
pause
exit /b 0

:failed
echo.
echo [ X ]  Tokey did not start. The most likely cause is that it is not
echo        installed for this Python yet.
echo.
echo        Double-click  setup.bat  in the tokey folder, then try again.
echo        Any error message above this line has the details.
echo.
pause
exit /b 1

:no_python
echo Python was not found. Please run setup.bat first.
echo.
pause
exit /b 1
