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

# Initialize scenario state storage within Streamlit's runtime memory session
if "scenario_matrix" not in st.session_state:
    st.session_state.scenario_matrix = pd.DataFrame({
        "Scenario Case": ["🟢 Base Case Plan", "🔥 Best Case Expansion", "⚠️ High-Inflation Downside"],
        "Annual Volume Growth (%)": [12.0, 25.0, 2.0],
        "Annual Price Increase (%)": [5.0, 2.0, 12.0],
        "Annual Supplier Inflation (%)": [4.0, 2.0, 10.0],
        "Annual Wage Inflation (%)": [5.0, 3.0, 8.0]
    })

# RENDER FULLY EDITABLE INTERACTIVE SCENARIO MATRIX
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

# Active Case Radio Selector
selected_case = st.radio(
    "Activate Macro Matrix Tracking Profile:",
    options=edited_scenario_df["Scenario Case"].tolist(),
    horizontal=True
)

# Parse selected parameters out dynamically
case_row = edited_scenario_df[edited_scenario_df["Scenario Case"] == selected_case].iloc[0]
vol_growth_annual = float(case_row["Annual Volume Growth (%)"])
price_inc_annual = float(case_row["Annual Price Increase (%)"])
supplier_inf_annual = float(case_row["Annual Supplier Inflation (%)"])
wage_inf_annual = float(case_row["Annual Wage Inflation (%)"])

# Convert annual compounding targets down to exact monthly index vectors
vol_growth_monthly = (1 + (vol_growth_annual / 100.0)) ** (1/12) - 1
price_inc_monthly = (1 + (price_inc_annual / 100.0)) ** (1/12) - 1
supplier_inf_monthly = (1 + (supplier_inf_annual / 100.0)) ** (1/12) - 1
wage_inf_monthly = (1 + (wage_inf_annual / 100.0)) ** (1/12) - 1

st.markdown("---")

# --- SIDEBAR INTERFACE: DATA ENTRY METHOD SELECTION ---
st.sidebar.header("📥 Data Entry Mode Configuration")
entry_method = st.sidebar.radio(
    "Select Input Mechanism:",
    ["🎛️ Live Scenario Sliders", "📁 Bulk CSV Ledger Upload"]
)

st.sidebar.markdown("---")
st.sidebar.header("📅 Timeline Horizon Configuration")
horizon_months = st.sidebar.slider("Forecast Horizon Runway (Months)", 12, 60, 36, 12)
st.sidebar.markdown("---")

forecast_df = None

# ==========================================
# MODE A: NATIVE INTERACTIVE SLIDERS
# ==========================================
if entry_method == "🎛️ Live Scenario Sliders":
    st.sidebar.subheader("📊 Operational Baseline Parameters")
    sales_input = st.sidebar.slider("Base Monthly Revenue (£)", 10000.0, 500000.0, 100000.0, 5000.0, format="£%.2f")
    opex_input = st.sidebar.slider("Base Monthly Overheads / OpEx (£)", 0.0, 100000.0, 15000.0, 1000.0, format="£%.2f")
    gp_input = st.sidebar.slider("Base Gross Profit Margin (%)", 10.0, 100.0, 65.0, 0.5)
    wages_input = st.sidebar.slider("Base Monthly Payroll / Wages (£)", 0.0, 100000.0, 8672.57, 500.0, format="£%.2f")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("⏳ Working Capital Timing")
    debtor_days = st.sidebar.number_input("Debtor Days (Continuous Lag)", 0, 120, 30, 5, key="f_debtor")
    creditor_days = st.sidebar.number_input("Creditor Days (Payment Lag)", 0, 120, 30, 5, key="f_creditor")

    records = []
    current_cash = STARTING_CASH_BASELINE
    current_retained_earnings = STARTING_CASH_BASELINE
    paye_ni_rate, pension_rate, vat_rate = 0.25, 0.05, 0.20
    
    for m in range(1, horizon_months + 1):
        v_mult = (1 + vol_growth_monthly) ** (m - 1)
        p_mult = (1 + price_inc_monthly) ** (m - 1)
        s_mult = (1 + supplier_inf_monthly) ** (m - 1)
        w_mult = (1 + wage_inf_monthly) ** (m - 1)
        
        turnover = sales_input * v_mult * p_mult
        
        # CORRECTED: Explicit breakdown of Direct Expenses (COGS) and Indirect Overheads (OpEx)
        direct_expenses = (sales_input * v_mult * (1 - (gp_input / 100.0))) * s_mult
        indirect_overheads = opex_input * w_mult
        
        wages_expense = wages_input * w_mult
        total_payroll = wages_expense * (1 + paye_ni_rate + pension_rate)
        
        # True Net Profit Calculation Loop
        net_profit = turnover - direct_expenses - indirect_overheads - total_payroll
        current_retained_earnings += net_profit
        
        debtors_balance = (turnover * (1 + vat_rate)) * (debtor_days / 30.0)
        trade_creditors = (direct_expenses * (1 + vat_rate)) * (creditor_days / 30.0)
        
        total_creditors = trade_creditors + (wages_expense * paye_ni_rate) + (wages_expense * pension_rate) + ((turnover * vat_rate) - (direct_expenses * vat_rate))
        current_cash = current_retained_earnings + total_creditors - debtors_balance
        variance = (current_cash + debtors_balance) - (total_creditors + current_retained_earnings)
        
        records.append({
            "Month": f"Month {m}", "Turnover (£)": turnover, "Direct Expenses (COGS) (£)": direct_expenses,
            "Indirect Overheads (£)": indirect_overheads, "Payroll Costs (£)": total_payroll,
            "Net Profit (£)": net_profit, "Bank Cash Position (£)": current_cash, "Debtors Asset (£)": debtors_balance,
            "Creditors Under 1 Yr (£)": total_creditors, "Retained Earnings Balance (£)": current_retained_earnings, "Variance (£)": variance
        })
    forecast_df = pd.DataFrame(records)

