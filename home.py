import streamlit as st
import sys
from pathlib import Path
import os

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

# --- 4. DYNAMIC PATH DISCOVERY RESOLUTION ---
# This layer scans your physical directory to match file roots regardless of emojis.
pages_dir = Path("pages")
all_discovered_files = os.listdir(pages_dir) if pages_dir.exists() else []

def locate_target_page(file_prefix: str, fallback_path: str) -> str:
    for f_name in all_discovered_files:
        if f_name.startswith(file_prefix) and f_name.endswith(".py"):
            return f"pages/{f_name}"
    return fallback_path

# Resolve exact relative references dynamically from disk
path_launcher = locate_target_page("0_", "pages/0_🛡️_launcher.py")
path_ingestion = locate_target_page("1_", "pages/1_🔌_ingestion.py")
path_sandbox = locate_target_page("2_", "pages/2_🔮_sandbox.py")
path_forecast = locate_target_page("3_", "pages/3_📊_forecast.py")
path_compliance = locate_target_page("4_", "pages/4_⚖️_compliance.py")

# --- 5. COMPILING THE EXPANDED SIDEBAR GRAPH ---
try:
    pg = st.navigation(
        {
            "Core Console": [
                st.Page(path_launcher, title="Secure Portal Launcher", icon="🛡️", default=True),
            ],
            "Dashboards": [
                st.Page(path_ingestion, title="Data Ingestion Suite", icon="🔌"),
                st.Page(path_sandbox, title="Stewardship Sandbox", icon="🔮"),
                st.Page(path_forecast, title="Financial Forecast", icon="📊"),
                st.Page(path_compliance, title="Compliance & Tax Portal", icon="⚖️"),
            ]
        }, 
        position="sidebar"
    )
    pg.run()
except Exception as e:
    st.error(f"Routing Fault: Streamlit engine could not map the dashboard page files. Details: {str(e)}")