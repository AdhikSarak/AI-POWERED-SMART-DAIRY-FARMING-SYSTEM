"""
Seed script — populates the database with realistic dairy farm data.
Run: python seed_data.py
"""
import requests, json, io, time
from PIL import Image
import numpy as np

BASE = "http://127.0.0.1:8000"

# ── Colours ──────────────────────────────────────────────────────
G  = "\033[92m"   # green
R  = "\033[91m"   # red
Y  = "\033[93m"   # yellow
B  = "\033[94m"   # blue
W  = "\033[0m"    # reset
OK = f"{G}[OK]{W}"
FL = f"{R}[FAIL]{W}"

def p(label, resp, ok_code=200):
    ok = resp.status_code == ok_code
    print(f"  {'  [OK]' if ok else '[FAIL]'} {label} (HTTP {resp.status_code})")
    if not ok:
        try: print(f"         {resp.json()}")
        except: print(f"         {resp.text[:120]}")
    return ok, resp

# ── Step 1: Register / login farmer ──────────────────────────────
print(f"\n{B}=== STEP 1: ACCOUNTS ==={W}")

# Register main farmer
r = requests.post(f"{BASE}/auth/register", json={
    "name": "Somnath Kumar", "email": "somnathtk198@gmail.com",
    "phone": "9876543210", "password": "Soma@123", "role": "farmer"
})
if r.status_code in (201, 400):
    print(f"  [OK] Farmer account (HTTP {r.status_code})")

# Register admin
r2 = requests.post(f"{BASE}/auth/register", json={
    "name": "Farm Admin", "email": "admin@dairyfarm.com",
    "phone": "9000000001", "password": "Admin@123", "role": "admin"
})
if r2.status_code in (201, 400):
    print(f"  [OK] Admin account (HTTP {r2.status_code})")

# Login farmer
r = requests.post(f"{BASE}/auth/login", json={
    "email": "somnathtk198@gmail.com", "password": "Soma@123"
})
ok, r = p("Login farmer", r, 200)
if not ok: exit()
token   = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
farmer_id = r.json()["user"]["id"]

# Login admin
r3 = requests.post(f"{BASE}/auth/login", json={
    "email": "admin@dairyfarm.com", "password": "Admin@123"
})
ok3, r3 = p("Login admin", r3, 200)
admin_headers = {"Authorization": f"Bearer {r3.json()['access_token']}"} if ok3 else {}

# ── Step 2: Add Cows ─────────────────────────────────────────────
print(f"\n{B}=== STEP 2: COWS ==={W}")

cows_data = [
    {"name": "Ganga",    "breed": "Holstein Friesian", "age": 4.0,  "weight_kg": 480.0, "cow_uid": "COW-GANGA-01"},
    {"name": "Lakshmi",  "breed": "Gir",               "age": 3.5,  "weight_kg": 360.0, "cow_uid": "COW-LAXMI-02"},
    {"name": "Shyama",   "breed": "Sahiwal",            "age": 5.0,  "weight_kg": 410.0, "cow_uid": "COW-SHYAM-03"},
    {"name": "Kamdhenu", "breed": "Jersey",             "age": 2.5,  "weight_kg": 320.0, "cow_uid": "COW-KAMDH-04"},
    {"name": "Nandini",  "breed": "Red Sindhi",         "age": 6.0,  "weight_kg": 395.0, "cow_uid": "COW-NANDI-05"},
]

cow_ids = []
for cd in cows_data:
    r = requests.post(f"{BASE}/cows/", json=cd, headers=headers)
    if r.status_code == 201:
        cow_ids.append(r.json()["id"])
        print(f"  [OK] Added cow: {cd['name']} (ID: {r.json()['id']}, UID: {r.json()['cow_uid']})")
    elif r.status_code == 400:
        # Already exists — fetch it
        all_cows = requests.get(f"{BASE}/cows/", headers=headers).json()
        match = next((c for c in all_cows if c["name"] == cd["name"]), None)
        if match:
            cow_ids.append(match["id"])
            print(f"  [OK] Cow exists: {cd['name']} (ID: {match['id']})")

print(f"  Total cows available: {len(cow_ids)}")

# ── Step 3: Milk Quality Tests ───────────────────────────────────
print(f"\n{B}=== STEP 3: MILK QUALITY TESTS ==={W}")

