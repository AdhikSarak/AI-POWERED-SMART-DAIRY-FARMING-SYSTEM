"""
Data augmentation pipeline for cattle disease image classification.

Dataset folder structure (REQUIRED):
    data/disease_images/
        healthy/          (≥200 images each)
        bovine_disease/
        foot_and_mouth/
        lumpy_skin/

Run from project root:
    python ml_models/disease_detection/data_augmentation.py
"""
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import os

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Your dataset already has a train/ subfolder — point to it directly
DATA_DIR  = os.path.join(BASE_DIR, "data", "disease_images", "train")

VALIDATION_SPLIT = 0.20   # 80% train / 20% val


def get_augmentation_generator() -> ImageDataGenerator:
    """Heavy augmentation applied only to training images.

    IMPORTANT: NO rescale here. EfficientNetV2B0 has its own preprocessing
    built inside the model and expects raw pixels in [0, 255].
    If we also rescale to [0,1], EfficientNet squashes all values to ~-1.0
    (constant signal) and the model cannot learn anything.
    """
    return ImageDataGenerator(
        # rescale intentionally omitted — EfficientNetV2 preprocesses internally
        rotation_range=30,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.3,
        horizontal_flip=True,
        vertical_flip=False,      # cows are never upside-down
        brightness_range=[0.7, 1.3],
        fill_mode="nearest",
        validation_split=VALIDATION_SPLIT,
    )


def get_val_generator() -> ImageDataGenerator:
    """No augmentation on validation. No rescale either (EfficientNetV2 handles it)."""
    return ImageDataGenerator(
        # rescale intentionally omitted — EfficientNetV2 preprocesses internally
        validation_split=VALIDATION_SPLIT,
    )


def get_data_generators(img_size=(224, 224), batch_size=32):
    """
    Returns (train_ds, val_ds).

    Both generators use the SAME validation_split value so Keras correctly
    partitions images: 80% → train, 20% → val (no overlap / no leakage).
    Both also use the same seed so the partition is reproducible.
    """
    if not os.path.isdir(DATA_DIR):
        raise FileNotFoundError(
            f"Image directory not found: {DATA_DIR}\n"
            "Create it with sub-folders: healthy/, bovine_disease/, "
            "foot_and_mouth/, lumpy_skin/"
        )

    aug_gen = get_augmentation_generator()
    val_gen = get_val_generator()

    train_ds = aug_gen.flow_from_directory(
        DATA_DIR,
        target_size=img_size,
        batch_size=batch_size,
        class_mode="categorical",
        subset="training",
        shuffle=True,
        seed=42,
    )
    val_ds = val_gen.flow_from_directory(
        DATA_DIR,
        target_size=img_size,
        batch_size=batch_size,
        class_mode="categorical",
        subset="validation",
        shuffle=False,
        seed=42,        # FIXED: same seed ensures identical partition
    )

    print(f"Classes        : {train_ds.class_indices}")
    print(f"Train samples  : {train_ds.samples}")
    print(f"Val   samples  : {val_ds.samples}")
    print(f"Split          : {100*(1-VALIDATION_SPLIT):.0f}% train / {100*VALIDATION_SPLIT:.0f}% val")

    return train_ds, val_ds


if __name__ == "__main__":
    train_ds, val_ds = get_data_generators()
