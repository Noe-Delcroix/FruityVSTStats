@echo off

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed.
    echo Please install Python version 3.10.11 before continuing.
    pause
) else (
    echo Python is installed.
    echo Installing required pip packages from requirements.txt...
    call python -m pip install -r requirements.txt
    echo Packages installed.
    cls
    call python ./main.py
)

REM End of script
pause
