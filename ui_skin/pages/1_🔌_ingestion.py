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

# --- 3. SESSION MEMORY SEEDING LAYER ---
if "baseline_inputs" not in st.session_state:
    st.session_state["baseline_inputs"] = {
        "opening_cash_balance": 69488.00,
        "opening_fixed_assets_nbv": 531385.00,
        "admin_overheads_monthly": 18575.00,
        "base_monthly_gross_wages": 12000.00,
        "directors_salaries_monthly": 5150.00,
        "pension_opt_out": False,
        "y1_monthly_revenue_curve": [249310.0, 356310.0, 385200.0, 404460.0, 447260.0, 470800.0, 508785.0, 707525.0, 763067.0, 750127.0, 750025.0, 736017.0],
        "debt_facilities": [
            {"Facility Name": "DBW Tranche 1", "Opening Balance (£)": 50000.0, "Annual Interest Rate (%)": 7.5, "Term (Months)": 60},
            {"Facility Name": "Funding Circle Line", "Opening Balance (£)": 45000.0, "Annual Interest Rate (%)": 9.2, "Term (Months)": 48},
            {"Facility Name": "IWOCA Short-Term", "Opening Balance (£)": 35176.0, "Annual Interest Rate (%)": 12.0, "Term (Months)": 24}
        ]
    }

# --- 4. STEP 1: TRIAL BALANCE AND REVENUE VERIFICATION ---
st.markdown("### **Step 1: Core Operations Run-Rates**")
col1, col2, col3 = st.columns(3)
with col1:
    admin_input = st.number_input("Monthly Admin Overheads (£):", value=float(st.session_state["baseline_inputs"]["admin_overheads_monthly"]), step=500.0)
with col2:
    wages_input = st.number_input("Monthly Gross Staff Wages (£):", value=float(st.session_state["baseline_inputs"]["base_monthly_gross_wages"]), step=500.0)
with col3:
    pension_toggle = st.checkbox("Statutory Auto-Enrolment Opt-Out", value=st.session_state["baseline_inputs"]["pension_opt_out"])

# --- 5. STEP 2: DYNAMIC DEBT LIABILITIES CONFIGURATOR ---
st.markdown("---")
st.markdown("### **Step 2: Corporate Debt Liabilities Amortization Grid**")
st.caption("Configure outstanding debt liabilities below. The engine will automatically compile dynamic monthly principal vs. interest splits.")

# Convert session state dictionary array to editable pandas dataframe structure
current_debt_df = pd.DataFrame(st.session_state["baseline_inputs"]["debt_facilities"])

# Inject Streamlit's structural native data editor component
edited_debt_df = st.data_editor(
    current_debt_df,
    num_rows="dynamic", # Allows the user to add or delete rows on the fly
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
    # Map the edited tabular interface data back into our master model dictionary format
    formatted_debt_list = []
    for _, row in edited_debt_df.iterrows():
        formatted_debt_list.append({
            "facility_name": row["Facility Name"],
            "opening_balance": float(row["Opening Balance (£)"]),
            "interest_rate_annual": float(row["Annual Interest Rate (%)"]) / 100.0, # Convert percentage back to decimal multiplier
            "term_months": int(row["Term (Months)"])
        })
        
    # Write back to persistent browser state RAM
    st.session_state["baseline_inputs"]["admin_overheads_monthly"] = admin_input
    st.session_state["baseline_inputs"]["base_monthly_gross_wages"] = wages_input
    st.session_state["baseline_inputs"]["pension_opt_out"] = pension_toggle
    st.session_state["baseline_inputs"]["debt_facilities"] = edited_debt_df.to_dict(orient="records") # UI persistence
    
    # Pack optimized variants for core_engine use
    st.session_state["baseline_inputs"]["debt_facilities_clean"] = formatted_debt_list
    
    st.success("🎉 System parameters synchronized! Debt amortization loops successfully updated inside core calculation engines.")