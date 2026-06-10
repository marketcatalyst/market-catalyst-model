# ui_skin/pages/1_🔌_ingestion.py
import sys
from pathlib import Path

# --- 1. CRITICAL PATH RESOLUTION ---
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="STRATA Ingestion Engine")

# --- 2. SECURITY GATEKEEPER CONSTRAINT ---
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("🔒 **Access Denied: Unauthorized Endpoints Locked**")
    st.info("Please return to the main portal landing page and authenticate your corporate credentials to unlock this session.")
    if st.button("Return to Portal Landing Page", use_container_width=True):
        st.switch_page("home.py")
    st.stop()

st.title("🔌 Corporate Data Ingestion & Mapping Suite")
st.caption("Synchronize Trial Balances, Map Account Architectures, and Configure Location Tax Schedules")
st.markdown("---")

# --- 3. BULLETPROOF SESSION MEMORY SEEDING LAYER ---
if "baseline_inputs" not in st.session_state:
    st.session_state["baseline_inputs"] = {}

inputs_ref = st.session_state["baseline_inputs"]

if "opening_cash_balance" not in inputs_ref: inputs_ref["opening_cash_balance"] = 69488.00
if "opening_fixed_assets_nbv" not in inputs_ref: inputs_ref["opening_fixed_assets_nbv"] = 531385.00
if "admin_overheads_monthly" not in inputs_ref: inputs_ref["admin_overheads_monthly"] = 18575.00
if "base_monthly_gross_wages" not in inputs_ref: inputs_ref["base_monthly_gross_wages"] = 12000.00
if "directors_salaries_monthly" not in inputs_ref: inputs_ref["directors_salaries_monthly"] = 5150.00
if "pension_opt_out" not in inputs_ref: inputs_ref["pension_opt_out"] = False
if "y1_monthly_revenue_curve" not in inputs_ref: 
    inputs_ref["y1_monthly_revenue_curve"] = [249310.0, 356310.0, 385200.0, 404460.0, 447260.0, 470800.0, 508785.0, 707525.0, 763067.0, 750127.0, 750025.0, 736017.0]

if "debt_facilities" not in inputs_ref:
    inputs_ref["debt_facilities"] = [
        {"Facility Name Description": "DBW Tranche 1", "Opening Principal Balance (£)": 50000.0, "Annual Interest Rate (%)": 7.5, "Contractual Amortization Term (Months)": 60},
        {"Facility Name Description": "Funding Circle Line", "Opening Principal Balance (£)": 45000.0, "Annual Interest Rate (%)": 9.2, "Contractual Amortization Term (Months)": 48},
        {"Facility Name Description": "IWOCA Short-Term", "Opening Principal Balance (£)": 35176.0, "Annual Interest Rate (%)": 12.0, "Contractual Amortization Term (Months)": 24}
    ]

if "sales_locations" not in inputs_ref:
    inputs_ref["sales_locations"] = [
        {"Trading Location Name": "Bridgend Hub", "Corporate Revenue Share (%)": 40.0, "Zero-Rated / Exempt Mix (%)": 65.0},
        {"Trading Location Name": "Cardiff Bay Center", "Corporate Revenue Share (%)": 35.0, "Zero-Rated / Exempt Mix (%)": 0.0},
        {"Trading Location Name": "Penarth Acquisition", "Corporate Revenue Share (%)": 25.0, "Zero-Rated / Exempt Mix (%)": 100.0}
    ]

# --- 4. STEP 1: TRIAL BALANCE AND REVENUE VERIFICATION ---
st.markdown("### **Step 1: Core Operations Run-Rates**")
col1, col2, col3 = st.columns(3)
with col1:
    admin_input = st.number_input("Monthly Admin Overheads (£):", value=float(inputs_ref["admin_overheads_monthly"]), step=500.0)
with col2:
    wages_input = st.number_input("Monthly Gross Staff Wages (£):", value=float(inputs_ref["base_monthly_gross_wages"]), step=500.0)
with col3:
    pension_toggle = st.checkbox("Statutory Auto-Enrolment Opt-Out", value=inputs_ref["pension_opt_out"])

# --- 5. STEP 2: DYNAMIC DEBT LIABILITIES CONFIGURATOR ---
st.markdown("---")
st.markdown("### **Step 2: Corporate Debt Liabilities Amortization Grid**")
current_debt_df = pd.DataFrame(inputs_ref["debt_facilities"])

