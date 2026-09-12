# home.py
# STRATA SUITE ACCESS GATEWAY // MAIN ENTRANCE PORTAL v8.0-PRODUCTION

import os
import sys
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.scenario_manager import (
    list_available_scenarios,
    load_scenario_from_disk,
    save_scenario_to_disk,
)

st.set_page_config(
    page_title="STRATA // Intelligence Suite", page_icon="🏛️", layout="wide"
)

st.markdown(
    """
    <style>
        div[data-testid="stSidebarNav"] {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "sic_profile" not in st.session_state:
    st.session_state["sic_profile"] = {
        "sic_code": "71121",
        "sector": "Professional R&D Services (Default)",
        "default_vat_type": "Standard 20%",
        "base_er_nic_rate": 0.138,
    }

if "active_data" not in st.session_state:
    st.session_state["active_data"] = {
        "sales": [],
        "milestones": [],
        "cogs": [],
        "opex": [],
        "financed_assets": [],
        "outright_capex": [],
        "payroll": [],
        "equity_funding": [],
    }
if "vector_couplings" not in st.session_state:
    st.session_state["vector_couplings"] = []
if "custom_curves" not in st.session_state:
    st.session_state["custom_curves"] = {}

if "active_project_name" not in st.session_state:
    st.session_state["active_project_name"] = "Padel_Centre_Baseline"


# --- GATEWAY VIEW 1: SECURE SIGN-IN PORTAL ---
if not st.session_state["authenticated"]:
    st.title("🏛️ STRATA // Financial Intelligence Gateway")
    st.markdown(
        "Please authenticate with your secure portal access tokens to open active forecast project workspaces."
    )
    st.markdown("---")

    login_col1, login_col2, login_col3 = st.columns([4, 4, 4])
    with login_col2:
        st.subheader("Executive Portal Access")
        with st.form("portal_login_form"):
            user_id = st.text_input(
                "User Name / Email Address:", placeholder="e.g. user@theperry.group"
            )
            user_key = st.text_input("Secure Access Key:", type="password")

            if st.form_submit_button(
                "🔒 Authenticate Secure Session", use_container_width=True
            ):
                if user_id and user_key:
                    st.session_state["authenticated"] = True
                    st.toast("Session authenticated successfully.")
                    st.rerun()
                else:
                    st.error("Please enter a valid User Name and Access Key.")
    st.stop()


# --- GATEWAY VIEW 2: EXECUTIVE PLATFORM HUB ---
st.title("🏛️ STRATA // Financial Intelligence Suite")
st.markdown("---")

st.subheader("📁 Project Workspace Directory Room")
p_col1, p_col2 = st.columns([6, 6])
with p_col1:
    avail_blueprints = list_available_scenarios()
    curr_active = st.session_state.get("active_project_name", "Padel_Centre_Baseline")
    
    options = ["-- Select Saved Project Scenario --"] + avail_blueprints
    selected_blueprint = st.selectbox(
        "Switch Active Project Model Context:",
        options=options,
    )
    if (
        selected_blueprint != "-- Select Saved Project Scenario --"
        and selected_blueprint != curr_active
    ):
        if load_scenario_from_disk(selected_blueprint):
            st.toast(f"Loaded Core State Matrix: {selected_blueprint}")
            st.rerun()

with p_col2:
    active_project_handle = st.text_input(
        "Create / Save Project Name Identifier:",
        value=curr_active,
    )
    if st.button("💾 Save Project Configuration", use_container_width=True):
        if active_project_handle.strip():
            save_scenario_to_disk(active_project_handle.strip())
            st.toast("Project Configuration committed successfully to disk!")
            st.rerun()

st.markdown("---")
st.subheader("🧭 Guided Corporate Optimization Pipeline")
st.info(
    f"💡 **Active Working Blueprint Instance Context:** `{st.session_state.get('active_project_name', 'Unsaved_Draft_Scenario')}`"
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("### 1️⃣ Data Ingestion")
    st.page_link(
        "pages/1_Data_Ingestion_Gateway.py",
        label="📥 Open Ingestion Gateway",
        use_container_width=True,
    )
with col2:
    st.markdown("### 2️⃣ Input Parameters")
    st.page_link(
        "pages/onboarding.py",
        label="🕸️ Open Parameters Panel",
        use_container_width=True,
    )
with col3:
    st.markdown("### 3️⃣ Data Entry Panel")
    st.page_link(
        "pages/app.py", label="✍️ Open Data Entry Panel", use_container_width=True
    )
with col4:
    st.markdown("### 4️⃣ Performance Tab")
    st.page_link(
        "pages/reports.py", label="📊 Open Performance Tab", use_container_width=True
    )

# --- RECONCILED NAVIGATION SIDEBAR ---
st.sidebar.markdown("### Compass Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link(
    "pages/1_Data_Ingestion_Gateway.py", label="📥 Data Ingestion Gateway"
)
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry Panel")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")

st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 Session Controls")

if st.sidebar.button("🚪 Log Off Session", use_container_width=True):
    st.session_state["authenticated"] = False
    st.toast("Session terminated safely.")
    st.rerun()