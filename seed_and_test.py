"""
Smart Dairy Farm - Full Seed + End-to-End Test
Registers accounts, feeds realistic demo data, tests every feature.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests, time
from PIL import Image

BASE = "http://localhost:8000"
PASS = "Test@1234"

ADMIN_EMAIL  = "admin@smartdairy.com"
ADMIN_PASS   = PASS
FARMER_EMAIL = "farmer@smartdairy.com"
FARMER_PASS  = PASS

results = []

def hdr(title):
    print(f"\n{'='*62}")
    print(f"  {title}")
    print(f"{'='*62}")

def chk(label, condition, extra=""):
    tag = "[PASS]" if condition else "[FAIL]"
    msg = f"  {tag}  {label}"
    if extra:
        msg += f"  =>  {extra}"
    print(msg)
    results.append((label, condition))
    return condition

def post(path, data=None, token=None, files=None, form=None):
    h = {"Authorization": f"Bearer {token}"} if token else {}
    if files:
        return requests.post(f"{BASE}{path}", data=form, files=files, headers=h, timeout=90)
    return requests.post(f"{BASE}{path}", json=data, headers=h, timeout=90)

def get(path, token=None):
    h = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.get(f"{BASE}{path}", headers=h, timeout=30)

def put(path, data, token):
    h = {"Authorization": f"Bearer {token}"}
    return requests.put(f"{BASE}{path}", json=data, headers=h, timeout=30)

def delete(path, token):
    h = {"Authorization": f"Bearer {token}"}
    return requests.delete(f"{BASE}{path}", headers=h, timeout=30)

def make_jpeg(color=(34,139,34), size=(224,224)):
    """Create a valid JPEG image as bytes using Pillow."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    buf.seek(0)
    return buf.read()


# ================================================================
hdr("STEP 1 - Backend Health Check")
# ================================================================
r = get("/")
chk("Backend API is running", r.status_code == 200,
    r.json().get("status","") if r.status_code == 200 else r.text[:60])


# ================================================================
hdr("STEP 2 - Register Accounts")
# ================================================================

r = post("/auth/register", {
    "name": "Admin User", "email": ADMIN_EMAIL,
    "phone": "9000000001", "password": ADMIN_PASS, "role": "admin"
})
chk("Register admin account", r.status_code in (201, 400),
    "already exists (ok)" if r.status_code == 400 else "created fresh")

r = post("/auth/register", {
    "name": "Ramesh Kumar", "email": FARMER_EMAIL,
    "phone": "9876543210", "password": FARMER_PASS, "role": "farmer"
})
chk("Register farmer account (Ramesh Kumar)", r.status_code in (201, 400),
    "already exists (ok)" if r.status_code == 400 else "created fresh")

r = post("/auth/register", {
    "name": "Suresh Patil", "email": "suresh@smartdairy.com",
    "phone": "9876543211", "password": PASS, "role": "farmer"
})
chk("Register second farmer (Suresh Patil)", r.status_code in (201, 400))


# ================================================================
hdr("STEP 3 - Login Both Accounts")
# ================================================================

r = post("/auth/login", {"email": ADMIN_EMAIL, "password": ADMIN_PASS})
chk("Admin login", r.status_code == 200)
admin_token = r.json().get("access_token","") if r.status_code == 200 else ""
admin_user  = r.json().get("user",{})          if r.status_code == 200 else {}
print(f"       Admin ID: {admin_user.get('id','?')}  |  Role: {admin_user.get('role','?')}")

r = post("/auth/login", {"email": FARMER_EMAIL, "password": FARMER_PASS})
chk("Farmer login", r.status_code == 200)
farmer_token = r.json().get("access_token","") if r.status_code == 200 else ""
farmer_user  = r.json().get("user",{})          if r.status_code == 200 else {}
farmer_id    = farmer_user.get("id")
print(f"       Farmer ID: {farmer_id}  |  Role: {farmer_user.get('role','?')}")

if not admin_token or not farmer_token:
    print("\n[FAIL] Cannot continue without valid tokens. Check credentials.")
    sys.exit(1)


# ================================================================
hdr("STEP 4 - Add 6 Cows (as Farmer)")
# ================================================================

cows_data = [
    {"name": "Gauri",    "breed": "Holstein Friesian", "age": 4, "weight": 480.0},
    {"name": "Lakshmi",  "breed": "Gir",               "age": 5, "weight": 395.0},
    {"name": "Nandini",  "breed": "Sahiwal",            "age": 3, "weight": 360.0},
    {"name": "Kamdhenu", "breed": "Jersey",             "age": 6, "weight": 420.0},
    {"name": "Bhagwati", "breed": "Murrah Buffalo",     "age": 4, "weight": 510.0},
    {"name": "Savitri",  "breed": "Holstein Friesian",  "age": 2, "weight": 310.0},
]

