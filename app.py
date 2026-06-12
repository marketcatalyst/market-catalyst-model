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

# Define your corporate project portfolio directory
PROJECT_PORTFOLIO = [
    "Ammanford 72-Home Development (Dragonboard DIPs)",
    "AEGIS Vacuum Insulated Composite Panel R&D",
    "Augmented Vertical Axis Wind Turbine (AVAWT) Joint Venture",
    "Swalek Ltd High-Voltage Energy Management Framework"
]

# --- 🛠️ DYNAMIC STREAMLIT MULTI-PAGE NAVIGATION ROUTER ---
# Define sub-pages explicitly using the modern st.Page constructor
login_page = st.Page("app.py", title="Security Gateway", icon="🔑")
data_input_page = st.Page("pages/1_✍️_Data_Input_Workspace.py", title="Data Input Workspace", icon="✍️")
sandbox_page = st.Page("pages/2_🔮_sandbox.py", title="Scenario Sandbox", icon="🔮")
forecast_page = st.Page("pages/3_📊_forecast.py", title="Forecast Ledger", icon="📊")
compliance_page = st.Page("pages/4_🛡️_compliance.py", title="Compliance Gateway", icon="🛡️")

# Build the sidebar navigation mapping based on active authentication state
if not st.session_state["authenticated"]:
    # If locked, only expose the root login page
    nav = st.navigation([login_page], position="sidebar")
else:
    # If verified, expose the full enterprise modeling suite grouped into structural categories
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
    # RUNTIME ROUTER: If verified, let st.navigation execute the active sidebar tab selection
    # If the user is on the home portal tab, render the main dashboard with the Project Selector
    if nav == login_page:
        st.title("🛡️ STRATA // Financial Intelligence Portal")
        st.caption(f"Active Environment: {st.session_state['username']} Management Matrix")
        st.markdown("---")
        
        st.subheader(f"👋 Welcome back, {st.session_state['username']}")
        st.markdown("Your secure runtime session is fully verified. Select an active project from the enterprise portfolio matrix below to mount its operational variables:")
        
        # --- PROJECT SELECTION PLATFORM PANEL ---
        proj_box_col1, proj_box_col2 = st.columns([2, 1])
        with proj_box_col1:
            chosen_proj = st.selectbox(
                "Select Active Project Environment", 
                options=PROJECT_PORTFOLIO,
                index=0 if st.session_state["selected_project"] == "None Activated" else PROJECT_PORTFOLIO.index(st.session_state["selected_project"])
            )
            
        if st.button("⚡ Activate Project Workspace Parameters", use_container_width=True):
            st.session_state["selected_project"] = chosen_proj
            st.success(f"📂 Workspace Context updated to: **{chosen_proj}**. Calculation models hydrated.")
            st.rerun()
            
        st.markdown("---")
        st.markdown(f"**Current Mounted Context:** `{st.session_state['selected_project']}`")
        st.info("Navigate through the sub-modules using the sidebar links to run scenario overrides, compile multi-year rolling forecasts, or audit regulatory frameworks.")
        
        # Explicit session termination button
        if st.sidebar.button("🔒 Terminate Secure Session"):
            st.session_state["authenticated"] = False
            st.session_state["username"] = None
            st.session_state["selected_project"] = "None Activated"
            st.rerun()
    else:
        # If any other page is selected in the sidebar, let it run natively inside this router frame
        try:
            nav.run()
        except Exception as e:
            st.error(f"Navigation router execution error: {str(e)}")