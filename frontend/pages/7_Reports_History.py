import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from frontend.utils.auth_state import require_login, get_token
from frontend.utils import api_client as api

st.set_page_config(page_title="Reports", page_icon="📋", layout="wide")
require_login()
token = get_token()

st.markdown("""<style>
    
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#14532d,#166534,#15803d); }
    [data-testid="stSidebar"] * { color:white !important; }
    [data-testid="stSidebar"] hr { border-color:rgba(255,255,255,0.15); }
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu{visibility:hidden} footer{visibility:hidden}
</style>""", unsafe_allow_html=True)

st.markdown("""
<div style='background:linear-gradient(135deg,#14532d,#16a34a);
     border-radius:16px; padding:24px 28px; margin-bottom:24px; color:white;
     display:flex; align-items:center; justify-content:space-between;'>
    <div>
        <h2 style='margin:0; font-size:1.6rem; font-weight:800;'>📋 Reports & History</h2>
        <p style='margin:6px 0 0; opacity:0.85; font-size:0.92rem;'>Full health, milk quality and recommendation history for each cow</p>
    </div>
    <div style='font-size:3rem; opacity:0.3;'>📋</div>
</div>
""", unsafe_allow_html=True)

cows_res = api.get_cows(token)
if cows_res.status_code != 200 or not cows_res.json():
    st.warning("No cows found. Please add cows first.")
    st.stop()

cows     = cows_res.json()
cow_opts = {f"{c['name']} ({c['cow_uid']})": c["id"] for c in cows}

selected = st.selectbox("Select a Cow", list(cow_opts.keys()))
cow_id   = cow_opts[selected]

if st.button("Load Report", type="primary", use_container_width=True):
    with st.spinner("Loading full report..."):
        res = api.get_cow_report(token, cow_id)

    if res.status_code == 200:
        report = res.json()
        cow    = report["cow"]

        # Header
        st.markdown(f"""
        <div style='background:white;border-radius:14px;padding:20px 24px;border:1px solid #e8f5e9;margin:16px 0'>
            <div style='font-size:1.5rem;font-weight:700;color:#1b5e20'>🐄 {cow['name']}</div>
            <div style='color:#888;margin-top:4px'>UID: {cow['cow_uid']}</div>
            <div style='margin-top:12px;display:flex;gap:24px;flex-wrap:wrap'>
                <div><b>{cow['breed']}</b><div style='color:#888;font-size:0.85rem'>Breed</div></div>
                <div><b>{cow['age']} years</b><div style='color:#888;font-size:0.85rem'>Age</div></div>
                <div><b>{len(report['health_records'])}</b><div style='color:#888;font-size:0.85rem'>Health Checks</div></div>
                <div><b>{len(report['milk_records'])}</b><div style='color:#888;font-size:0.85rem'>Milk Tests</div></div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Health Records
        st.markdown("### 🏥 Health Records")
        health = report["health_records"]
        if health:
            for h in health:
                bcolor = "#2e7d32" if h["status"] == "Healthy" else "#c62828"
                icon   = "🟢" if h["status"] == "Healthy" else "🔴"
                st.markdown(f"""
                <div style='background:white;border-radius:10px;padding:14px 18px;margin:6px 0;
                    border:1px solid #eee;border-left:4px solid {bcolor}'>
                    {icon} <b>{h["disease"]}</b>
                    <span style='color:#888;font-size:0.85rem;margin-left:12px'>
                        Confidence: {h["confidence"]*100:.1f}% &nbsp;|&nbsp; {h["date"][:10]}
                    </span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No health records.")

        # Milk Records
        st.markdown("### 🥛 Milk Quality Records")
        milk = report["milk_records"]
        if milk:
            for m in milk:
                bcolor = "#2e7d32" if m["grade"] == "Good" else ("#f9a825" if m["grade"] == "Average" else "#c62828")
                icon   = "🟢" if m["grade"] == "Good" else ("🟡" if m["grade"] == "Average" else "🔴")
                st.markdown(f"""
                <div style='background:white;border-radius:10px;padding:14px 18px;margin:6px 0;
                    border:1px solid #eee;border-left:4px solid {bcolor}'>
                    {icon} <b>{m["grade"]} Quality</b>
                    <span style='color:#888;font-size:0.85rem;margin-left:12px'>
                        Score: {m["score"]*100:.0f}% &nbsp;|&nbsp;
                        pH: {m["ph"]} &nbsp;|&nbsp;
                        Fat: {m["fat"]}% &nbsp;|&nbsp;
                        {m["date"][:10]}
                    </span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No milk records.")

        # Recommendations
        st.markdown("### 💡 AI Recommendations")
        recs  = report["recommendations"]
        icons = {"feeding": "🌾", "medication": "💊", "preventive": "🛡️", "general": "📌"}
        if recs:
            for r in recs:
                icon = icons.get(r["type"], "📌")
                with st.expander(f"{icon} {r['type'].upper()} — {r['date'][:10]}"):
                    st.write(r["content"])
        else:
            st.info("No recommendations yet.")
    else:
        st.error("Failed to load report. Please try again.")
