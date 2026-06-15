# pages/1_✍️_Data_Input_Workspace.py

import os
import sys
import json
import streamlit as st
import pandas as pd
import google.generativeai as genai
from pypdf import PdfReader
from pathlib import Path

# Path resolution for standalone multi-page layout environments
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

if not st.session_state.get("authenticated", False):
    st.error("🔒 Access Denied: Unauthorized Endpoints Locked")
    st.stop()

PROJECTS_DIR = "saved_projects"
CACHE_FILE = os.path.join(PROJECTS_DIR, "UNSAVED_WORKSPACE_DRAFT_BACKUP.json")

if not os.path.exists(PROJECTS_DIR):
    os.makedirs(PROJECTS_DIR)

gemini_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

# --- AUTOMATIC DATA RETENTION CACHE ENGINE ---
def save_local_backup_cache():
    cache_payload = {
        "sales": st.session_state.get("manual_sales_entries", []),
        "opex": st.session_state.get("manual_opex_entries", []),
        "capital": st.session_state.get("manual_capital_entries", [])
    }
    try:
        with open(CACHE_FILE, "w") as cf:
            json.dump(cache_payload, cf, indent=4)
    except:
        pass

def purge_local_backup_cache():
    if os.path.exists(CACHE_FILE):
        try: os.remove(CACHE_FILE)
        except: pass

# Ensure list anchors exist within session memory matrix
if "manual_sales_entries" not in st.session_state: st.session_state.manual_sales_entries = []
if "manual_opex_entries" not in st.session_state: st.session_state.manual_opex_entries = []
if "manual_capital_entries" not in st.session_state: st.session_state.manual_capital_entries = []

st.title("✍️ Data Input Workspace")
st.caption("Directly build your model rows, type parameters, or utilize the intelligent document analysis conduit.")
st.markdown("---")

# --- USER EXPERIENCE RESTORATION PROMPT ---
if os.path.exists(CACHE_FILE):
    if not st.session_state.manual_sales_entries and not st.session_state.manual_opex_entries and not st.session_state.manual_capital_entries:
        st.info("✨ **Session Recovery Anchor Active:** We detected an unsaved data entry session that closed unexpectedly.")
        restore_col1, restore_col2 = st.columns([1, 1])
        with restore_col1:
            if st.button("🔄 Restore My Lost Data Rows Instantly", use_container_width=True):
                try:
                    with open(CACHE_FILE, "r") as cf: loaded_cache = json.load(cf)
                    st.session_state.manual_sales_entries = loaded_cache.get("sales", [])
                    st.session_state.manual_opex_entries = loaded_cache.get("opex", [])
                    st.session_state.manual_capital_entries = loaded_cache.get("capital", [])
                    st.success("Data repositories restored successfully!")
                    st.rerun()
                except Exception as e: st.error(f"Recovery Error: {str(e)}")
        with restore_col2:
            if st.button("🗑️ Discard Draft & Start Completely Fresh", use_container_width=True):
                purge_local_backup_cache()
                st.success("Draft cleared.")
                st.rerun()
        st.markdown("---")

# =========================================================================
# ✍️ DIRECT PARAMETER SETUP FORMS (FORM BLOCK ARCHITECTURE INSTALLED)
# =========================================================================
st.subheader("📝 Direct Parameter Setup Desks")
inc_col1, inc_col2, inc_col3 = st.columns(3)

with inc_col1:
    st.markdown("### 📊 Revenue Streams")
    with st.form("revenue_entry_form", clear_on_submit=True):
        s_name = st.text_input("Income Name / Description:", placeholder="e.g., Court Hire Fees")
        s_amt = st.number_input("Projected Annual Income (£):", min_value=0.0, step=5000.0)
        s_vat = st.checkbox("Apply Standard 20% VAT?", value=True)
        if st.form_submit_button("➕ Add Income Row", use_container_width=True):
            if s_name.strip():
                st.session_state.manual_sales_entries.append({"name": s_name.strip(), "amount": float(s_amt), "vat": 0.20 if s_vat else 0.0})
                save_local_backup_cache()
                st.rerun()

with inc_col2:
    st.markdown("### 💸 Overhead Costs")
    with st.form("opex_entry_form", clear_on_submit=True):
        o_name = st.text_input("Cost Name / Description:", placeholder="e.g., Site Utilities & Rent")
        o_amt = st.number_input("Projected Annual Cost (£):", min_value=0.0, step=1000.0)
        o_vat = st.checkbox("Apply Standard 20% VAT?", value=True)
        if st.form_submit_button("➕ Add Overhead Row", use_container_width=True):
            if o_name.strip():
                st.session_state.manual_opex_entries.append({"name": o_name.strip(), "amount": float(o_amt), "vat": 0.20 if o_vat else 0.0})
                save_local_backup_cache()
                st.rerun()