# Realistic milk samples per cow — varying quality
milk_samples = {
    "Ganga": [
        {"ph":6.8,"temperature":37.0,"taste":1,"odor":1,"fat":3.8,"turbidity":0,"colour":254},  # Good
        {"ph":6.7,"temperature":36.5,"taste":1,"odor":1,"fat":4.0,"turbidity":0,"colour":253},  # Good
        {"ph":6.5,"temperature":38.0,"taste":1,"odor":1,"fat":3.2,"turbidity":1,"colour":248},  # Avg
    ],
    "Lakshmi": [
        {"ph":6.9,"temperature":37.5,"taste":1,"odor":1,"fat":4.2,"turbidity":0,"colour":255},  # Good
        {"ph":6.6,"temperature":39.0,"taste":1,"odor":1,"fat":3.0,"turbidity":0,"colour":250},  # Good
        {"ph":5.8,"temperature":55.0,"taste":0,"odor":0,"fat":1.5,"turbidity":1,"colour":210},  # Poor
    ],
    "Shyama": [
        {"ph":6.8,"temperature":37.0,"taste":1,"odor":1,"fat":3.5,"turbidity":0,"colour":252},  # Good
        {"ph":6.4,"temperature":42.0,"taste":1,"odor":1,"fat":2.5,"turbidity":1,"colour":240},  # Avg
        {"ph":6.2,"temperature":45.0,"taste":1,"odor":0,"fat":2.0,"turbidity":1,"colour":235},  # Avg
    ],
    "Kamdhenu": [
        {"ph":6.9,"temperature":36.0,"taste":1,"odor":1,"fat":4.5,"turbidity":0,"colour":254},  # Good
        {"ph":6.8,"temperature":37.0,"taste":1,"odor":1,"fat":4.1,"turbidity":0,"colour":253},  # Good
    ],
    "Nandini": [
        {"ph":6.7,"temperature":38.0,"taste":1,"odor":1,"fat":3.6,"turbidity":0,"colour":251},  # Good
        {"ph":4.8,"temperature":75.0,"taste":0,"odor":0,"fat":0.8,"turbidity":1,"colour":150},  # Poor
        {"ph":6.6,"temperature":38.5,"taste":1,"odor":1,"fat":3.4,"turbidity":0,"colour":252},  # Good
    ],
}

cow_name_map = {cd["name"]: i for i, cd in enumerate(cows_data) if i < len(cow_ids)}
for cow_name, samples in milk_samples.items():
    idx = list(cow_name_map.keys()).index(cow_name) if cow_name in cow_name_map else None
    if idx is None or idx >= len(cow_ids): continue
    cid = cow_ids[idx]
    for s in samples:
        s["cow_id"] = cid
        r = requests.post(f"{BASE}/milk/analyze", json=s, headers=headers)
        if r.status_code == 200:
            grade = r.json()["quality_grade"]
            score = r.json()["quality_score"]
            print(f"  [OK] {cow_name}: {grade} ({score*100:.0f}% confidence)")
        else:
            print(f"  [FAIL] {cow_name} milk: {r.text[:80]}")
        time.sleep(0.3)

# ── Step 4: Disease Detection ────────────────────────────────────
print(f"\n{B}=== STEP 4: DISEASE DETECTION ==={W}")

def make_cow_image(healthy=True):
    """Create a synthetic cow-like image."""
    arr = np.ones((224, 224, 3), dtype=np.uint8)
    if healthy:
        arr[:, :, 0] = np.random.randint(140, 180, (224, 224))
        arr[:, :, 1] = np.random.randint(110, 150, (224, 224))
        arr[:, :, 2] = np.random.randint(80, 120, (224, 224))
    else:
        arr[:, :, 0] = np.random.randint(100, 140, (224, 224))
        arr[:, :, 1] = np.random.randint(60, 90, (224, 224))
        arr[:, :, 2] = np.random.randint(50, 80, (224, 224))
        # Add irregular patches to simulate lesions
        for _ in range(8):
            x, y = np.random.randint(20, 200), np.random.randint(20, 200)
            arr[x:x+15, y:y+15, 0] = 60
            arr[x:x+15, y:y+15, 1] = 40
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf

health_checks = [
    ("Ganga",    True,  "ganga_check1.jpg"),
    ("Lakshmi",  True,  "lakshmi_check1.jpg"),
    ("Shyama",   False, "shyama_check1.jpg"),
    ("Kamdhenu", True,  "kamdhenu_check1.jpg"),
    ("Nandini",  False, "nandini_check1.jpg"),
    ("Ganga",    True,  "ganga_check2.jpg"),
    ("Shyama",   True,  "shyama_check2.jpg"),
]

for cow_name, healthy, fname in health_checks:
    idx = list(cow_name_map.keys()).index(cow_name) if cow_name in cow_name_map else None
    if idx is None or idx >= len(cow_ids): continue
    cid = cow_ids[idx]
    buf = make_cow_image(healthy)
    r = requests.post(f"{BASE}/health/analyze",
        data={"cow_id": cid},
        files={"file": (fname, buf, "image/jpeg")},
        headers=headers)
    if r.status_code == 200:
        d = r.json()
        print(f"  [OK] {cow_name}: {d['health_status']} — {d['disease_name']} ({d['confidence_score']*100:.0f}%)")
    else:
        print(f"  [FAIL] {cow_name} health: {r.text[:80]}")
    time.sleep(0.5)

