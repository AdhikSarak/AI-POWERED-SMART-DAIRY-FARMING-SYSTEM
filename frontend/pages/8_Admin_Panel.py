import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from frontend.utils.auth_state import require_admin, get_token
from frontend.utils import api_client as api
from frontend.utils.charts import collection_bar
from datetime import date

st.set_page_config(page_title="Admin Panel", page_icon="⚙️", layout="wide")
require_admin()
token = get_token()

st.markdown("""<style>
    .stat-card { background:white; border-radius:14px; padding:20px; text-align:center;
        border:1px solid #e8f5e9; box-shadow:0 2px 10px rgba(0,0,0,0.06); }
    .stat-card .val { font-size:2rem; font-weight:700; color:#1b5e20; }
    .stat-card .lbl { font-size:0.88rem; color:#888; margin-top:4px; }
    
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
        <h2 style='margin:0; font-size:1.6rem; font-weight:800;'>⚙️ Admin Panel</h2>
        <p style='margin:6px 0 0; opacity:0.85; font-size:0.92rem;'>Manage farmers, record milk collections, and generate monthly bills</p>
    </div>
    <div style='font-size:3rem; opacity:0.3;'>⚙️</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["  System Stats  ", "  Farmers  ", "  Milk Collection  ", "  Billing  "])

with tab1:
    st.markdown("#### System Overview")
    res = api.get_admin_stats(token)
    if res.status_code == 200:
        s = res.json()
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class='stat-card'>
                <div style='font-size:1.8rem'>👨‍🌾</div>
                <div class='val'>{s.get("total_farmers",0)}</div>
                <div class='lbl'>Registered Farmers</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class='stat-card'>
                <div style='font-size:1.8rem'>🐄</div>
                <div class='val'>{s.get("total_cows",0)}</div>
                <div class='lbl'>Total Cows</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class='stat-card'>
                <div style='font-size:1.8rem'>🏥</div>
                <div class='val'>{s.get("total_health_checks",0)}</div>
                <div class='lbl'>Health Checks Done</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        c4, c5, c6 = st.columns(3)
        with c4:
            st.markdown(f"""<div class='stat-card'>
                <div style='font-size:1.8rem'>🥛</div>
                <div class='val'>{s.get("total_milk_tests",0)}</div>
                <div class='lbl'>Milk Tests Done</div>
            </div>""", unsafe_allow_html=True)
        with c5:
            st.markdown(f"""<div class='stat-card'>
                <div style='font-size:1.8rem'>📦</div>
                <div class='val'>{s.get("total_collections",0)}</div>
                <div class='lbl'>Milk Collections</div>
            </div>""", unsafe_allow_html=True)
        with c6:
            st.markdown(f"""<div class='stat-card'>
                <div style='font-size:1.8rem'>📄</div>
                <div class='val'>{s.get("total_bills",0)}</div>
                <div class='lbl'>Bills Generated</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.error("Could not load stats.")

with tab2:
    st.markdown("#### Registered Farmers")
    res = api.get_farmers(token)
    if res.status_code == 200:
        farmers = res.json()
        if not farmers:
            st.info("No farmers registered yet.")
        else:
            st.markdown(f"<div style='color:#666;margin-bottom:12px'><b>{len(farmers)}</b> farmer(s) registered</div>", unsafe_allow_html=True)
            for f in farmers:
                st.markdown(f"""
                <div style='background:white;border-radius:12px;padding:14px 18px;margin:6px 0;
                    border:1px solid #eee;border-left:4px solid #2e7d32;
                    display:flex;justify-content:space-between;align-items:center'>
                    <div>
                        <div style='font-weight:700'>👨‍🌾 {f["name"]}</div>
                        <div style='color:#888;font-size:0.85rem;margin-top:2px'>
                            {f["email"]} &nbsp;|&nbsp; {f.get("phone") or "No phone"} &nbsp;|&nbsp; Joined: {f["created_at"][:10]}
                        </div>
                    </div>
                    <div style='background:#e8f5e9;color:#1b5e20;padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:600'>
                        ID #{f["id"]}
                    </div>
                </div>""", unsafe_allow_html=True)
    else:
        st.error("Failed to load farmers.")

with tab3:
    st.markdown("#### Record Daily Milk Collection")
    farmers_res = api.get_farmers(token)
    farmers     = farmers_res.json() if farmers_res.status_code == 200 else []
    farmer_opts = {f"{f['name']} ({f['email']})": f["id"] for f in farmers}

    if not farmer_opts:
        st.warning("No farmers registered yet.")
    else:
        with st.form("collection_form"):
            c1, c2 = st.columns(2)
            sel_farmer = c1.selectbox("Select Farmer", list(farmer_opts.keys()))
            farmer_id  = farmer_opts[sel_farmer]
            quality    = c2.selectbox("Milk Quality Grade", ["Good", "Average", "Poor"])

            c3, c4, c5 = st.columns(3)
            quantity   = c3.number_input("Quantity (Liters)", min_value=0.1, value=10.0, step=0.5)
            rate_map   = {"Good": 50.0, "Average": 40.0, "Poor": 30.0}
            rate       = c4.number_input("Rate per Liter (Rs.)", min_value=1.0, value=rate_map[quality], step=1.0)
            coll_date  = c5.date_input("Collection Date", value=date.today())
            notes      = st.text_input("Notes (optional)", placeholder="Any additional notes...")
            submit     = st.form_submit_button("Record Collection", use_container_width=True)

        if submit:
            payload = {"farmer_id": farmer_id, "quantity_liters": quantity,
                       "quality_grade": quality, "rate_per_liter": rate,
                       "collection_date": str(coll_date), "notes": notes or None}
            res = api.record_collection(token, payload)
            if res.status_code == 201:
                amount = quantity * rate
                st.success(f"Recorded: **{quantity}L** of **{quality}** quality milk — Rs. **{amount:.0f}**")
            else:
                st.error(res.json().get("detail", "Failed to record collection."))

    st.markdown("---")
    st.markdown("#### Collection History")
    coll_res = api.get_collections(token)
    if coll_res.status_code == 200:
        colls = coll_res.json()
        if colls:
            st.plotly_chart(collection_bar(colls[:30]), use_container_width=True)
            for c in colls[:20]:
                icon = "🟢" if c["quality_grade"]=="Good" else ("🟡" if c["quality_grade"]=="Average" else "🔴")
                amount = c["quantity_liters"] * c["rate_per_liter"]
                st.markdown(f"""
                <div style='background:white;border-radius:10px;padding:12px 16px;margin:5px 0;border:1px solid #eee'>
                    {icon} <b>Farmer #{c["farmer_id"]}</b> —
                    {c["quantity_liters"]}L | {c["quality_grade"]} |
                    Rs.{c["rate_per_liter"]}/L = <b>Rs.{amount:.0f}</b> |
                    <span style='color:#888'>{c["collection_date"]}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No collections recorded yet.")

with tab4:
    st.markdown("#### Generate Monthly Bill")
    farmers_res2 = api.get_farmers(token)
    farmers2     = farmers_res2.json() if farmers_res2.status_code == 200 else []
    farmer_opts2 = {f"{f['name']} ({f['email']})": f["id"] for f in farmers2}

    if not farmer_opts2:
        st.warning("No farmers registered.")
    else:
        col1, col2 = st.columns(2)
        sel_f2 = col1.selectbox("Select Farmer", list(farmer_opts2.keys()), key="bill_farmer")
        fid2   = farmer_opts2[sel_f2]
        month  = col2.text_input("Billing Month (YYYY-MM)", value=str(date.today())[:7])

        if st.button("Generate Bill", type="primary", use_container_width=True):
            res = api.generate_bill(token, fid2, month)
            if res.status_code == 200:
                bill = res.json()
                st.success("Bill generated successfully!")
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Liters",  f"{bill['total_liters']} L")
                c2.metric("Total Amount",  f"Rs. {bill['total_amount']}")
                c3.metric("Month",         bill["month"])
                if bill.get("bill_pdf_path"):
                    st.info(f"PDF saved at: `{bill['bill_pdf_path']}`")
            else:
                st.error(res.json().get("detail", "Bill generation failed. No collections found for this month."))

    st.markdown("---")
    st.markdown("#### All Bills")
    bills_res = api.get_bills(token)
    if bills_res.status_code == 200:
        bills = bills_res.json()
        if not bills:
            st.info("No bills generated yet.")
        else:
            for b in bills:
                with st.expander(f"Bill #{b['id']} — Farmer #{b['farmer_id']} | {b['month']} | Rs. {b['total_amount']}"):
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Total Liters",  f"{b['total_liters']} L")
                    c2.metric("Total Amount",  f"Rs. {b['total_amount']}")
                    c3.metric("Generated On",  b["created_at"][:10])
