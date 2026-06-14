# pages/1_✍️_Data_Input_Workspace.py

import os
import sys
import json
import streamlit as st
import pandas as pd
from pathlib import Path

# Absolute project path resolution to handle multi-page layout shifts smoothly
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

# =========================================================================
# 🔒 ENDPOINT SECURITY GUARDS
# =========================================================================
if not st.session_state.get("authenticated", False):
    st.error("🔒 Access Denied: Unauthorized Endpoints Locked")
    st.info("This environment is shielded by an enterprise security framework. You must log in via the main portal to open this workspace.")
    st.stop()

PROJECTS_DIR = "saved_projects"
if not os.path.exists(PROJECTS_DIR):
    os.makedirs(PROJECTS_DIR)

st.title("✍️ Data Input Workspace")
st.caption("Directly build your model rows, type parameters, and manage saved project baselines.")
st.markdown("---")

# =========================================================================
# ✍️ PANEL 1: MANUAL DIRECT DATA ENTRY FORMS
# =========================================================================
st.subheader("📝 Direct Parameter Setup Desks")
st.markdown("Type numbers and descriptions below to build or expand your project tracking parameters:")

inc_col1, inc_col2, inc_col3 = st.columns(3)

with inc_col1:
    st.markdown("### 📊 Revenue Streams")
    s_name = st.text_input("Income Name / Description:", placeholder="e.g., Court Hire Fees", key="s_name")
    s_amt = st.number_input("Projected Annual Income (£):", min_value=0.0, step=5000.0, key="s_amt")
    s_vat = st.checkbox("Apply Standard 20% VAT?", value=True, key="s_vat")
    
    if st.button("➕ Add Income Row", use_container_width=True):
        if s_name.strip():
            st.session_state.manual_sales_entries.append({
                "name": s_name.strip(), 
                "amount": float(s_amt), 
                "vat": 0.20 if s_vat else 0.0
            })
            st.success(f"Added income: {s_name}")
            st.rerun()

with inc_col2:
    st.markdown("### 💸 Running Overhead Costs")
    o_name = st.text_input("Cost Name / Description:", placeholder="e.g., Site Utilities & Rent", key="o_name")
    o_amt = st.number_input("Projected Annual Cost (£):", min_value=0.0, step=1000.0, key="o_amt")
    
    if st.button("➕ Add Overhead Row", use_container_width=True):
        if o_name.strip():
            st.session_state.manual_opex_entries.append({
                "name": o_name.strip(), 
                "amount": float(o_amt), 
                "vat": 0.20
            })
            st.success(f"Added overhead: {o_name}")
            st.rerun()

with inc_col3:
    st.markdown("### 🏗️ Setup Costs & Funding")
    c_name = st.text_input("Investment Item / Asset Name:", placeholder="e.g., Main Building Build", key="c_name")
    c_type = st.selectbox("Classification Category:", [
        "Fixed Asset Purchase", 
        "Director / Equity Inflow", 
        "New Bank Loan Injection"
    ])
    c_val = st.number_input("Transaction Value (£):", min_value=0.0, step=5000.0, key="c_val")
    
    if st.button("➕ Add Capital Row", use_container_width=True):
        if c_name.strip():
            # Setup purchases default to Day 1 (Month 1) with 10% structural depreciation rules
            st.session_state.manual_capital_entries.append({
                "name": c_name.strip(), 
                "type": c_type, 
                "value": float(c_val), 
                "month": 1, 
                "parameter": 10.0 if c_type == "Fixed Asset Purchase" else 0.0
            })
            st.success(f"Added capital row: {c_name}")
            st.rerun()

st.markdown("---")

# =========================================================================
# 💾 PANEL 2: COMPACT WORKSPACE PROFILE EXPORTS
# =========================================================================
st.subheader("💾 Master Save Workspace Registry")
st.markdown("Commit your active data inputs to disk storage so they populate your dynamic forecast screens.")

save_col1, save_col2 = st.columns([2, 1])

with save_col1:
    current_default_title = st.session_state.get("selected_project", "My-Padel-Baseline")
    save_title = st.text_input("Project Filename Target Identifier:", value=current_default_title)

with save_col2:
    st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("💾 Export Project to Secure File Target", use_container_width=True):
        clean_title = "".join(c for c in save_title if c.isalnum() or c in ("-", "_")).strip()
        if clean_title:
            project_payload = {
                "sales": st.session_state.manual_sales_entries,
                "opex": st.session_state.manual_opex_entries,
                "capital": st.session_state.manual_capital_entries
            }
            try:
                filepath = os.path.join(PROJECTS_DIR, f"{clean_title}.json")
                with open(filepath, "w") as pf:
                    json.dump(project_payload, pf, indent=4)
                st.session_state["selected_project"] = clean_title
                st.session_state["active_project_name"] = clean_title
                st.success(f"🚀 Active dataset locked and saved perfectly as: `{clean_title}.json`")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to export data rows: {str(e)}")

st.markdown("---")

# =========================================================================
# 📁 PANEL 3: LIVE REPOSITORY QUEUES MONITOR
# =========================================================================
st.subheader("📁 Active Workspace Data Repositories")
st.markdown("Review the raw tables currently held in active model memory context:")

if (st.session_state.manual_sales_entries or 
    st.session_state.manual_opex_entries or 
    st.session_state.manual_capital_entries) and not st.session_state.get("selected_project"):
    st.warning("⚠️ Notice: Active data rows are currently unsaved. Save your workspace configuration above to unlock the forecast sheets.")

tab1, tab2, tab3 = st.tabs(["📈 Income Streams", "💸 Running Overhead Costs", "🏗️ Setup & Injected Funds"])

with tab1:
    if st.session_state.manual_sales_entries:
        df_sales = pd.DataFrame(st.session_state.manual_sales_entries)
        df_sales.columns = ["Revenue Stream Name", "Annual Gross Amount (£)", "VAT Rate Fraction"]
        st.dataframe(df_sales.style.format({"Annual Gross Amount (£)": "{:,.2f}"}), use_container_width=True)
        if st.button("🗑️ Clear Income Rows", key="clear_s"):
            st.session_state.manual_sales_entries = []
            st.rerun()
    else:
        st.caption("No revenue lines currently configured in this workspace.")

with tab2:
    if st.session_state.manual_opex_entries:
        df_opex = pd.DataFrame(st.session_state.manual_opex_entries)
        df_opex.columns = ["Overhead Cost Name", "Annual Running Rate (£)", "VAT Rate Fraction"]
        st.dataframe(df_opex.style.format({"Annual Running Rate (£)": "{:,.2f}"}), use_container_width=True)
        if st.button("🗑️ Clear Overhead Rows", key="clear_o"):
            st.session_state.manual_opex_entries = []
            st.rerun()
    else:
        st.caption("No operational overhead lines currently configured in this workspace.")

with tab3:
    if st.session_state.manual_capital_entries:
        df_cap = pd.DataFrame(st.session_state.manual_capital_entries)
        df_cap = df_cap[["name", "type", "value", "month"]]
        df_cap.columns = ["Asset / Funding Source Name", "Structural Category", "Transaction Value (£)", "Target Month"]
        st.dataframe(df_cap.style.format({"Transaction Value (£)": "{:,.2f}"}), use_container_width=True)
        if st.button("🗑️ Clear Capital Rows", key="clear_c"):
            st.session_state.manual_capital_entries = []
            st.rerun()
    else:
        st.caption("No asset build costs or opening cash cushions currently configured in this workspace.")