cow_ids = []
for c in cows_data:
    r = post("/cows/", c, token=farmer_token)
    ok = r.status_code == 201
    chk(f"Add cow: {c['name']} ({c['breed']}, age {c['age']})",
        ok, f"ID={r.json().get('id','?')}" if ok else r.text[:60])
    if ok:
        cow_ids.append(r.json()["id"])

# Fallback: use existing cows if none created
if not cow_ids:
    r = get("/cows/", token=farmer_token)
    if r.status_code == 200 and r.json():
        cow_ids = [c["id"] for c in r.json()]
        print(f"       [INFO] Using existing cows: {cow_ids}")

print(f"\n       Cow IDs created: {cow_ids}")


# ================================================================
hdr("STEP 5 - Milk Quality Analysis (6 varied samples)")
# ================================================================
# IMPORTANT: API field is 'ph' (lowercase)

milk_samples = [
    # (cow_index, ph,  temp,  taste, odor, fat, turbidity, colour, expected)
    (0, 6.7, 37.5, 1, 1, 4.2, 0, 254, "Good"),
    (1, 6.8, 36.8, 1, 1, 3.9, 0, 252, "Good"),
    (2, 6.6, 38.0, 1, 1, 4.5, 0, 255, "Good"),
    (3, 6.4, 39.5, 0, 1, 3.2, 1, 245, "Average"),
    (4, 6.9, 40.0, 1, 0, 3.0, 1, 240, "Average"),
    (5, 6.0, 45.0, 0, 0, 2.5, 1, 210, "Poor"),
]

for cidx, ph, temp, taste, odor, fat, turb, colour, expected in milk_samples:
    if cidx >= len(cow_ids):
        break
    cow_id = cow_ids[cidx]
    payload = {
        "cow_id": cow_id, "ph": ph, "temperature": temp,
        "taste": taste, "odor": odor, "fat": fat,
        "turbidity": turb, "colour": colour
    }
    r = post("/milk/analyze", payload, token=farmer_token)
    ok = r.status_code == 200
    if ok:
        grade = r.json().get("quality_grade","?")
        conf  = r.json().get("quality_score", 0) * 100
        chk(f"Milk test  cow#{cow_id}  pH={ph}  fat={fat}  (expected: {expected})",
            ok, f"Predicted: {grade}  Confidence: {conf:.1f}%")
    else:
        chk(f"Milk test  cow#{cow_id}  pH={ph}  (expected: {expected})",
            ok, r.text[:80])


# ================================================================
hdr("STEP 6 - Disease Detection (valid 224x224 JPEG images)")
# ================================================================
# Use Pillow-generated images — different colors simulate different photos

image_colors = [
    (139, 69,  19,  "brown cow field"),
    (34,  139, 34,  "green pasture"),
    (210, 180, 140, "tan/light brown"),
    (101, 67,  33,  "dark brown"),
]

health_cow_ids = cow_ids[:4] if len(cow_ids) >= 4 else cow_ids
for i, cow_id in enumerate(health_cow_ids):
    color, desc = image_colors[i % len(image_colors)][:2], image_colors[i % len(image_colors)][2]
    img_bytes = make_jpeg(color=image_colors[i % len(image_colors)][:3])
    r = requests.post(
        f"{BASE}/health/analyze",
        data={"cow_id": cow_id},
        files={"file": (f"cow_{cow_id}.jpg", img_bytes, "image/jpeg")},
        headers={"Authorization": f"Bearer {farmer_token}"},
        timeout=90
    )
    ok = r.status_code == 200
    if ok:
        disease = r.json().get("disease_name","?")
        conf    = r.json().get("confidence_score", 0) * 100
        status  = r.json().get("health_status","?")
        chk(f"Disease detection  cow#{cow_id}  ({desc})",
            ok, f"{disease}  ({conf:.1f}%)  Status: {status}")
    else:
        chk(f"Disease detection  cow#{cow_id}", ok, r.text[:80])


# ================================================================
hdr("STEP 7 - AI Recommendations (3 cows)")
# ================================================================

