"""
Standalone cattle disease prediction (for testing outside FastAPI)
Usage: python ml_models/disease_detection/predict.py path/to/image.jpg
"""
import numpy as np
import sys
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import tensorflow as tf
from PIL import Image

BASE_DIR        = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH      = os.path.join(BASE_DIR, "ml_models", "disease_detection", "saved", "efficientnetv2.h5")
DISEASE_CLASSES = ["Bovine Disease", "Foot and Mouth Disease", "Healthy", "Lumpy Skin Disease"]


def predict(image_path: str) -> dict:
    model = tf.keras.models.load_model(MODEL_PATH)
    img   = Image.open(image_path).convert("RGB").resize((224, 224))
    arr   = np.array(img, dtype=np.float32) / 255.0
    arr   = np.expand_dims(arr, axis=0)
    preds = model.predict(arr, verbose=0)[0]
    idx   = int(np.argmax(preds))
    return {
        "disease":    DISEASE_CLASSES[idx],
        "confidence": round(float(preds[idx]), 4),
        "status":     "Healthy" if DISEASE_CLASSES[idx] == "Healthy" else "Diseased",
        "all":        {cls: round(float(preds[i]), 4) for i, cls in enumerate(DISEASE_CLASSES)},
    }


if __name__ == "__main__":
    img_path = sys.argv[1] if len(sys.argv) > 1 else "test.jpg"
    result   = predict(img_path)
    print(f"Disease:    {result['disease']}")
    print(f"Confidence: {result['confidence']*100:.1f}%")
    print(f"Status:     {result['status']}")
    print(f"All scores: {result['all']}")
