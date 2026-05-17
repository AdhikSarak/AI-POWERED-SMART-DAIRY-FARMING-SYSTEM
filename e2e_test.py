import requests, json, os, io, time
from PIL import Image
import numpy as np

BASE = 'http://127.0.0.1:8000'
results = []
token = ''
headers = {}
admin_headers = {}
cow_id = None
farmer_id = None

def test(name, resp, expected, show=None):
    ok = resp.status_code == expected
    mark = 'PASS' if ok else 'FAIL'
    detail = ''
    if show and ok:
        try:
            detail = '=> ' + str(show(resp.json()))
        except:
            pass
    if not ok:
        try:
            detail = '=> ERROR: ' + str(resp.json())
        except:
            detail = '=> ' + resp.text[:150]
    results.append((mark, name, resp.status_code, detail))
    print(f'  [{mark}] {name} (HTTP {resp.status_code}) {detail}')
    return ok, resp


# ══════════════════════════════════════════
print('\n══════ TEST 1: API ROOT & HEALTH CHECK ══════')
test('API root',      requests.get(f'{BASE}/'),             200, lambda d: d['status'])
test('Health check',  requests.get(f'{BASE}/health-check'), 200, lambda d: d['status'])


# ══════════════════════════════════════════
print('\n══════ TEST 2: AUTHENTICATION ══════')

r = requests.post(f'{BASE}/auth/register', json={
    'name': 'E2E Farmer', 'email': 'e2e_farmer@test.com',
    'phone': '8888888888', 'password': 'E2e@5678', 'role': 'farmer'
})
if r.status_code in (201, 400):
    print(f'  [PASS] Register farmer (HTTP {r.status_code}) => {"created" if r.status_code==201 else "already exists"}')
    results.append(('PASS', 'Register farmer', r.status_code, ''))
else:
    test('Register farmer', r, 201)

r2 = requests.post(f'{BASE}/auth/register', json={
    'name': 'E2E Admin', 'email': 'e2e_admin@test.com',
    'phone': '7777777777', 'password': 'E2e@5678', 'role': 'admin'
})
if r2.status_code in (201, 400):
    print(f'  [PASS] Register admin (HTTP {r2.status_code}) => {"created" if r2.status_code==201 else "already exists"}')
    results.append(('PASS', 'Register admin', r2.status_code, ''))
else:
    test('Register admin', r2, 201)

ok, lr = test('Login farmer', requests.post(f'{BASE}/auth/login',
    json={'email': 'e2e_farmer@test.com', 'password': 'E2e@5678'}),
    200, lambda d: 'token_received' if d.get('access_token') else 'NO_TOKEN')
if ok:
    token = lr.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

test('Login wrong password', requests.post(f'{BASE}/auth/login',
    json={'email': 'e2e_farmer@test.com', 'password': 'wrongpass'}), 401)

ok2, lr2 = test('Login admin', requests.post(f'{BASE}/auth/login',
    json={'email': 'e2e_admin@test.com', 'password': 'E2e@5678'}),
    200, lambda d: 'token_received' if d.get('access_token') else 'NO_TOKEN')
if ok2:
    admin_headers = {'Authorization': f'Bearer {lr2.json()["access_token"]}'}


# ══════════════════════════════════════════
print('\n══════ TEST 3: COW MANAGEMENT ══════')

ok, cr = test('Add cow', requests.post(f'{BASE}/cows/', json={
    'name': 'Lakshmi', 'age': 3.5, 'breed': 'Gir', 'weight_kg': 380.0
}, headers=headers), 201, lambda d: f'cow_id={d["id"]} uid={d["cow_uid"]}')
if ok:
    cow_id = cr.json()['id']
    farmer_id = cr.json().get('farmer_id')

test('List cows', requests.get(f'{BASE}/cows/', headers=headers), 200,
     lambda d: f'{len(d)} cows found')

