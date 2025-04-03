@echo off
:: 배치 스크립트가 있는 디렉토리로 이동
cd /d %~dp0

echo Creating Python virtual environment (venv)...
python -m venv venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment. Make sure Python 3 is installed and accessible.
    pause
    exit /b %errorlevel%
)

echo Activating virtual environment...
call .\venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b %errorlevel%
)

echo Installing required libraries from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install libraries. Check requirements.txt and network connection.
    pause
    exit /b %errorlevel%
)

echo Setup completed successfully!
echo You can now run the application using run_app.bat
pause 