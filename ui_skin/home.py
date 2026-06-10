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

# --- 3. SECURE SIGN-IN GATING LOGIC ---
# If already authenticated, bypass the form and offer direct entrance
if st.session_state["authenticated"]:
    st.success("🔒 Your corporate session is active and authenticated.")
    if st.button("Enter Active Workspace Hub", use_container_width=True):
        st.switch_page("pages/1_🔌_ingestion.py")
else:
    # Render secure sign-in panel container
    with st.form("login_form"):
        st.subheader("Corporate Workspace Sign-In")
        st.markdown("Please input your designated operational passkey to initialize your baseline metrics and unlock your analytical endpoints.")
        
        user_password = st.text_input("Enter Workspace Security Passkey:", type="password")
        submit_button = st.form_submit_button("Authenticate & Initialize Session")

    if submit_button:
        # Secure credential gate comparison block
        # For security best practices, we cross-reference a set key. 
        # (You can also map this to st.secrets['passkeys'] later if preferred)
        if user_password == "STRATA2026!": 
            # Raise the master session token flag in hidden application RAM
            st.session_state["authenticated"] = True
            st.success("✅ Authentication successful! System state unlocked.")
            
            # Flush UI and reroute the authenticated session directly into Ingestion
            st.rerun()
        else:
            st.error("❌ Invalid passkey detected. Access denied. Please verify your credentials or contact system operations.")

# --- 4. OPTIONAL FOOTER TRACEABILITY ---
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.caption("STRATA Engine v1.4 • Data Security Layer Enforced")