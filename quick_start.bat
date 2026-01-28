@echo off
REM Quick Start Script for Telangana Portal Automation (Windows)

echo ==========================================
echo Telangana Portal Automation - Quick Start
echo ==========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo √ Python found
python --version

REM Install dependencies
echo.
echo Installing Python dependencies...
pip install -r requirements.txt

REM Install Playwright browsers
echo.
echo Installing Playwright browsers...
playwright install chromium

REM Check for .env file
if not exist .env (
    echo.
    echo Warning: .env file not found. Creating from template...
    copy .env.example .env
    echo.
    echo Please edit .env and add your GEMINI_API_KEY
    echo Get your key from: https://makersuite.google.com/app/apikey
    echo.
    pause
)

REM Create output directory
if not exist output mkdir output

REM Run test
echo.
echo Running tests...
python test_both.py

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Usage examples:
echo.
echo CCLA Portal:
echo   python ccla_search.py --district 31 --division 67 --mandal 609 --village 3111005 --buyer Kumar --seller Reddy
echo.
echo Registration Portal:
echo   python registration_search.py --doc 1234 --year 2024 --sro "HYDERABAD (R.O)"
echo.
echo For more options, see README.md
echo.
pause