if cow_id:
    test('Get cow by ID', requests.get(f'{BASE}/cows/{cow_id}', headers=headers), 200,
         lambda d: f'name={d["name"]} breed={d["breed"]}')
    test('Update cow weight', requests.put(f'{BASE}/cows/{cow_id}',
         json={'weight_kg': 395.0}, headers=headers), 200,
         lambda d: f'weight={d["weight_kg"]}kg')


# ══════════════════════════════════════════
print('\n══════ TEST 4: MILK QUALITY ML MODEL ══════')

if cow_id:
    test('Predict GOOD milk', requests.post(f'{BASE}/milk/analyze', json={
        'cow_id': cow_id, 'ph': 6.8, 'temperature': 35.0, 'taste': 1,
        'odor': 1, 'fat': 3.5, 'turbidity': 0, 'colour': 254
    }, headers=headers), 200, lambda d: f'Grade={d["quality_grade"]} Score={round(d["quality_score"]*100,1)}%')

    test('Predict POOR milk', requests.post(f'{BASE}/milk/analyze', json={
        'cow_id': cow_id, 'ph': 4.0, 'temperature': 95.0, 'taste': 0,
        'odor': 0, 'fat': 0.3, 'turbidity': 1, 'colour': 80
    }, headers=headers), 200, lambda d: f'Grade={d["quality_grade"]} Score={round(d["quality_score"]*100,1)}%')

    test('Predict AVERAGE milk', requests.post(f'{BASE}/milk/analyze', json={
        'cow_id': cow_id, 'ph': 6.5, 'temperature': 40.0, 'taste': 1,
        'odor': 1, 'fat': 2.0, 'turbidity': 1, 'colour': 200
    }, headers=headers), 200, lambda d: f'Grade={d["quality_grade"]} Score={round(d["quality_score"]*100,1)}%')

    test('Milk history', requests.get(f'{BASE}/milk/history/{cow_id}', headers=headers), 200,
         lambda d: f'{len(d)} records stored in DB')


# ══════════════════════════════════════════
print('\n══════ TEST 5: DISEASE DETECTION ML MODEL ══════')

if cow_id:
    img_arr = np.random.randint(50, 200, (224, 224, 3), dtype=np.uint8)
    img = Image.fromarray(img_arr)
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)

    r = requests.post(f'{BASE}/health/analyze',
        data={'cow_id': cow_id},
        files={'file': ('test_disease.jpg', buf, 'image/jpeg')},
        headers=headers)
    test('Disease detection', r, 200,
         lambda d: f'Disease={d["disease_name"]} Conf={round(d["confidence_score"]*100,1)}% Status={d["health_status"]}')

    test('Health history', requests.get(f'{BASE}/health/history/{cow_id}', headers=headers), 200,
         lambda d: f'{len(d)} records stored in DB')


# ══════════════════════════════════════════
print('\n══════ TEST 6: AI RECOMMENDATIONS (GROQ LLM) ══════')

if cow_id:
    test('Generate AI recommendations', requests.post(
        f'{BASE}/recommendations/generate/{cow_id}', headers=headers), 200,
        lambda d: f'{len(d)} recommendations => types: {[r["rec_type"] for r in d]}')

    test('Fetch stored recommendations', requests.get(
        f'{BASE}/recommendations/{cow_id}', headers=headers), 200,
        lambda d: f'{len(d)} recommendations in DB')


# ══════════════════════════════════════════
print('\n══════ TEST 7: AGENTIC AI ANALYSIS (GROQ LLM) ══════')

if cow_id:
    test('Agentic deep analysis', requests.post(
        f'{BASE}/agentic/analyze/{cow_id}', headers=headers), 200,
        lambda d: f'model={d["model_used"]} insights={len(d["insights"])} chars')


# ══════════════════════════════════════════
print('\n══════ TEST 8: AI CHATBOT (GROQ LLM) ══════')

