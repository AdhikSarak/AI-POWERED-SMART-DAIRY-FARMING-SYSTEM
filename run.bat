@echo off
echo =============================================
echo   Smart Dairy Farming System - Startup
echo =============================================

echo.
echo [1/2] Starting FastAPI Backend on port 8000...
start "FastAPI Backend" cmd /k "cd /d %~dp0 && uvicorn backend.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Streamlit Frontend on port 8501...
start "Streamlit Frontend" cmd /k "cd /d %~dp0 && streamlit run frontend/app.py --server.port 8501"

echo.
echo =============================================
echo  Backend  -> http://localhost:8000
echo  API Docs -> http://localhost:8000/docs
echo  Frontend -> http://localhost:8501
echo =============================================
pause