with inc_col3:
    st.markdown("### 🏛️ Cap-Ex & Finance")
    with st.form("capital_entry_form", clear_on_submit=True):
        c_name = st.text_input("Asset Description / Capital Event:", placeholder="e.g., Core Court Infrastructure")
        c_type_display = st.selectbox("Classification Category:", [
            "New / Existing Fixed Asset CapEx", 
            "Equity Capital / Share Premium Injection", 
            "Commercial Debt / Facility Drawdown"
        ])
        c_val = st.number_input("Transaction Value (£):", min_value=0.0, step=5000.0)
        if st.form_submit_button("➕ Add Capital Row", use_container_width=True):
            if c_name.strip():
                backend_type_map = {
                    "New / Existing Fixed Asset CapEx": "Fixed Asset Purchase",
                    "Equity Capital / Share Premium Injection": "Director / Equity Inflow",
                    "Commercial Debt / Facility Drawdown": "New Bank Loan Injection"
                }
                mapped_type = backend_type_map[c_type_display]
                st.session_state.manual_capital_entries.append({
                    "name": c_name.strip(), "type": mapped_type, "value": float(c_val), "month": 1, 
                    "parameter": 10.0 if mapped_type == "Fixed Asset Purchase" else 0.0
                })
                save_local_backup_cache()
                st.rerun()

st.markdown("---")

# =========================================================================
# 💾 MASTER SAVE WORKSPACE REGISTRY
# =========================================================================
st.subheader("💾 Master Save Workspace Registry")
save_col1, save_col2 = st.columns([2, 1])
with save_col1:
    save_title = st.text_input("Project Filename Target Identifier:", value=st.session_state.get("selected_project", "Vanguard-Arena-Expansion"))
with save_col2:
    st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("💾 Export Project to Secure File Target", use_container_width=True):
        clean_title = "".join(c for c in save_title if c.isalnum() or c in ("-", "_")).strip()
        if clean_title:
            project_payload = {"sales": st.session_state.manual_sales_entries, "opex": st.session_state.manual_opex_entries, "capital": st.session_state.manual_capital_entries}
            try:
                with open(os.path.join(PROJECTS_DIR, f"{clean_title}.json"), "w") as pf: json.dump(project_payload, pf, indent=4)
                st.session_state["selected_project"] = clean_title
                purge_local_backup_cache()
                st.success(f"🚀 Active dataset saved as: `{clean_title}.json`")
                st.rerun()
            except Exception as e: st.error(f"Export error: {str(e)}")

st.markdown("---")

# =========================================================================
# 📁 LIVE MONITOR LEDGERS WITH SURGICAL SINGLE-ROW DELETION
# =========================================================================
st.subheader("📁 Active Workspace Data Repositories")
tab1, tab2, tab3 = st.tabs(["📈 Income Streams", "💸 Overhead Costs", "🏛️ Cap-Ex & Capitalization Ledger"])

with tab1:
    if st.session_state.manual_sales_entries:
        for idx, item in enumerate(st.session_state.manual_sales_entries):
            r_col1, r_col2, r_col3, r_col4 = st.columns([3, 2, 1, 1])
            with r_col1: st.markdown(f"**Stream:** {item['name']}")
            with r_col2: st.markdown(f"**Annual Gross:** £{item['amount']:,.2f}")
            with r_col3: st.markdown(f"**VAT:** {int(item['vat']*100)}%")
            with r_col4:
                if st.button("🗑️ Delete", key=f"del_s_{idx}"):
                    st.session_state.manual_sales_entries.pop(idx)
                    save_local_backup_cache()
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚨 Wipe Entire Revenue Repository", key="clear_s"): st.session_state.manual_sales_entries = []; save_local_backup_cache(); st.rerun()
    else: st.caption("No revenue lines configured.")

with tab2:
    if st.session_state.manual_opex_entries:
        for idx, item in enumerate(st.session_state.manual_opex_entries):
            o_col1, o_col2, o_col3, o_col4 = st.columns([3, 2, 1, 1])
            with o_col1: st.markdown(f"**Overhead:** {item['name']}")
            with o_col2: st.markdown(f"**Annual Rate:** £{item['amount']:,.2f}")
            with o_col3: st.markdown(f"**VAT:** {int(item['vat']*100)}%")
            with o_col4:
                if st.button("🗑️ Delete", key=f"del_o_{idx}"):
                    st.session_state.manual_opex_entries.pop(idx)
                    save_local_backup_cache()
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚨 Wipe Entire Overhead Repository", key="clear_o"): st.session_state.manual_opex_entries = []; save_local_backup_cache(); st.rerun()
    else: st.caption("No operational overhead lines configured.")

with tab3:
    if st.session_state.manual_capital_entries:
        for idx, item in enumerate(st.session_state.manual_capital_entries):
            c_col1, c_col2, c_col3, c_col4 = st.columns([3, 2, 1, 1])
            with c_col1: st.markdown(f"**Asset/Funding:** {item['name']}")
            with c_col2: st.markdown(f"**Category:** {item['type']}")
            with c_col3: st.markdown(f"**Value:** £{item['value']:,.2f}")
            with c_col4:
                if st.button("🗑️ Delete", key=f"del_c_{idx}"):
                    st.session_state.manual_capital_entries.pop(idx)
                    save_local_backup_cache()
                    st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚨 Wipe Entire Capital Repository", key="clear_c"): st.session_state.manual_capital_entries = []; save_local_backup_cache(); st.rerun()
    else: st.caption("No asset allocations or long-term funding entries configured.")