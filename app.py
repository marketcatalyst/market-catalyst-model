# app.py

import streamlit as st

# 1. Enforce global wide-screen layout configurations across the portal session
st.set_page_config(page_title="STRATA // Corporate Portal", page_icon="🛡️", layout="wide")

# 2. Initialize global session states in runtime memory
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "selected_project" not in st.session_state:
    st.session_state["selected_project"] = "None Activated"

# Dynamic portfolio initialization: Starts clean and empty if not yet tracking
if "project_portfolio" not in st.session_state:
    st.session_state["project_portfolio"] = []

# --- 🛠️ DYNAMIC STREAMLIT MULTI-PAGE NAVIGATION ROUTER ---
# FIXED: Removed the old launcher_page definition completely to resolve the file routing fault
login_page = st.Page("app.py", title="Security Gateway", icon="🔑")
data_input_page = st.Page("pages/1_✍️_Data_Input_Workspace.py", title="Data Input Workspace", icon="✍️")
sandbox_page = st.Page("pages/2_🔮_sandbox.py", title="Scenario Sandbox", icon="🔮")
forecast_page = st.Page("pages/3_📊_forecast.py", title="Forecast Ledger", icon="📊")
compliance_page = st.Page("pages/4_🛡️_compliance.py", title="Compliance Gateway", icon="🛡️")

if not st.session_state["authenticated"]:
    nav = st.navigation([login_page], position="sidebar")
else:
    # FIXED: Cleaned up mapping groups so that only actual existing script paths are compiled
    nav = st.navigation({
        "Core Portal": [login_page],
        "Modeling Workspaces": [data_input_page, sandbox_page],
        "Ledgers & Audits": [forecast_page, compliance_page]
    }, position="sidebar")

# --- 🔓 SECURE PORTAL RENDERING LAYER ---
if not st.session_state["authenticated"]:
    st.title("🛡️ STRATA // Financial Intelligence Portal")
    st.caption("Enterprise Workspace Security Engine & Scenario Access Control Gateway")
    st.markdown("---")
    
    st.subheader("🔑 Security Authentication Required")
    st.markdown("Please provide your authorized environment passphrase to hydrate calculation modules and unlock multi-page project workspaces.")
    
    login_col1, login_col2 = st.columns([1, 2])
    with login_col1:
        user_passphrase = st.text_input("Environment Passphrase", type="password", help="Enter your secure corporate access code.")
        submit_btn = st.button("Authorize Session", use_container_width=True)
        
    if submit_btn:
        if user_passphrase == "strata-catalyst-2026":
            st.session_state["authenticated"] = True
            st.session_state["username"] = "Market Catalyst"
            st.success("🔒 Session authorized. Synchronizing registry matrix...")
            st.rerun()
        else:
            st.error("❌ Invalid passphrase. Access denied to secure endpoints.")
else:
    if nav == login_page:
        st.title("🛡️ STRATA // Financial Intelligence Portal")
        st.caption(f"Active Environment: {st.session_state['username']} Management Matrix")
        st.markdown("---")
        
        st.subheader(f"👋 Welcome back, {st.session_state['username']}")
        st.markdown("Select an existing active project modeling workspace below, or mount a brand-new scenario matrix environment:")
        
        # --- PHASE 1: DYNAMIC WORKSPACE SELECTOR ---
        proj_box_col1, proj_box_col2 = st.columns([2, 1])
        
        with proj_box_col1:
            if not st.session_state["project_portfolio"]:
                options_list = ["No Active Models Found — Please Create a New Workspace Below"]
                disabled_select = True
            else:
                options_list = st.session_state["project_portfolio"]
                disabled_select = False
                
            chosen_proj = st.selectbox(
                "Select Active Project Environment", 
                options=options_list,
                disabled=disabled_select,
                index=0 if st.session_state["selected_project"] == "None Activated" or disabled_select else st.session_state["project_portfolio"].index(st.session_state["selected_project"])
            )
            
        with proj_box_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⚡ Activate Project Context", disabled=disabled_select, use_container_width=True):
                st.session_state["selected_project"] = chosen_proj
                st.success(f"📂 Workspace Context updated to: **{chosen_proj}**.")
                st.rerun()
                
        st.markdown("---")
        
        # --- PHASE 2: NEW MODEL ARCHITECTURE WORKSPACE FORGE ---
        st.subheader("🏗️ Forge New Model Environment")
        st.markdown("Type the name of your new asset or operational structure below to instantly provision a dedicated zero-based ledger:")
        
        forge_col1, forge_col2 = st.columns([2, 1])
        with forge_col1:
            new_project_name = st.text_input("New Project Description Name", placeholder="e.g., Ammanford Phase 1 Development or AVAWT Test Bed", label_visibility="collapsed")
        
        with forge_col2:
            if st.button("🔨 Forge New Workspace", use_container_width=True):
                clean_name = new_project_name.strip()
                if clean_name and clean_name not in st.session_state["project_portfolio"]:
                    st.session_state["project_portfolio"].append(clean_name)
                    st.session_state["selected_project"] = clean_name
                    st.session_state.manual_sales_entries = []
                    st.session_state.manual_opex_entries = []
                    st.session_state.manual_capital_entries = []
                    st.success(f"⚡ Success! Provisioned new environment: **{clean_name}**. Baseline matrices zeroed.")
                    st.rerun()
                elif clean_name in st.session_state["project_portfolio"]:
                    st.warning("⚠️ This project name already exists in your active portfolio matrix.")
                else:
                    st.error("❌ Project name description cannot be left blank.")
                    
        st.markdown("---")
        st.markdown(f"**Current Mounted Context:** `{st.session_state['selected_project']}`")
        st.info("Navigate through the sub-modules using the sidebar links to run scenario overrides, compile multi-year rolling forecasts, or audit regulatory frameworks.")
        
        if st.sidebar.button("🔒 Terminate Secure Session"):
            st.session_state["authenticated"] = False
            st.session_state["username"] = None
            st.session_state["selected_project"] = "None Activated"
            st.rerun()
    else:
        try:
            nav.run()
        except Exception as e:
            st.error(f"Navigation router execution error: {str(e)}")