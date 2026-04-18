import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from frontend.utils.auth_state import require_login, get_token, get_user
from frontend.utils import api_client as api
from frontend.utils.charts import milk_quality_pie, health_status_bar

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
require_login()
token = get_token()
user  = get_user()

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .metric-card {
        background:white; border-radius:16px; padding:22px 18px; text-align:center;
        border:1px solid #e5e7eb; box-shadow:0 4px 16px rgba(0,0,0,0.07);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover { transform:translateY(-2px); box-shadow:0 8px 24px rgba(0,0,0,0.1); }
    .metric-card .value { font-size:2.4rem; font-weight:800; color:#16a34a; }
    .metric-card .label { font-size:0.85rem; color:#6b7280; margin-top:6px; font-weight:500; }
    .metric-card .icon  { font-size:2rem; margin-bottom:10px; }
    .activity-item {
        background:white; border-radius:12px; padding:14px 16px;
        margin:6px 0; border:1px solid #f0fdf4;
        box-shadow:0 2px 8px rgba(0,0,0,0.04);
        display:flex; align-items:center; gap:12px;
        transition: box-shadow 0.2s;
    }
    .activity-item:hover { box-shadow:0 4px 14px rgba(0,0,0,0.08); }
    #MainMenu{visibility:hidden} footer{visibility:hidden}
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#14532d,#166534,#15803d); }
    [data-testid="stSidebar"] * { color:white !important; }
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style='background:linear-gradient(135deg,#14532d,#16a34a);
     border-radius:16px; padding:24px 28px; margin-bottom:24px; color:white;
     display:flex; align-items:center; justify-content:space-between;'>
    <div>
        <h2 style='margin:0; font-size:1.6rem; font-weight:800;'>📊 Farm Dashboard</h2>
        <p style='margin:6px 0 0; opacity:0.85; font-size:0.92rem;'>
            Real-time overview for <b>{user.get("name")}</b> — all data live from database
        </p>
    </div>
    <div style='font-size:3rem; opacity:0.3;'>🐄</div>
</div>
""", unsafe_allow_html=True)

res = api.get_dashboard(token)
if res.status_code != 200:
    st.error("Could not load dashboard. Please try refreshing.")
    st.stop()

data = res.json()

# KPI Cards
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class='metric-card'>
        <div class='icon'>🐄</div>
        <div class='value'>{data.get("total_cows", 0)}</div>
        <div class='label'>Total Cows</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class='metric-card'>
        <div class='icon'>🏥</div>
        <div class='value'>{data.get("total_health_checks", 0)}</div>
        <div class='label'>Health Checks</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class='metric-card'>
        <div class='icon'>🥛</div>
        <div class='value'>{data.get("total_milk_tests", 0)}</div>
        <div class='label'>Milk Tests</div>
    </div>""", unsafe_allow_html=True)
with c4:
    diseased = data.get("diseased_count", 0)
    color = "#c62828" if diseased > 0 else "#1b5e20"
    st.markdown(f"""<div class='metric-card'>
        <div class='icon'>{'⚠️' if diseased > 0 else '✅'}</div>
        <div class='value' style='color:{color}'>{diseased}</div>
        <div class='label'>Diseased Cattle</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Charts
col_left, col_right = st.columns(2)
with col_left:
    good = data.get("good_milk_count", 0)
    avg  = data.get("average_milk_count", 0)
    poor = data.get("poor_milk_count", 0)
    if good + avg + poor > 0:
        st.plotly_chart(milk_quality_pie(good, avg, poor), use_container_width=True)
    else:
        st.markdown("""<div style='background:white;border-radius:14px;padding:40px;
            text-align:center;border:1px solid #e8f5e9;'>
            <div style='font-size:2.5rem'>🥛</div>
            <div style='color:#888;margin-top:8px'>No milk tests yet</div>
        </div>""", unsafe_allow_html=True)

with col_right:
    total    = data.get("total_cows", 0)
    diseased = data.get("diseased_count", 0)
    healthy  = max(0, total - diseased)
    if total > 0:
        st.plotly_chart(health_status_bar(healthy, diseased), use_container_width=True)
    else:
        st.markdown("""<div style='background:white;border-radius:14px;padding:40px;
            text-align:center;border:1px solid #e8f5e9;'>
            <div style='font-size:2.5rem'>🏥</div>
            <div style='color:#888;margin-top:8px'>No health checks yet</div>
        </div>""", unsafe_allow_html=True)

# Recent Activity
st.markdown("<br>", unsafe_allow_html=True)
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### 🏥 Recent Health Checks")
    recent_health = data.get("recent_health", [])
    if recent_health:
        for h in recent_health:
            icon  = "🟢" if h["status"] == "Healthy" else "🔴"
            label = "Healthy" if h["status"] == "Healthy" else h["disease"]
            st.markdown(f"""<div class='activity-item'>
                <span style='font-size:1.2rem'>{icon}</span>
                <div>
                    <div style='font-weight:600'>Cow #{h["cow_id"]} — {label}</div>
                    <div style='font-size:0.8rem;color:#888'>{h["date"]}</div>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No health checks recorded yet.")

with col_b:
    st.markdown("#### 🥛 Recent Milk Tests")
    recent_milk = data.get("recent_milk", [])
    if recent_milk:
        for m in recent_milk:
            icon  = "🟢" if m["grade"] == "Good" else ("🟡" if m["grade"] == "Average" else "🔴")
            st.markdown(f"""<div class='activity-item'>
                <span style='font-size:1.2rem'>{icon}</span>
                <div>
                    <div style='font-weight:600'>Cow #{m["cow_id"]} — {m["grade"]} Quality</div>
                    <div style='font-size:0.8rem;color:#888'>Score: {m["score"]*100:.0f}% &nbsp;|&nbsp; {m["date"]}</div>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("No milk tests recorded yet.")
