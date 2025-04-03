@echo off
:: 배치 스크립트가 있는 디렉토리로 이동
cd /d %~dp0

:: venv 폴더 존재 확인
if not exist .\venv\Scripts\activate.bat (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call .\venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b %errorlevel%
)

echo Starting Streamlit app...
streamlit run youtube_downloader.py

echo App execution finished. Press any key to exit...
pause 