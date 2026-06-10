# ui_skin/pages/4_🛡️_compliance.py
import sys
from pathlib import Path

# --- 1. CRITICAL PATH RESOLUTION ---
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

import streamlit as st

# --- 2. THE ABSOLUTE FIRST LINE SECURITY GATEKEEPER ---
# We force a hard-stop here before any data processing or page layouts compile
if "authenticated" not in st.session_state or not st.session_state["authenticated"] or "baseline_inputs" not in st.session_state:
    st.set_page_config(layout="wide", page_title="Access Denied")
    st.error("🔒 **Access Denied: Unauthorized Endpoints Locked**")
    st.info("This environment is shielded by an enterprise security framework. You must log in via the main portal to open this workspace.")
    if st.button("Return to Portal Landing Page", use_container_width=True):
        st.switch_page("home.py")
    st.stop()  # Completely kills downstream execution instantly

# --- 3. AFTER SECURITY CLEARANCE: STAND-UP COMPLIANCE RUNTIME ---
import pandas as pd
import numpy as np
from ui_skin.core_engine.master_model import generate_integrated_3way_forecast

st.set_page_config(layout="wide", page_title="Compliance & Payroll Deck")

st.title("🛡️ Corporate Compliance & Payroll Auditor")
st.caption("Statutory Tax Schedules, PAYE/NI Obligations, and Auto-Enrolment Pension Auditing")
st.markdown("---")

# Safely copy inputs now that we have absolute verification data exists
inputs_package = st.session_state["baseline_inputs"].copy()

# --- 4. RENDER STATIC STATUTORY REPORTS ---
st.markdown("### **Step 1: Statutory Payroll Burden Review**")
st.markdown("This section maps out corporate employer overhead obligations based on synchronized ingestion baselines.")

# Process baseline metrics through our unified master calculation engine wheel
try:
    compliance_matrix = generate_integrated_3way_forecast(inputs_package, overrides={})
    
    # Create a targeted compliance display dataframe
    months = compliance_matrix.index
    compliance_display = pd.DataFrame({
        "Gross Wages (£)": [inputs_package.get("base_monthly_gross_wages", 0.0)] * 60,
        "Director Salaries (£)": [inputs_package.get("directors_salaries_monthly", 0.0)] * 60,
        "Accrued Corp Tax (£)": compliance_matrix["Tax Expense (£)"],
        "HMRC Outstanding Balance (£)": compliance_matrix["Tax Liability BS (£)"]
    }, index=months)
    
    st.dataframe(
        compliance_display,
        use_container_width=True,
        column_config={col: st.column_config.NumberColumn(format="£%,.0f") for col in compliance_display.columns}
    )
except Exception as e:
    st.warning(f"Compliance ledger rendering paused until active inputs are fully locked on the ingestion screen.")