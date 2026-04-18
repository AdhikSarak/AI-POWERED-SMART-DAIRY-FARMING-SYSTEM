import requests
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ─── Auth ──────────────────────────────────────────────
def register(name, email, phone, password, role="farmer"):
    return requests.post(f"{BASE_URL}/auth/register", json={"name": name, "email": email, "phone": phone, "password": password, "role": role})

def login(email, password):
    return requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})


# ─── Cows ──────────────────────────────────────────────
def get_cows(token):
    return requests.get(f"{BASE_URL}/cows/", headers=_headers(token))

def add_cow(token, data):
    return requests.post(f"{BASE_URL}/cows/", json=data, headers=_headers(token))

def update_cow(token, cow_id, data):
    return requests.put(f"{BASE_URL}/cows/{cow_id}", json=data, headers=_headers(token))

def delete_cow(token, cow_id):
    return requests.delete(f"{BASE_URL}/cows/{cow_id}", headers=_headers(token))


# ─── Health ────────────────────────────────────────────
def analyze_health(token, cow_id, image_bytes, filename):
    return requests.post(
        f"{BASE_URL}/health/analyze",
        data={"cow_id": cow_id},
        files={"file": (filename, image_bytes, "image/jpeg")},
        headers=_headers(token),
    )

def get_health_history(token, cow_id):
    return requests.get(f"{BASE_URL}/health/history/{cow_id}", headers=_headers(token))


# ─── Milk ──────────────────────────────────────────────
def analyze_milk(token, data):
    return requests.post(f"{BASE_URL}/milk/analyze", json=data, headers=_headers(token))

def get_milk_history(token, cow_id):
    return requests.get(f"{BASE_URL}/milk/history/{cow_id}", headers=_headers(token))


# ─── Recommendations ───────────────────────────────────
def generate_recommendations(token, cow_id):
    return requests.post(f"{BASE_URL}/recommendations/generate/{cow_id}", headers=_headers(token))

def get_recommendations(token, cow_id):
    return requests.get(f"{BASE_URL}/recommendations/{cow_id}", headers=_headers(token))


# ─── Chatbot ───────────────────────────────────────────
def ask_chatbot(token, question, history=None):
    return requests.post(f"{BASE_URL}/chatbot/ask", json={"question": question, "conversation_history": history or []}, headers=_headers(token))


# ─── Agentic AI ────────────────────────────────────────
def agentic_analyze(token, cow_id):
    return requests.post(f"{BASE_URL}/agentic/analyze/{cow_id}", headers=_headers(token))


# ─── Billing ───────────────────────────────────────────
def record_collection(token, data):
    return requests.post(f"{BASE_URL}/billing/collection", json=data, headers=_headers(token))

def get_collections(token):
    return requests.get(f"{BASE_URL}/billing/collection", headers=_headers(token))

def generate_bill(token, farmer_id, month):
    return requests.post(f"{BASE_URL}/billing/generate-bill", json={"farmer_id": farmer_id, "month": month}, headers=_headers(token))

def get_bills(token):
    return requests.get(f"{BASE_URL}/billing/bills", headers=_headers(token))

def get_farmer_bills(token, farmer_id):
    return requests.get(f"{BASE_URL}/billing/bills/farmer/{farmer_id}", headers=_headers(token))


# ─── Reports ───────────────────────────────────────────
def get_dashboard(token):
    return requests.get(f"{BASE_URL}/reports/dashboard", headers=_headers(token))

def get_cow_report(token, cow_id):
    return requests.get(f"{BASE_URL}/reports/cow/{cow_id}", headers=_headers(token))


# ─── Admin ─────────────────────────────────────────────
def get_farmers(token):
    return requests.get(f"{BASE_URL}/admin/farmers", headers=_headers(token))

def get_admin_stats(token):
    return requests.get(f"{BASE_URL}/admin/stats", headers=_headers(token))
