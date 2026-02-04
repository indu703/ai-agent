@echo off
setlocal
echo RESET START: %date% %time%
echo 1. Stopping any python processes on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a /T
echo 2. Running reset_db_for_ai.py...
backend\venv\Scripts\python backend\reset_db_for_ai.py
echo RESET END: %date% %time%
endlocal
pause
