# pyright: reportMissingImports=false
# pages/onboarding.py
# STRATA SUITE PRODUCTION ENGINE // DATA INPUT PARAMETERS & SETUP WIZARD

import os
import sys
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.scenario_manager import render_global_scenario_sidebar

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
    st.warning("🔒 This workspace session is currently unauthenticated or has timed out.")
    if st.button("🔑 Return to Home Portal & Sign In", width="stretch"):
        st.switch_page("home.py")
    st.stop()

st.title("🕸️ Data Input Parameters & Configuration Wizard")
st.caption(f"Active Scenario Context: `{st.session_state.get('active_project_name', 'Unsaved_Draft_Scenario')}`")

st.markdown("---")
st.markdown("### Onboarding Setup & Parameters")
st.write("Configure baseline parameter defaults, corporate tax profiles, and initialization structures for your scenario workspace.")

if "onboarding_config" not in st.session_state:
    st.session_state["onboarding_config"] = {
        "business_model": "Padel Facility & Sports Club",
        "default_currency": "GBP (£)",
        "working_capital_buffer": 25000.0,
    }

config = st.session_state["onboarding_config"]
config["business_model"] = st.text_input("Business Model Classification", value=config.get("business_model", ""))
config["default_currency"] = st.selectbox("Base Reporting Currency", ["GBP (£)", "EUR (€)", "USD ($)"], index=0)
config["working_capital_buffer"] = st.number_input("Target Initial Working Capital Reserve (£)", value=float(config.get("working_capital_buffer", 25000.0)), step=5000.0)

if st.button("💾 Save Parameter Setup & Proceed to Data Entry", width="stretch"):
    st.success("✔️ Onboarding configuration updated successfully.")
    st.switch_page("pages/app.py")

st.markdown("---")

# =========================================================================
# 🧭 SIDEBAR COMPASS & SCENARIO CONTROL DESK
# =========================================================================
st.sidebar.markdown("### Compass Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link("pages/1_Data_Ingestion_Gateway.py", label="📥 Data Ingestion Gateway")
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry Panel")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")

render_global_scenario_sidebar()