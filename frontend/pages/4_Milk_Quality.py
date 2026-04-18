import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from frontend.utils.auth_state import require_login, get_token
from frontend.utils import api_client as api
from frontend.utils.charts import milk_trend_line

st.set_page_config(page_title="Milk Quality", page_icon="🥛", layout="wide")
require_login()
token = get_token()

st.markdown("""<style>
    .result-good    { background:#e8f5e9; border:2px solid #2e7d32; border-radius:14px; padding:24px; text-align:center; }
    .result-average { background:#fff8e1; border:2px solid #f9a825; border-radius:14px; padding:24px; text-align:center; }
    .result-poor    { background:#ffebee; border:2px solid #c62828; border-radius:14px; padding:24px; text-align:center; }
    
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
        <h2 style='margin:0; font-size:1.6rem; font-weight:800;'>🥛 Milk Quality Analysis</h2>
        <p style='margin:6px 0 0; opacity:0.85; font-size:0.92rem;'>Enter sensor readings to grade milk quality using Random Forest ML (98.5% accuracy)</p>
    </div>
    <div style='font-size:3rem; opacity:0.3;'>🥛</div>
</div>
""", unsafe_allow_html=True)

cows_res = api.get_cows(token)
if cows_res.status_code != 200 or not cows_res.json():
    st.warning("No cows registered. Please add cows first.")
    st.stop()

cows     = cows_res.json()
cow_opts = {f"{c['name']} ({c['cow_uid']})": c["id"] for c in cows}

tab1, tab2 = st.tabs(["  Analyze Milk  ", "  Milk History  "])

