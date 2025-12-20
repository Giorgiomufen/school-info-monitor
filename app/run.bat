@echo off
echo Starting School Info Monitor...
cd /d "%~dp0"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Installing dependencies...
    venv\Scripts\pip install -r requirements.txt -q
)

venv\Scripts\python main.py
pause
