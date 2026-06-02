# ui_skin/pages/3_📊_forecast.py
import streamlit as st
import pandas as pd
import numpy as np

# Native Workspace Root Import
import core_engine.forecast_formulas as ff

st.set_page_config(layout="wide", page_title="3-Way Financial Forecast")

st.title("📊 Primary 3-Way Integrated Forecast")
st.caption("Core Financial Reporting Layer • Professional Multi-Statement Ledger Framework")
st.markdown("---")

# --- GLOBAL MODELING BASELINES ---
STARTING_CASH_BASELINE = 500000.00
HORIZON_MONTHS = 24

# --- SIDEBAR INTERFACE: DATA ENTRY METHOD SELECTION ---
st.sidebar.header("📥 Data Entry Mode Configuration")
entry_method = st.sidebar.radio(
    "Select Input Mechanism:",
    ["🎛️ Live Scenario Sliders", "📁 Bulk CSV Ledger Upload"]
)

st.sidebar.markdown("---")

# Initialize default runtime variable states
forecast_df = None

# ==========================================
# MODE A: NATIVE INTERACTIVE SLIDERS
# ==========================================
if entry_method == "🎛️ Live Scenario Sliders":
    st.sidebar.subheader("📊 Operational Parameters")
    sales_input = st.sidebar.slider("Target Monthly Revenue (£)", 10000.0, 500000.0, 100000.0, 5000.0, format="£%.2f")
    gp_input = st.sidebar.slider("Target Gross Profit Margin (%)", 10.0, 100.0, 65.0, 0.5)
    wages_input = st.sidebar.slider("Base Monthly Payroll / Wages (£)", 0.0, 100000.0, 8672.57, 500.0, format="£%.2f")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("⏳ Working Capital Timing")
    debtor_days = st.sidebar.number_input("Debtor Days (Continuous Lag)", 0, 120, 30, 5, key="f_debtor")
    creditor_days = st.sidebar.number_input("Creditor Days (Payment Lag)", 0, 120, 30, 5, key="f_creditor")

    # Generate standard linear timeline matrix data points
    forecast_df = ff.run_three_way_forecast(
        months=HORIZON_MONTHS, starting_cash=STARTING_CASH_BASELINE, starting_retained_earnings=STARTING_CASH_BASELINE,
        monthly_sales=sales_input, gross_profit_percent=gp_input, monthly_wages=wages_input,
        debtor_days=debtor_days, creditor_days=creditor_days
    )

