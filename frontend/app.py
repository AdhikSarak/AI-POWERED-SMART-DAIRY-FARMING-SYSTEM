import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from frontend.utils.auth_state import init_session, is_logged_in, get_user, login, logout
from frontend.utils import api_client as api

st.set_page_config(
    page_title="Smart Dairy Farm — AI-Powered Cattle Management",
    page_icon="🐄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #14532d 0%, #166534 50%, #15803d 100%);
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15); }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    color: white !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.25) !important;
}

/* ── Global Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #16a34a, #15803d);
    color: white; border-radius: 10px; border: none;
    font-weight: 600; padding: 0.55rem 1.5rem;
    transition: all 0.2s ease;
    box-shadow: 0 2px 8px rgba(22,163,74,0.35);
}
.stButton > button:hover {
    background: linear-gradient(135deg, #15803d, #14532d);
    box-shadow: 0 4px 16px rgba(22,163,74,0.45);
    transform: translateY(-1px);
}

/* ── Metric containers ── */
div[data-testid="metric-container"] {
    background: white; padding: 16px; border-radius: 14px;
    border: 1px solid #dcfce7; box-shadow: 0 2px 10px rgba(0,0,0,0.06);
}

/* ── Cards ── */
.card {
    background: white; border-radius: 14px; padding: 20px;
    border: 1px solid #e5e7eb; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 12px; transition: box-shadow 0.2s;
}
.card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.1); }
.card-green  { border-left: 5px solid #16a34a; }
.card-yellow { border-left: 5px solid #d97706; }
.card-red    { border-left: 5px solid #dc2626; }
.card-blue   { border-left: 5px solid #2563eb; }

/* ── Page header ── */
.page-header {
    background: linear-gradient(135deg, #f0fdf4, #dcfce7);
    border-radius: 16px; padding: 22px 28px; margin-bottom: 24px;
    border-left: 5px solid #16a34a;
}
.page-header h2 { margin: 0; color: #14532d; font-size: 1.6rem; font-weight: 700; }
.page-header p  { margin: 6px 0 0; color: #4b5563; font-size: 0.95rem; }

/* ── Status badges ── */
.badge-good    { background:#dcfce7; color:#14532d; padding:4px 12px; border-radius:20px; font-weight:600; font-size:0.82rem; }
.badge-average { background:#fef3c7; color:#92400e; padding:4px 12px; border-radius:20px; font-weight:600; font-size:0.82rem; }
.badge-poor    { background:#fee2e2; color:#991b1b; padding:4px 12px; border-radius:20px; font-weight:600; font-size:0.82rem; }
.badge-healthy { background:#dcfce7; color:#14532d; padding:4px 12px; border-radius:20px; font-weight:600; font-size:0.82rem; }
.badge-disease { background:#fee2e2; color:#991b1b; padding:4px 12px; border-radius:20px; font-weight:600; font-size:0.82rem; }

/* ── Inputs ── */
.stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div {
    border-radius: 8px;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background:#f0fdf4; border-radius:10px; padding:4px; }
.stTabs [data-baseweb="tab"] { border-radius:8px; font-weight:500; }
.stTabs [aria-selected="true"] { background:white; color:#16a34a; font-weight:600; }

/* ── Hide Streamlit chrome ── */
#MainMenu { visibility:hidden; }
footer    { visibility:hidden; }

/* ── Landing page specific ── */
.hero-section {
    background: linear-gradient(135deg, #14532d 0%, #166534 40%, #16a34a 100%);
    border-radius: 20px; padding: 60px 48px; margin-bottom: 0;
    color: white; position: relative; overflow: hidden;
}
.hero-section::before {
    content: '';
    position: absolute; top: -50px; right: -50px;
    width: 300px; height: 300px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.hero-section::after {
    content: '';
    position: absolute; bottom: -80px; right: 100px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.stat-card {
    background: white; border-radius: 16px; padding: 24px 20px;
    text-align: center; border: 1px solid #dcfce7;
    box-shadow: 0 4px 16px rgba(0,0,0,0.07);
    transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
.stat-card .num  { font-size: 2.4rem; font-weight: 800; color: #16a34a; line-height: 1; }
.stat-card .lbl  { font-size: 0.88rem; color: #6b7280; margin-top: 6px; font-weight: 500; }
.feature-card {
    background: white; border-radius: 16px; padding: 28px 24px;
    border: 1px solid #e5e7eb; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    height: 100%; transition: all 0.2s;
}
.feature-card:hover {
    border-color: #86efac; box-shadow: 0 8px 24px rgba(22,163,74,0.15);
    transform: translateY(-2px);
}
.feature-icon {
    width: 56px; height: 56px; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.6rem; margin-bottom: 16px;
}
.step-card {
    background: white; border-radius: 16px; padding: 28px 20px;
    text-align: center; border: 2px dashed #bbf7d0;
    position: relative;
}
.step-num {
    width: 42px; height: 42px; background: #16a34a;
    border-radius: 50%; display: flex; align-items: center;
    justify-content: center; color: white; font-weight: 700;
    font-size: 1.1rem; margin: 0 auto 14px;
}
.login-card {
    background: white; border-radius: 20px; padding: 40px 36px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.1); border: 1px solid #dcfce7;
}
.footer-bar {
    background: #14532d; border-radius: 16px; padding: 32px 40px;
    color: white; margin-top: 40px;
}
</style>
""", unsafe_allow_html=True)

init_session()


# ════════════════════════════════════════════════════════════════
# LANDING PAGE  (shown when user is NOT logged in)
# ════════════════════════════════════════════════════════════════
def show_landing():

    # ── NAVBAR ─────────────────────────────────────────────────
    # NOTE: Use 100% inline styles only. No class attributes, no JS.
    _NL = "display:flex;align-items:center;gap:6px;padding:10px 15px;border-right:1px solid #f0f0f0;white-space:nowrap;"
    _LBL = "font-size:0.82rem;font-weight:600;color:#374151;"
    _BADGE = "font-size:0.65rem;font-weight:700;padding:1px 7px;border-radius:10px;margin-left:3px;"
    st.markdown(
        "<div style='background:white;border-radius:16px;box-shadow:0 2px 16px rgba(0,0,0,0.08);margin-bottom:24px;border-bottom:3px solid #16a34a;overflow:hidden;'>"

        # ── top row ──
        "<div style='display:flex;align-items:center;justify-content:space-between;padding:13px 26px;border-bottom:1px solid #f3f4f6;'>"
            "<div style='display:flex;align-items:center;gap:12px;'>"
                "<div style='background:linear-gradient(135deg,#14532d,#16a34a);width:42px;height:42px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:1.4rem;'>🐄</div>"
                "<div>"
                    "<div style='font-weight:800;font-size:1.1rem;color:#14532d;line-height:1.1;'>Smart Dairy Farm</div>"
                    "<div style='font-size:0.7rem;color:#6b7280;font-weight:500;margin-top:2px;'>AI-Powered Cattle Management System</div>"
                "</div>"
            "</div>"
            "<div style='display:flex;align-items:center;gap:10px;'>"
                "<div style='background:#f0fdf4;border:1px solid #bbf7d0;padding:5px 13px;border-radius:20px;font-size:0.78rem;color:#15803d;font-weight:600;'>🟢 System Online</div>"
                "<div style='background:linear-gradient(135deg,#16a34a,#15803d);color:white;padding:9px 20px;border-radius:10px;font-weight:700;font-size:0.88rem;box-shadow:0 3px 10px rgba(22,163,74,0.35);'>Login / Register</div>"
            "</div>"
        "</div>"

        # ── feature links row ──
        "<div style='display:flex;align-items:center;background:#fafafa;padding:0 8px;overflow-x:auto;'>"
            "<div style='" + _NL + "'><span style='font-size:1rem;'>🐄</span><span style='" + _LBL + "'>Cow Management</span></div>"
            "<div style='" + _NL + "background:#f0fdf4;'><span style='font-size:1rem;'>🏥</span><span style='font-size:0.82rem;font-weight:600;color:#15803d;'>Disease Detection</span><span style='" + _BADGE + "background:#dcfce7;color:#15803d;'>93.8% AI</span></div>"
            "<div style='" + _NL + "'><span style='font-size:1rem;'>🥛</span><span style='" + _LBL + "'>Milk Quality</span><span style='" + _BADGE + "background:#dbeafe;color:#1d4ed8;'>98.5% ML</span></div>"
            "<div style='" + _NL + "'><span style='font-size:1rem;'>💡</span><span style='" + _LBL + "'>AI Recommendations</span></div>"
            "<div style='" + _NL + "'><span style='font-size:1rem;'>🤖</span><span style='" + _LBL + "'>AI Chatbot</span><span style='" + _BADGE + "background:#f3e8ff;color:#7e22ce;'>Llama 3</span></div>"
            "<div style='" + _NL + "'><span style='font-size:1rem;'>🔍</span><span style='" + _LBL + "'>Agentic Analysis</span></div>"
            "<div style='" + _NL + "'><span style='font-size:1rem;'>📋</span><span style='" + _LBL + "'>Reports &amp; History</span></div>"
            "<div style='display:flex;align-items:center;gap:6px;padding:10px 15px;white-space:nowrap;'><span style='font-size:1rem;'>🧾</span><span style='" + _LBL + "'>Billing &amp; Admin</span></div>"
        "</div>"

        "</div>",
        unsafe_allow_html=True
    )

    # ── HERO SECTION ───────────────────────────────────────────
    col_hero, col_img = st.columns([1.1, 0.9])

    with col_hero:
        st.markdown("""
        <div class='hero-section'>
            <div style='display:inline-block; background:rgba(255,255,255,0.15);
                padding:6px 14px; border-radius:20px; font-size:0.82rem;
                font-weight:600; margin-bottom:20px; letter-spacing:0.5px;'>
                🇮🇳 Made for Indian Dairy Farmers
            </div>
            <h1 style='font-size:2.8rem; font-weight:800; margin:0 0 16px;
                line-height:1.2; color:white;'>
                Smart Dairy Farm<br>
                <span style='color:#86efac;'>Management System</span>
            </h1>
            <p style='font-size:1.05rem; color:rgba(255,255,255,0.88);
                margin-bottom:28px; line-height:1.7; max-width:480px;'>
                AI-powered cattle health monitoring, milk quality analysis,
                and automated billing — all in one platform designed for
                modern Indian dairy farms.
            </p>
            <div style='display:flex; gap:12px; flex-wrap:wrap; margin-bottom:36px;'>
                <span style='background:white; color:#16a34a; padding:11px 24px;
                    border-radius:10px; font-weight:700; font-size:0.95rem;
                    box-shadow:0 4px 12px rgba(0,0,0,0.15);'>
                    ✅ Get Started Free
                </span>
                <span style='background:rgba(255,255,255,0.15); color:white;
                    padding:11px 24px; border-radius:10px; font-weight:600;
                    font-size:0.95rem; border:1.5px solid rgba(255,255,255,0.4);'>
                    📖 View Demo
                </span>
            </div>
            <div style='display:flex; gap:28px; flex-wrap:wrap;'>
                <div style='color:rgba(255,255,255,0.9);'>
                    <span style='font-size:1.4rem; font-weight:800;'>93.8%</span>
                    <span style='font-size:0.8rem; margin-left:6px;'>Disease Accuracy</span>
                </div>
                <div style='color:rgba(255,255,255,0.9);'>
                    <span style='font-size:1.4rem; font-weight:800;'>98.5%</span>
                    <span style='font-size:0.8rem; margin-left:6px;'>Milk Quality Accuracy</span>
                </div>
                <div style='color:rgba(255,255,255,0.9);'>
                    <span style='font-size:1.4rem; font-weight:800;'>24/7</span>
                    <span style='font-size:0.8rem; margin-left:6px;'>AI Assistant</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_img:
        st.markdown("""
        <div style='border-radius:20px; overflow:hidden; height:100%;
            box-shadow:0 16px 48px rgba(0,0,0,0.18); position:relative;'>
            <img src='https://images.unsplash.com/photo-1500595046743-cd271d694d30?w=700&q=80&fit=crop'
                 style='width:100%; height:420px; object-fit:cover; display:block;'
                 alt='Dairy Cows on Farm'/>
            <div style='position:absolute; bottom:0; left:0; right:0;
                background:linear-gradient(transparent, rgba(20,83,45,0.85));
                padding:24px 20px;'>
                <div style='color:white; font-weight:700; font-size:1rem;'>
                    🐄 AI-Powered Cattle Health Detection
                </div>
                <div style='color:rgba(255,255,255,0.8); font-size:0.85rem; margin-top:4px;'>
                    Upload a photo — get disease diagnosis in seconds
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── STATS BAR ──────────────────────────────────────────────
    st.markdown("""
    <div style='text-align:center; margin:8px 0 20px;'>
        <span style='background:#dcfce7; color:#14532d; padding:6px 16px;
            border-radius:20px; font-weight:600; font-size:0.85rem;'>
            📊 Platform Results
        </span>
    </div>
    """, unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    stats = [
        ("93.8%", "Disease Detection Accuracy", "🏥"),
        ("98.5%", "Milk Quality Accuracy",       "🥛"),
        ("6+",    "AI Features Built-in",         "🤖"),
        ("5",     "Cattle Breeds Supported",       "🐄"),
    ]
    for col, (num, lbl, icon) in zip([s1,s2,s3,s4], stats):
        with col:
            st.markdown(f"""
            <div class='stat-card'>
                <div style='font-size:1.6rem; margin-bottom:6px;'>{icon}</div>
                <div class='num'>{num}</div>
                <div class='lbl'>{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── FEATURES SECTION ───────────────────────────────────────
    st.markdown("""
    <div style='text-align:center; margin-bottom:32px;'>
        <h2 style='font-size:2rem; font-weight:800; color:#111827; margin-bottom:10px;'>
            Everything Your Dairy Farm Needs
        </h2>
        <p style='color:#6b7280; font-size:1rem; max-width:540px; margin:0 auto;'>
            One platform combining AI, machine learning, and smart management
            tools designed specifically for Indian dairy farmers.
        </p>
    </div>
    """, unsafe_allow_html=True)

    features = [
        ("#dcfce7", "#16a34a", "🏥", "Disease Detection",
         "Upload a cow photograph — our EfficientNetV2B0 AI model detects Lumpy Skin, FMD, and Bovine diseases with 93.8% accuracy in under 200ms."),
        ("#dbeafe", "#2563eb", "🥛", "Milk Quality Analysis",
         "Enter 7 sensor readings (pH, fat, temperature...) and get instant Good/Average/Poor quality grading with 98.5% accuracy via Random Forest ML."),
        ("#fef3c7", "#d97706", "🤖", "AI Chatbot Assistant",
         "Ask any dairy farming question 24/7. Powered by Llama 3 (Groq), the chatbot gives expert advice on diseases, feeding, and prevention."),
        ("#f3e8ff", "#9333ea", "💡", "Smart Recommendations",
         "AI reads your cow's full health and milk history, then generates personalized feeding, medication, and preventive care plans for each cow."),
        ("#ffe4e6", "#e11d48", "📊", "Reports & Dashboard",
         "Real-time farm dashboard with Plotly charts, full cow health/milk/recommendation history, and exportable reports — all from live database."),
        ("#ecfdf5", "#059669", "🧾", "Billing & Collections",
         "Admin records daily milk collections, and the system auto-generates monthly PDF bills with total liters and amount — no manual calculation needed."),
    ]

    row1 = st.columns(3)
    row2 = st.columns(3)

    for i, (bg, accent, icon, title, desc) in enumerate(features):
        col = row1[i] if i < 3 else row2[i-3]
        with col:
            st.markdown(f"""
            <div class='feature-card'>
                <div class='feature-icon' style='background:{bg};'>
                    {icon}
                </div>
                <h3 style='font-size:1.05rem; font-weight:700; color:#111827;
                    margin:0 0 10px;'>{title}</h3>
                <p style='font-size:0.88rem; color:#6b7280; line-height:1.65;
                    margin:0;'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── HOW IT WORKS ───────────────────────────────────────────
    st.markdown("""
    <div style='background:linear-gradient(135deg,#f0fdf4,#dcfce7);
        border-radius:20px; padding:40px 32px; margin-bottom:32px;'>
        <div style='text-align:center; margin-bottom:32px;'>
            <h2 style='font-size:1.8rem; font-weight:800; color:#14532d; margin:0 0 10px;'>
                How It Works
            </h2>
            <p style='color:#4b5563; font-size:0.95rem;'>
                Get your farm AI-powered in 3 simple steps
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    steps = [
        ("1", "📋", "Register & Add Cows",
         "Create your farmer account and add your cows with name, breed, age and weight. Each cow gets a unique ID for tracking."),
        ("2", "📸", "Analyze Health & Milk",
         "Upload cow photos for instant disease detection. Enter milk sensor readings for quality grading. AI gives results in seconds."),
        ("3", "💡", "Get AI Insights",
         "Receive personalized feeding recommendations, ask the chatbot, view reports, and let the admin generate your monthly payment bill."),
    ]
    for col, (num, icon, title, desc) in zip([c1,c2,c3], steps):
        with col:
            st.markdown(f"""
            <div class='step-card'>
                <div class='step-num'>{num}</div>
                <div style='font-size:2rem; margin-bottom:10px;'>{icon}</div>
                <h3 style='font-size:1rem; font-weight:700; color:#14532d;
                    margin:0 0 10px;'>{title}</h3>
                <p style='font-size:0.88rem; color:#4b5563; line-height:1.65; margin:0;'>
                    {desc}
                </p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── FARMER IMAGE STRIP ─────────────────────────────────────
    img1, img2, img3 = st.columns(3)
    images = [
        ("https://images.unsplash.com/photo-1589923188900-85dae523342b?w=500&q=80&fit=crop",
         "🐄 Cattle Health Monitoring", "AI-powered disease detection"),
        ("https://images.unsplash.com/photo-1563298723-dcfebaa392e3?w=500&q=80&fit=crop",
         "🥛 Milk Quality Testing", "Instant sensor-based grading"),
        ("https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?w=500&q=80&fit=crop",
         "👨‍🌾 Farm Management", "Complete dairy farm platform"),
    ]
    for col, (url, title, sub) in zip([img1,img2,img3], images):
        with col:
            st.markdown(f"""
            <div style='border-radius:16px; overflow:hidden;
                box-shadow:0 8px 24px rgba(0,0,0,0.12); position:relative;'>
                <img src='{url}'
                     style='width:100%; height:220px; object-fit:cover; display:block;'/>
                <div style='position:absolute; bottom:0; left:0; right:0;
                    background:linear-gradient(transparent, rgba(20,83,45,0.9));
                    padding:16px 14px;'>
                    <div style='color:white; font-weight:700; font-size:0.95rem;'>{title}</div>
                    <div style='color:rgba(255,255,255,0.8); font-size:0.8rem; margin-top:2px;'>{sub}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── LOGIN / REGISTER SECTION ────────────────────────────────
    st.markdown("""
    <div style='text-align:center; margin-bottom:24px;'>
        <h2 style='font-size:1.8rem; font-weight:800; color:#111827; margin-bottom:8px;'>
            Start Managing Your Farm Today
        </h2>
        <p style='color:#6b7280; font-size:0.95rem;'>
            Login to your account or create a new one — it's free
        </p>
    </div>
    """, unsafe_allow_html=True)

    _, col_form, _ = st.columns([1, 1.4, 1])
    with col_form:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs(["  🔑 Login  ", "  ✨ Create Account  "])

        with tab_login:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("login_form"):
                email    = st.text_input("📧 Email Address", placeholder="you@example.com")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Login to Dashboard →", use_container_width=True)
            if submit:
                if not email or not password:
                    st.warning("Please enter your email and password.")
                else:
                    res = api.login(email, password)
                    if res.status_code == 200:
                        data = res.json()
                        login(data["access_token"], data["user"])
                        st.success(f"✅ Welcome back, {data['user']['name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Incorrect email or password. Please try again.")

            st.markdown("""
            <div style='text-align:center; margin-top:16px; padding:12px;
                background:#f0fdf4; border-radius:10px;'>
                <div style='font-size:0.82rem; color:#4b5563; font-weight:500;'>
                    Demo Accounts
                </div>
                <div style='font-size:0.8rem; color:#6b7280; margin-top:4px;'>
                    🌾 <b>Farmer:</b> somnathtk198@gmail.com / Soma@123<br>
                    ⚙️ <b>Admin:</b> admin@dairyfarm.com / Admin@123
                </div>
            </div>
            """, unsafe_allow_html=True)

        with tab_reg:
            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("reg_form"):
                name     = st.text_input("👤 Full Name", placeholder="e.g. Ramesh Kumar")
                email_r  = st.text_input("📧 Email Address", placeholder="you@example.com", key="reg_email")
                phone    = st.text_input("📱 Phone Number", placeholder="e.g. 9876543210")
                password_r = st.text_input("🔒 Password", type="password",
                                           placeholder="Min 6 characters", key="reg_pass")
                role     = st.selectbox("👔 Account Type", ["farmer", "admin"],
                                        format_func=lambda x: "🌾 Farmer" if x=="farmer" else "⚙️ Admin")
                st.markdown("<br>", unsafe_allow_html=True)
                submit_r = st.form_submit_button("Create My Account →", use_container_width=True)
            if submit_r:
                if not name or not email_r or not password_r:
                    st.warning("Please fill in all required fields.")
                elif len(password_r) < 6:
                    st.warning("Password must be at least 6 characters.")
                else:
                    res = api.register(name, email_r, phone, password_r, role)
                    if res.status_code == 201:
                        st.success("🎉 Account created successfully! Please login.")
                    else:
                        st.error(res.json().get("detail", "Registration failed. Email may already exist."))

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── FOOTER ─────────────────────────────────────────────────
    st.markdown("""
    <div class='footer-bar'>
        <div style='display:flex; justify-content:space-between; align-items:center;
            flex-wrap:wrap; gap:20px;'>
            <div>
                <div style='display:flex; align-items:center; gap:10px; margin-bottom:8px;'>
                    <span style='font-size:1.8rem;'>🐄</span>
                    <span style='font-weight:800; font-size:1.1rem;'>Smart Dairy Farm</span>
                </div>
                <div style='color:rgba(255,255,255,0.7); font-size:0.85rem; max-width:340px;'>
                    AI-powered cattle health monitoring & milk quality management
                    platform built for Indian dairy farmers.
                </div>
            </div>
            <div style='display:flex; gap:40px; flex-wrap:wrap;'>
                <div>
                    <div style='font-weight:700; margin-bottom:10px; font-size:0.9rem;'>Features</div>
                    <div style='color:rgba(255,255,255,0.7); font-size:0.83rem; line-height:2;'>
                        🏥 Disease Detection<br>
                        🥛 Milk Quality<br>
                        🤖 AI Chatbot<br>
                        💡 Recommendations
                    </div>
                </div>
                <div>
                    <div style='font-weight:700; margin-bottom:10px; font-size:0.9rem;'>Technology</div>
                    <div style='color:rgba(255,255,255,0.7); font-size:0.83rem; line-height:2;'>
                        🧠 EfficientNetV2B0<br>
                        🌲 Random Forest<br>
                        ⚡ FastAPI Backend<br>
                        🗄️ PostgreSQL DB
                    </div>
                </div>
                <div>
                    <div style='font-weight:700; margin-bottom:10px; font-size:0.9rem;'>Results</div>
                    <div style='color:rgba(255,255,255,0.7); font-size:0.83rem; line-height:2;'>
                        93.8% Disease F1<br>
                        98.5% Milk Accuracy<br>
                        24/7 AI Assistant<br>
                        Zero Hardcoded Data
                    </div>
                </div>
            </div>
        </div>
        <div style='border-top:1px solid rgba(255,255,255,0.15);
            margin-top:24px; padding-top:16px; text-align:center;
            color:rgba(255,255,255,0.55); font-size:0.82rem;'>
            © 2026 Smart Dairy Farm System &nbsp;·&nbsp;
            Final Year AI/ML Project &nbsp;·&nbsp;
            Built with FastAPI · TensorFlow · Streamlit · PostgreSQL · Groq LLM
        </div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# LOGGED-IN HOME PAGE
# ════════════════════════════════════════════════════════════════
def show_sidebar():
    user = get_user()
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:12px 0 20px; text-align:center;'>
            <div style='font-size:3rem;'>🐄</div>
            <div style='font-weight:800; font-size:1.05rem; margin-top:6px;'>
                Smart Dairy Farm
            </div>
            <div style='margin-top:8px; display:inline-block;
                background:rgba(255,255,255,0.2); padding:3px 12px;
                border-radius:20px; font-size:0.8rem;'>
                {user.get('name','User')}
            </div>
            <div style='margin-top:4px; display:inline-block;
                background:rgba(255,255,255,0.15); padding:2px 10px;
                border-radius:20px; font-size:0.72rem;'>
                {user.get('role','farmer').upper()}
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        st.markdown("<div style='font-size:0.72rem; opacity:0.65; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:10px; padding:0 4px;'>Main Menu</div>", unsafe_allow_html=True)
        st.page_link("pages/1_Dashboard.py",        label="Dashboard",          icon="📊")
        st.page_link("pages/2_Cow_Management.py",   label="My Cows",            icon="🐄")
        st.page_link("pages/3_Health_Analysis.py",  label="Health Analysis",    icon="🏥")
        st.page_link("pages/4_Milk_Quality.py",     label="Milk Quality",       icon="🥛")
        st.page_link("pages/5_Recommendations.py",  label="AI Recommendations", icon="💡")
        st.page_link("pages/6_Chatbot.py",          label="AI Chatbot",         icon="🤖")
        st.page_link("pages/7_Reports_History.py",  label="Reports & History",  icon="📋")

        if user.get("role") == "admin":
            st.divider()
            st.markdown("<div style='font-size:0.72rem; opacity:0.65; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:10px; padding:0 4px;'>Admin</div>", unsafe_allow_html=True)
            st.page_link("pages/8_Admin_Panel.py", label="Admin Panel", icon="⚙️")

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
        st.markdown("""
        <div style='text-align:center; margin-top:12px; color:rgba(255,255,255,0.45);
            font-size:0.72rem;'>Smart Dairy Farm v1.0</div>
        """, unsafe_allow_html=True)


def show_home():
    user = get_user()

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#14532d,#16a34a);
        border-radius:18px; padding:28px 32px; margin-bottom:28px; color:white;
        display:flex; align-items:center; justify-content:space-between;'>
        <div>
            <div style='font-size:0.85rem; opacity:0.8; margin-bottom:6px;'>
                Welcome back 👋
            </div>
            <h2 style='margin:0; font-size:1.7rem; font-weight:800;'>
                {user.get('name','Farmer')}
            </h2>
            <p style='margin:6px 0 0; opacity:0.85; font-size:0.92rem;'>
                Smart Dairy Farming System — AI-powered cattle health & milk quality
            </p>
        </div>
        <div style='font-size:4rem; opacity:0.4;'>🐄</div>
    </div>
    """, unsafe_allow_html=True)

    # Quick action cards
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("🏥", "#dbeafe", "#2563eb", "Health Check",     "Detect diseases from cow photos using AI"),
        ("🥛", "#dcfce7", "#16a34a", "Milk Quality",     "Grade milk quality from sensor data"),
        ("💡", "#fef3c7", "#d97706", "AI Recommendations","Get personalized care advice per cow"),
        ("🤖", "#f3e8ff", "#9333ea", "AI Chatbot",       "Ask any dairy farming question"),
    ]
    for col, (icon, bg, accent, title, desc) in zip([c1,c2,c3,c4], cards):
        with col:
            st.markdown(f"""
            <div style='background:white; border-radius:16px; padding:22px 18px;
                border:1px solid {bg}; box-shadow:0 2px 12px rgba(0,0,0,0.06);
                border-top:4px solid {accent}; margin-bottom:8px;'>
                <div style='background:{bg}; width:44px; height:44px; border-radius:12px;
                    display:flex; align-items:center; justify-content:center;
                    font-size:1.4rem; margin-bottom:12px;'>{icon}</div>
                <div style='font-weight:700; color:#111827; margin-bottom:6px;'>{title}</div>
                <div style='font-size:0.83rem; color:#6b7280; line-height:1.5;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Navigation hint
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#f0fdf4,#dcfce7);
            border-radius:14px; padding:20px 22px; border:1px solid #bbf7d0;'>
            <div style='font-weight:700; color:#14532d; font-size:1rem; margin-bottom:8px;'>
                📌 Quick Start Guide
            </div>
            <div style='font-size:0.88rem; color:#374151; line-height:2;'>
                1. Go to <b>My Cows</b> → Add your cows<br>
                2. Go to <b>Health Analysis</b> → Upload cow photo<br>
                3. Go to <b>Milk Quality</b> → Enter sensor readings<br>
                4. Go to <b>Recommendations</b> → Get AI advice<br>
                5. Go to <b>AI Chatbot</b> → Ask any question
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_r:
        st.markdown("""
        <div style='background:linear-gradient(135deg,#eff6ff,#dbeafe);
            border-radius:14px; padding:20px 22px; border:1px solid #bfdbfe;'>
            <div style='font-weight:700; color:#1e3a8a; font-size:1rem; margin-bottom:8px;'>
                🧠 AI Models Ready
            </div>
            <div style='font-size:0.88rem; color:#374151; line-height:2;'>
                🏥 <b>Disease Detection:</b> 93.8% accuracy<br>
                🥛 <b>Milk Quality:</b> 98.5% accuracy<br>
                🤖 <b>Chatbot:</b> Llama 3.1 (Groq)<br>
                💡 <b>Recommendations:</b> Llama 3.3 70B<br>
                🔍 <b>Deep Analysis:</b> Agentic AI
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center; margin-top:20px;
        color:#9ca3af; font-size:0.82rem;'>
        👈 Use the sidebar to navigate between all features
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ════════════════════════════════════════════════════════════════
if not is_logged_in():
    show_landing()
else:
    show_sidebar()
    show_home()
