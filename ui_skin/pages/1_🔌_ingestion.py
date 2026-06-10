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
st.caption("Synchronize Trial Balances, Map Account Architectures, and Configure Debt Schedules")
st.markdown("---")

# --- 3. BULLETPROOF SESSION MEMORY SEEDING LAYER ---
# Initialize the base container if completely missing
if "baseline_inputs" not in st.session_state:
    st.session_state["baseline_inputs"] = {}

# Ensure individual target variables are seeded without wiping out other elements
inputs_ref = st.session_state["baseline_inputs"]

if "opening_cash_balance" not in inputs_ref: inputs_ref["opening_cash_balance"] = 69488.00
if "opening_fixed_assets_nbv" not in inputs_ref: inputs_ref["opening_fixed_assets_nbv"] = 531385.00
if "admin_overheads_monthly" not in inputs_ref: inputs_ref["admin_overheads_monthly"] = 18575.00
if "base_monthly_gross_wages" not in inputs_ref: inputs_ref["base_monthly_gross_wages"] = 12000.00
if "directors_salaries_monthly" not in inputs_ref: inputs_ref["directors_salaries_monthly"] = 5150.00
if "pension_opt_out" not in inputs_ref: inputs_ref["pension_opt_out"] = False
if "y1_monthly_revenue_curve" not in inputs_ref: 
    inputs_ref["y1_monthly_revenue_curve"] = [249310.0, 356310.0, 385200.0, 404460.0, 447260.0, 470800.0, 508785.0, 707525.0, 763067.0, 750127.0, 750025.0, 736017.0]

# CRITICAL FIX: Explicitly seed debt_facilities if missing from an old cached session dictionary
if "debt_facilities" not in inputs_ref:
    inputs_ref["debt_facilities"] = [
        {"Facility Name": "DBW Tranche 1", "Opening Balance (£)": 50000.0, "Annual Interest Rate (%)": 7.5, "Term (Months)": 60},
        {"Facility Name": "Funding Circle Line", "Opening Balance (£)": 45000.0, "Annual Interest Rate (%)": 9.2, "Term (Months)": 48},
        {"Facility Name": "IWOCA Short-Term", "Opening Balance (£)": 35176.0, "Annual Interest Rate (%)": 12.0, "Term (Months)": 24}
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
st.caption("Configure outstanding debt liabilities below. The engine will automatically compile dynamic monthly principal vs. interest splits.")

# This lookup is now entirely safe from KeyError crashes
current_debt_df = pd.DataFrame(inputs_ref["debt_facilities"])

# Inject Streamlit's structural native data editor component
edited_debt_df = st.data_editor(
    current_debt_df,
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "Facility Name": st.column_config.TextColumn("Facility Name Description", help="e.g., DBW Capital Growth Facility", required=True),
        "Opening Balance (£)": st.column_config.NumberColumn("Opening Principal Balance (£)", format="£%,.0f", min_value=0.0, required=True),
        "Annual Interest Rate (%)": st.column_config.NumberColumn("Annual Interest Rate (%)", format="%.2f%%", min_value=0.0, max_value=100.0, required=True),
        "Term (Months)": st.column_config.NumberColumn("Contractual Amortization Term (Months)", format="%d", min_value=1, required=True),
    }
)

# --- 6. SAVE AND EMIT INPUTS PIPELINE ---
st.markdown("---")
if st.button("💾 Lock and Synchronize System Attributes", use_container_width=True):
    formatted_debt_list = []
    for _, row in edited_debt_df.iterrows():
        formatted_debt_list.append({
            "facility_name": row["Facility Name"],
            "opening_balance": float(row["Opening Balance (£)"]),
            "interest_rate_annual": float(row["Annual Interest Rate (%)"]) / 100.0, 
            "term_months": int(row["Term (Months)"])
        })
        
    inputs_ref["admin_overheads_monthly"] = admin_input
    inputs_ref["base_monthly_gross_wages"] = wages_input
    inputs_ref["pension_opt_out"] = pension_toggle
    inputs_ref["debt_facilities"] = edited_debt_df.to_dict(orient="records") 
    inputs_ref["debt_facilities_clean"] = formatted_debt_list
    
    st.success("🎉 System parameters synchronized! Debt amortization loops successfully updated inside core calculation engines.")