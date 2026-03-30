@echo off
title GitLab Issue Tool
cd /d "%~dp0"
set GEMINI_CLI_PATH=C:\Users\wes1_chen\AppData\Roaming\npm\gemini.cmd
set GEMINI_TIMEOUT=300
set PYTHON="%~dp0.venv\Scripts\python.exe"
set PIP="%~dp0.venv\Scripts\pip.exe"

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Checking dependencies...
%PIP% install -r requirements.txt --quiet --disable-pip-version-check
echo Starting Flask...
echo URL: http://127.0.0.1:5000
echo Close this window to stop.
echo.
%PYTHON% app.py
pause
