import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from frontend.utils.auth_state import require_login, get_token
from frontend.utils import api_client as api
from frontend.utils.charts import disease_donut

st.set_page_config(page_title="Health Check", page_icon="🏥", layout="wide")
require_login()
token = get_token()

st.markdown("""<style>
    .result-box { border-radius:14px; padding:24px; text-align:center; margin:16px 0; }
    .result-healthy { background:#e8f5e9; border:2px solid #2e7d32; }
    .result-diseased { background:#ffebee; border:2px solid #c62828; }
    
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
        <h2 style='margin:0; font-size:1.6rem; font-weight:800;'>🏥 Cattle Health Check</h2>
        <p style='margin:6px 0 0; opacity:0.85; font-size:0.92rem;'>Upload a cow photo to detect diseases using EfficientNetV2B0 AI (93.8% accuracy)</p>
    </div>
    <div style='font-size:3rem; opacity:0.3;'>🏥</div>
</div>
""", unsafe_allow_html=True)

cows_res = api.get_cows(token)
if cows_res.status_code != 200 or not cows_res.json():
    st.warning("No cows found. Please add cows first from the 'My Cows' page.")
    st.stop()

cows     = cows_res.json()
cow_opts = {f"{c['name']} ({c['cow_uid']})": c["id"] for c in cows}

tab1, tab2 = st.tabs(["  Analyze Health  ", "  Health History  "])

with tab1:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Step 1 — Select Cow")
        selected = st.selectbox("Choose a cow", list(cow_opts.keys()), label_visibility="collapsed")
        cow_id   = cow_opts[selected]

        st.markdown("#### Step 2 — Upload Photo")
        st.markdown("<div style='color:#666;font-size:0.88rem;margin-bottom:8px'>Upload a clear photo of the cow (JPG or PNG)</div>", unsafe_allow_html=True)
        image = st.file_uploader("Upload", type=["jpg","jpeg","png"], label_visibility="collapsed")
        if image:
            st.image(image, caption=f"Photo of {selected.split('(')[0].strip()}", use_column_width=True)

    with col2:
        st.markdown("#### Step 3 — Run Analysis")
        if not image:
            st.markdown("""
            <div style='background:#f9f9f9;border-radius:12px;padding:40px 20px;text-align:center;
                border:2px dashed #ccc;margin-top:8px'>
                <div style='font-size:2.5rem'>📷</div>
                <div style='color:#888;margin-top:8px'>Upload a photo on the left to get started</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Detect Disease", type="primary", use_container_width=True):
                with st.spinner("AI is analyzing the image..."):
                    res = api.analyze_health(token, cow_id, image.getvalue(), image.name)

                if res.status_code == 200:
                    result = res.json()
                    status = result["health_status"]

                    if status == "Healthy":
                        st.markdown("""<div class='result-box result-healthy'>
                            <div style='font-size:2.5rem'>✅</div>
                            <div style='font-size:1.3rem;font-weight:700;color:#1b5e20;margin:8px 0'>Healthy</div>
                            <div style='color:#2e7d32'>No disease detected</div>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div class='result-box result-diseased'>
                            <div style='font-size:2.5rem'>⚠️</div>
                            <div style='font-size:1.3rem;font-weight:700;color:#c62828;margin:8px 0'>Disease Detected</div>
                            <div style='color:#b71c1c;font-weight:600'>{result["disease_name"]}</div>
                        </div>""", unsafe_allow_html=True)
                        st.error("Please consult a veterinarian immediately.")

                    c1, c2 = st.columns(2)
                    c1.metric("Disease", result["disease_name"])
                    c2.metric("Confidence", f"{result['confidence_score']*100:.1f}%")

                    if result.get("all_predictions"):
                        st.markdown("#### Prediction Breakdown")
                        st.plotly_chart(disease_donut(result["all_predictions"]), use_container_width=True)
                else:
                    st.error("Analysis failed. Please try again with a clearer image.")

with tab2:
    st.markdown("#### Select a Cow to View History")
    selected2 = st.selectbox("Cow", list(cow_opts.keys()), key="hist_cow", label_visibility="collapsed")
    cow_id2   = cow_opts[selected2]
    hist_res  = api.get_health_history(token, cow_id2)

    if hist_res.status_code == 200:
        records = hist_res.json()
        if not records:
            st.info("No health records for this cow yet. Run a health check first.")
        else:
            st.markdown(f"<div style='color:#666;margin-bottom:12px'><b>{len(records)}</b> health record(s) found</div>", unsafe_allow_html=True)
            for r in records:
                icon = "🟢" if r["health_status"] == "Healthy" else "🔴"
                color = "#e8f5e9" if r["health_status"] == "Healthy" else "#ffebee"
                bcolor = "#2e7d32" if r["health_status"] == "Healthy" else "#c62828"
                st.markdown(f"""
                <div style='background:white;border-radius:12px;padding:16px;margin:8px 0;
                    border:1px solid #eee;border-left:4px solid {bcolor}'>
                    <div style='display:flex;justify-content:space-between;align-items:center'>
                        <div>
                            <span style='font-size:1.2rem'>{icon}</span>
                            <b style='margin-left:8px;font-size:1rem'>{r["disease_name"]}</b>
                        </div>
                        <div style='color:#888;font-size:0.85rem'>{r["created_at"][:10]}</div>
                    </div>
                    <div style='margin-top:8px;color:#666;font-size:0.9rem'>
                        Status: <b>{r["health_status"]}</b> &nbsp;|&nbsp;
                        Confidence: <b>{r["confidence_score"]*100:.1f}%</b>
                    </div>
                </div>""", unsafe_allow_html=True)
