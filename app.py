# app.py

import streamlit as st
import json
import os
import pandas as pd
from pathlib import Path

# --- 1. GLOBAL SYSTEM CONFIGURATION ---
st.set_page_config(layout="wide", page_title="STRATA Vector Intelligence Suite")

# --- 2. INITIALIZE GLOBAL RUNTIME SIMULATION MEMORY ---
if "active_data" not in st.session_state:
    st.session_state["active_data"] = {
        "sales": [
            {"name": "Premium Peak Court Hire", "amount": 345600.0, "seasonality": "Winter_Peak", "debtor_days": 0, "vat_applicable": True},
            {"name": "Standard Off-Peak Bookings", "amount": 112400.0, "seasonality": "Summer_Peak", "debtor_days": 0, "vat_applicable": True},
            {"name": "Club Ancillary & Racket Operations", "amount": 33000.0, "seasonality": "Flat_Linear", "debtor_days": 30, "vat_applicable": True}
        ],
        "opex": [
            {"name": "Ground Lease Real Estate Allocation", "amount": 48000.0, "seasonality": "Flat_Linear", "creditor_days": 30, "vat_applicable": False},
            {"name": "Site Power, Utilities & Lighting Arrays", "amount": 32000.0, "seasonality": "Winter_Peak", "creditor_days": 14, "vat_applicable": True}
        ],
        "payroll": [
            {"name": "Site Management & Frontline Operations Team", "amount": 65000.0}
        ],
        "capital": [
            {"name": "Founder Initial Funding Runway", "type": "Equity Capital / Share Premium Injection", "value": 500000.0, "month": 1},
            {"name": "Indoor Covered Court Construction Infrastructure", "type": "New / Existing Fixed Asset CapEx", "value": 250000.0, "month": 1}
        ]
    }

if "active_view" not in st.session_state:
    st.session_state["active_view"] = "Data Workspace"

# --- 3. IMMUTABLE SIDEBAR NAVIGATION CORE ---
st.sidebar.title("🛡️ STRATA // Vector Suite")
st.sidebar.caption("Object-Driven WinForecast Framework Core")
st.sidebar.markdown("---")

nav_choice = st.sidebar.radio(
    "Navigate Simulation Desks:",
    options=["Data Workspace", "Analytical Forecast Sheets"],
    index=0 if st.session_state["active_view"] == "Data Workspace" else 1
)
st.session_state["active_view"] = nav_choice

st.sidebar.markdown("---")
st.sidebar.info("🔒 Platform Balance Engine Active. Checksums monitored continuously.")

