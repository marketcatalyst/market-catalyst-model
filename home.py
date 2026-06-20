# home.py
# STRATA SUITE PRODUCTION ENGINE // ACCESS ROUTER & GATEWAY CORE v5.7.0-MASTER

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

if "sic_profile" not in st.session_state:
    st.session_state["sic_profile"] = None

# Built-in UK SIC Regulatory Configuration Matrix Array
UK_SIC_REGULATORY_MATRIX = {
    "56100 - Restaurants and Mobile Food Services": {
        "sic_code": "56100",
        "sector": "Hospitality",
        "default_vat_type": "Standard 20%",
        "energy_vat_eligible": True,
        "base_er_nic_rate": 0.138,
        "macro_depreciation_baseline": 0.15,
    },
    "71121 - Domestic/Commercial Engineering Design": {
        "sic_code": "71121",
        "sector": "Professional R&D Services",
        "default_vat_type": "Standard 20%",
        "energy_vat_eligible": False,
        "base_er_nic_rate": 0.138,
        "macro_depreciation_baseline": 0.10,
    },
    "01110 - Growing of Cereals & Agricultural Crops": {
        "sic_code": "01110",
        "sector": "Agriculture",
        "default_vat_type": "Exempt / Zero 0%",
        "energy_vat_eligible": True,
        "base_er_nic_rate": 0.138,
        "macro_depreciation_baseline": 0.20,
    },
}


# =========================================================================
# 🔑 CREDENTIAL VERIFICATION CALLBACK
# =========================================================================
def execute_credential_verification():
    input_value = st.session_state.get("raw_password_token_entry", "")
    secure_target = os.environ.get("GATEWAY_KEY") or st.secrets.get(
        "GATEWAY_KEY", "STRATA_SECURE_2026"
    )

    if input_value == secure_target:
        st.session_state["authenticated"] = True
    else:
        st.session_state["auth_error_trigger"] = True


# =========================================================================
# 🛡️ STEP 1: SECURITY ACCESS VERIFICATION INTERCEPT
# =========================================================================
if not st.session_state["authenticated"]:
    st.error("🔒 **Access Restricted:** Secure session token context not detected.")
    st.markdown("### 🔑 Relational Tenant Authentication")

    st.text_input(
        "Enter Workspace Security Access Key:",
        type="password",
        key="raw_password_token_entry",
        on_change=execute_credential_verification,
    )

    if st.session_state.get("auth_error_trigger", False):
        st.error("Invalid security key sequence. Access Denied.")
        st.session_state["auth_error_trigger"] = False
    st.stop()

# =========================================================================
# 📋 STEP 2: MANDATORY UK SIC SECTOR MAPPING INTERCEPT
# =========================================================================
if not st.session_state["onboarding_complete"]:
    st.warning(
        "📋 **Onboarding Protocol Active:** Establish your standard industrial parameters before launching workspace environments."
    )
    st.markdown("### 🏗️ Standard Industrial Classification (SIC) Selection")
    st.info(
        "The selected industry profile injects sector-specific tax baselines, depreciation thresholds, and VAT configurations automatically."
    )

    selected_sic_label = st.selectbox(
        "Select Active Corporate Mapping Variant (UK SIC Code Grid):",
        ["-- Click to Select Verified Sector Profile --"]
        + list(UK_SIC_REGULATORY_MATRIX.keys()),
    )

    if st.button(
        "🚀 Confirm Industry Mapping & Hydrate Ledger Rules", use_container_width=True
    ):
        if selected_sic_label != "-- Click to Select Verified Sector Profile --":
            profile_data = UK_SIC_REGULATORY_MATRIX[selected_sic_label]

            # Commit the regulatory profile structural array data directly onto the session cache space
            st.session_state["sic_profile"] = profile_data
            st.session_state["onboarding_complete"] = True
            st.success(
                f"Successfully mapped rules for sector: {profile_data['sector']}"
            )
            st.rerun()
        else:
            st.error(
                "Please pick a valid industry code block to initialize macro frameworks."
            )
    st.stop()

# =========================================================================
# 🎛️ PORTAL FRONT-END USER INTERFACE CANVAS (ENGAGES ONLY IF STEP 1 & 2 CLEAR)
# =========================================================================

st.title("🏛️ STRATA // Corporate Command Center")

active_sic = st.session_state["sic_profile"]
st.markdown(
    f"🏭 **Active Industry Scope:** Code `{active_sic['sic_code']}` ({active_sic['sector']}) | "
    f"Tax Burden Base: `{active_sic['base_er_nic_rate']*100}%` ER NIC | "
    f"Asset Depr: `{active_sic['macro_depreciation_baseline']*100}%` straight-line"
)

st.info(
    "📊 **System Status:** Session authenticated and tracking thresholds successfully mapped to industry parameters."
)
st.markdown("---")

# -------------------------------------------------------------
# 🎨 INTERACTIVE NAVIGATION DESK (Framed, Balanced, Symmetrical)
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
        # Explicitly loop and clear state keys to fix the state-retention bug
        keys_to_clear = [k for k in st.session_state.keys()]
        for key in keys_to_clear:
            st.session_state.pop(key)
        st.toast("Session tokens successfully purged.")
        st.rerun()

st.markdown("---")
st.caption(
    "🛡️ STRATA Infrastructure Kernel v5.7.0 // Encrypted Session Pipeline Protected Under Relational Tenant Handshakes."
)
