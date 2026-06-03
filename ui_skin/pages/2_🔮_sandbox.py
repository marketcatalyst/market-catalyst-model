# ui_skin/pages/2_🧪_sandbox.py
import streamlit as st
import pandas as pd
from core_engine.master_model import generate_integrated_3way_forecast

st.set_page_config(layout="wide", page_title="Financial Sandbox")

st.title("🧪 Strategic Scenario Sandbox Playground")
st.caption("Isolated Risk Assessment Environment • Stress-Test Market Projections Without Changing Core Ledger Values")
st.markdown("---")

# --- SaaS Asset Class Mapping Configuration Bridge ---
# Translates user-friendly business logic to our abstract core backend codes
ASSET_TYPE_PRESETS = {
    "Industrial Kitchen Machinery / Ovens": {"code": "AIA_100", "uel": 120, "residual_pct": 0.15, "mult": 1.25},
    "Refrigerated Delivery Vans": {"code": "AIA_100", "uel": 60, "residual_pct": 0.20, "mult": 1.00},
    "Facility Outfitting & Integral Features": {"code": "WDA_SPECIAL", "uel": 180, "residual_pct": 0.00, "mult": 1.10},
    "Standard Office / Administrative Assets": {"code": "WDA_MAIN", "uel": 36, "residual_pct": 0.05, "mult": 1.00}
}

# Initialize global scenario option in session memory state
if "global_strategic_scenario" not in st.session_state:
    st.session_state.global_strategic_scenario = "Baseline Case"

# --- Layout Grid: Macro Scenario Selector ---
st.subheader("⚙️ Select Global Forecast Strategy Path")
chosen_scenario = st.selectbox(
    "Choose active scenario track to simulate across all core statements:",
    options=["Baseline Case", "Growth Expansion Case", "Supply-Chain Stress Case"],
    index=["Baseline Case", "Growth Expansion Case", "Supply-Chain Stress Case"].index(st.session_state.global_strategic_scenario),
    key="sandbox_scenario_selector"
)

# Apply context callout boxes explaining the parameters of each scenario
if chosen_scenario == "Baseline Case":
    st.success("🟢 **Baseline Mode Active:** Operating with direct user-defined slider metrics exactly.")
elif chosen_scenario == "Growth Expansion Case":
    st.info("🚀 **Growth Mode Active:** Simulating an automatic +15% surge in monthly turnover projections.")
elif chosen_scenario == "Supply-Chain Stress Case":
    st.warning("⚠️ **Stress-Test Mode Active:** Simulating an economic contraction that drops turnover by -20% across the board.")

st.markdown("---")

# --- Interactive Sidebar Controls ---
st.sidebar.header("📅 Simulation Boundaries")
sb_horizon = st.sidebar.slider("Simulation Horizon (Months)", 12, 60, 60, 12)

st.sidebar.header("💸 Core Operational Controls")
ui_sales = st.sidebar.number_input("Target Monthly Sales (£)", min_value=0.0, value=50000.0, step=2500.0)
ui_direct_costs = st.sidebar.number_input("Baseline Direct Costs (£)", min_value=0.0, value=22000.0, step=1000.0)
ui_admin = st.sidebar.number_input("Admin Overheads (£)", min_value=0.0, value=8000.0, step=500.0)
ui_directors = st.sidebar.number_input("Directors Salaries (£)", min_value=0.0, value=5000.0, step=500.0)

st.sidebar.header("👥 Workforce Payroll Controls")
ui_gross_wages = st.sidebar.number_input("Monthly Staff Gross Wages (£)", min_value=0.0, value=12000.0, step=500.0)
ui_pension_opt = st.sidebar.checkbox("Simulate Workforce Pension Opt-Out", value=False)

st.sidebar.header("🏗️ Planned Capital Expenditures")
enable_capex = st.sidebar.checkbox("Include Planned CapEx Event", value=False)

