@echo off
REM ============================================================
REM  Smart Dairy Farming System — Train All ML Models
REM  Run this from the project root: ML_Projevct\
REM  Once trained, models are saved to disk and never need
REM  to be retrained unless you update the dataset.
REM ============================================================

echo.
echo ============================================================
echo   SMART DAIRY FARMING — MODEL TRAINING PIPELINE
echo ============================================================
echo.

REM ── Verify we are in the right folder ────────────────────────
if not exist "data\milk_dataset.csv" (
    echo ERROR: Run this script from the ML_Projevct\ folder.
    echo        Cannot find data\milk_dataset.csv
    pause
    exit /b 1
)

REM ── STEP 1: Prepare / clean dataset ──────────────────────────
echo [1/4] Preparing and verifying dataset...
python prepare_dataset.py
if %ERRORLEVEL% neq 0 (
    echo ERROR: Dataset preparation failed.
    pause
    exit /b 1
)
echo.

REM ── STEP 2: Train Milk Quality model (fast, ~1 minute) ───────
echo [2/4] Training Milk Quality model (Random Forest)...
echo       Expected accuracy: 95%%+
echo.
python ml_models/milk_quality/train.py
if %ERRORLEVEL% neq 0 (
    echo ERROR: Milk quality training failed.
    pause
    exit /b 1
)
echo.

REM ── STEP 3: Evaluate all milk quality models ─────────────────
echo [3/4] Evaluating and comparing all milk quality models...
python ml_models/milk_quality/evaluate.py
if %ERRORLEVEL% neq 0 (
    echo ERROR: Milk quality evaluation failed.
    pause
    exit /b 1
)
echo.

REM ── STEP 4: Train Disease Detection model (slow, 30-90 min) ──
echo [4/4] Training Disease Detection model (EfficientNetV2)...
echo       Expected accuracy: 85%%+  (GPU will be much faster)
echo       This takes 30-90 minutes on CPU, 10-20 min on GPU.
echo.
python ml_models/disease_detection/train.py
if %ERRORLEVEL% neq 0 (
    echo ERROR: Disease detection training failed.
    pause
    exit /b 1
)
echo.

REM ── DONE ─────────────────────────────────────────────────────
echo ============================================================
echo   ALL MODELS TRAINED AND SAVED SUCCESSFULLY
echo.
echo   Saved files:
echo     ml_models\milk_quality\saved\random_forest.pkl
echo     ml_models\milk_quality\saved\scaler.pkl
echo     ml_models\milk_quality\saved\label_encoder.pkl
echo     ml_models\disease_detection\saved\efficientnetv2.h5
echo.
echo   The FastAPI server will load these automatically.
echo   You do NOT need to retrain unless you change the dataset.
echo ============================================================
echo.
pause