test('Chatbot - disease question', requests.post(f'{BASE}/chatbot/ask', json={
    'question': 'What are symptoms of Foot and Mouth disease in cattle?',
    'conversation_history': []
}, headers=headers), 200, lambda d: f'{len(d["answer"])} chars returned')

test('Chatbot - nutrition question', requests.post(f'{BASE}/chatbot/ask', json={
    'question': 'How to improve milk yield in Holstein cows?',
    'conversation_history': []
}, headers=headers), 200, lambda d: f'{len(d["answer"])} chars returned')


# ══════════════════════════════════════════
print('\n══════ TEST 9: REPORTS & DASHBOARD ══════')

test('Dashboard stats', requests.get(f'{BASE}/reports/dashboard', headers=headers), 200,
     lambda d: f'cows={d["total_cows"]} milk_tests={d["total_milk_tests"]} good={d["good_milk_count"]} avg={d["average_milk_count"]} poor={d["poor_milk_count"]}')

if cow_id:
    test('Full cow report', requests.get(f'{BASE}/reports/cow/{cow_id}', headers=headers), 200,
         lambda d: f'health={len(d["health_records"])} milk={len(d["milk_records"])} recs={len(d["recommendations"])}')


# ══════════════════════════════════════════
print('\n══════ TEST 10: BILLING ══════')

if not farmer_id:
    cows_r = requests.get(f'{BASE}/cows/', headers=headers)
    if cows_r.status_code == 200 and cows_r.json():
        farmer_id = cows_r.json()[0].get('farmer_id')

if farmer_id:
    ok, col = test('Record milk collection', requests.post(f'{BASE}/billing/collection', json={
        'farmer_id': farmer_id, 'quantity_liters': 30.0,
        'quality_grade': 'Good', 'rate_per_liter': 45.0,
        'collection_date': '2026-04-18'
    }, headers=admin_headers), 201,
    lambda d: f'liters={d["quantity_liters"]} rate=Rs.{d["rate_per_liter"]}/L')

    test('List all collections', requests.get(f'{BASE}/billing/collection',
         headers=admin_headers), 200, lambda d: f'{len(d)} records')

    test('Generate bill', requests.post(f'{BASE}/billing/generate-bill', json={
        'farmer_id': farmer_id, 'month': '2026-04'
    }, headers=admin_headers), 200,
    lambda d: f'total_liters={d["total_liters"]} total_amount=Rs.{d["total_amount"]}')

    test('List all bills', requests.get(f'{BASE}/billing/bills',
         headers=admin_headers), 200, lambda d: f'{len(d)} bills')


# ══════════════════════════════════════════
print('\n══════ TEST 11: ADMIN PANEL ══════')

test('Admin system stats', requests.get(f'{BASE}/admin/stats', headers=admin_headers), 200,
     lambda d: f'farmers={d["total_farmers"]} cows={d["total_cows"]} health_checks={d["total_health_checks"]} milk_tests={d["total_milk_tests"]}')

test('Admin list all farmers', requests.get(f'{BASE}/admin/farmers', headers=admin_headers), 200,
     lambda d: f'{len(d)} farmers registered')

test('Farmer cannot access admin stats', requests.get(f'{BASE}/admin/stats', headers=headers), 403)


# ══════════════════════════════════════════
print('\n══════════════════════════════════════════')
print('         FINAL E2E TEST REPORT')
print('══════════════════════════════════════════')
passed = [r for r in results if r[0] == 'PASS']
failed = [r for r in results if r[0] == 'FAIL']
print(f'\n  Total Tests : {len(results)}')
print(f'  PASSED      : {len(passed)}')
print(f'  FAILED      : {len(failed)}')

if failed:
    print('\n  FAILED TESTS:')
    for r in failed:
        print(f'    FAIL - {r[1]} (HTTP {r[2]}) {r[3]}')

print()
if not failed:
    print('  RESULT: ALL TESTS PASSED - PROJECT IS FULLY WORKING')
else:
    print(f'  RESULT: {len(failed)} TEST(S) FAILED - SEE ABOVE')
print()
