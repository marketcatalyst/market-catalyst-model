# home.py
# STRATA SUITE USER CONTROL MODULE // MASTER ACCESS GATEWAY

import streamlit as st
import sys
from pathlib import Path

# --- 1. THE ABSOLUTE FIRST SYSTEM CONFIGURATION COMMAND ---
st.set_page_config(layout="wide", page_title="STRATA Financial Intelligence Portal")

# Force tracking safety to isolate root modules cleanly
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

# --- 2. INITIALIZE SESSION STATE SECURITY ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- 3. SECURITY GATEKEEPER UX ---
if not st.session_state["authenticated"]:
    st.title("🔒 STRATA Security Access Gateway")
    st.caption("Enterprise Workspace Security Engine & Scenario Access Control Gateway")
    st.markdown("---")

    with st.form("identity_gate_form"):
        username = st.text_input("Corporate Username:")
        password = st.text_input("Security Access Key:", type="password")
        submit_auth = st.form_submit_button(
            "Authenticate Corporate Identity", use_container_width=True
        )

        if submit_auth:
            # Synchronised with your production security credentials
            if username.lower() == "marketcatalyst" and password == "@MCStrata080881":
                st.session_state["authenticated"] = True
                st.toast("✅ Workspace Identity Verified Successfully.")
                st.rerun()
            else:
                st.error("Authentication Fault: Invalid profile credentials.")
    st.stop()

# --- 4. CLEAN SAAS ROUTER: LINKING DIRECTLY TO UNIFIED MASTER COMPONENTS ---
try:
    # Explicitly map the multi-page console to your unified workspace core
    pg = st.navigation(
        {
            "Core Console": [
                st.Page("app.py", title="Interactive Data Workspace", icon="✍️"),
            ]
        },
        position="sidebar",
    )
    pg.run()
except Exception as e:
    st.error(
        f"Routing Fault: Streamlit engine could not map the dashboard page files. Details: {str(e)}"
    )