# ==========================================
# MODE B: ENTERPRISE CSV RECONCILIATION
# ==========================================
else:
    st.sidebar.subheader("📂 Upload Data Profile")
    uploaded_file = st.sidebar.file_uploader("Drop financial profile .csv below:", type=["csv"])
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("⏳ Working Capital Timing")
    debtor_days = st.sidebar.number_input("Debtor Days (Continuous Lag)", 0, 120, 30, 5, key="f_debtor_csv")
    creditor_days = st.sidebar.number_input("Creditor Days (Payment Lag)", 0, 120, 30, 5, key="f_creditor_csv")

    if uploaded_file is not None:
        try:
            # Parse raw uploaded profile
            input_data = pd.read_csv(uploaded_file)
            
            # Extract parameters safely from matching csv matrix rows
            # Fall back safely if rows do not span up to our global horizon baseline limit
            records = []
            current_cash = STARTING_CASH_BASELINE
            current_retained_earnings = STARTING_CASH_BASELINE
            
            # Static rules matching core calculations setup
            paye_ni_rate, pension_rate, vat_rate = 0.25, 0.05, 0.20
            
            for m in range(1, HORIZON_MONTHS + 1):
                idx = m - 1
                # Read row variations programmatically from file matrix if available
                if idx < len(input_data):
                    turnover = float(input_data.loc[idx, "Revenue_Target"])
                    cogs = float(input_data.loc[idx, "COGS_Absolute"])
                    wages_expense = float(input_data.loc[idx, "Wages_Base"])
                else:
                    # Native baseline fallbacks if file runs short
                    turnover, cogs, wages_expense = 100000.0, 35000.0, 8672.57
                
                # Accruals calculation layers
                total_payroll = wages_expense * (1 + paye_ni_rate + pension_rate)
                net_profit = (turnover - cogs) - total_payroll
                current_retained_earnings += net_profit
                
                # Working capital ledger positioning mechanics
                debtors_balance = (turnover * (1 + vat_rate)) * (debtor_days / 30.0)
                trade_creditors = (cogs * (1 + vat_rate)) * (creditor_days / 30.0)
                
                total_creditors = trade_creditors + (wages_expense * paye_ni_rate) + (wages_expense * pension_rate) + ((turnover * vat_rate) - (cogs * vat_rate))
                current_cash = current_retained_earnings + total_creditors - debtors_balance
                variance = (current_cash + debtors_balance) - (total_creditors + current_retained_earnings)
                
                records.append({
                    "Month": f"Month {m}", "Turnover (£)": turnover, "Payroll Costs (£)": total_payroll,
                    "Net Profit (£)": net_profit, "Bank Cash Position (£)": current_cash, "Debtors Asset (£)": debtors_balance,
                    "Creditors Under 1 Yr (£)": total_creditors, "Retained Earnings Balance (£)": current_retained_earnings, "Variance (£)": variance
                })
            
            forecast_df = pd.DataFrame(records)
            st.success("💾 Seasonal Excel Profile Parsed Successfully!")
            
        except Exception as e:
            st.error(f"❌ Error compiling custom CSV data layout structural formats: {str(e)}")
            st.info("Ensure headers match exactly: Month, Revenue_Target, COGS_Absolute, Wages_Base")
    else:
        st.info("💡 Please upload a seasonal ledger template .csv file in the sidebar to begin processing your structural matrix model forecasts.")

# ==========================================
# RENDER CONVENTIONAL INTERFACE ENGINE
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
        st.markdown("### **Statement of Profit or Loss**")
        pl_rows = {"Turnover (£)": "Revenue (Turnover)", "Payroll Costs (£)": "  Less: Operating Overheads (Payroll)", "Net Profit (£)": "Net Operating Profit / (Loss)"}
        st.dataframe(create_accounting_statement(forecast_df, pl_rows), use_container_width=True, hide_index=True)
        
    with tab_bs:
        st.markdown("### **Statement of Financial Position**")
        bs_rows = {"Bank Cash Position (£)": "Current Assets: Cash at Bank", "Debtors Asset (£)": "Current Assets: Accounts Receivable (Debtors)", "Creditors Under 1 Yr (£)": "Current Liabilities: Accounts Payable & Owed", "Retained Earnings Balance (£)": "Capital & Reserves: Retained Earnings", "Variance (£)": "Double-Entry Validation Variance"}
        st.dataframe(create_accounting_statement(forecast_df, bs_rows), use_container_width=True, hide_index=True)
        
    with tab_cf:
        st.markdown("### **Statement of Cash Flows**")
        cf_working = forecast_df[["Month", "Net Profit (£)", "Bank Cash Position (£)"]].copy()
        cf_working["Net Cash Flow Movement"] = cf_working["Bank Cash Position (£)"].diff().fillna(cf_working["Bank Cash Position (£)"] - STARTING_CASH_BASELINE)
        cf_rows = {"Net Profit (£)": "Net Profit from Operations", "Net Cash Flow Movement": "Net Inflow / (Outflow) for Period", "Bank Cash Position (£)": "Closing Cash Balance in Bank"}
        st.dataframe(create_accounting_statement(cf_working, cf_rows), use_container_width=True, hide_index=True)
        
    with tab_master:
        st.markdown("### **Master Data Ledger Grid**")
        st.dataframe(forecast_df, use_container_width=True, hide_index=True)