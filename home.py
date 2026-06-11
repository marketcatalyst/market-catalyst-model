import streamlit as st
import sys
from pathlib import Path

# --- 1. INITIAL SYSTEM STATE PARAMETERS ---
st.set_page_config(layout="wide", page_title="STRATA Financial Intelligence Portal")

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- 2. SECURITY GATEKEEPER ---
if not st.session_state["authenticated"]:
    st.title("🔒 STRATA Security Access Gateway")
    st.caption("Enterprise Workspace Security Engine & Scenario Access Control Gateway")
    st.markdown("---")
    
    username = st.text_input("Corporate Username:")
    password = st.text_input("Security Access Key:", type="password")
    
    if st.button("Authenticate Corporate Identity", use_container_width=True):
        if username.lower() in ["admin", "marketcatalyst", "user2"] and password == "strata2026":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Authentication Fault: Invalid profile credentials.")
    st.stop()

# --- 3. MASTER SCENARIO REGISTRY DATA MATRIX ---
st.session_state["available_projects"] = {
    "Greenfield Project Alpha (Scenario 1)": {
        "opening_cash_balance": 150000.00,
        "opening_fixed_assets_nbv": 780000.00,
        "admin_overheads_monthly": 24500.00,
        "base_monthly_gross_wages": 16500.00,
        "directors_salaries_monthly": 6500.00,
        "pension_opt_out": False,
        "y1_monthly_revenue_curve": [120000.0, 145000.0, 160000.0, 185000.0, 190000.0, 210000.0, 225000.0, 240000.0, 265000.0, 280000.0, 310000.0, 335000.0],
        "debt_facilities": [
            {"Facility Name Description": "DBW Greenfield Loan", "Opening Principal Balance (£)": 120000.0, "Annual Interest Rate (%)": 6.5, "Contractual Amortization Term (Months)": 60}
        ],
        "sales_locations": [
            {"Trading Location Name": "Ammanford Site A", "Corporate Revenue Share (%)": 60.0, "Zero-Rated / Exempt Mix (%)": 10.0},
            {"Trading Location Name": "Swansea Testing Site", "Corporate Revenue Share (%)": 40.0, "Zero-Rated / Exempt Mix (%)": 20.0}
        ]
    },
    "AHOTG Multi-Shop Baseline (Scenario 2)": {
        "opening_cash_balance": 69488.00,
        "opening_fixed_assets_nbv": 531385.00,
        "admin_overheads_monthly": 18575.00,
        "base_monthly_gross_wages": 12000.00,
        "directors_salaries_monthly": 5150.00,
        "pension_opt_out": False,
        "y1_monthly_revenue_curve": [249310.0, 356310.0, 385200.0, 404460.0, 447260.0, 470800.0, 508785.0, 707525.0, 763067.0, 750127.0, 750025.0, 736017.0],
        "debt_facilities": [
            {"Facility Name Description": "DBW Tranche 1", "Opening Principal Balance (£)": 50000.0, "Annual Interest Rate (%)": 7.5, "Contractual Amortization Term (Months)": 60},
            {"Facility Name Description": "Funding Circle Line", "Opening Principal Balance (£)": 45000.0, "Annual Interest Rate (%)": 9.2, "Contractual Amortization Term (Months)": 48}
        ],
        "sales_locations": [
            {"Trading Location Name": "Bridgend Hub", "Corporate Revenue Share (%)": 40.0, "Zero-Rated / Exempt Mix (%)": 65.0},
            {"Trading Location Name": "Cardiff Bay Center", "Corporate Revenue Share (%)": 35.0, "Zero-Rated / Exempt Mix (%)": 0.0}
        ]
    }
}

# --- 4. FULLY EXPANDED PROGRAMMATIC ROUTING GRAPH ---
# Here we declare and bind all active dashboard components across the platform
try:
    page_launcher = st.Page("pages/0_🛡️_launcher.py", title="Secure Portal Launcher", icon="🛡️", default=True)
    page_ingestion = st.Page("pages/1_🔌_ingestion.py", title="Data Ingestion Suite", icon="🔌")
    
    # Restored Page Assets
    page_sandbox = st.Page("pages/2_🔮_sandbox.py", title="Stewardship Sandbox", icon="🔮")
    page_forecast = st.Page("pages/3_📊_forecast.py", title="Financial Forecast", icon="📊")
    page_compliance = st.Page("pages/4_⚖️_compliance.py", title="Compliance & Tax Portal", icon="⚖️")
    
    # Mount the complete multi-page architecture tree to the sidebar
    pg = st.navigation(
        [page_launcher, page_ingestion, page_sandbox, page_forecast, page_compliance], 
        position="sidebar"
    )
    pg.run()
except Exception as e:
    st.error(f"Routing Fault: Streamlit engine could not compile paths. Details: {str(e)}")