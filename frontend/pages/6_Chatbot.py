import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from frontend.utils.auth_state import require_login, get_token
from frontend.utils import api_client as api

st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")
require_login()
token = get_token()

st.markdown("""<style>
    .user-msg { background:#e3f2fd; border-radius:14px 14px 4px 14px; padding:12px 16px;
        margin:8px 0; max-width:80%; margin-left:auto; text-align:right; }
    .bot-msg  { background:#f1f8e9; border-radius:14px 14px 14px 4px; padding:12px 16px;
        margin:8px 0; max-width:85%; border-left:3px solid #2e7d32; }
    
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
        <h2 style='margin:0; font-size:1.6rem; font-weight:800;'>🤖 AI Farming Assistant</h2>
        <p style='margin:6px 0 0; opacity:0.85; font-size:0.92rem;'>Ask anything about cattle diseases, milk quality, feeding & care — powered by Llama 3</p>
    </div>
    <div style='font-size:3rem; opacity:0.3;'>🤖</div>
</div>
""", unsafe_allow_html=True)

# ── Session state init ────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Helper: send a question to the API ───────────────────────────
def send_question(question: str):
    """Call chatbot API, append result to chat_history, rerun."""
    question = question.strip()
    if not question:
        return
    st.session_state.chat_history.append({"role": "user", "content": question})
    history = [{"role": m["role"], "content": m["content"]}
               for m in st.session_state.chat_history[:-1]]
    with st.spinner("🤖 Thinking..."):
        res = api.ask_chatbot(token, question, history)
    if res.status_code == 200:
        answer = res.json()["answer"]
    else:
        answer = "Sorry, I could not process that. Please try again."
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    st.rerun()

# ── Process quick question IMMEDIATELY (before rendering form) ────
if "pending_question" in st.session_state:
    q = st.session_state.pop("pending_question")
    send_question(q)          # calls st.rerun() internally after API response

# ── Layout ────────────────────────────────────────────────────────
col_chat, col_quick = st.columns([3, 1])

# ── RIGHT: Quick Questions ────────────────────────────────────────
with col_quick:
    st.markdown("#### 💡 Quick Questions")
    st.markdown(
        "<div style='color:#888;font-size:0.82rem;margin-bottom:10px'>"
        "Click any question to ask instantly</div>",
        unsafe_allow_html=True
    )

    quick_questions = [
        "What is Lumpy Skin Disease?",
        "How to improve milk quality?",
        "Signs of Foot and Mouth Disease?",
        "Best feed for dairy cows?",
        "How to prevent mastitis?",
        "Ideal milk pH range?",
        "How to increase milk fat content?",
        "What causes low milk production?",
    ]

    for q in quick_questions:
        if st.button(q, use_container_width=True, key=f"quick_{q}"):
            st.session_state.pending_question = q
            st.rerun()   # rerun → pending_question processed at top

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()

# ── LEFT: Chat window ─────────────────────────────────────────────
with col_chat:

    # Chat history display
    chat_box = st.container(height=460)
    with chat_box:
        if not st.session_state.chat_history:
            st.markdown("""<div class='bot-msg'>
                <b>🤖 Assistant</b><br><br>
                Hello! I'm your AI dairy farming expert. I can help you with:<br><br>
                🐄 Cattle diseases &amp; treatments<br>
                🥛 Milk quality improvement<br>
                🌾 Feeding &amp; nutrition plans<br>
                💊 Preventive healthcare<br><br>
                <i>Type a question below or click any Quick Question on the right →</i>
            </div>""", unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"""<div class='user-msg'>
                    <div style='font-weight:600;color:#1565c0;margin-bottom:4px'>You</div>
                    {msg['content']}
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class='bot-msg'>
                    <div style='font-weight:600;color:#1b5e20;margin-bottom:4px'>🤖 Assistant</div>
                    {msg['content']}
                </div>""", unsafe_allow_html=True)

    # Text input form for manual questions
    with st.form("chat_form", clear_on_submit=True):
        question = st.text_input(
            "Type your question...",
            placeholder="e.g. How to increase milk fat content?",
            label_visibility="collapsed"
        )
        submitted = st.form_submit_button("📨 Send Message", use_container_width=True)

    if submitted and question.strip():
        send_question(question)
