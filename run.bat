@echo off
cd /d "%~dp0"
echo Starting Billing System...
echo Do not close this window while billing.
python -m pip install -r requirements.txt --quiet
python app.py
pause
