import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from frontend.utils.auth_state import require_login, get_token
from frontend.utils import api_client as api

st.set_page_config(page_title="My Cows", page_icon="🐄", layout="wide")
require_login()
token = get_token()

st.markdown("""
<style>
    .cow-card { background:white; border-radius:14px; padding:20px;
        border:1px solid #e8f5e9; box-shadow:0 2px 10px rgba(0,0,0,0.06); margin-bottom:14px; }
    .cow-card h3 { margin:0 0 4px; color:#1b5e20; font-size:1.15rem; }
    .cow-uid { background:#e8f5e9; color:#2e7d32; padding:3px 10px;
        border-radius:20px; font-size:0.8rem; font-weight:600; display:inline-block; margin-bottom:12px; }
    .info-row { display:flex; gap:24px; flex-wrap:wrap; margin-top:10px; }
    .info-item { text-align:center; }
    .info-item .val { font-weight:700; font-size:1.1rem; color:#1b5e20; }
    .info-item .lbl { font-size:0.78rem; color:#888; }
    
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#14532d,#166534,#15803d); }
    [data-testid="stSidebar"] * { color:white !important; }
    [data-testid="stSidebar"] hr { border-color:rgba(255,255,255,0.15); }
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    #MainMenu{visibility:hidden} footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='background:linear-gradient(135deg,#14532d,#16a34a);
     border-radius:16px; padding:24px 28px; margin-bottom:24px; color:white;
     display:flex; align-items:center; justify-content:space-between;'>
    <div>
        <h2 style='margin:0; font-size:1.6rem; font-weight:800;'>🐄 My Cattle Herd</h2>
        <p style='margin:6px 0 0; opacity:0.85; font-size:0.92rem;'>Add, manage and track all your cows</p>
    </div>
    <div style='font-size:3rem; opacity:0.3;'>🐄</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["  All Cows  ", "  Add New Cow  "])

with tab1:
    res = api.get_cows(token)
    if res.status_code == 200:
        cows = res.json()
        if not cows:
            st.markdown("""
            <div style='text-align:center;padding:60px 20px;background:white;border-radius:14px;border:1px solid #e8f5e9'>
                <div style='font-size:3rem'>🐄</div>
                <h3 style='color:#1b5e20;margin:12px 0 8px'>No Cows Yet</h3>
                <p style='color:#888'>Add your first cow using the "Add New Cow" tab above.</p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='color:#666;margin-bottom:16px'>Showing <b>{len(cows)}</b> registered cow(s)</div>", unsafe_allow_html=True)
            for cow in cows:
                with st.container():
                    st.markdown(f"""
                    <div class='cow-card'>
                        <h3>🐄 {cow['name']}</h3>
                        <span class='cow-uid'>{cow['cow_uid']}</span>
                        <div class='info-row'>
                            <div class='info-item'><div class='val'>{cow['breed']}</div><div class='lbl'>Breed</div></div>
                            <div class='info-item'><div class='val'>{cow['age']} yrs</div><div class='lbl'>Age</div></div>
                            <div class='info-item'><div class='val'>{cow.get('weight_kg') or 'N/A'} kg</div><div class='lbl'>Weight</div></div>
                        </div>
                    </div>""", unsafe_allow_html=True)

                    with st.expander(f"Edit / Delete — {cow['name']}"):
                        col_edit, col_del = st.columns([4, 1])
                        with col_edit:
                            with st.form(f"edit_{cow['id']}"):
                                c1, c2 = st.columns(2)
                                new_name  = c1.text_input("Name",  value=cow["name"])
                                new_breed = c2.text_input("Breed", value=cow["breed"])
                                c3, c4 = st.columns(2)
                                new_age = c3.number_input("Age (years)", value=float(cow["age"]), min_value=0.1, step=0.5)
                                new_wt  = c4.number_input("Weight (kg)", value=float(cow.get("weight_kg") or 0), min_value=0.0, step=5.0)
                                if st.form_submit_button("Save Changes", use_container_width=True):
                                    upd = api.update_cow(token, cow["id"], {"name": new_name, "age": new_age, "breed": new_breed, "weight_kg": new_wt})
                                    if upd.status_code == 200:
                                        st.success("Cow updated successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Update failed.")
                        with col_del:
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("Delete", key=f"del_{cow['id']}", type="primary"):
                                d = api.delete_cow(token, cow["id"])
                                if d.status_code == 204:
                                    st.success("Deleted.")
                                    st.rerun()
    else:
        st.error("Failed to load cows. Please refresh the page.")

with tab2:
    st.markdown("### Add a New Cow")
    st.markdown("Fill in the details below to register a new cow.")
    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("add_cow_form"):
        c1, c2 = st.columns(2)
        name    = c1.text_input("Cow Name *", placeholder="e.g. Ganga, Lakshmi")
        breed   = c2.text_input("Breed *",    placeholder="e.g. Holstein, Gir, Sahiwal")
        c3, c4 = st.columns(2)
        age     = c3.number_input("Age (years) *", min_value=0.1, max_value=30.0, value=2.0, step=0.5)
        weight  = c4.number_input("Weight (kg)", min_value=0.0, max_value=1000.0, value=350.0, step=5.0)
        cow_uid = st.text_input("Custom Cow ID (optional)", placeholder="Leave blank to auto-generate")
        st.markdown("<br>", unsafe_allow_html=True)
        submit  = st.form_submit_button("Add Cow", use_container_width=True)

    if submit:
        if not name or not breed:
            st.warning("Please enter cow name and breed.")
        else:
            payload = {"name": name, "breed": breed, "age": age, "weight_kg": weight}
            if cow_uid.strip():
                payload["cow_uid"] = cow_uid.strip()
            res = api.add_cow(token, payload)
            if res.status_code == 201:
                st.success(f"Cow **{name}** added! ID: `{res.json()['cow_uid']}`")
                st.rerun()
            else:
                st.error(res.json().get("detail", "Failed to add cow."))