# Initialize default empty CapEx variables
ui_asset_cost = 0.0
ui_purchase_month = -1
ui_selected_preset = "Standard Office / Administrative Assets"
ui_custom_residual = 0.0

if enable_capex:
    ui_asset_cost = st.sidebar.number_input("Asset Purchase Price (£)", min_value=0.0, value=25000.0, step=1000.0)
    ui_purchase_month = st.sidebar.slider("Purchase Month Index", 0, sb_horizon - 1, 3)
    ui_selected_preset = st.sidebar.selectbox("Infrastructure Type / Industry Profile", options=list(ASSET_TYPE_PRESETS.keys()))
    ui_custom_residual = st.sidebar.number_input("Estimated Asset Residual Value (£)", min_value=0.0, value=ui_asset_cost * ASSET_TYPE_PRESETS[ui_selected_preset]["residual_pct"])

# --- Macro Scenario Modifier Math ---
# Apply systemic variations based on the active scenario toggle choice
final_sales_input = ui_sales
if chosen_scenario == "Growth Expansion Case":
    final_sales_input = ui_sales * 1.15
elif chosen_scenario == "Supply-Chain Stress Case":
    final_sales_input = ui_sales * 0.80

# --- Package Inputs for the Master Coordination Engine ---
inputs_package = {
    "target_monthly_sales": final_sales_input,
    "base_monthly_gross_wages": ui_gross_wages,
    "pension_opt_out": ui_pension_opt,
    "direct_costs_monthly": ui_direct_costs,
    "admin_overheads_monthly": ui_admin,
    "directors_salaries_monthly": ui_directors,
    "opening_cash_balance": 15000.0, # Seed baseline
    "opening_retained_earnings": 15000.0,
    
    # CapEx parameters
    "planned_asset_cost": ui_asset_cost,
    "planned_asset_purchase_month_index": ui_purchase_month,
    "planned_asset_uel_months": ASSET_TYPE_PRESETS[ui_selected_preset]["uel"],
    "planned_asset_residual_value": ui_custom_residual,
    "planned_asset_tax_code": ASSET_TYPE_PRESETS[ui_selected_preset]["code"],
    "planned_asset_systemic_multiplier": ASSET_TYPE_PRESETS[ui_selected_preset]["mult"]
}

# --- Execution Row ---
if st.button("Execute High-Speed Sandbox Simulation", use_container_width=True, type="primary"):
    st.session_state.global_strategic_scenario = chosen_scenario
    
    # Fire the unified master forecast engine
    sandbox_df = generate_integrated_3way_forecast(inputs_package)
    
    # Trim dataframe rows to match user selected horizon slider
    sandbox_df = sandbox_df.iloc[:sb_horizon]
    
    if sandbox_df is not None:
        st.markdown("### 📊 Scenario Trajectory Visualizations")
        
        # Split visualizations into clean columns for scannability
        col1, col2 = st.columns(2)
        
        with col1:
            st.caption("📈 **Revenue vs. Net Profit Performance Runway (£)**")
            st.line_chart(sandbox_df[["Turnover (£)", "Net Profit (£)"]], y_label="Value (£)")
            
        with col2:
            st.caption("💰 **3-Way Cash Position & Capital Asset Net Book Value (£)**")
            st.line_chart(sandbox_df[["Bank Cash Position (£)", "Fixed Asset NBV (£)"]], y_label="Value (£)")
            
        # Display workforce analytics
        st.markdown("### 👥 Operational Resource Strain Analysis")
        st.info(f"👷 **Simulated Kitchen / Team Capacity Allocation:** {sandbox_df['Ops_FTE_Strain'].iloc[0]} FTE Base Load Requirement.")
        
        # Dataframe Inspector Row
        with st.expander("🗃️ Inspect Raw Simulation Output Ledger Data Frame", expanded=False):
            st.dataframe(sandbox_df, use_container_width=True, hide_index=False)