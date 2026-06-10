# home.py
import streamlit as st
import sys
from pathlib import Path

# Critical Path Resolution
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from ui_skin.core_engine.project_registry import get_user_projects

st.set_page_config(layout="centered", page_title="STRATA Portal Landing")

st.title("🛡️ STRATA Financial Intelligence Portal")
st.caption("Enterprise Workspace Security Engine & Scenario Access Control Gateway")
st.markdown("---")

# 1. INITIALIZE AUTHORIZATION STATE VARIABLES
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# 2. RENDER LOGIN SCREEN IF NOT AUTHENTICATED
if not st.session_state["authenticated"]:
    st.subheader("Secure Session Sign-In")
    user_input = st.text_input("Corporate Username Identification:")
    pass_input = st.text_input("Security Access Passphrase:", type="password")
    
    if st.button("Authenticate Corporate Identity", use_container_width=True):
        # Demo credentials check (Accepts username 'admin' or 'user2' with password 'strata2026')
        if (user_input in ["admin", "user2"]) and pass_input == "strata2026":
            st.session_state["authenticated"] = True
            st.session_state["username"] = user_input
            st.success("🔒 Access Granted. Initializing authorized project files...")
            st.rerun()
        else:
            st.error("❌ Authentication Failed: Invalid credentials or unauthorized token signature.")

# 3. RENDER ENVIRONMENT SELECTOR Post-Authentication
else:
    current_user = st.session_state["username"]
    st.subheader(f"👋 Welcome back, {current_user.capitalize()}")
    st.markdown("Select an active project workspace below. The platform will dynamically hydrate your calculation modules, local tax shapes, and loan structures.")
    
    # Pull projects allocated to this user from the ledger
    available_projects = get_user_projects(current_user)
    
    if available_projects:
        # User dropdown select element
        selected_project_name = st.selectbox(
            "Available Corporate Environments Registries:",
            options=list(available_projects.keys())
        )
        
        st.markdown("---")
        
        # Hydration Trigger Action Button
        if st.button(f"🚀 Hydrate Workspace & Launch {selected_project_name}", use_container_width=True):
            # Overwrite active session baseline variables with the selected project dictionary snapshot
            st.session_state["baseline_inputs"] = available_projects[selected_project_name].copy()
            
            # Explicitly force clean translated data models to clear historical tracking states
            if "debt_facilities_clean" in st.session_state["baseline_inputs"]:
                del st.session_state["baseline_inputs"]["debt_facilities_clean"]
            if "sales_locations_clean" in st.session_state["baseline_inputs"]:
                del st.session_state["baseline_inputs"]["sales_locations_clean"]
                
            st.toast(f"🎉 Fully hydrated {selected_project_name} into operational RAM!", icon="🧠")
            st.success("✅ Engine synchronized! Use the sidebar navigation panel to manage your active modules.")
            
    else:
        st.warning("⚠️ No active project registries linked to your account profile. Contact your system controller.")
        
    if st.button("Log Out of Session", type="secondary", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
        if "baseline_inputs" in st.session_state:
            del st.session_state["baseline_inputs"]
        st.rerun()