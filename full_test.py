"""
Full end-to-end test — special focus on chatbot.
Run: python -X utf8 full_test.py
"""
import requests, json, io, time
from PIL import Image
import numpy as np

BASE = "http://127.0.0.1:8000"
passed = []
failed = []

def test(name, resp, expected, show=None):
    ok = resp.status_code == expected
    detail = ""
    if show and ok:
        try: detail = "=> " + str(show(resp.json()))
        except: pass
    if not ok:
        try: detail = "=> ERROR: " + json.dumps(resp.json())[:200]
        except: detail = "=> " + resp.text[:200]
    mark = "PASS" if ok else "FAIL"
    (passed if ok else failed).append(name)
    print(f"  [{mark}] {name} (HTTP {resp.status_code}) {detail}")
    return ok, resp

print("\n======= TEST 1: HEALTH CHECK =======")
test("API root",    requests.get(f"{BASE}/"),             200, lambda d: d["status"])
test("Health ping", requests.get(f"{BASE}/health-check"), 200, lambda d: d["status"])

print("\n======= TEST 2: AUTH =======")
# login with user's account
ok, lr = test("Login somnathtk198@gmail.com", requests.post(f"{BASE}/auth/login",
    json={"email": "somnathtk198@gmail.com", "password": "Soma@123"}),
    200, lambda d: "token_ok" if d.get("access_token") else "NO_TOKEN")
if not ok:
    print("  Cannot continue without login. Exiting.")
    exit()

token   = lr.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

ok2, lr2 = test("Login admin@dairyfarm.com", requests.post(f"{BASE}/auth/login",
    json={"email": "admin@dairyfarm.com", "password": "Admin@123"}),
    200, lambda d: "token_ok" if d.get("access_token") else "NO_TOKEN")
admin_headers = {"Authorization": f"Bearer {lr2.json()['access_token']}"} if ok2 else {}

test("Wrong password rejected", requests.post(f"{BASE}/auth/login",
    json={"email": "somnathtk198@gmail.com", "password": "wrongpass"}), 401)

print("\n======= TEST 3: COW MANAGEMENT =======")
cows_r = requests.get(f"{BASE}/cows/", headers=headers)
test("List cows", cows_r, 200, lambda d: f"{len(d)} cows found")
cows   = cows_r.json() if cows_r.status_code == 200 else []
cow_id = cows[0]["id"] if cows else None
if cow_id:
    test("Get single cow", requests.get(f"{BASE}/cows/{cow_id}", headers=headers),
         200, lambda d: f"{d['name']} ({d['breed']})")
    test("Update cow weight", requests.put(f"{BASE}/cows/{cow_id}",
         json={"weight_kg": 460.0}, headers=headers), 200, lambda d: f"weight={d['weight_kg']}kg")

print("\n======= TEST 4: MILK QUALITY ML =======")
if cow_id:
    test("Good milk",    requests.post(f"{BASE}/milk/analyze", json={
        "cow_id":cow_id,"ph":6.8,"temperature":37.0,"taste":1,
        "odor":1,"fat":3.8,"turbidity":0,"colour":254}, headers=headers),
        200, lambda d: f"Grade={d['quality_grade']} Score={d['quality_score']*100:.0f}%")

    test("Poor milk",    requests.post(f"{BASE}/milk/analyze", json={
        "cow_id":cow_id,"ph":4.5,"temperature":80.0,"taste":0,
        "odor":0,"fat":0.8,"turbidity":1,"colour":120}, headers=headers),
        200, lambda d: f"Grade={d['quality_grade']} Score={d['quality_score']*100:.0f}%")

    test("Average milk", requests.post(f"{BASE}/milk/analyze", json={
        "cow_id":cow_id,"ph":6.4,"temperature":44.0,"taste":1,
        "odor":1,"fat":2.2,"turbidity":1,"colour":230}, headers=headers),
        200, lambda d: f"Grade={d['quality_grade']} Score={d['quality_score']*100:.0f}%")

    test("Milk history", requests.get(f"{BASE}/milk/history/{cow_id}", headers=headers),
         200, lambda d: f"{len(d)} records in DB")

print("\n======= TEST 5: DISEASE DETECTION ML =======")
if cow_id:
    arr = np.random.randint(80, 180, (224, 224, 3), dtype=np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="JPEG")
    buf.seek(0)
    test("Disease detection", requests.post(f"{BASE}/health/analyze",
         data={"cow_id": cow_id},
         files={"file": ("cow.jpg", buf, "image/jpeg")},
         headers=headers), 200,
         lambda d: f"Disease={d['disease_name']} Conf={d['confidence_score']*100:.0f}% Status={d['health_status']}")
    test("Health history", requests.get(f"{BASE}/health/history/{cow_id}", headers=headers),
         200, lambda d: f"{len(d)} records in DB")

