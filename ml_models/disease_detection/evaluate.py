"""
Evaluate the trained EfficientNetV2 disease detection model.
Uses the dedicated test/ folder (never seen during training).
Reports: Accuracy, Precision, Recall, F1, Confusion Matrix per class.

Run from project root:
    python ml_models/disease_detection/evaluate.py
"""
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    classification_report, confusion_matrix,
    accuracy_score, f1_score
)
import matplotlib.pyplot as plt
import seaborn as sns

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEST_DIR   = os.path.join(BASE_DIR, "data", "disease_images", "test")   # held-out test set
SAVE_DIR   = os.path.join(BASE_DIR, "ml_models", "disease_detection", "saved")
MODEL_PATH = os.path.join(SAVE_DIR, "efficientnetv2.h5")


def evaluate():
    # ── Load model ───────────────────────────────────────────────────────────
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Trained model not found: {MODEL_PATH}\n"
            "Run train.py first."
        )
    model = tf.keras.models.load_model(MODEL_PATH)
    print(f"Model loaded   : {MODEL_PATH}")
    print(f"Test data from : {TEST_DIR}")

    # ── Test generator (NO augmentation, NO shuffle — order must be preserved)
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    test_gen = ImageDataGenerator(rescale=1.0 / 255)
    test_ds  = test_gen.flow_from_directory(
        TEST_DIR,
        target_size=(224, 224),
        batch_size=32,
        class_mode="categorical",
        shuffle=False,     # CRITICAL: must be False for y_true/y_pred alignment
    )

    if test_ds.samples == 0:
        raise ValueError(
            f"No images found in test directory: {TEST_DIR}\n"
            "Run prepare_dataset.py first, then check folder structure."
        )

    # Class names detected from test/ folder (sorted alphabetically by Keras)
    actual_classes = list(test_ds.class_indices.keys())
    print(f"Classes found  : {test_ds.class_indices}")
    print(f"Test samples   : {test_ds.samples}\n")

    # ── Predict ──────────────────────────────────────────────────────────────
    print("Running predictions...")
    preds  = model.predict(test_ds, verbose=1)
    y_pred = np.argmax(preds, axis=1)
    y_true = test_ds.classes

    # ── Core Metrics ─────────────────────────────────────────────────────────
    acc = accuracy_score(y_true, y_pred)
    f1  = f1_score(y_true, y_pred, average="macro")

    print(f"\n{'='*55}")
    print(f"  TEST ACCURACY   : {acc * 100:.2f}%")
    print(f"  MACRO F1 SCORE  : {f1  * 100:.2f}%")
    print(f"{'='*55}")

    # ── Detailed Per-Class Report ─────────────────────────────────────────────
    print("\nPer-Class Classification Report:")
    print(classification_report(y_true, y_pred, target_names=actual_classes))

    # ── Per-Class Accuracy Bar ────────────────────────────────────────────────
    print("Per-Class Accuracy:")
    for i, cls in enumerate(actual_classes):
        mask      = y_true == i
        if mask.sum() == 0:
            print(f"  {cls:<30} No test samples found!")
            continue
        cls_acc   = accuracy_score(y_true[mask], y_pred[mask])
        cls_count = int(mask.sum())
        bar       = "█" * int(cls_acc * 35)
        print(f"  {cls:<30} {bar} {cls_acc*100:.1f}%  ({cls_count} samples)")

    # ── Confusion Matrix ─────────────────────────────────────────────────────
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm, annot=True, fmt="d",
        xticklabels=actual_classes, yticklabels=actual_classes,
        cmap="Greens"
    )
    plt.title(
        f"Disease Detection — Test Set Confusion Matrix\n"
        f"Accuracy: {acc*100:.1f}%  |  Macro F1: {f1*100:.1f}%"
    )
    plt.ylabel("Actual Label")
    plt.xlabel("Predicted Label")
    plt.xticks(rotation=20, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    save_path = os.path.join(SAVE_DIR, "eval_confusion_matrix.png")
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"\nConfusion matrix saved : {save_path}")


if __name__ == "__main__":
    evaluate()
