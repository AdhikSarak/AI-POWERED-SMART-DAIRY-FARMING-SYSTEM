"""
Dataset Preparation Script — Smart Dairy Farming System
Run this ONCE before training any model.

What this script does:
  1. Flattens Bovine Disease Detection images (removes nested train/test/valid subfolders)
  2. Removes 38 corrupted .jpg~ temp files from foot-and-mouth/
  3. Removes 4 .svg (non-image) files from Healthy/
  4. Reports final clean counts per class

Run from project root:
    python prepare_dataset.py
"""
import os
import shutil

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
TRAIN_DIR  = os.path.join(BASE_DIR, "data", "disease_images", "train")
TEST_DIR   = os.path.join(BASE_DIR, "data", "disease_images", "test")

VALID_EXTS = {".jpg", ".jpeg", ".png"}


def count_images(folder, maxdepth=1):
    """Count valid images directly inside folder (maxdepth=1 = no recursion)."""
    total = 0
    for f in os.listdir(folder):
        if os.path.splitext(f)[1].lower() in VALID_EXTS:
            if os.path.isfile(os.path.join(folder, f)):
                total += 1
    return total


def count_images_recursive(folder):
    """Count all valid images recursively."""
    total = 0
    for root, _, files in os.walk(folder):
        for f in files:
            if os.path.splitext(f)[1].lower() in VALID_EXTS:
                total += 1
    return total


# ─────────────────────────────────────────────────────────────────────────────
print("=" * 60)
print("  DATASET PREPARATION — Smart Dairy Farming System")
print("=" * 60)

# ── Step 1: Fix Bovine Disease Detection (flatten nested subfolders) ──────────
print("\n[STEP 1] Fixing 'Bovine Disease Detection' folder structure...")
bovine_root  = os.path.join(TRAIN_DIR, "Bovine Disease Detection")
nested_subs  = ["train", "test", "valid"]
moved_total  = 0
skipped      = 0

for sub in nested_subs:
    sub_path = os.path.join(bovine_root, sub)
    if not os.path.isdir(sub_path):
        continue
    images = [f for f in os.listdir(sub_path)
               if os.path.splitext(f)[1].lower() in VALID_EXTS]
    print(f"  Found {len(images)} images in Bovine/{sub}/")
    for img in images:
        src  = os.path.join(sub_path, img)
        dst  = os.path.join(bovine_root, img)
        if os.path.exists(dst):
            # avoid overwrite: add sub-prefix to filename
            name, ext = os.path.splitext(img)
            dst = os.path.join(bovine_root, f"{sub}_{name}{ext}")
        if not os.path.exists(dst):
            shutil.move(src, dst)
            moved_total += 1
        else:
            skipped += 1

# Remove now-empty nested subfolders
for sub in nested_subs:
    sub_path = os.path.join(bovine_root, sub)
    if os.path.isdir(sub_path):
        # also remove _classes.csv inside them
        for f in os.listdir(sub_path):
            fp = os.path.join(sub_path, f)
            if os.path.isfile(fp):
                os.remove(fp)
        try:
            os.rmdir(sub_path)
            print(f"  Removed empty folder: Bovine/{sub}/")
        except OSError:
            print(f"  Could not remove Bovine/{sub}/ (not empty?) — check manually")

print(f"  ✅  Moved {moved_total} images to Bovine root ({skipped} skipped - already exist)")
print(f"  Bovine images now at root: {count_images(bovine_root)}")

# ── Step 2: Remove .jpg~ temp files from foot-and-mouth ──────────────────────
print("\n[STEP 2] Removing .jpg~ temp files from 'foot-and-mouth'...")
fam_dir    = os.path.join(TRAIN_DIR, "foot-and-mouth")
tilde_files = [f for f in os.listdir(fam_dir) if f.endswith("~")]
for f in tilde_files:
    os.remove(os.path.join(fam_dir, f))
print(f"  ✅  Removed {len(tilde_files)} temp files (.jpg~)")

# ── Step 3: Remove .svg files from Healthy ───────────────────────────────────
print("\n[STEP 3] Removing .svg files from 'Healthy'...")
healthy_dir = os.path.join(TRAIN_DIR, "Healthy")
svg_files   = [f for f in os.listdir(healthy_dir) if f.endswith(".svg")]
for f in svg_files:
    os.remove(os.path.join(healthy_dir, f))
print(f"  ✅  Removed {len(svg_files)} SVG files")

# ── Final Report ──────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("  FINAL DATASET REPORT")
print("=" * 60)

classes = {
    "Bovine Disease Detection": os.path.join(TRAIN_DIR, "Bovine Disease Detection"),
    "foot-and-mouth":           os.path.join(TRAIN_DIR, "foot-and-mouth"),
    "Healthy":                  os.path.join(TRAIN_DIR, "Healthy"),
    "Lumpy Skin":               os.path.join(TRAIN_DIR, "Lumpy Skin"),
}
test_classes = {
    "Bovine Disease Detection": os.path.join(TEST_DIR, "Bovine Disease Detection"),
    "foot-and-mouth":           os.path.join(TEST_DIR, "foot-and-mouth"),
    "Healthy":                  os.path.join(TEST_DIR, "Healthy"),
    "Lumpy Skin":               os.path.join(TEST_DIR, "Lumpy Skin"),
}

print(f"\n{'Class':<30} {'Train':>8} {'Val(20%)':>10} {'Test':>8}  Status")
print("─" * 65)

total_train = 0
total_test  = 0
all_ok      = True

for cls, path in classes.items():
    train_count = count_images(path)
    val_count   = int(train_count * 0.20)
    actual_train = train_count - val_count
    test_count  = count_images(test_classes[cls]) if os.path.isdir(test_classes[cls]) else 0

    if train_count < 200:
        status = "⚠️  LOW (need ≥200)"
        all_ok = False
    elif train_count < 500:
        status = "✅  OK (good)"
    else:
        status = "✅  EXCELLENT"

    total_train += train_count
    total_test  += test_count
    print(f"  {cls:<28} {train_count:>6}   ~{val_count:>6}   {test_count:>6}  {status}")

print("─" * 65)
print(f"  {'TOTAL':<28} {total_train:>6}            {total_test:>6}")

print(f"\n📊 Milk Quality CSV:")
csv_path = os.path.join(BASE_DIR, "data", "milk_dataset.csv")
if os.path.exists(csv_path):
    with open(csv_path) as f:
        rows = sum(1 for _ in f) - 1  # subtract header
    print(f"   ✅  {rows:,} rows found — Train: {int(rows*0.8):,} | Test: {int(rows*0.2):,}")
else:
    print(f"   ❌  milk_dataset.csv NOT FOUND at {csv_path}")

print("\n" + "=" * 60)
if all_ok:
    print("  ✅  DATASET IS READY — You can now run training!")
    print("\n  Next steps:")
    print("    python ml_models/milk_quality/train.py")
    print("    python ml_models/milk_quality/evaluate.py")
    print("    python ml_models/disease_detection/train.py")
    print("    python ml_models/disease_detection/evaluate.py")
else:
    print("  ⚠️  Some classes have low image counts — training may be poor")
    print("     Add more images to flagged classes before training")
print("=" * 60)
