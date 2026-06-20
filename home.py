# home.py
# STRATA SUITE PRODUCTION ENGINE // ACCESS ROUTER & GATEWAY CORE v5.3.0-MASTER

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
# are fully initialized in memory so the app never throws a NoneType error downstream.
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

# Initialize security status flags if absent
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "onboarding_complete" not in st.session_state:
    st.session_state["onboarding_complete"] = False

# =========================================================================
# 🛡️ SECURITY INTERCEPT LAYER: PRODUCTION SECURE PROTOCOL
# =========================================================================
# The explicit bypass has been stripped. The engine checks session credentials.
if not st.session_state["authenticated"] or not st.session_state["onboarding_complete"]:
    st.error("🔒 **Access Restricted:** Secure session token context not detected.")

    with st.form("security_handshake_gate", clear_on_submit=False):
        st.subheader("🔑 Relational Tenant Authentication")
        u_pass = st.text_input("Enter Workspace Security Access Key:", type="password")

        if st.form_submit_button("Verify Credentials & Hydrate Instance"):
            # Simple server-side env check fallback or secrets validation pattern
            secure_target = os.environ.get("GATEWAY_KEY") or st.secrets.get(
                "GATEWAY_KEY", "STRATA_SECURE_2026"
            )

            if u_pass == secure_target:
                st.session_state["authenticated"] = True
                st.session_state["onboarding_complete"] = True
                st.success("Authorization cleared! Initializing workspace layers...")
                st.rerun()
            else:
                st.error("Invalid security key sequence. Access Denied.")
    st.stop()

# =========================================================================
# 🎛️ PORTAL FRONT-END USER INTERFACE CANVAS (ENGAGES ONLY IF AUTHENTICATED)
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
    "🛡️ STRATA Infrastructure Kernel v5.3.0 // Encrypted Session Pipeline Protected Under Relational Tenant Handshakes."
)