# ==========================================
# MODE B: ENTERPRISE CSV RECONCILIATION
# ==========================================
else:
    uploaded_file = st.sidebar.file_uploader("Drop financial profile .csv below:", type=["csv"])
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("⏳ Working Capital Timing")
    debtor_days = st.sidebar.number_input("Debtor Days (Continuous Lag)", 0, 120, 30, 5, key="f_debtor_csv")
    creditor_days = st.sidebar.number_input("Creditor Days (Payment Lag)", 0, 120, 30, 5, key="f_creditor_csv")

    if uploaded_file is not None:
        try:
            input_data = pd.read_csv(uploaded_file)
            records = []
            current_cash = STARTING_CASH_BASELINE
            current_retained_earnings = STARTING_CASH_BASELINE
            paye_ni_rate, pension_rate, vat_rate = 0.25, 0.05, 0.20
            
            for m in range(1, horizon_months + 1):
                idx = m - 1
                if idx < len(input_data):
                    turnover_base = float(input_data.loc[idx, "Revenue_Target"])
                    cogs_base = float(input_data.loc[idx, "COGS_Absolute"])
                    opex_base = float(input_data.loc[idx, "OpEx_Absolute"]) if "OpEx_Absolute" in input_data.columns else 15000.0
                    wages_base = float(input_data.loc[idx, "Wages_Base"])
                else:
                    turnover_base, cogs_base, opex_base, wages_base = 100000.0, 35000.0, 15000.0, 8672.57
                
                v_mult = (1 + vol_growth_monthly) ** (m - 1)
                p_mult = (1 + price_inc_monthly) ** (m - 1)
                s_mult = (1 + supplier_inf_monthly) ** (m - 1)
                w_mult = (1 + wage_inf_monthly) ** (m - 1)
                
                turnover = turnover_base * v_mult * p_mult
                direct_expenses = (cogs_base * v_mult) * s_mult
                indirect_overheads = opex_base * w_mult
                wages_expense = wages_base * w_mult
                
                total_payroll = wages_expense * (1 + paye_ni_rate + pension_rate)
                net_profit = turnover - direct_expenses - indirect_overheads - total_payroll
                current_retained_earnings += net_profit
                
                debtors_balance = (turnover * (1 + vat_rate)) * (debtor_days / 30.0)
                trade_creditors = (direct_expenses * (1 + vat_rate)) * (creditor_days / 30.0)
                
                total_creditors = trade_creditors + (wages_expense * paye_ni_rate) + (wages_expense * pension_rate) + ((turnover * vat_rate) - (direct_expenses * vat_rate))
                current_cash = current_retained_earnings + total_creditors - debtors_balance
                variance = (current_cash + debtors_balance) - (total_creditors + current_retained_earnings)
                
                records.append({
                    "Month": f"Month {m}", "Turnover (£)": turnover, "Direct Expenses (COGS) (£)": direct_expenses,
                    "Indirect Overheads (£)": indirect_overheads, "Payroll Costs (£)": total_payroll,
                    "Net Profit (£)": net_profit, "Bank Cash Position (£)": current_cash, "Debtors Asset (£)": debtors_balance,
                    "Creditors Under 1 Yr (£)": total_creditors, "Retained Earnings Balance (£)": current_retained_earnings, "Variance (£)": variance
                })
            forecast_df = pd.DataFrame(records)
            st.success("💾 Seasonal Excel Profile & Expense Matrices Synced!")
        except Exception as e:
            st.error(f"❌ Error compiling custom CSV data structures: {str(e)}")
    else:
        st.info(f"💡 Please upload your baseline seasonal ledger template .csv file to activate modeling views.")

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
        bs_rows = {"Bank Cash Position (£)": "Current Assets: Cash at Bank", "Debtors Asset (£)": "Current Assets: Accounts Receivable (Debtors)", "Creditors Under 1 Yr (£)": "Current Liabilities: Accounts Payable & Owed", "Retained Earnings Balance (£)": "Capital & Reserves: Retained Earnings", "Variance (£)": "Double-Entry Validation Variance"}
        st.data_editor(create_accounting_statement(forecast_df, bs_rows), use_container_width=True, hide_index=True, key="bs_view_editor")
        
    with tab_cf:
        st.markdown(f"### **Statement of Cash Flows ({horizon_months}-Month Indirect Reconciliation)**")
        cf_working = forecast_df[["Month", "Net Profit (£)", "Bank Cash Position (£)"]].copy()
        cf_working["Net Cash Flow Movement"] = cf_working["Bank Cash Position (£)"].diff().fillna(cf_working["Bank Cash Position (£)"] - STARTING_CASH_BASELINE)
        cf_rows = {"Net Profit (£)": "Net Profit from Operations", "Net Cash Flow Movement": "Net Inflow / (Outflow) for Period", "Bank Cash Position (£)": "Closing Cash Balance in Bank"}
        st.data_editor(create_accounting_statement(cf_working, cf_rows), use_container_width=True, hide_index=True, key="cf_view_editor")
        
    with tab_master:
        st.markdown("### **Master Data Ledger Grid (Fully Editable Raw Rows)**")
        st.data_editor(forecast_df, use_container_width=True, hide_index=True, key="master_grid_editor")