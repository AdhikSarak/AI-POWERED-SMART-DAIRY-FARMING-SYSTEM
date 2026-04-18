"""
Milk Quality Prediction Service
- Loads Random Forest model, StandardScaler, and LabelEncoder ONCE at startup.
- Uses the label encoder saved during training to decode predictions correctly.
- Feature order matches EXACTLY what was used in training.
"""
import os
import threading
import numpy as np
import joblib

# ── Absolute paths ────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SAVE_DIR      = os.path.join(BASE_DIR, "ml_models", "milk_quality", "saved")
MODEL_PATH    = os.path.join(SAVE_DIR, "random_forest.pkl")
SCALER_PATH   = os.path.join(SAVE_DIR, "scaler.pkl")
ENCODER_PATH  = os.path.join(SAVE_DIR, "label_encoder.pkl")

# Feature order must match training column order exactly:
# train.py FEATURE_COLS = ["pH", "Temperature", "Taste", "Odor", "Fat", "Turbidity", "Colour"]
# API sends keys:          ph,   temperature,   taste,  odor,   fat,  turbidity,   colour
# We map API key → position in the trained feature vector:
FEATURE_ORDER = ["ph", "temperature", "taste", "odor", "fat", "turbidity", "colour"]

# Display labels: CSV grades (high/medium/low) → user-facing text
GRADE_DISPLAY = {
    "high":   "Good",
    "medium": "Average",
    "low":    "Poor",
}

# ── Thread-safe singleton cache ───────────────────────────────────────────────
_model   = None
_scaler  = None
_encoder = None
_lock    = threading.Lock()


def load_model():
    """
    Load the trained RandomForest + scaler + label encoder exactly once.
    Thread-safe. Raises RuntimeError if models have not been trained yet.
    """
    global _model, _scaler, _encoder

    if _model is not None:
        return _model, _scaler, _encoder

    with _lock:
        if _model is not None:               # another thread loaded while we waited
            return _model, _scaler, _encoder

        missing = [p for p in [MODEL_PATH, SCALER_PATH, ENCODER_PATH]
                   if not os.path.exists(p)]
        if missing:
            raise RuntimeError(
                f"Milk quality model files not found:\n" +
                "\n".join(f"  {p}" for p in missing) +
                "\nTrain the model first:\n"
                "  python ml_models/milk_quality/train.py"
            )

        _model   = joblib.load(MODEL_PATH)
        _scaler  = joblib.load(SCALER_PATH)
        _encoder = joblib.load(ENCODER_PATH)
        print(f"[milk_service] Model loaded. Classes: {_encoder.classes_}")

    return _model, _scaler, _encoder


def predict_milk_quality(features: dict) -> dict:
    """
    Predict milk quality from 7 sensor readings.

    Args:
        features: dict with keys — ph, temperature, taste, odor, fat, turbidity, colour
                  keys must match FEATURE_ORDER exactly

    Returns:
        {
            "grade": str   — "Good" / "Average" / "Poor",
            "score": float — confidence of the prediction (0.0 – 1.0),
        }

    Raises:
        RuntimeError if model files are missing.
        KeyError     if a required feature key is missing from features dict.
    """
    model, scaler, encoder = load_model()

    # Build feature vector in the exact order used during training
    try:
        X = np.array(
            [[features[f] for f in FEATURE_ORDER]],
            dtype=np.float32,
        )
    except KeyError as e:
        raise KeyError(
            f"Missing feature key: {e}. "
            f"Expected keys: {FEATURE_ORDER}. Got: {list(features.keys())}"
        )

    # Normalise with the same scaler fitted on training data
    X = scaler.transform(X)

    # Predict class index and probability
    pred_idx  = model.predict(X)[0]          # integer label (0, 1, or 2)
    proba     = model.predict_proba(X)[0]    # probability array
    score     = float(np.max(proba))

    # Decode: integer → CSV grade string → user-friendly display text
    raw_label   = encoder.inverse_transform([pred_idx])[0]   # e.g. "high"
    grade       = GRADE_DISPLAY.get(raw_label, raw_label.capitalize())

    return {
        "grade": grade,
        "score": round(score, 4),
    }
