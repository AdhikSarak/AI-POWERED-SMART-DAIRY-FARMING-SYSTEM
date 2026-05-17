@echo off
echo =============================================
echo   Smart Dairy Farming System - Setup
echo =============================================

echo.
echo [1/4] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate

echo.
echo [2/4] Installing dependencies...
pip install -r requirements.txt

echo.
echo [3/4] NOTE: Update your .env file with:
echo   - DATABASE_URL (your PostgreSQL password)
echo   - GROQ_API_KEY (from console.groq.com)

echo.
echo [4/4] Setup complete!
echo.
echo NEXT STEPS:
echo  1. Open pgAdmin and create database: dairy_farm_db
echo  2. Update .env with your credentials
echo  3. Run: python ml_models/milk_quality/train.py
echo  4. Run: python ml_models/disease_detection/train.py
echo  5. Run: run.bat to start the application
echo.
pause
