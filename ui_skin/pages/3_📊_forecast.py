# ui_skin/pages/3_📊_forecast.py
import streamlit as st
import pandas as pd
import numpy as np

# Native Workspace Root Import targeting our verified nested path
import ui_skin.core_engine.forecast_formulas as ff

st.set_page_config(layout="wide", page_title="3-Way Financial Forecast")

st.title("📊 Primary 3-Way Integrated Forecast")
st.caption("Core Financial Reporting Layer • Professional Multi-Statement Ledger Framework")
st.markdown("---")

# Global Starting Baselines
STARTING_CASH_BASELINE = 500000.00

# ==========================================
# 📊 DATA AGGREGATION LINKAGE LAYER
# ==========================================
# Extract baseline figures directly from the user's live Ingestion Trial Balance matrix
if "trial_balance_matrix" in st.session_state:
    tb_df = st.session_state.trial_balance_matrix.copy()
    
    # Coerce data types to ensure arithmetic stability
    tb_df["Amount (£)"] = pd.to_numeric(tb_df["Amount (£)"], errors="coerce").fillna(0.0)
    
    # Dynamically extract and sum baseline rows assigned to each bucket
    derived_sales = float(tb_df[tb_df["Accounting Allocation Bucket"] == "Revenue"]["Amount (£)"].sum())
    derived_wages = float(tb_df[tb_df["Accounting Allocation Bucket"] == "Gross Wages"]["Amount (£)"].sum())
    derived_cogs  = float(tb_df[tb_df["Accounting Allocation Bucket"] == "Direct Expenses (COGS)"]["Amount (£)"].sum())
    derived_opex  = float(tb_df[tb_df["Accounting Allocation Bucket"] == "Indirect Overheads (OpEx)"]["Amount (£)"].sum())
    
    # Dynamically compute base Gross Profit Margin from ingestion inputs
    if derived_sales > 0:
        derived_gp_pct = ((derived_sales - derived_cogs) / derived_sales) * 100.0
    else:
        derived_gp_pct = 65.0 # Stable fallback if matrix sales are empty
else:
    # Safe fallback standards if the Ingestion matrix session layer hasn't initialized
    derived_sales, derived_wages, derived_opex, derived_gp_pct = 100000.00, 8672.57, 15000.00, 65.0

# ==========================================
# 📈 INTERACTIVE SCENARIO MATRIX INPUT SHEET
# ==========================================
st.subheader("🚀 Strategic Macro Scenario Configuration Suite")

col_scen_title, col_scen_pop = st.columns([5, 1])
with col_scen_title:
    st.markdown("Select an economic case template below. **Double-click any cell to manually edit/override growth, inflation, or price increases live!**")

with col_scen_pop:
    with st.popover("ℹ️ Cases: What, When & Why?", use_container_width=True):
        st.markdown("### **📋 Scenario Matrix Documentation**")
        st.markdown("---")
        st.markdown("**🟢 BASE CASE PLAN**")
        st.markdown("* *What:* Balanced 12% volume growth, 5% defensive price increases matching macro inflation.")
        st.markdown("---")
        st.markdown("**🔥 BEST CASE EXPANSION**")
        st.markdown("* *What:* High volume penetration (25%) with stable pricing (2%) due to economies of scale.")
        st.markdown("---")
        st.markdown("**⚠️ HIGH-INFLATION DOWNSIDE**")
        st.markdown("* *What:* Stagnant demand (2%) where pricing must be forced up (12%) to combat extreme 10% supplier cost creep.")

if "scenario_matrix" not in st.session_state:
    st.session_state.scenario_matrix = pd.DataFrame({
        "Scenario Case": ["🟢 Base Case Plan", "🔥 Best Case Expansion", "⚠️ High-Inflation Downside"],
        "Annual Volume Growth (%)": [12.0, 25.0, 2.0],
        "Annual Price Increase (%)": [5.0, 2.0, 12.0],
        "Annual Supplier Inflation (%)": [4.0, 2.0, 10.0],
        "Annual Wage Inflation (%)": [5.0, 3.0, 8.0]
    })

edited_scenario_df = st.data_editor(
    st.session_state.scenario_matrix,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Scenario Case": st.column_config.TextColumn(disabled=True),
        "Annual Volume Growth (%)": st.column_config.NumberColumn(format="%.1f%%", min_value=0.0, max_value=200.0),
        "Annual Price Increase (%)": st.column_config.NumberColumn(format="%.1f%%", min_value=0.0, max_value=100.0),
        "Annual Supplier Inflation (%)": st.column_config.NumberColumn(format="%.1f%%", min_value=0.0, max_value=100.0),
        "Annual Wage Inflation (%)": st.column_config.NumberColumn(format="%.1f%%", min_value=0.0, max_value=100.0),
    },
    key="macro_scenario_editor"
)