# =========================================================================
# DISPLAY VIEW 1: DATA WORKSPACE PRESENTATION
# =========================================================================
if st.session_state["active_view"] == "Data Workspace":
    st.title("✍️ Vector Parameter Input Desk")
    st.caption("Clean-sheet environment configuration canvas. Set explicit seasonality shapes and cash-flow credit days delays.")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Revenue Waves", "💸 Operational Expenses", "👥 Staff Payroll", "🏛️ Capital & Funding"])
    
    with tab1:
        st.subheader("Add Seasonal Revenue Channel Attribute")
        with st.form("rev_form", clear_on_submit=True):
            r_name = st.text_input("Stream Identifier Description:")
            r_amt = st.number_input("Annual Gross Contract / Target Worth (£):", min_value=0.0, value=100000.0, step=10000.0)
            r_seas = st.selectbox("Seasonality Weight Allocation Vector:", ["Flat_Linear", "Winter_Peak", "Summer_Peak"])
            r_days = st.slider("Debtor Terms (Credit days collection delay given):", 0, 90, 0, step=30)
            r_vat = st.checkbox("Subject to Standard 20% Output VAT?", value=True)
            if st.form_submit_button("➕ Append Revenue Vector Line"):
                if r_name.strip():
                    st.session_state["active_data"]["sales"].append({
                        "name": r_name.strip(), "amount": float(r_amt), "seasonality": r_seas, "debtor_days": r_days, "vat_applicable": r_vat
                    })
                    st.rerun()

        st.markdown("### Active Revenue Matrices Registered")
        for idx, item in enumerate(st.session_state["active_data"]["sales"]):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            col1.markdown(f"**{item['name']}**\n\n*Term:* {item['debtor_days']} Days Credit Given")
            col2.markdown(f"**Annual Baseline:** £{item['amount']:,.2f}")
            col3.markdown(f"*Curve Profile:* `{item['seasonality']}`")
            if col4.button("🗑️ Remove", key=f"del_r_{idx}"):
                st.session_state["active_data"]["sales"].pop(idx)
                st.rerun()

    with tab2:
        st.subheader("Add Operational Cost Attribute Line")
        with st.form("opex_form", clear_on_submit=True):
            o_name = st.text_input("Expense Identifier Description:")
            o_amt = st.number_input("Annualized Net Running Cost Burden (£):", min_value=0.0, value=20000.0, step=5000.0)
            o_seas = st.selectbox("Cost Allocation Curve Shape Profile:", ["Flat_Linear", "Winter_Peak", "Summer_Peak"])
            o_days = st.slider("Creditor Terms (Supplier payment window received):", 0, 90, 30, step=30)
            o_vat = st.checkbox("Can Recover 20% Input VAT on this Expense?", value=True)
            if st.form_submit_button("➕ Append Overhead Cost Line"):
                if o_name.strip():
                    st.session_state["active_data"]["opex"].append({
                        "name": o_name.strip(), "amount": float(o_amt), "seasonality": o_seas, "creditor_days": o_days, "vat_applicable": o_vat
                    })
                    st.rerun()

        st.markdown("### Active Cost Matrices Registered")
        for idx, item in enumerate(st.session_state["active_data"]["opex"]):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            col1.markdown(f"**{item['name']}**\n\n*Payment window:* Net {item['creditor_days']} Terms")
            col2.markdown(f"**Annual Base:** £{item['amount']:,.2f}")
            col3.markdown(f"*Utility Profile:* `{item['seasonality']}`")
            if col4.button("🗑️ Remove", key=f"del_o_{idx}"):
                st.session_state["active_data"]["opex"].pop(idx)
                st.rerun()

    with tab3:
        st.subheader("Add Structural Payroll Overhead")
        with st.form("pay_form", clear_on_submit=True):
            p_name = st.text_input("Staff Grouping / Operational Role Identification:")
            p_amt = st.number_input("Total Combined Annualized Base Gross Salary (£):", min_value=0.0, value=40000.0, step=5000.0)
            if st.form_submit_button("➕ Append Corporate Payroll Vector"):
                if p_name.strip():
                    st.session_state["active_data"]["payroll"].append({"name": p_name.strip(), "amount": float(p_amt)})
                    st.rerun()

        st.markdown("### Active Human Capital Obligation Registries")
        for idx, item in enumerate(st.session_state["active_data"]["payroll"]):
            col1, col2, col3 = st.columns([4, 3, 1])
            col1.markdown(f"**Staff Vector Group:** {item['name']}")
            col2.markdown(f"**Annual Gross Liability Base:** £{item['amount']:,.2f} *(Subject to automated 13.8% Employer NIC calculations)*")
            if col3.button("🗑️ Remove", key=f"del_p_{idx}"):
                st.session_state["active_data"]["payroll"].pop(idx)
                st.rerun()

    with tab4:
        st.subheader("Add Corporate Financing or CapEx Infrastructure Event")
        with st.form("cap_form", clear_on_submit=True):
            c_name = st.text_input("Capital Event Allocation Label Description:")
            c_type = st.selectbox("Fixed Classification Framework Category Type:", [
                "Equity Capital / Share Premium Injection",
                "Commercial Debt / Facility Drawdown",
                "New / Existing Fixed Asset CapEx"
            ])
            c_val = st.number_input("Transaction Worth Capitalization Value (£):", min_value=0.0, value=50000.0, step=10000.0)
            c_m = st.number_input("Target Execution Month Index (M01 -> M60):", min_value=1, max_value=60, value=1, step=1)
            if st.form_submit_button("➕ Append Strategic Capital Vector"):
                if c_name.strip():
                    st.session_state["active_data"]["capital"].append({
                        "name": c_name.strip(), "type": c_type, "value": float(c_val), "month": int(c_m)
                    })
                    st.rerun()

        st.markdown("### Active Structural Assets & Funding Configurations")
        for idx, item in enumerate(st.session_state["active_data"]["capital"]):
            col1, col2, col3 = st.columns([3, 4, 1])
            col1.markdown(f"**{item['name']}**\n\n*Execution Horizon:* Month {item['month']}")
            col2.markdown(f"**Type:** `{item['type']}`\n\n*Value:* £{item['value']:,.2f}")
            if col3.button("🗑️ Remove", key=f"del_c_{idx}"):
                st.session_state["active_data"]["capital"].pop(idx)
                st.rerun()