with tab1:
    st.markdown("#### Enter Milk Parameters")
    st.markdown("<div style='color:#666;font-size:0.9rem;margin-bottom:16px'>Fill in the readings from your milk quality sensor</div>", unsafe_allow_html=True)

    selected = st.selectbox("Select Cow", list(cow_opts.keys()))
    cow_id   = cow_opts[selected]

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Basic Parameters**")
        ph   = st.slider("pH Level", min_value=3.0, max_value=9.5, value=6.8, step=0.1,
                         help="Normal milk pH: 6.4 - 6.8")
        temp = st.slider("Temperature (°C)", min_value=34.0, max_value=100.0, value=38.0, step=0.5,
                         help="Fresh milk temperature")
        fat  = st.slider("Fat Content (%)", min_value=0.1, max_value=10.0, value=3.5, step=0.1,
                         help="Normal fat: 3.0% - 4.5%")

    with col2:
        st.markdown("**Sensory Parameters**")
        taste  = st.radio("Taste",     [1, 0], format_func=lambda x: "Good" if x == 1 else "Bad",
                          help="Is the milk taste acceptable?")
        odor   = st.radio("Odor",      [1, 0], format_func=lambda x: "Good" if x == 1 else "Bad",
                          key="odor", help="Does the milk smell fresh?")
        turbid = st.radio("Turbidity", [0, 1], format_func=lambda x: "Low (Clear)" if x == 0 else "High (Cloudy)",
                          help="Is the milk clear or cloudy?")

    with col3:
        st.markdown("**Visual Parameter**")
        colour = st.number_input("Colour Value (0-255)", min_value=0, max_value=255, value=250,
                                 help="Fresh white milk is close to 255")
        st.markdown("""
        <div style='background:#f9f9f9;border-radius:10px;padding:12px;margin-top:16px;font-size:0.85rem;color:#666'>
            <b>Reference Guide:</b><br>
            pH 6.4-6.8 = Normal<br>
            Fat 3-4.5% = Good<br>
            Colour 240-255 = Fresh
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Predict Milk Quality", type="primary", use_container_width=True):
        payload = {"cow_id": cow_id, "ph": ph, "temperature": temp,
                   "taste": taste, "odor": odor, "fat": fat,
                   "turbidity": turbid, "colour": colour}
        with st.spinner("Running ML model prediction..."):
            res = api.analyze_milk(token, payload)

        if res.status_code == 200:
            result = res.json()
            grade  = result["quality_grade"]
            score  = result["quality_score"]

            if grade == "Good":
                st.markdown(f"""<div class='result-good'>
                    <div style='font-size:2.5rem'>🟢</div>
                    <div style='font-size:1.5rem;font-weight:700;color:#1b5e20;margin:8px 0'>Good Quality</div>
                    <div style='font-size:1rem;color:#2e7d32'>Confidence: {score*100:.1f}%</div>
                </div>""", unsafe_allow_html=True)
                st.success("Excellent milk quality! Safe for consumption.")
            elif grade == "Average":
                st.markdown(f"""<div class='result-average'>
                    <div style='font-size:2.5rem'>🟡</div>
                    <div style='font-size:1.5rem;font-weight:700;color:#e65100;margin:8px 0'>Average Quality</div>
                    <div style='font-size:1rem;color:#bf360c'>Confidence: {score*100:.1f}%</div>
                </div>""", unsafe_allow_html=True)
                st.warning("Average quality. Consider improving cow diet and hygiene.")
            else:
                st.markdown(f"""<div class='result-poor'>
                    <div style='font-size:2.5rem'>🔴</div>
                    <div style='font-size:1.5rem;font-weight:700;color:#c62828;margin:8px 0'>Poor Quality</div>
                    <div style='font-size:1rem;color:#b71c1c'>Confidence: {score*100:.1f}%</div>
                </div>""", unsafe_allow_html=True)
                st.error("Poor milk quality detected. Check cow health immediately.")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("pH",          ph)
            c2.metric("Temperature", f"{temp}°C")
            c3.metric("Fat",         f"{fat}%")
            c4.metric("Grade",       grade)
        else:
            st.error("Analysis failed. Please try again.")

with tab2:
    st.markdown("#### Select a Cow to View Milk History")
    sel2 = st.selectbox("Cow", list(cow_opts.keys()), key="milk_hist", label_visibility="collapsed")
    cid2 = cow_opts[sel2]
    hr   = api.get_milk_history(token, cid2)

    if hr.status_code == 200:
        records = hr.json()
        if not records:
            st.info("No milk records yet. Run a milk quality analysis first.")
        else:
            st.plotly_chart(milk_trend_line(records), use_container_width=True)
            st.markdown(f"<div style='color:#666;margin-bottom:12px'><b>{len(records)}</b> milk test(s) recorded</div>", unsafe_allow_html=True)
            for r in records:
                grade  = r.get("quality_grade", "")
                icon   = "🟢" if grade == "Good" else ("🟡" if grade == "Average" else "🔴")
                bcolor = "#2e7d32" if grade == "Good" else ("#f9a825" if grade == "Average" else "#c62828")
                date   = r.get("created_at", "")[:10]
                st.markdown(f"""
                <div style='background:white;border-radius:12px;padding:14px 18px;margin:6px 0;
                    border:1px solid #eee;border-left:4px solid {bcolor}'>
                    <div style='display:flex;justify-content:space-between;align-items:center'>
                        <div><span style='font-size:1.1rem'>{icon}</span>
                            <b style='margin-left:8px'>{grade} Quality</b>
                            <span style='color:#888;font-size:0.85rem;margin-left:8px'>Score: {r.get("quality_score",0)*100:.0f}%</span>
                        </div>
                        <div style='color:#888;font-size:0.85rem'>{date}</div>
                    </div>
                    <div style='margin-top:6px;color:#666;font-size:0.85rem'>
                        pH: {r.get("ph","N/A")} &nbsp;|&nbsp;
                        Temp: {r.get("temperature","N/A")}°C &nbsp;|&nbsp;
                        Fat: {r.get("fat","N/A")}%
                    </div>
                </div>""", unsafe_allow_html=True)
