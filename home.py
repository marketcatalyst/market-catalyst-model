import streamlit as st
import pandas as pd

# --- 1. INITIALIZE ENHANCED SESSION STATE SECURITY ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Force security barrier if credentials aren't initialized
if not st.session_state["authenticated"]:
    st.title("🔒 STRATA Security Access Gateway")
    st.caption("Enterprise Workspace Security Engine & Scenario Access Control Gateway")
    st.markdown("---")
    
    username = st.text_input("Corporate Username:")
    password = st.text_input("Security Access Key:", type="password")
    
    if st.button("Authenticate Corporate Identity", use_container_width=True):
        if username.lower() in ["admin", "marketcatalyst", "user2"] and password == "strata2026":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Authentication Fault: Invalid profile configuration credentials.")
    st.stop()

# --- 2. LOGGED IN PORTAL INTERFACE ---
st.title("🛡️ STRATA Financial Intelligence Portal")
st.caption("Enterprise Workspace Security Engine & Scenario Access Control Gateway")
st.markdown("---")

st.subheader("👋 Welcome back, Marketcatalyst")
st.write("Select an active project workspace below. The platform will dynamically hydrate your calculation modules, local tax shapes, and loan structures.")

# Define your real production workspace data configurations inside the registry
available_projects = {
    "Greenfield Project Alpha (Scenario 1)": {
        "opening_cash_balance": 150000.00,
        "opening_fixed_assets_nbv": 780000.00,
        "admin_overheads_monthly": 24500.00,
        "base_monthly_gross_wages": 16500.00,
        "directors_salaries_monthly": 6500.00,
        "pension_opt_out": False,
        "y1_monthly_revenue_curve": [120000.0, 145000.0, 160000.0, 185000.0, 190000.0, 210000.0, 225000.0, 240000.0, 265000.0, 280000.0, 310000.0, 335000.0],
        "debt_facilities": [
            {"Facility Name Description": "DBW Greenfield Loan", "Opening Principal Balance (£)": 120000.0, "Annual Interest Rate (%)": 6.5, "Contractual Amortization Term (Months)": 60}
        ],
        "sales_locations": [
            {"Trading Location Name": "Ammanford Site A", "Corporate Revenue Share (%)": 60.0, "Zero-Rated / Exempt Mix (%)": 10.0},
            {"Trading Location Name": "Swansea Testing Site", "Corporate Revenue Share (%)": 40.0, "Zero-Rated / Exempt Mix (%)": 20.0}
        ]
    },
    "AHOTG Multi-Shop Baseline (Scenario 2)": {
        "opening_cash_balance": 69488.00,
        "opening_fixed_assets_nbv": 531385.00,
        "admin_overheads_monthly": 18575.00,
        "base_monthly_gross_wages": 12000.00,
        "directors_salaries_monthly": 5150.00,
        "pension_opt_out": False,
        "y1_monthly_revenue_curve": [249310.0, 356310.0, 385200.0, 404460.0, 447260.0, 470800.0, 508785.0, 707525.0, 763067.0, 750127.0, 750025.0, 736017.0],
        "debt_facilities": [
            {"Facility Name Description": "DBW Tranche 1", "Opening Principal Balance (£)": 50000.0, "Annual Interest Rate (%)": 7.5, "Contractual Amortization Term (Months)": 60},
            {"Facility Name Description": "Funding Circle Line", "Opening Principal Balance (£)": 45000.0, "Annual Interest Rate (%)": 9.2, "Contractual Amortization Term (Months)": 48}
        ],
        "sales_locations": [
            {"Trading Location Name": "Bridgend Hub", "Corporate Revenue Share (%)": 40.0, "Zero-Rated / Exempt Mix (%)": 65.0},
            {"Trading Location Name": "Cardiff Bay Center", "Corporate Revenue Share (%)": 35.0, "Zero-Rated / Exempt Mix (%)": 0.0}
        ]
    }
}

selected_project_name = st.selectbox(
    "Available Corporate Environments Registries:",
    options=list(available_projects.keys()),
    key="portal_environment_selector"
)

# --- 3. THE HYDRATION EXECUTION LINK (CRITICAL COMPONENT) ---
st.markdown(" ")
if st.button(f"🚀 Hydrate Workspace & Launch [{selected_project_name}]", use_container_width=True):
    # Deep-copy properties into active session memory context
    st.session_state["baseline_inputs"] = available_projects[selected_project_name].copy()
    
    st.toast(f"Operational variables for {selected_project_name} successfully cached in RAM!", icon="🔥")
    st.success("✔️ Workspace Hydrated. Use the navigation sidebar to review active modules.")