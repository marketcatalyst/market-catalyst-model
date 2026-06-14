# app.py

import streamlit as st
import sys
from pathlib import Path
import os
import json

# --- 1. THE ABSOLUTE FIRST SYSTEM CONFIGURATION COMMAND ---
st.set_page_config(layout="wide", page_title="STRATA Financial Intelligence Portal")

root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

# Ensure nested subfolders are visible to the internal system interpreter
ui_skin_dir = root_dir / "ui_skin"
if ui_skin_dir.exists() and str(ui_skin_dir) not in sys.path:
    sys.path.append(str(ui_skin_dir))

# --- 2. DEFENSIVE SESSION STATE INITIALIZATION MATRIX ---
# All core tracking registers are explicitly instantiated here to safeguard
# dropdown elements and prevent structural key-value race conditions.
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "selected_project" not in st.session_state:
    st.session_state["selected_project"] = ""

if "active_project_name" not in st.session_state:
    st.session_state["active_project_name"] = ""

if "manual_sales_entries" not in st.session_state:
    st.session_state.manual_sales_entries = []

if "manual_opex_entries" not in st.session_state:
    st.session_state.manual_opex_entries = []

if "manual_capital_entries" not in st.session_state:
    st.session_state.manual_capital_entries = []

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

# --- 4. WELCOME EXECUTIVE BANNER ---
st.title("🛡️ STRATA // Financial Intelligence Portal")
st.caption("Active Environment: Market Catalyst Management Matrix")
st.markdown("---")

st.markdown("### 👋 Welcome back, Market Catalyst")
st.markdown("Select an existing active project modeling workspace below to open your dashboard suite:")

# --- 5. SYSTEM REGISTRY DATA LOOKUPS ---
PROJECTS_DIR = "saved_projects"
if not os.path.exists(PROJECTS_DIR):
    os.makedirs(PROJECTS_DIR)

# Auto-seed a standard template if the project folder lands completely empty
saved_files = [f.replace(".json", "") for f in os.listdir(PROJECTS_DIR) if f.endswith(".json") and not f.startswith("SANDBOX_VARIANT_")]
if not saved_files:
    default_template = {
        "sales": [{"name": "Standard Court Hire Inflow", "amount": 491000.0, "vat": 0.20}],
        "opex": [{"name": "Standard Ground Site Overheads", "amount": 145000.0, "vat": 0.20}],
        "capital": [
            {"name": "Initial Upfront Cash Cushion", "type": "Director / Equity Inflow", "value": 500000.0, "month": 1, "parameter": 0.0},
            {"name": "Infrastructure & Court Build", "type": "Fixed Asset Purchase", "value": 250000.0, "month": 1, "parameter": 10.0}
        ]
    }
    with open(os.path.join(PROJECTS_DIR, "Padel-Project-Standard-Baseline.json"), "w") as f:
        json.dump(default_template, f, indent=4)
    saved_files = ["Padel-Project-Standard-Baseline"]

# --- 6. WORKSPACE CONTEXT SECTOR ---
disabled_select = len(saved_files) == 0
dropdown_options = ["-- None Active --"] + saved_files
current_selection = st.session_state["selected_project"]

target_index = dropdown_options.index(current_selection) if current_selection in dropdown_options else 0

selected_box = st.selectbox(
    "Active Scenario Workspace Context Selector",
    options=dropdown_options,
    index=target_index,
    disabled=disabled_select
)

# Commit project binding rules cleanly back to state variables upon change
if selected_box != "-- None Active --" and not disabled_select:
    if st.session_state["selected_project"] != selected_box:
        st.session_state["selected_project"] = selected_box
        st.session_state["active_project_name"] = selected_box
        
        # Hydrate historical session variables from the selected JSON file context instantly
        with open(os.path.join(PROJECTS_DIR, f"{selected_box}.json"), "r") as pf:
            payload = json.load(pf)
        st.session_state.manual_sales_entries = payload.get("sales", [])
        st.session_state.manual_opex_entries = payload.get("opex", [])
        st.session_state.manual_capital_entries = payload.get("capital", [])
        st.success(f"Context mapped to workspace: `{selected_box}`. Use the sidebar menu to view reports.")
        st.rerun()

st.markdown("---")
st.info("💡 Use the sidebar navigation drawer to hop across into your dynamic workspaces and financial forecast sheets seamlessly.")

# --- 7. DYNAMIC PATH DISCOVERY RESOLUTION ---
pages_dir = Path("pages")
all_discovered_files = os.listdir(pages_dir) if pages_dir.exists() else []

def locate_target_page(file_prefix: str, fallback_path: str) -> str:
    for f_name in all_discovered_files:
        if f_name.startswith(file_prefix) and f_name.endswith(".py"):
            return f"pages/{f_name}"
    return fallback_path

# Target files mapped exactly to your root directory names without ingestion jargon
path_input_desk = locate_target_page("1_", "pages/1_✍️_Data_Input_Workspace.py")
path_sandbox    = locate_target_page("2_", "pages/2_🔮_sandbox.py")
path_forecast   = locate_target_page("3_", "pages/3_📊_forecast.py")
path_compliance = locate_target_page("4_", "pages/4_🛡️_compliance.py")

# --- 8. COMPILING THE SIDEBAR NAVIGATION ---
try:
    pg = st.navigation(
        {
            "Commercial Dashboards": [
                st.Page(path_input_desk, title="Data Input Workspace", icon="✍️"),
                st.Page(path_sandbox, title="Multi-Variant Sandbox", icon="🔮"),
                st.Page(path_forecast, title="Financial Forecast Sheets", icon="📊"),
                st.Page(path_compliance, title="Compliance & Tax Portal", icon="🛡️"),
            ]
        }, 
        position="sidebar"
    )
    pg.run()
except Exception as e:
    st.error(f"Routing Fault: Streamlit engine could not map the dashboard page files. Details: {str(e)}")