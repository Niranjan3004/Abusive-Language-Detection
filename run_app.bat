@echo off
REM Abusive Language Detection - Start Server
REM This script activates the virtual environment and runs the Flask app

echo.
echo ============================================
echo Abusive Language Detection System
echo ============================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if model exists
if not exist "output\best_model.pth" (
    echo Warning: Trained model not found!
    echo Please train the model first: python src/train.py
    echo.
)

REM Start the Flask app
echo Starting Flask application...
echo.
python app.py

pause