selected_case = st.radio(
    "Activate Macro Matrix Tracking Profile:",
    options=edited_scenario_df["Scenario Case"].tolist(),
    horizontal=True
)

case_row = edited_scenario_df[edited_scenario_df["Scenario Case"] == selected_case].iloc[0]
vol_growth_annual = float(case_row["Annual Volume Growth (%)"])
price_inc_annual = float(case_row["Annual Price Increase (%)"])
supplier_inf_annual = float(case_row["Annual Supplier Inflation (%)"])
wage_inf_annual = float(case_row["Annual Wage Inflation (%)"])

vol_growth_monthly = (1 + (vol_growth_annual / 100.0)) ** (1/12) - 1
price_inc_monthly = (1 + (price_inc_annual / 100.0)) ** (1/12) - 1
supplier_inf_monthly = (1 + (supplier_inf_annual / 100.0)) ** (1/12) - 1
wage_inf_monthly = (1 + (wage_inf_annual / 100.0)) ** (1/12) - 1

st.markdown("---")

# --- SIDEBAR INTERFACE: DATA ENTRY METHOD SELECTION ---
st.sidebar.header("📥 Data Entry Mode Configuration")
entry_method = st.sidebar.radio(
    "Select Input Mechanism:",
    ["🔗 Synced Ingestion Ledger", "🎛️ Manual Override Sliders"]
)

st.sidebar.markdown("---")
st.sidebar.header("📅 Timeline Horizon Configuration")
horizon_months = st.sidebar.slider("Forecast Horizon Runway (Months)", 12, 60, 36, 12)
st.sidebar.markdown("---")

forecast_df = None

# ==========================================
# METHOD A: SYNCED INGESTION LEDGER DATA FLOW
# ==========================================
if entry_method == "🔗 Synced Ingestion Ledger":
    st.sidebar.subheader("🔒 Active Ingestion Ledger States")
    st.sidebar.disabled = True
    st.sidebar.metric("Live Ledger Sales Base", f"£{derived_sales:,.2f}")
    st.sidebar.metric("Live Ledger Overheads (OpEx)", f"£{derived_opex:,.2f}")
    st.sidebar.metric("Calculated GP Margin", f"{derived_gp_pct:,.1f}%")
    st.sidebar.metric("Live Ledger Payroll Base", f"£{derived_wages:,.2f}")
    
    st.sidebar.markdown("---")
    debtor_days = st.sidebar.number_input("Debtor Days (Continuous Lag)", 0, 120, 30, 5, key="f_debtor_sync")
    creditor_days = st.sidebar.number_input("Creditor Days (Payment Lag)", 0, 120, 30, 5, key="f_creditor_sync")

    # Feed the inputs extracted directly from your ingestion grid down to the central forecasting module
    forecast_df = ff.run_three_way_forecast(
        months=horizon_months, starting_cash=STARTING_CASH_BASELINE, starting_retained_earnings=STARTING_CASH_BASELINE,
        monthly_sales=derived_sales, opex_input=derived_opex, gross_profit_percent=derived_gp_pct, monthly_wages=derived_wages,
        debtor_days=debtor_days, creditor_days=creditor_days,
        vol_growth_monthly=vol_growth_monthly, price_inc_monthly=price_inc_monthly,
        supplier_inf_monthly=supplier_inf_monthly, wage_inf_monthly=wage_inf_monthly
    )

# ==========================================
# METHOD B: MANUAL OVERRIDE SLIDERS
# ==========================================
else:
    st.sidebar.subheader("📊 Operational Override Sliders")
    sales_input = st.sidebar.slider("Override Monthly Revenue (£)", 10000.0, 500000.0, 100000.0, 5000.0, format="£%.2f")
    opex_input = st.sidebar.slider("Override Monthly Overheads / OpEx (£)", 0.0, 100000.0, 15000.0, 1000.0, format="£%.2f")
    gp_input = st.sidebar.slider("Override Gross Profit Margin (%)", 10.0, 100.0, 65.0, 0.5)
    wages_input = st.sidebar.slider("Override Monthly Payroll / Wages (£)", 0.0, 100000.0, 8672.57, 500.0, format="£%.2f")
    
    st.sidebar.markdown("---")
    debtor_days = st.sidebar.number_input("Debtor Days (Continuous Lag)", 0, 120, 30, 5, key="f_debtor_override")
    creditor_days = st.sidebar.number_input("Creditor Days (Payment Lag)", 0, 120, 30, 5, key="f_creditor_override")

    forecast_df = ff.run_three_way_forecast(
        months=horizon_months, starting_cash=STARTING_CASH_BASELINE, starting_retained_earnings=STARTING_CASH_BASELINE,
        monthly_sales=sales_input, opex_input=opex_input, gross_profit_percent=gp_input, monthly_wages=wages_input,
        debtor_days=debtor_days, creditor_days=creditor_days,
        vol_growth_monthly=vol_growth_monthly, price_inc_monthly=price_inc_monthly,
        supplier_inf_monthly=supplier_inf_monthly, wage_inf_monthly=wage_inf_monthly
    )

