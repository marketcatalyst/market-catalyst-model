# home.py

import streamlit as st
import sys
from pathlib import Path
import os

# --- 1. THE ABSOLUTE FIRST SYSTEM CONFIGURATION COMMAND ---
st.set_page_config(layout="wide", page_title="STRATA Financial Intelligence Portal")

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

# Ensure nested subfolders are visible to the internal system interpreter
ui_skin_dir = root_dir / "ui_skin"
if ui_skin_dir.exists() and str(ui_skin_dir) not in sys.path:
    sys.path.append(str(ui_skin_dir))

# --- 2. INITIALIZE ENHANCED SESSION STATE SECURITY ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- 3. SECURITY GATEKEEPER ---
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

# --- 4. AUTOMATIC TRANS-STATEMENT COMPILATION HOOK ---
# Whenever a valid project baseline selection is loaded in session memory,
# trigger the background double-entry balancing engine to update the statements.
selected_project = st.session_state.get("selected_project", "")
if selected_project:
    project_file_path = os.path.join("saved_projects", f"{selected_project}.json")
    if os.path.exists(project_file_path):
        try:
            # Absolute structural import from our nested core folder path
            from ui_skin.core_engine.double_entry_matrix import compile_three_way_forecast
            compile_three_way_forecast(project_file_path)
        except Exception as engine_err:
            st.sidebar.error(f"⚠️ Calculation Engine Fault: {str(engine_err)}")

# --- 5. CLEAN OPERATIONAL REGISTRY DATA MATRIX ---
st.session_state["available_projects"] = {
    "Greenfield Project Alpha (Scenario 1)": {
        "opening_cash_balance": 0.00,
        "opening_fixed_assets_nbv": 0.00,
        "admin_overheads_monthly": 0.00,
        "base_monthly_gross_wages": 0.00,
        "directors_salaries_monthly": 0.00,
        "pension_opt_out": True,
        "y1_monthly_revenue_curve": [0.0] * 12,
        "debt_facilities": [
            {"Facility Name Description": "New Facility Entry", "Opening Principal Balance (£)": 0.00, "Annual Interest Rate (%)": 0.00, "Contractual Amortization Term (Months)": 12}
        ],
        "sales_locations": [
            {"Trading Location Name": "Primary Site", "Corporate Revenue Share (%)": 100.0, "Zero-Rated / Exempt Mix (%)": 0.0}
        ]
    }
}

# --- 6. DYNAMIC PATH DISCOVERY RESOLUTION ---
pages_dir = Path("pages")
all_discovered_files = os.listdir(pages_dir) if pages_dir.exists() else []

def locate_target_page(file_prefix: str, fallback_path: str) -> str:
    for f_name in all_discovered_files:
        if f_name.startswith(file_prefix) and f_name.endswith(".py"):
            return f"pages/{f_name}"
    return fallback_path

path_launcher = locate_target_page("0_", "pages/0_🛡️_launcher.py")
path_ingestion = locate_target_page("1_", "pages/1_🔌_ingestion.py")
path_sandbox = locate_target_page("2_", "pages/2_🔮_sandbox.py")
path_forecast = locate_target_page("3_", "pages/3_📊_forecast.py")
path_compliance = locate_target_page("4_", "pages/4_⚖️_compliance.py")

# --- 7. COMPILING THE REFINED SIDEBAR GRAPH ---
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