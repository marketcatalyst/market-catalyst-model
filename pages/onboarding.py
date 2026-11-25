# pyright: reportMissingImports=false
# pages/onboarding.py
# STRATA SUITE PRODUCTION ENGINE // DATA INPUT PARAMETERS & SETUP WIZARD v11.14-SSOT

import os
import sys
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.scenario_manager import (
    DEFAULT_BLANK_SCENARIO,
    render_global_scenario_sidebar,
    save_scenario_to_disk,
)

st.markdown(
    """
    <style>
        div[data-testid="stSidebarNav"], 
        section[data-testid="stSidebarNav"], 
        ul[data-testid="stSidebarNav"], 
        .stSidebarNav {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.get("authenticated"):
    st.title("🏛️ STRATA // Security Intercept")
    st.warning(
        "🔒 This workspace session is currently unauthenticated or has timed out."
    )
    if st.button("🔑 Return to Home Portal & Sign In", use_container_width=True):
        st.switch_page("home.py")
    st.stop()

active_project = st.session_state.get("active_project_name", DEFAULT_BLANK_SCENARIO)

st.title("🕸️ Data Input Parameters & Configuration Wizard")
st.caption(f"Active Scenario Context: `{active_project}`")

st.markdown("---")
st.markdown("### Onboarding Setup & Parameters")
st.write(
    "Configure baseline parameter defaults, corporate tax profiles, and initialization structures for your scenario workspace."
)

if "onboarding_config" not in st.session_state:
    st.session_state["onboarding_config"] = {
        "business_model": "Standard Commercial Enterprise",
        "default_currency": "GBP (£)",
        "working_capital_buffer": 25000.0,
    }

config = st.session_state["onboarding_config"]
currencies = ["GBP (£)", "EUR (€)", "USD ($)"]
cur_idx = (
    currencies.index(config.get("default_currency", "GBP (£)"))
    if config.get("default_currency", "GBP (£)") in currencies
    else 0
)

config["business_model"] = st.text_input(
    "Business Model Classification", value=config.get("business_model", "")
)
config["default_currency"] = st.selectbox(
    "Base Reporting Currency", currencies, index=cur_idx
)
config["working_capital_buffer"] = st.number_input(
    "Target Initial Working Capital Reserve (£)",
    value=float(config.get("working_capital_buffer", 25000.0)),
    step=5000.0,
)

if st.button(
    "💾 Save Parameter Setup & Proceed to Data Entry", use_container_width=True
):
    current_state = st.session_state.get("active_data", {})
    current_curves = st.session_state.get("custom_curves", {})

    st.session_state["onboarding_config"] = config
    save_scenario_to_disk(active_project, current_state, current_curves)

    st.success(
        "✔️ Onboarding configuration updated and persisted to disk successfully."
    )
    st.switch_page("pages/app.py")

st.markdown("---")

# =========================================================================
# 🧭 SIDEBAR COMPASS & SCENARIO CONTROL DESK
# =========================================================================
st.sidebar.markdown("### Compass Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link(
    "pages/1_Data_Ingestion_Gateway.py", label="📥 Data Ingestion Gateway"
)
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry Panel")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")

render_global_scenario_sidebar()
