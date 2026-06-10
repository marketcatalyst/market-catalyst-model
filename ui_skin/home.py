# ui_skin/home.py
import sys
from pathlib import Path

# --- 1. CRITICAL PATH RESOLUTION ---
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

import streamlit as st

st.set_page_config(layout="centered", page_title="STRATA Enterprise Portal")

# --- 2. GLOBAL SECURITY STATE INITIALIZATION ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

st.title("🔐 STRATA Enterprise Forecasting Portal")
st.caption("Secure Accounting Migration & Analytical Suite (WinForecast Compliance Pipeline)")
st.markdown("---")

# --- 3. SECURE CREDENTIAL SIGN-IN GATING ---
if st.session_state["authenticated"]:
    st.success("🔒 Your corporate session is active and authenticated.")
    if st.button("Enter Active Workspace Hub", use_container_width=True):
        st.switch_page("pages/1_🔌_ingestion.py")
else:
    # Safely look for configuration secrets
    if "workspace_credentials" not in st.secrets:
        st.error("❌ Configuration Error: 'workspace_credentials' block is missing from secrets configuration.")
        st.stop()
        
    target_user = st.secrets["workspace_credentials"]["username"]
    target_pass = st.secrets["workspace_credentials"]["password"]

    with st.form("login_form"):
        st.subheader("Corporate Workspace Sign-In")
        st.markdown("Please input your designated corporate credentials to verify identity and unlock your analytical endpoints.")
        
        username_input = st.text_input("Username:", placeholder="Enter your username")
        password_input = st.text_input("Password:", type="password", placeholder="••••••••")
        
        submit_button = st.form_submit_button("Authenticate & Initialize Session")

    if submit_button:
        # Cross-reference entered values with secret vaults
        if username_input == target_user and password_input == target_pass: 
            st.session_state["authenticated"] = True
            st.success("✅ Authentication successful! System state unlocked.")
            st.rerun()
        else:
            st.error("❌ Invalid Username or Password combination detected. Access denied.")

# --- 4. FOOTER TRACEABILITY ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.caption("STRATA Engine v1.4 • Data Security Layer Enforced")