@echo off

REM --- Clone repo if missing ---
if not exist capstone-project-team-10 (
    echo Cloning repository...
    git clone https://github.com/COSC-499-W2025/capstone-project-team-10.git || goto :error
)

cd capstone-project-team-10 || goto :error

REM --- Create venv if missing ---
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv || goto :error
)

REM --- Activate venv ---
call venv\Scripts\activate || goto :error

REM --- Install dependencies if not already installed ---
REM (basic check: look for a known package from requirements)
pip show nltk >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt || goto :error
) else (
    echo Dependencies already installed. Skipping...
)

REM --- Setup NLTK data (safe to rerun, but we can still check) ---
if not exist "%APPDATA%\nltk_data" (
    echo Setting up NLTK data...
    python utils\setup_nltk_data.py || goto :error
) else (
    echo NLTK data already exists. Skipping...
)

REM --- Run app ---
echo Running application...
python -m src.main

pause
exit /b

:error
echo Setup failed. Fix the error above.
pause
exit /b