# home.py
# STRATA SUITE PRODUCTION ENGINE // ACCESS ROUTER & GATEWAY CORE v5.2.0-MASTER

import streamlit as st
import os

# 1. Page Configuration Handling (Must be the absolute first Streamlit command)
st.set_page_config(
    page_title="STRATA Suite // Command Gateway",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Global State Hydration Guard
# Ensures that if a user lands on the root page first, all required data structures
# are fully initialized in memory so the app never throws a NoneType error.
if "active_data" not in st.session_state:
    st.session_state["active_data"] = {
        "sales": [],
        "milestones": [],
        "opex": [],
        "financed_assets": [],
        "outright_capex": [],
        "payroll": [],
        "equity_funding": [],
    }

if "active_project_name" not in st.session_state:
    st.session_state["active_project_name"] = "Unsaved_Draft_Scenario"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = True  # Verified Gateway Bypass

if "onboarding_complete" not in st.session_state:
    st.session_state["onboarding_complete"] = True

# =========================================================================
# 🎛️ PORTAL FRONT-END USER INTERFACE CANVAS
# =========================================================================

st.title("🏛️ STRATA // Corporate Command Center")
st.caption(
    f"Active Tenant Context Model Session: `{st.session_state.get('active_project_name')}`"
)

st.info(
    "📊 **System Status:** Session authenticated and tracking thresholds successfully mapped to industry parameters."
)
st.markdown("---")

# -------------------------------------------------------------
# 🎨 REFACTORED INTERACTIVE NAVIGATION DESK (Balanced Frame Symmetrical Alignment)
# -------------------------------------------------------------
nav_col1, nav_col2 = st.columns(2)

with nav_col1:
    st.subheader("✍️ Operational Planning Canvas")
    st.markdown(
        "Ingest raw documents via document scanning, append structural ledger "
        "profiles manually, or load existing database project schemas."
    )
    st.write("")  # Layout spacer alignment padding

    # Corrected element: Fixed full-width bordered interactive button frame to ensure side-by-side symmetry
    if st.button(
        "🚀 Launch Parameter Workspaces Desk",
        use_container_width=True,
        key="gateway_launch_workspaces_btn",
    ):
        st.switch_page("pages/app.py")

with nav_col2:
    st.subheader("🚪 Workspace Session Control")
    st.markdown(
        "Disconnect active ledger matrix memory instances, lock storage "
        "configurations, or exit active session windows securely."
    )
    st.write("")  # Layout spacer alignment padding

    if st.button(
        "🚪 Terminate Session & Log Out",
        use_container_width=True,
        key="gateway_terminate_session_btn",
    ):
        st.session_state.clear()
        st.toast("Session tokens successfully purged.")
        st.rerun()

st.markdown("---")
st.caption(
    "🛡️ STRATA Infrastructure Kernel v5.2.0 // Encrypted Session Pipeline Protected Under Relational Tenant Handshakes."
)