# ==========================================
# RENDER STATEMENT VIEWS
# ==========================================
if forecast_df is not None:
    cumulative_variance = forecast_df["Variance (£)"].iloc[-1]
    
    col_layout_1, col_layout_2 = st.columns([3, 1])
    with col_layout_1:
        st.subheader("📋 Conventional Financial Statements")
    with col_layout_2:
        if abs(cumulative_variance) < 0.05:
            st.success("🟢 Model Balanced!")
        else:
            st.error(f"❌ Balance Sheet Out of Sync! £{cumulative_variance:,.2f}")
            
    st.markdown("---")
    tab_pl, tab_bs, tab_cf, tab_master = st.tabs([
        "📈 Profit & Loss (P&L)", "⚖️ Balance Sheet (BS)", "💸 Cash Flow Statement (CF)", "🗃️ Master Data Ledger Grid"
    ])
    
    def create_accounting_statement(df: pd.DataFrame, row_mapping: dict) -> pd.DataFrame:
        statement_df = df[list(row_mapping.keys())].rename(columns=row_mapping)
        statement_df.index = df["Month"]
        return statement_df.T.reset_index().rename(columns={"index": "Financial Line Item"})
        
    with tab_pl:
        st.markdown(f"### **Statement of Profit or Loss ({horizon_months}-Month Runway)** — *{selected_case}*")
        pl_rows = {
            "Turnover (£)": "Revenue (Turnover)", 
            "Direct Expenses (COGS) (£)": "  Less: Cost of Sales (Direct COGS)",
            "Indirect Overheads (£)": "  Less: Operating Expenses (Indirect OpEx)",
            "Payroll Costs (£)": "  Less: Operating Overheads (Payroll)", 
            "Net Profit (£)": "Net Operating Profit / (Loss) EBITDA"
        }
        st.data_editor(create_accounting_statement(forecast_df, pl_rows), use_container_width=True, hide_index=True, key="pl_view_editor")
        
    with tab_bs:
        st.markdown(f"### **Statement of Financial Position ({horizon_months}-Month Snapshot)** — *{selected_case}*")
        
        st.markdown("---")
        audit_mode = st.toggle("🔍 Activate Granular Auditor View (Unpack Constituent Accounts)", key="bs_audit_toggle")
        st.markdown("---")
        
        if not audit_mode:
            bs_rows = {
                "Bank Cash Position (£)": "Current Assets: Cash at Bank", 
                "Debtors Asset (£)": "Current Assets: Accounts Receivable (Debtors)", 
                "Creditors Under 1 Yr (£)": "Current Liabilities: Accounts Payable & Owed", 
                "Retained Earnings Balance (£)": "Capital & Reserves: Retained Earnings", 
                "Variance (£)": "Double-Entry Validation Variance"
            }
            st.data_editor(create_accounting_statement(forecast_df, bs_rows), use_container_width=True, hide_index=True, key="bs_view_editor")
        else:
            st.info("📊 Deep-Dive Audit Active: Isolating constituent ledger rows assigned to baseline buckets.")
            if "trial_balance_matrix" in st.session_state:
                raw_tb_df = st.session_state.trial_balance_matrix.copy()
                for bucket in raw_tb_df["Accounting Allocation Bucket"].unique():
                    with st.expander(f"📁 Bucket Group: {bucket}", expanded=True):
                        filtered_bucket_df = raw_tb_df[raw_tb_df["Accounting Allocation Bucket"] == bucket]
                        st.dataframe(filtered_bucket_df[["Account Code", "Account Name", "Amount (£)"]], use_container_width=True, hide_index=True)
            else:
                st.warning("⚠️ No base trial balance matrix found in session memory.")
        
    with tab_cf:
        st.markdown(f"### **Statement of Cash Flows ({horizon_months}-Month Indirect Reconciliation)**")
        cf_working = forecast_df[["Month", "Net Profit (£)", "Bank Cash Position (£)"]].copy()
        cf_working["Net Cash Flow Movement"] = cf_working["Bank Cash Position (£)"].diff().fillna(cf_working["Bank Cash Position (£)"] - STARTING_CASH_BASELINE)
        cf_rows = {"Net Profit (£)": "Net Profit from Operations", "Net Cash Flow Movement": "Net Inflow / (Outflow) for Period", "Bank Cash Position (£)": "Closing Cash Balance in Bank"}
        st.data_editor(create_accounting_statement(cf_working, cf_rows), use_container_width=True, hide_index=True, key="cf_view_editor")
        
    with tab_master:
        st.markdown("### **Master Data Ledger Grid (Fully Editable Raw Rows)**")
        st.data_editor(forecast_df, use_container_width=True, hide_index=True, key="master_grid_editor")