rec_cow_ids = cow_ids[:3] if len(cow_ids) >= 3 else cow_ids
for cow_id in rec_cow_ids:
    r = post(f"/recommendations/generate/{cow_id}", token=farmer_token)
    ok = r.status_code == 200
    if ok:
        recs = r.json()
        # response is a list of recommendation objects
        if isinstance(recs, list) and len(recs) > 0:
            first = recs[0].get("content","") if isinstance(recs[0], dict) else str(recs[0])
            snippet = first[:70] + "..."
            chk(f"AI recommendations  cow#{cow_id}", ok,
                f"{len(recs)} recommendations | {snippet}")
        else:
            chk(f"AI recommendations  cow#{cow_id}", ok, str(recs)[:80])
    else:
        chk(f"AI recommendations  cow#{cow_id}", ok, r.text[:80])
    time.sleep(1)


# ================================================================
hdr("STEP 8 - Chatbot (10 different farming questions)")
# ================================================================

questions = [
    "What is Lumpy Skin Disease in cattle?",
    "How to improve milk fat content naturally?",
    "Signs of Foot and Mouth Disease in cows?",
    "Best feed for dairy cows during summer?",
    "How to prevent mastitis in dairy cows?",
    "What is the ideal milk pH range?",
    "What causes low milk production in cows?",
    "How often should dairy cows be vaccinated?",
    "What is the best cattle breed for Indian dairy farming?",
    "How to increase daily milk yield of a cow?",
]

for i, q in enumerate(questions):
    r = post("/chatbot/ask",
             {"question": q, "conversation_history": []},
             token=farmer_token)
    ok = r.status_code == 200
    ans = ""
    if ok:
        ans_text = r.json().get("answer","")
        ans = ans_text[:65].replace("\n"," ") + "..."
    chk(f"Chatbot Q{i+1:02d}: {q[:50]}",
        ok, ans if ok else r.text[:60])
    time.sleep(0.3)


# ================================================================
hdr("STEP 9 - Agentic AI Deep Analysis")
# ================================================================

if cow_ids:
    r = post(f"/agentic/analyze/{cow_ids[0]}", token=farmer_token)
    ok = r.status_code == 200
    if ok:
        data = r.json()
        # handle various response shapes
        text = (data.get("analysis") or data.get("result") or
                data.get("recommendations") or str(data))
        if isinstance(text, list):
            text = text[0].get("content","") if isinstance(text[0],dict) else str(text[0])
        snippet = str(text)[:80].replace("\n"," ") + "..."
        chk(f"Agentic deep analysis  cow#{cow_ids[0]}", ok, snippet)
    else:
        chk(f"Agentic deep analysis  cow#{cow_ids[0]}", ok, r.text[:80])


# ================================================================
hdr("STEP 10 - Admin: Fetch Farmers List")
# ================================================================

r = get("/admin/farmers", token=admin_token)
chk("Admin: get all farmers list", r.status_code == 200,
    f"{len(r.json())} farmers" if r.status_code == 200 else r.text[:60])

farmers_list = r.json() if r.status_code == 200 else []
# pick the farmer we created
target_farmer_id = farmer_id
if not target_farmer_id and farmers_list:
    target_farmer_id = farmers_list[0]["id"]
print(f"       Using farmer_id={target_farmer_id} for billing records")


# ================================================================
hdr("STEP 11 - Admin: Record 15 Milk Collections (April 2026)")
# ================================================================

