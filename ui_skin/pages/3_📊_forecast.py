# ui_skin/pages/3_📊_forecast.py
import streamlit as st
import pandas as pd
import numpy as np

# 1. Native Workspace Root Import
import core_engine.forecast_formulas as ff

st.set_page_config(layout="wide", page_title="3-Way Financial Forecast")

st.title("📊 Primary 3-Way Integrated Forecast")
st.caption("Core Financial Reporting Layer • Live General Ledger Data Engine Matrix")
st.markdown("---")

# --- SIDEBAR CONTROLS FOR LIVE USER INPUTS ---
st.sidebar.header("📊 Forecast Parameter Control")

sales_input = st.sidebar.slider(
    "Target Monthly Revenue (£)", 
    min_value=10000.00, 
    max_value=500000.00, 
    value=100000.00, 
    step=5000.00,
    format="£%.2f"
)

gp_input = st.sidebar.slider(
    "Target Gross Profit Margin (%)", 
    min_value=10.0, 
    max_value=100.0, 
    value=65.0, 
    step=0.5
)

wages_input = st.sidebar.slider(
    "Base Monthly Payroll / Wages (£)", 
    min_value=0.00, 
    max_value=100000.00, 
    value=8672.57, 
    step=500.00,
    format="£%.2f"
)

st.sidebar.markdown("---")
st.sidebar.subheader("⏳ Working Capital Timing")
debtor_days_input = st.sidebar.number_input("Debtor Days (Collection Lag)", min_value=0, max_value=120, value=30, step=5, key="f_debtor")
creditor_days_input = st.sidebar.number_input("Creditor Days (Payment Lag)", min_value=0, max_value=120, value=30, step=5, key="f_creditor")


# --- RUN THE FORECAST CALCULATIONS ---
STARTING_CASH_BASELINE = 500000.00

forecast_df = ff.run_three_way_forecast(
    months=24,
    starting_cash=STARTING_CASH_BASELINE,
    starting_retained_earnings=STARTING_CASH_BASELINE,
    monthly_sales=sales_input,
    gross_profit_percent=gp_input,
    monthly_wages=wages_input,
    debtor_days=debtor_days_input,
    creditor_days=creditor_days_input
)

# Grab snapshot integrity balance variance from the final column array element
cumulative_variance = forecast_df["Variance (£)"].iloc[-1]


# --- MODULE DEPLOYMENT: VALIDATION BANNERS ---
col_layout_1, col_layout_2 = st.columns([3, 1])

with col_layout_1:
    st.subheader("📋 Conventional Financial Statements")
    st.markdown("Displaying standardized financial statement models with time distributed across columns.")

with col_layout_2:
    if abs(cumulative_variance) < 0.05:
        st.success("🟢 Model Balanced!\n\nAssets exactly equal Liabilities + Equity.")
    else:
        st.error(f"❌ 3-Way Model Out of Balance!\n\nCurrent Variance: £{cumulative_variance:,.2f}")

st.markdown("---")

# --- TAB NAVIGATION LAYOUT MATRIX ---
tab_pl, tab_bs, tab_cf, tab_master = st.tabs([
    "📈 Profit & Loss (P&L)", 
    "⚖️ Balance Sheet (BS)", 
    "💸 Cash Flow Statement (CF)", 
    "🗃️ Master Data Ledger Grid"
])

# ==========================================
# HELPER: TRANSPOSE ENGINE WITH FORMATTING
# ==========================================
def create_accounting_statement(df: pd.DataFrame, row_mapping: dict) -> pd.DataFrame:
    """Isolates statement lines, renames to standard labels, and transposes time to columns."""
    # Slice columns and rename to traditional line item labels
    statement_df = df[list(row_mapping.keys())].rename(columns=row_mapping)
    
    # Set Month as index, transpose (.T), and restore row headers as a column name
    statement_df.index = df["Month"]
    transposed_df = statement_df.T.reset_index().rename(columns={"index": "Financial Line Item"})
    return transposed_df


# ==========================================
# 1. TAB: PROFIT & LOSS STATEMENT (P&L)
# ==========================================
with tab_pl:
    st.markdown("### **Statement of Profit or Loss**")
    
    # Map raw engine metrics to standardized accounting row descriptions
    pl_rows = {
        "Turnover (£)": "Revenue (Turnover)",
        "Payroll Costs (£)": "  Less: Operating Overheads (Payroll)",
        "Net Profit (£)": "Net Operating Profit / (Loss)"
    }
    
    pl_statement = create_accounting_statement(forecast_df, pl_rows)
    st.dataframe(pl_statement, use_container_width=True, hide_index=True)

# ==========================================
# 2. TAB: BALANCE SHEET SNAPSHOT (BS)
# ==========================================
with tab_bs:
    st.markdown("### **Statement of Financial Position**")
    
    bs_rows = {
        "Bank Cash Position (£)": "Current Assets: Cash at Bank",
        "Debtors Asset (£)": "Current Assets: Accounts Receivable (Debtors)",
        "Creditors Under 1 Yr (£)": "Current Liabilities: Accounts Payable & Owed",
        "Retained Earnings Balance (£)": "Capital & Reserves: Retained Earnings",
        "Variance (£)": "Double-Entry Validation Variance"
    }
    
    bs_statement = create_accounting_statement(forecast_df, bs_rows)
    st.dataframe(bs_statement, use_container_width=True, hide_index=True)

# ==========================================
# 3. TAB: CASH FLOW STATEMENT (CF)
# ==========================================
with tab_cf:
    st.markdown("### **Statement of Cash Flows**")
    
    # Generate incremental net delta tracking prior to transposing
    cf_working = forecast_df[["Month", "Net Profit (£)", "Bank Cash Position (£)"]].copy()
    cf_working["Net Cash Flow Movement"] = cf_working["Bank Cash Position (£)"].diff().fillna(
        cf_working["Bank Cash Position (£)"] - STARTING_CASH_BASELINE
    )
    
    cf_rows = {
        "Net Profit (£)": "Net Profit from Operations",
        "Net Cash Flow Movement": "Net Inflow / (Outflow) for Period",
        "Bank Cash Position (£)": "Closing Cash Balance in Bank"
    }
    
    cf_statement = create_accounting_statement(cf_working, cf_rows)
    st.dataframe(cf_statement, use_container_width=True, hide_index=True)

# ==========================================
# 4. TAB: MASTER LEDGER GRID MATRIX
# ==========================================
with tab_master:
    st.markdown("### **Integrated Master General Ledger Data Grid**")
    st.caption("Raw underlying vertical timeline matrix view.")
    st.dataframe(forecast_df, use_container_width=True, hide_index=True)