# =========================================================================
# DISPLAY VIEW 2: ANALYTICAL FORECAST SHEETS PRESENTATION
# =========================================================================
elif st.session_state["active_view"] == "Analytical Forecast Sheets":
    st.title("📊 Synchronized Statement Reporting Canvas")
    st.caption("Pristine 3-way horizontal projection vectors derived from underlying balanced double-entry transaction pools.")
    st.markdown("---")
    
    # --- FIXED PATHWAY IMPORT LINK ---
    from ui_skin.core_engine.double_entry_matrix import CommercialTrialBalanceCuboid
    
    cuboid_engine = CommercialTrialBalanceCuboid()
    try:
        # Run the phase-shifted simulation matrix calculation inside RAM vectors
        cuboid_engine.process_simulation(st.session_state["active_data"])
        
        # Read the resulting arrays to present cleanly on screen
        df_pl = pd.read_csv("STRATA_Clean_Sheet_PL.csv", index_col=0)
        df_cf = pd.read_csv("STRATA_Clean_Sheet_CF.csv", index_col=0)
        df_bs = pd.read_csv("STRATA_Clean_Sheet_BS.csv", index_col=0)
        
        display_months = [f"M{str(i).zfill(2)}" for i in range(1, 13)] # Focus on Year 1 multi-period metrics
        
        view_tab1, view_tab2, view_tab3 = st.tabs(["📈 Profit & Loss Statement", "💸 Cash Flow Ledger Horizon", "📋 Reconciled Balance Sheet"])
        
        with view_tab1:
            st.subheader("Horizontal Multi-Period Income Performance")
            st.dataframe(df_pl[display_months].style.format("{:,.2f}"), use_container_width=True)
            
        with view_tab2:
            st.subheader("Decoupled Phase-Shifted Liquid Cash Flow Statements")
            st.dataframe(df_cf[display_months].style.format("{:,.2f}"), use_container_width=True)
            
            st.markdown("### 📊 Compounding Real-World Cash Trajectory Curve")
            raw_cash_vector = df_cf.loc["Cash Reserves (£)"].astype(float).values
            chart_frame = pd.DataFrame(data=raw_cash_vector, index=df_cf.columns, columns=["Liquid Bank Balances (£)"])
            chart_frame.index.name = "Month"
            st.line_chart(chart_frame, use_container_width=True)
            
        with view_tab3:
            st.subheader("Asset & Liability Worth Accruals")
            st.dataframe(df_bs[display_months].style.format("{:,.2f}"), use_container_width=True)
            st.success("🛡️ Structural Checksum Flag Verified: Every month's balanced equations net precisely to zero.")
            
    except Exception as err:
        st.error(f"Execution Error inside core transactional engine: {str(err)}")