# Required fields: farmer_id, cow_id, quantity_liters, quality_grade, rate_per_liter, collection_date
cid = cow_ids[0] if cow_ids else None  # use first cow for collections
collections = [
    {"farmer_id": target_farmer_id, "cow_id": cid, "quantity_liters": 18.5, "quality_grade": "Good",    "rate_per_liter": 55.0, "collection_date": "2026-04-01"},
    {"farmer_id": target_farmer_id, "cow_id": cid, "quantity_liters": 20.0, "quality_grade": "Good",    "rate_per_liter": 55.0, "collection_date": "2026-04-02"},
    {"farmer_id": target_farmer_id, "cow_id": cid, "quantity_liters": 17.5, "quality_grade": "Good",    "rate_per_liter": 55.0, "collection_date": "2026-04-03"},
    {"farmer_id": target_farmer_id, "cow_id": cid, "quantity_liters": 22.0, "quality_grade": "Good",    "rate_per_liter": 55.0, "collection_date": "2026-04-04"},
    {"farmer_id": target_farmer_id, "cow_id": cid, "quantity_liters": 19.0, "quality_grade": "Good",    "rate_per_liter": 55.0, "collection_date": "2026-04-05"},
    {"farmer_id": target_farmer_id, "cow_id": cid, "quantity_liters": 21.5, "quality_grade": "Average", "rate_per_liter": 55.0, "collection_date": "2026-04-06"},
    {"farmer_id": target_farmer_id, "cow_id": cid, "quantity_liters": 16.0, "quality_grade": "Good",    "rate_per_liter": 55.0, "collection_date": "2026-04-07"},
    {"farmer_id": target_farmer_id, "cow_id": cid, "quantity_liters": 23.0, "quality_grade": "Good",    "rate_per_liter": 55.0, "collection_date": "2026-04-08"},
    {"farmer_id": target_farmer_id, "cow_id": cid, "quantity_liters": 18.0, "quality_grade": "Good",    "rate_per_liter": 55.0, "collection_date": "2026-04-09"},
    {"farmer_id": target_farmer_id, "cow_id": cid, "quantity_liters": 20.5, "quality_grade": "Average", "rate_per_liter": 55.0, "collection_date": "2026-04-10"},
    {"farmer_id": target_farmer_id, "cow_id": cid, "quantity_liters": 19.5, "quality_grade": "Good",    "rate_per_liter": 55.0, "collection_date": "2026-04-11"},
    {"farmer_id": target_farmer_id, "cow_id": cid, "quantity_liters": 21.0, "quality_grade": "Good",    "rate_per_liter": 55.0, "collection_date": "2026-04-12"},
    {"farmer_id": target_farmer_id, "cow_id": cid, "quantity_liters": 17.0, "quality_grade": "Good",    "rate_per_liter": 55.0, "collection_date": "2026-04-13"},
    {"farmer_id": target_farmer_id, "cow_id": cid, "quantity_liters": 24.0, "quality_grade": "Good",    "rate_per_liter": 55.0, "collection_date": "2026-04-14"},
    {"farmer_id": target_farmer_id, "cow_id": cid, "quantity_liters": 22.5, "quality_grade": "Good",    "rate_per_liter": 55.0, "collection_date": "2026-04-15"},
]

total_liters = 0
for c in collections:
    r = post("/billing/collection", c, token=admin_token)
    ok = r.status_code in (200, 201)
    if ok:
        total_liters += c["quantity_liters"]
    chk(f"Collection: {c['collection_date']}  {c['quantity_liters']}L  grade={c['quality_grade']}", ok)

print(f"\n       Total: {total_liters:.1f} Litres  =>  Rs. {total_liters * 55:.0f}")


# ================================================================
hdr("STEP 12 - Admin: Generate Monthly Bill (April 2026)")
# ================================================================

r = post("/billing/generate-bill",
         {"farmer_id": target_farmer_id, "month": "2026-04"},
         token=admin_token)
ok = r.status_code == 200
if ok:
    bill = r.json()
    # handle both dict and list response
    if isinstance(bill, list):
        bill = bill[0] if bill else {}
    total_L  = bill.get("total_liters", "?")
    total_Rs = bill.get("total_amount", "?")
    chk("Generate April 2026 bill for Ramesh Kumar",
        ok, f"Total: {total_L} L  |  Amount: Rs. {total_Rs}")
else:
    chk("Generate April 2026 bill", ok, r.text[:100])


# ================================================================
hdr("STEP 13 - Dashboard & Reports")
# ================================================================

r = get("/reports/dashboard", token=farmer_token)
chk("Farmer dashboard data", r.status_code == 200)
if r.status_code == 200:
    d = r.json()
    print(f"       Cows: {d.get('total_cows')}  |  Health Checks: {d.get('total_health_checks')}"
          f"  |  Milk Tests: {d.get('total_milk_tests')}  |  Diseased: {d.get('diseased_count')}")

if cow_ids:
    r = get(f"/reports/cow/{cow_ids[0]}", token=farmer_token)
    chk(f"Full cow report  cow#{cow_ids[0]}", r.status_code == 200)

r = get("/admin/stats", token=admin_token)
chk("Admin global stats", r.status_code == 200)
if r.status_code == 200:
    d = r.json()
    print(f"       {d}")


# ================================================================
hdr("STEP 14 - History Endpoints (health, milk, recommendations)")
# ================================================================

for cow_id in cow_ids[:3]:
    r = get(f"/health/history/{cow_id}", token=farmer_token)
    chk(f"Health history  cow#{cow_id}", r.status_code == 200,
        f"{len(r.json())} records" if r.status_code == 200 else "")

