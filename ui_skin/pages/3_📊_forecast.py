# ui_skin/pages/3_📊_forecast.py
import streamlit as st
import pandas as pd
from core_engine.master_model import generate_integrated_3way_forecast

st.set_page_config(layout="wide", page_title="3-Way Financial Statements")

st.title("📊 Integrated 3-Way Financial Projections")
st.caption("Master Reporting Terminal • Fully Synchronized Profit & Loss, Balance Sheet, and Cash Flow Projections")
st.markdown("---")

# --- 1. SAFE STATE CAPTURE & CONSOLIDATION ---
# Ensure the viewport loads gracefully even if a user bypasses the intake wizard
baseline = st.session_state.get("baseline_inputs", {
    "nominal_seasonal_sales_base": 600000.0 / 12,
    "fixed_contractual_sales_base": 60000.0 / 12,
    "nominal_cogs_base": 240000.0 / 12,
    "base_monthly_gross_wages": 180000.0 / 12,
    "admin_overheads_monthly": 72000.0 / 12,
    "directors_salaries_monthly": 5000.0,
    "pension_opt_out": False,
    "seasonality_weights": [1.0] * 12,
    "opening_cash_balance": 20000.0,
    "opening_fixed_assets_nbv": 150000.0,
    "opening_accounts_receivable": 10000.0,
    "opening_accounts_payable": 8000.0,
    "opening_long_term_debt": 50000.0,
    "opening_retained_earnings": 122000.0
})

# Safely extract the dynamic capex table from Page 1's data editor
capex_register = st.session_state.get("capex_asset_register", pd.DataFrame())

# Convert the UI DataFrame into a raw record list for the core engine array loop
if not capex_register.empty:
    planned_capex_list = capex_register.to_dict(orient="records")
else:
    planned_capex_list = []

# Construct the master computational payload pack
inputs_package = baseline.copy()
inputs_package["planned_capex_list"] = planned_capex_list

# Intercept active macro scenarios from Sandbox if selected
active_scenario = st.session_state.get("global_strategic_scenario", "Baseline Case")
if active_scenario == "Growth Expansion Case":
    inputs_package["nominal_seasonal_sales_base"] *= 1.15
elif active_scenario == "Supply-Chain Stress Case":
    inputs_package["nominal_seasonal_sales_base"] *= 0.80

# --- 2. RUN INTEGRATED THREE-WAY LEDGER PASS ---
try:
    forecast_df = generate_integrated_3way_forecast(inputs_package)
    engine_error = None
except Exception as e:
    engine_error = str(e)

# --- 3. EXPLICIT CALCULATED PERFORMANCE CARDS ---
if engine_error is None:
    total_turnover = forecast_df["Turnover (£)"].sum()
    total_net_profit = forecast_df["Net Profit (£)"].sum()
    final_bank_cash = forecast_df["Bank Cash Position (£)"].iloc[-1]
    
    st.subheader(f"📈 Performance Pulse Grid — [{active_scenario}]")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Simulated Total Horizon Turnover", value=f"£{total_turnover:,.2f}")
    with col2:
        st.metric(label="Cumulative Projected Net Profit", value=f"£{total_net_profit:,.2f}")
    with col3:
        st.metric(label="Month 60 Closing Liquidity Reserve", value=f"£{final_bank_cash:,.2f}")
        
    st.markdown("---")
    
    # --- 4. THE INTERACTIVE THREE-WAY REPORTING TABS ---
    tab_pl, tab_bs, tab_cf = st.tabs(["📈 Profit & Loss Statement", "⚖️ Balance Sheet Position", "💸 Cash Flow Bridges"])
    
    with tab_pl:
        st.markdown("### **Forecasted Statement of Comprehensive Income (P&L)**")
        st.markdown("Tracks localized operational metrics, rolling ingredient material usage burdens, and labor expenses.")
        
        pl_cols = ["Turnover (£)", "Direct Costs (£)", "Admin Overheads (£)", "Directors Salaries (£)", "Depreciation Expense (£)", "Net Profit (£)"]
        st.dataframe(forecast_df[pl_cols].T, use_container_width=True)
        
    with tab_bs:
        st.markdown("### **Forecasted Statement of Financial Position (Balance Sheet)**")
        st.markdown("Monitors asset-carrying values against ongoing organizational long-term debt facilities.")
        
        bs_cols = ["Fixed Asset NBV (£)", "Bank Cash Position (£)", "Accounts Payable & Debt (£)", "Retained Earnings (£)", "Double_Entry_Check"]
        
        # Highlight double-entry health status
        variance_check = forecast_df["Double_Entry_Check"].abs().max()
        if variance_check == 0.0:
            st.success("✔️ **Ledger Verification Passed:** Balanced double-entry mechanics maintained (Total Assets = Liabilities + Equity).")
        else:
            st.error(f"⚠️ **Ledger Variance Detected:** Maximum variance gap of £{variance_check:.2f} identified in time vectors.")
            
        st.dataframe(forecast_df[bs_cols].T, use_container_width=True)
        
    with tab_cf:
        st.markdown("### **Forecasted Indirect Statement of Cash Flows**")
        st.markdown("Bridges operational accounting profits back into liquid corporate bank positions by tracking spending changes.")
        
        cf_cols = ["Bridge: Net Profit", "Bridge: Depreciation", "Bridge: Operating CF", "Bridge: Investing CF", "Bridge: Financing CF", "Bridge: Net Movement"]
        st.dataframe(forecast_df[cf_cols].T, use_container_width=True)
        
    st.markdown("---")
    st.markdown("### 📊 Macro Capital Flight Path Horizon")
    st.line_chart(forecast_df[["Bank Cash Position (£)", "Accounts Payable & Debt (£)", "Fixed Asset NBV (£)"]])

else:
    st.error(f"❌ **Forecast Blocked:** Core computational orchestration failed during runtime processing. Reason: {engine_error}")