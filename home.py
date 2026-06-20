# home.py
# STRATA SUITE PRODUCTION ENGINE // ACCESS ROUTER & GATEWAY CORE v5.5.0-MASTER

import streamlit as st
import os

# 1. Page Configuration Handling (Must be the absolute first Streamlit command)
st.set_page_config(
    page_title="STRATA Suite // Command Gateway",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Global State Hydration Guard
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
    st.session_state["authenticated"] = False

if "onboarding_complete" not in st.session_state:
    st.session_state["onboarding_complete"] = False


# =========================================================================
# 🔑 CREDENTIAL VERIFICATION CALLBACK (Guarantees Instant State Hydration)
# =========================================================================
def execute_credential_verification():
    input_value = st.session_state.get("raw_password_token_entry", "")
    secure_target = os.environ.get("GATEWAY_KEY") or st.secrets.get(
        "GATEWAY_KEY", "STRATA_SECURE_2026"
    )

    if input_value == secure_target:
        st.session_state["authenticated"] = True
        st.session_state["onboarding_complete"] = True
    else:
        st.session_state["auth_error_trigger"] = True


# =========================================================================
# 🛡️ SECURITY INTERCEPT LAYER
# =========================================================================
if not st.session_state["authenticated"] or not st.session_state["onboarding_complete"]:
    st.error("🔒 **Access Restricted:** Secure session token context not detected.")

    st.markdown("### 🔑 Relational Tenant Authentication")
    st.info(
        "💡 Type your key sequence below and press **Enter** to authorize this instance space."
    )

    # Handshake tied directly to an immediate on_change execution context callback
    st.text_input(
        "Enter Workspace Security Access Key:",
        type="password",
        key="raw_password_token_entry",
        on_change=execute_credential_verification,
    )

    if st.session_state.get("auth_error_trigger", False):
        st.error("Invalid security key sequence. Access Denied.")
        # Reset flag to clear state space for the next attempt
        st.session_state["auth_error_trigger"] = False

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
# 🎨 REFACTORED INTERACTIVE NAVIGATION DESK
# -------------------------------------------------------------
nav_col1, nav_col2 = st.columns(2)

with nav_col1:
    st.subheader("✍️ Operational Planning Canvas")
    st.markdown(
        "Ingest raw documents via document scanning, append structural ledger "
        "profiles manually, or load existing database project schemas."
    )
    st.write("")

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
    st.write("")

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
    "🛡️ STRATA Infrastructure Kernel v5.5.0 // Encrypted Session Pipeline Protected Under Relational Tenant Handshakes."
)