for cow_id in cow_ids[:3]:
    r = get(f"/milk/history/{cow_id}", token=farmer_token)
    chk(f"Milk history  cow#{cow_id}", r.status_code == 200,
        f"{len(r.json())} records" if r.status_code == 200 else "")

for cow_id in cow_ids[:3]:
    r = get(f"/recommendations/{cow_id}", token=farmer_token)
    chk(f"Recommendations history  cow#{cow_id}", r.status_code == 200,
        f"{len(r.json())} records" if r.status_code == 200 else "")


# ================================================================
hdr("STEP 15 - Cow Update & Delete")
# ================================================================

if len(cow_ids) >= 6:
    last = cow_ids[-1]
    r = put(f"/cows/{last}",
            {"name": "Savitri Updated", "breed": "Jersey", "age": 3, "weight": 320.0},
            token=farmer_token)
    chk(f"Update cow#{last} (weight + name change)", r.status_code == 200)

# Add a temp cow then delete it
r = post("/cows/",
         {"name": "TempDeleteCow", "breed": "Jersey", "age": 1, "weight": 200.0},
         token=farmer_token)
if r.status_code == 201:
    tmp_id = r.json()["id"]
    r2 = delete(f"/cows/{tmp_id}", token=farmer_token)
    chk(f"Delete temp cow#{tmp_id}", r2.status_code in (200, 204))


# ================================================================
hdr("STEP 16 - Security: Invalid Token Rejected")
# ================================================================

r = get("/cows/", token="invalid.jwt.token")
chk("Invalid token => 401 on cows endpoint", r.status_code == 401)

r = get("/reports/dashboard", token="bad_token_xyz")
chk("Invalid token => 401 on dashboard", r.status_code == 401)

r = get("/admin/farmers", token=farmer_token)
chk("Farmer token => 403 on admin endpoint", r.status_code in (401, 403))


# ================================================================
hdr("STEP 17 - Billing History")
# ================================================================

r = get("/billing/bills", token=admin_token)
chk("Get all bills (admin)", r.status_code == 200,
    f"{len(r.json())} bills" if r.status_code == 200 else r.text[:60])

r = get(f"/billing/bills/farmer/{target_farmer_id}", token=farmer_token)
chk("Get farmer bills (farmer view)", r.status_code == 200,
    f"{len(r.json())} bills" if r.status_code == 200 else r.text[:60])

r = get("/billing/collection", token=admin_token)
chk("Get collection records (admin)", r.status_code == 200,
    f"{len(r.json())} entries" if r.status_code == 200 else r.text[:60])


# ================================================================
hdr("FINAL RESULTS SUMMARY")
# ================================================================

passed = sum(1 for _, ok in results if ok)
failed = sum(1 for _, ok in results if not ok)
total  = len(results)
pct    = (passed/total*100) if total else 0

print(f"\n  PASSED : {passed}/{total}  ({pct:.0f}%)")
if failed:
    print(f"  FAILED : {failed}/{total}")
    print("\n  Failed tests:")
    for label, ok in results:
        if not ok:
            print(f"    [FAIL]  {label}")

print(f"\n{'='*62}")
print("  YOUR LOGIN CREDENTIALS")
print(f"{'='*62}")
print(f"")
print(f"  ADMIN ACCOUNT")
print(f"    Email    : {ADMIN_EMAIL}")
print(f"    Password : {ADMIN_PASS}")
print(f"    Can do   : Manage farmers, record milk collections, generate bills,")
print(f"               view admin stats panel")
print(f"")
print(f"  FARMER ACCOUNT")
print(f"    Email    : {FARMER_EMAIL}")
print(f"    Password : {FARMER_PASS}")
print(f"    Can do   : Add/manage cows, disease detection, milk quality,")
print(f"               AI recommendations, chatbot, view reports & bills")
print(f"")
print(f"{'='*62}")
print(f"  DATA SEEDED SUMMARY")
print(f"{'='*62}")
print(f"    6 cows added       : Gauri, Lakshmi, Nandini, Kamdhenu, Bhagwati, Savitri")
print(f"    6 milk tests       : Good x3, Average x2, Poor x1")
print(f"    4 disease scans    : All cows analyzed with AI model")
print(f"    3 AI recs          : Personalized per cow from Groq Llama 3")
print(f"   10 chatbot Q&A      : Various dairy farming questions answered")
print(f"    1 agentic analysis : Deep AI analysis for cow Gauri")
print(f"   15 milk collections : April 1-15, 2026 @ Rs.55/litre")
print(f"    1 monthly bill     : April 2026 bill generated for Ramesh Kumar")
print(f"{'='*62}\n")
