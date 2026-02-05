@echo off
TITLE AI Agent Backend Server
echo ---------------------------------------------------
echo Starting AI Agent Backend...
echo ---------------------------------------------------

:: Change directory to the script's location (backend folder)
cd /d "%~dp0"

:: Check if venv exists
if not exist "venv" (
    echo [ERROR] Virtual environment 'venv' not found!
    echo Please make sure you have set up the python environment.
    pause
    exit
)

:: Activate the virtual environment
call venv\Scripts\activate

:: detailed feedback
echo Virtual Environment Activated.
echo Database Port Configured in app/core/config.py
echo Starting Python Server...
echo.

:: Run the server
python run.py

echo.
echo Server detected shutdown.
pause