edited_debt_df = st.data_editor(
    current_debt_df, num_rows="dynamic", use_container_width=True, key="debt_editor_v3",
    column_config={
        "Facility Name Description": st.column_config.TextColumn("Facility Name Description", required=True),
        "Opening Principal Balance (£)": st.column_config.NumberColumn("Opening Principal Balance (£)", format="£%,.0f", min_value=0.0, required=True),
        "Annual Interest Rate (%)": st.column_config.NumberColumn("Annual Interest Rate (%)", format="%.2f%%", min_value=0.0, required=True),
        "Contractual Amortization Term (Months)": st.column_config.NumberColumn("Contractual Amortization Term (Months)", format="%d", min_value=1, required=True),
    }
)

# --- 6. STEP 3: DYNAMIC MULTI-SHOP SALES TRACKER ---
st.markdown("---")
st.markdown("### **Step 3: Multi-Shop Revenue & VAT Profile Allocation**")
st.caption("Allocate corporate revenue share weights and local tax attributes. Total Corporate Revenue Share MUST sum to 100%.")

current_locations_df = pd.DataFrame(inputs_ref["sales_locations"])
edited_locations_df = st.data_editor(
    current_locations_df, num_rows="dynamic", use_container_width=True, key="location_editor_v3",
    column_config={
        "Trading Location Name": st.column_config.TextColumn("Trading Location Name", required=True),
        "Corporate Revenue Share (%)": st.column_config.NumberColumn("Corporate Revenue Share (%)", format="%.1f%%", min_value=0.0, max_value=100.0, required=True),
        "Zero-Rated / Exempt Mix (%)": st.column_config.NumberColumn("Zero-Rated / Exempt Mix (%)", format="%.1f%%", min_value=0.0, max_value=100.0, required=True),
    }
)

total_share_entered = edited_locations_df["Corporate Revenue Share (%)"].sum() if not edited_locations_df.empty else 0
if abs(total_share_entered - 100.0) > 0.01:
    st.warning(f"⚠️ **Total Revenue Share Warning:** Your current location shares total **{total_share_entered:.1f}%**. Please adjust rows so they sum up to exactly 100.0%.")

# --- 7. SAVE AND EMIT INPUTS PIPELINE ---
st.markdown("---")
if st.button("💾 Lock and Synchronize System Attributes", use_container_width=True):
    # Process Debt Rows Defensively
    formatted_debt_list = []
    for _, row in edited_debt_df.iterrows():
        name = row.get("Facility Name Description", row.get("Facility Name", "Corporate Loan"))
        bal = row.get("Opening Principal Balance (£)", row.get("Opening Balance (£)", 0.0))
        rate = row.get("Annual Interest Rate (%)", 0.0)
        term = row.get("Contractual Amortization Term (Months)", row.get("Term (Months)", 60))
        
        formatted_debt_list.append({
            "facility_name": name, 
            "opening_balance": float(bal),
            "interest_rate_annual": float(rate) / 100.0, 
            "term_months": int(term)
        })
        
    # Process Location Rows Defensively
    formatted_locations_list = []
    for _, row in edited_locations_df.iterrows():
        name = row.get("Trading Location Name", row.get("Site Location Name", "Retail Outlet"))
        share = row.get("Corporate Revenue Share (%)", 0.0)
        zero_mix = row.get("Zero-Rated / Exempt Mix (%)", row.get("Zero-Rated Mix (%)", 0.0))
        
        std_share = (100.0 - float(zero_mix)) / 100.0
        formatted_locations_list.append({
            "site_name": name,
            "revenue_share": float(share) / 100.0,
            "standard_rated_share": std_share
        })
        
    # Commit directly to the persistent master state dictionary
    inputs_ref["admin_overheads_monthly"] = admin_input
    inputs_ref["base_monthly_gross_wages"] = wages_input
    inputs_ref["pension_opt_out"] = pension_toggle
    inputs_ref["debt_facilities"] = edited_debt_df.to_dict(orient="records")
    inputs_ref["debt_facilities_clean"] = formatted_debt_list
    inputs_ref["sales_locations"] = edited_locations_df.to_dict(orient="records")
    inputs_ref["sales_locations_clean"] = formatted_locations_list
    
    st.success("🎉 System parameters synchronized! Multi-shop location profiles and local VAT mixes successfully locked down.")