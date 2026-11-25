# home.py
# STRATA SUITE ACCESS GATEWAY // MAIN ENTRANCE PORTAL v12.0-SSOT-BLANK-CLIENT

import os
import sys
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.scenario_manager import (
    DEFAULT_BLANK_SCENARIO,
    create_blank_scenario,
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
        "cogs": [],
        "opex": [],
        "payroll": [],
        "financed_assets": [],
        "outright_capex": [],
        "equity_funding": [],
    }
if "vector_couplings" not in st.session_state:
    st.session_state["vector_couplings"] = []
if "custom_curves" not in st.session_state:
    st.session_state["custom_curves"] = {}
if "scratchpad_queue" not in st.session_state:
    st.session_state["scratchpad_queue"] = []
if "cached_ai_analysis" not in st.session_state:
    st.session_state["cached_ai_analysis"] = ""

available_on_boot = list_available_scenarios()
default_active = available_on_boot[0] if available_on_boot else DEFAULT_BLANK_SCENARIO
if (
    "active_project_name" not in st.session_state
    or not st.session_state["active_project_name"]
):
    st.session_state["active_project_name"] = default_active


def wipe_slate_for_new_client(project_name: str):
    clean_name = create_blank_scenario(project_name or DEFAULT_BLANK_SCENARIO)
    st.session_state["scratchpad_queue"] = []
    st.session_state["cached_ai_analysis"] = ""
    return clean_name


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
curr_active = st.session_state.get("active_project_name", DEFAULT_BLANK_SCENARIO)
avail_blueprints = list_available_scenarios()

p_col1, p_col2, p_col3 = st.columns([4, 4, 4])

with p_col1:
    options = ["-- Select Saved Project Scenario --"] + avail_blueprints
    selected_blueprint = st.selectbox(
        "Switch Existing Project Scenario:",
        options=options,
    )
    if (
        selected_blueprint != "-- Select Saved Project Scenario --"
        and selected_blueprint != curr_active
    ):
        loaded_data = load_scenario_from_disk(selected_blueprint)
        if loaded_data:
            st.session_state["active_project_name"] = selected_blueprint
            st.session_state["active_data"] = loaded_data.get("active_data", {})
            st.session_state["custom_curves"] = loaded_data.get("custom_curves", {})
            st.session_state["vector_couplings"] = loaded_data.get(
                "vector_couplings", []
            )
            st.session_state["cached_ai_analysis"] = ""
            st.toast(f"Loaded Core State Matrix: {selected_blueprint}")
            st.rerun()

with p_col2:
    new_client_name = st.text_input(
        "New Client / Project Name:",
        placeholder="e.g. Acme_Ltd_Baseline",
        key="home_new_client_input",
    )
    if st.button("✨ Start New Blank Project", use_container_width=True):
        created_name = wipe_slate_for_new_client(new_client_name)
        st.toast(f"Started clean blank project: {created_name}")
        st.rerun()

with p_col3:
    rename_or_save_name = st.text_input(
        "Save Current Project As:",
        value=curr_active,
        key="home_save_current_input",
    )
    if st.button("💾 Save Current Project", use_container_width=True):
        if rename_or_save_name.strip():
            clean_name = rename_or_save_name.strip().replace(" ", "_")
            save_scenario_to_disk(
                clean_name,
                st.session_state.get("active_data", {}),
                st.session_state.get("custom_curves", {}),
            )
            st.session_state["active_project_name"] = clean_name
            st.toast(f"Saved project '{clean_name}' to disk!")
            st.rerun()

st.markdown("---")
st.subheader("🧭 Guided Corporate Optimization Pipeline")
st.info(
    f"💡 **Active Working Blueprint Instance Context:** `{st.session_state.get('active_project_name', DEFAULT_BLANK_SCENARIO)}`"
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

if st.sidebar.button("🧹 Reset to Blank Client", use_container_width=True):
    wipe_slate_for_new_client(DEFAULT_BLANK_SCENARIO)
    st.sidebar.success("Workspace reset to a clean blank client!")
    st.rerun()

if st.sidebar.button("🚪 Log Off Session", use_container_width=True):
    st.session_state["authenticated"] = False
    st.toast("Session terminated safely.")
    st.rerun()