# ── Step 5: AI Recommendations ───────────────────────────────────
print(f"\n{B}=== STEP 5: AI RECOMMENDATIONS ==={W}")

for i, (cow_name, _) in enumerate(zip(cow_name_map.keys(), cow_ids)):
    if i >= len(cow_ids): break
    cid = cow_ids[i]
    r = requests.post(f"{BASE}/recommendations/generate/{cid}", headers=headers)
    if r.status_code == 200:
        types = [x["rec_type"] for x in r.json()]
        print(f"  [OK] {cow_name}: {len(r.json())} recs — {types}")
    else:
        print(f"  [FAIL] {cow_name}: {r.text[:80]}")
    time.sleep(1)

# ── Step 6: Milk Collections (Admin) ─────────────────────────────
print(f"\n{B}=== STEP 6: MILK COLLECTIONS (ADMIN) ==={W}")

collections = [
    {"farmer_id": farmer_id, "quantity_liters": 42.5, "quality_grade": "Good",    "rate_per_liter": 52.0, "collection_date": "2026-04-01"},
    {"farmer_id": farmer_id, "quantity_liters": 38.0, "quality_grade": "Good",    "rate_per_liter": 52.0, "collection_date": "2026-04-03"},
    {"farmer_id": farmer_id, "quantity_liters": 45.0, "quality_grade": "Good",    "rate_per_liter": 52.0, "collection_date": "2026-04-05"},
    {"farmer_id": farmer_id, "quantity_liters": 30.5, "quality_grade": "Average", "rate_per_liter": 42.0, "collection_date": "2026-04-07"},
    {"farmer_id": farmer_id, "quantity_liters": 40.0, "quality_grade": "Good",    "rate_per_liter": 52.0, "collection_date": "2026-04-09"},
    {"farmer_id": farmer_id, "quantity_liters": 35.0, "quality_grade": "Good",    "rate_per_liter": 52.0, "collection_date": "2026-04-11"},
    {"farmer_id": farmer_id, "quantity_liters": 20.0, "quality_grade": "Poor",    "rate_per_liter": 30.0, "collection_date": "2026-04-13"},
    {"farmer_id": farmer_id, "quantity_liters": 44.0, "quality_grade": "Good",    "rate_per_liter": 52.0, "collection_date": "2026-04-15"},
    {"farmer_id": farmer_id, "quantity_liters": 41.5, "quality_grade": "Good",    "rate_per_liter": 52.0, "collection_date": "2026-04-17"},
    {"farmer_id": farmer_id, "quantity_liters": 38.5, "quality_grade": "Average", "rate_per_liter": 42.0, "collection_date": "2026-04-18"},
]

total_l = 0
total_a = 0
for col in collections:
    r = requests.post(f"{BASE}/billing/collection", json=col, headers=admin_headers)
    if r.status_code == 201:
        d = r.json()
        total_l += d["quantity_liters"]
        total_a += d["quantity_liters"] * d["rate_per_liter"]
        print(f"  [OK] {d['collection_date']}: {d['quantity_liters']}L {d['quality_grade']} @ Rs.{d['rate_per_liter']}/L")
    else:
        print(f"  [FAIL] Collection: {r.text[:80]}")
    time.sleep(0.2)

print(f"  Total: {total_l:.1f}L = Rs.{total_a:.0f}")

# ── Step 7: Generate Bill ─────────────────────────────────────────
print(f"\n{B}=== STEP 7: GENERATE BILL ==={W}")
r = requests.post(f"{BASE}/billing/generate-bill",
    json={"farmer_id": farmer_id, "month": "2026-04"},
    headers=admin_headers)
ok, r = p("Generate April 2026 bill", r, 200)
if ok:
    b = r.json()
    print(f"  Total Liters: {b['total_liters']}L | Total Amount: Rs.{b['total_amount']}")

# ── Final Summary ─────────────────────────────────────────────────
print(f"\n{B}=== FINAL SUMMARY ==={W}")
dash = requests.get(f"{BASE}/reports/dashboard", headers=headers)
if dash.status_code == 200:
    d = dash.json()
    print(f"  Cows          : {d['total_cows']}")
    print(f"  Health Checks : {d['total_health_checks']}")
    print(f"  Milk Tests    : {d['total_milk_tests']}")
    print(f"  Good Milk     : {d['good_milk_count']}")
    print(f"  Average Milk  : {d['average_milk_count']}")
    print(f"  Poor Milk     : {d['poor_milk_count']}")
    print(f"  Diseased      : {d['diseased_count']}")

print(f"\n  Login with:")
print(f"  Email    : somnathtk198@gmail.com")
print(f"  Password : Soma@123")
print(f"\n  Admin login:")
print(f"  Email    : admin@dairyfarm.com")
print(f"  Password : Admin@123")
print(f"\n  Done! Open http://localhost:8501 to see the app.\n")
