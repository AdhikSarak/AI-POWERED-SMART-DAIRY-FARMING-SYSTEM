"""
Disease Detection Service
- Loads EfficientNetV2 model ONCE at startup and caches it (never reloads).
- Returns structured prediction results to the router.
- Class names match the ACTUAL folder names used during training (alphabetical order).
"""
import os
import threading
import numpy as np
from PIL import Image

# ── Absolute paths (works regardless of working directory) ───────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "disease_detection", "saved", "efficientnetv2.h5")

# Class names MUST match folder names sorted alphabetically (Keras ordering):
#   0 = Bovine Disease Detection
#   1 = Healthy
#   2 = Lumpy Skin
#   3 = foot-and-mouth
DISEASE_CLASSES = [
    "Bovine Disease Detection",
    "Healthy",
    "Lumpy Skin",
    "foot-and-mouth",
]

IMG_SIZE = (224, 224)

# ── Thread-safe singleton model cache ─────────────────────────────────────────
_model      = None
_model_lock = threading.Lock()


def load_model():
    """
    Load the trained Keras model exactly once and cache it in memory.
    Thread-safe — safe for concurrent FastAPI requests.
    Raises RuntimeError if the model file has not been trained yet.
    """
    global _model
    if _model is not None:
        return _model

    with _model_lock:
        # Double-check inside the lock (another thread may have loaded it)
        if _model is not None:
            return _model

        if not os.path.exists(MODEL_PATH):
            raise RuntimeError(
                f"Disease model not found: {MODEL_PATH}\n"
                "Train the model first:\n"
                "  python ml_models/disease_detection/train.py"
            )

        import tensorflow as tf
        tf.get_logger().setLevel("ERROR")
        _model = tf.keras.models.load_model(MODEL_PATH)
        print(f"[disease_service] Model loaded from: {MODEL_PATH}")

    return _model


def preprocess_image(image_path: str) -> np.ndarray:
    """
    Load image from disk, resize to 224×224, normalise to [0, 1],
    and add the batch dimension → shape (1, 224, 224, 3).
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    img = Image.open(image_path).convert("RGB")
    img = img.resize(IMG_SIZE, Image.LANCZOS)
    # Do NOT divide by 255 — EfficientNetV2 has its own internal preprocessing
    # and expects raw pixel values in [0, 255]. Dividing here causes all values
    # to collapse to ~-1.0 inside the model, producing wrong predictions.
    arr = np.array(img, dtype=np.float32)
    return np.expand_dims(arr, axis=0)


def predict_disease(image_path: str) -> dict:
    """
    Run inference on a single image.

    Returns:
        {
            "disease":         str   — predicted class name,
            "confidence":      float — confidence of top prediction (0-1),
            "status":          str   — "Healthy" or "Diseased",
            "all_predictions": dict  — {class_name: confidence} for all classes,
        }

    Raises:
        RuntimeError  if model file is missing (not trained yet).
        FileNotFoundError if image_path does not exist.
    """
    model     = load_model()
    img_array = preprocess_image(image_path)

    preds = model.predict(img_array, verbose=0)[0]   # shape: (num_classes,)
    idx   = int(np.argmax(preds))
    label = DISEASE_CLASSES[idx]
    conf  = float(preds[idx])

    return {
        "disease":         label,
        "confidence":      round(conf, 4),
        "status":          "Healthy" if label == "Healthy" else "Diseased",
        "all_predictions": {
            cls: round(float(preds[i]), 4)
            for i, cls in enumerate(DISEASE_CLASSES)
        },
    }
