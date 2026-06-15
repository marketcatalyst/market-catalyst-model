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

# --- 3. DYNAMIC PATH DISCOVERY RESOLUTION ---
pages_dir = Path("pages")
all_discovered_files = os.listdir(pages_dir) if pages_dir.exists() else []

def locate_target_page(file_prefix: str, fallback_path: str) -> str:
    for f_name in all_discovered_files:
        if f_name.startswith(file_prefix) and f_name.endswith(".py"):
            return f"pages/{f_name}"
    return fallback_path

path_input_desk = locate_target_page("1_", "pages/1_✍️_Data_Input_Workspace.py")
path_sandbox    = locate_target_page("2_", "pages/2_🔮_sandbox.py")
path_forecast   = locate_target_page("3_", "pages/3_📊_forecast.py")
path_compliance = locate_target_page("4_", "pages/4_🛡️_compliance.py")

# --- 4. STATIC LAUNCHPAD DESK DISPLAY LAYOUT ---
def render_landing_launchpad():
    st.title("🛡️ STRATA // Financial Intelligence Portal")
    st.caption("Active Environment: Market Catalyst Management Matrix")
    st.markdown("---")

    st.markdown("### 👋 Welcome back, Market Catalyst")
    st.markdown("To begin modeling your business scenario, you can either select an existing project template from the dropdown below or jump straight into a fresh workspace:")

    PROJECTS_DIR = "saved_projects"
    if not os.path.exists(PROJECTS_DIR):
        os.makedirs(PROJECTS_DIR)

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

    disabled_select = len(saved_files) == 0
    dropdown_options = ["-- None Active / Start Fresh --"] + saved_files
    current_selection = st.session_state["selected_project"]

    target_index = dropdown_options.index(current_selection) if current_selection in dropdown_options else 0

    selected_box = st.selectbox(
        "Active Scenario Workspace Context Selector",
        options=dropdown_options,
        index=target_index,
        disabled=disabled_select
    )

    if selected_box != "-- None Active / Start Fresh --" and not disabled_select:
        if st.session_state["selected_project"] != selected_box:
            st.session_state["selected_project"] = selected_box
            st.session_state["active_project_name"] = selected_box
            
            with open(os.path.join(PROJECTS_DIR, f"{selected_box}.json"), "r") as pf:
                payload = json.load(pf)
            st.session_state.manual_sales_entries = payload.get("sales", [])
            st.session_state.manual_opex_entries = payload.get("opex", [])
            st.session_state.manual_capital_entries = payload.get("capital", [])
            st.success(f"📁 Workspace context mapped to: `{selected_box}`. Use the sidebar menu to navigate.")
            st.rerun()

    st.markdown("---")
    
    # --- ENCOURAGING ONBOARDING ACTION LOGIC ---
    if st.session_state.get("selected_project"):
        st.info(f"📁 Active Scenario Loaded: `{st.session_state['selected_project']}`. Ready to review forecasts or tweak parameters.")
    else:
        st.markdown("### ✨ Ready to start fresh?")
        st.markdown("Click the action button below to head straight into the manual data entry panels where we will construct your custom business matrix lines step-by-step.")
        
        # Friendly, high-visibility guidance redirection link
        if st.button("✍️ Open Data Input Workspace", use_container_width=True):
            st.switch_page(path_input_desk)

    # --- 💡 ONSCREEN PROMPT / INTERACTIVE GUIDANCE SUITE ---
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("💡 New to STRATA? Click here for a quick guidance walkthrough", expanded=False):
        st.markdown("""
        #### 🗺️ Navigating your Business Stress-Test
        Don't worry about breaking the model—this framework is designed for exploration! Here is how your journey unfolds:
        
        * **Step 1: Data Input Workspace** ➔ This is where you outline your numbers. You'll input your basic income streams, recurring overhead costs, and large capital/financing events. 
        * **Step 2: Financial Forecast Sheets** ➔ Once your lines are entered, head over here to see your Profit & Loss, compounding Cash flow trajectory, and corporate worth calculated across a 60-month horizon automatically.
        * **Step 3: Multi-Variant Sandbox** ➔ Want to run a 'What-If' risk review? The sandbox allows you to alter your baseline parameters defensively without corrupting your master file.
        
        *Need immediate help? Look for the dynamic help tabs embedded at the top of each operational page.*
        """)

# --- 5. COMPILING THE DYNAMIC SIDEBAR NAVIGATION GATEWAY ---
try:
    page_launchpad  = st.Page(render_landing_launchpad, title="Project Setup Hub", icon="🛡️")
    page_input      = st.Page(path_input_desk, title="Data Input Workspace", icon="✍️")
    page_sandbox    = st.Page(path_sandbox, title="Multi-Variant Sandbox", icon="🔮")
    page_forecast   = st.Page(path_forecast, title="Financial Forecast Sheets", icon="📊")
    page_compliance = st.Page(path_compliance, title="Compliance & Tax Portal", icon="🛡️")

    if not st.session_state["authenticated"]:
        sidebar_mapping = {
            "Workspace Gateway": [page_launchpad]
        }
    else:
        sidebar_mapping = {
            "Workspace Manager": [page_launchpad],
            "Financial Forecasting Suite": [page_input, page_sandbox, page_forecast, page_compliance]
        }

    pg = st.navigation(sidebar_mapping, position="sidebar")
except Exception as e:
    st.error(f"Routing Fault: Streamlit engine could not map the dashboard page files. Details: {str(e)}")
    st.stop()

# --- 6. SECURITY GATEKEEPER INTERCEPT ---
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
            
    st.sidebar.info("🔑 Standing By // Verification Required")
    st.stop()

# --- 7. GLOBAL SIDEBAR UTILITIES (AUTHENTICATED ONLY) ---
active_target = st.session_state.get("selected_project", "")
if active_target:
    st.sidebar.markdown(f"**📁 Active Workspace:**\n`{active_target}`")
    if st.sidebar.button("🔄 Clear & Switch Project", use_container_width=True):
        st.session_state["selected_project"] = ""
        st.session_state["active_project_name"] = ""
        st.rerun()
else:
    st.sidebar.info("📁 Ready to Build // Awaiting Context")

st.sidebar.markdown("---")

# --- 8. UNCONDITIONAL SYSTEM EXECUTION ---
pg.run()