print("\n======= TEST 6: AI RECOMMENDATIONS =======")
if cow_id:
    test("Generate 3 recommendations", requests.post(
        f"{BASE}/recommendations/generate/{cow_id}", headers=headers),
        200, lambda d: f"{len(d)} recs: {[r['rec_type'] for r in d]}")
    test("Fetch recommendations", requests.get(
        f"{BASE}/recommendations/{cow_id}", headers=headers),
        200, lambda d: f"{len(d)} stored in DB")

print("\n======= TEST 7: AGENTIC AI =======")
if cow_id:
    test("Agentic deep analysis", requests.post(
        f"{BASE}/agentic/analyze/{cow_id}", headers=headers),
        200, lambda d: f"model={d['model_used']} length={len(d['insights'])} chars")

print("\n======= TEST 8: CHATBOT (DEEP TESTING) =======")

chatbot_tests = [
    ("Dairy disease question",   "What are the symptoms of Lumpy Skin Disease in cattle?"),
    ("Milk quality question",    "How can I improve the fat content in cow milk?"),
    ("Feed question",            "What is the best diet for a Holstein Friesian dairy cow?"),
    ("Disease prevention",       "How do I prevent Foot and Mouth Disease on my farm?"),
    ("pH question",              "What is the ideal pH range for fresh cow milk?"),
    ("Multi-turn conversation",  "What causes mastitis in dairy cows?"),
]

conversation_history = []
for test_name, question in chatbot_tests:
    r = requests.post(f"{BASE}/chatbot/ask", json={
        "question": question,
        "conversation_history": conversation_history
    }, headers=headers)

    ok, _ = test(f"Chatbot: {test_name}", r, 200,
        lambda d: f"{len(d['answer'])} chars | model={d['model_used']}")

    if ok:
        answer = r.json()["answer"]
        # Add to conversation history for multi-turn test
        conversation_history.append({"role": "user",      "content": question})
        conversation_history.append({"role": "assistant", "content": answer})
        # Keep only last 4 messages
        conversation_history = conversation_history[-4:]

        # Validate answer quality
        if len(answer) < 50:
            print(f"         WARNING: Answer too short ({len(answer)} chars)")
            failed.append(f"Short answer: {test_name}")
            passed.pop()
        else:
            print(f"         Preview: {answer[:120]}...")
    time.sleep(0.5)

# Empty question test
r_empty = requests.post(f"{BASE}/chatbot/ask", json={
    "question": "   ", "conversation_history": []
}, headers=headers)
print(f"  [INFO] Empty question => HTTP {r_empty.status_code} (server handled it)")

print("\n======= TEST 9: DASHBOARD & REPORTS =======")
test("Dashboard stats", requests.get(f"{BASE}/reports/dashboard", headers=headers),
     200, lambda d: f"cows={d['total_cows']} milk={d['total_milk_tests']} good={d['good_milk_count']} poor={d['poor_milk_count']} diseased={d['diseased_count']}")

if cow_id:
    test("Full cow report", requests.get(f"{BASE}/reports/cow/{cow_id}", headers=headers),
         200, lambda d: f"health={len(d['health_records'])} milk={len(d['milk_records'])} recs={len(d['recommendations'])}")

print("\n======= TEST 10: BILLING =======")
farmer_id = lr.json()["user"]["id"]
test("Record collection", requests.post(f"{BASE}/billing/collection", json={
    "farmer_id": farmer_id, "quantity_liters": 28.0,
    "quality_grade": "Good", "rate_per_liter": 52.0,
    "collection_date": "2026-04-18"
}, headers=admin_headers), 201, lambda d: f"{d['quantity_liters']}L @ Rs.{d['rate_per_liter']}/L")
test("List collections", requests.get(f"{BASE}/billing/collection", headers=admin_headers),
     200, lambda d: f"{len(d)} total records")
test("List bills", requests.get(f"{BASE}/billing/bills", headers=admin_headers),
     200, lambda d: f"{len(d)} bills generated")

print("\n======= TEST 11: ADMIN PANEL =======")
test("Admin stats", requests.get(f"{BASE}/admin/stats", headers=admin_headers),
     200, lambda d: f"farmers={d['total_farmers']} cows={d['total_cows']} health={d['total_health_checks']} milk={d['total_milk_tests']}")
test("List farmers", requests.get(f"{BASE}/admin/farmers", headers=admin_headers),
     200, lambda d: f"{len(d)} farmers")
test("Farmer blocked from admin", requests.get(f"{BASE}/admin/stats", headers=headers), 403)

# ── FINAL REPORT ─────────────────────────────────────────────────
total = len(passed) + len(failed)
print(f"""
==========================================
         FINAL TEST REPORT
==========================================
  Total Tests : {total}
  PASSED      : {len(passed)}
  FAILED      : {len(failed)}""")

if failed:
    print("\n  FAILED TESTS:")
    for f in failed:
        print(f"    - {f}")

print(f"""
  RESULT: {"ALL TESTS PASSED" if not failed else f"{len(failed)} FAILED"}
==========================================
""")
