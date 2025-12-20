@echo off
echo Starting School Info Monitor...
cd /d "%~dp0"
pip install -r requirements.txt -q
python main.py
pause
