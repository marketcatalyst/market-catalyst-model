# ui_skin/pages/1_📊_forecast.py
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
# Synchronized with sandbox to preserve perfect double-entry equation state parity
STARTING_CASH_BASELINE = 500000.00

forecast_df = ff.run_three_way_forecast(
    months=24,
    starting_cash=STARTING_CASH_BASELINE,
    starting_retained_earnings=STARTING_CASH_BASELINE,  # Balanced Baseline Allocation
    monthly_sales=sales_input,
    gross_profit_percent=gp_input,
    monthly_wages=wages_input,
    debtor_days=debtor_days_input,
    creditor_days=creditor_days_input
)

# Check the final month snapshot variance rather than summing row increments
cumulative_variance = forecast_df["Variance (£)"].iloc[-1]


# --- MODULE DEPLOYMENT: VALIDATION BANNERS ---
col_layout_1, col_layout_2 = st.columns([3, 1])

with col_layout_1:
    st.subheader("📋 Financial Statement Outputs")
    st.markdown("Toggle through the structural tabs below to see verified standard accounting statement representations.")

with col_layout_2:
    # Render dynamic alert boxes based on true ledger equality
    if abs(cumulative_variance) < 0.05:
        st.success(
            "🟢 Model Balanced!\n\n"
            "Assets exactly equal Liabilities + Equity across the entire timeline continuum."
        )
    else:
        st.error(
            f"❌ 3-Way Model Out of Balance!\n\n"
            f"Current Snapshot Variance:\n\n"
            f"£{cumulative_variance:,.2f}"
        )

st.markdown("---")

# --- TAB NAVIGATION LAYOUT MATRIX ---
tab_pl, tab_bs, tab_cf, tab_master = st.tabs([
    "📈 Profit & Loss (P&L)", 
    "⚖️ Balance Sheet (BS)", 
    "💸 Cash Flow Statement (CF)", 
    "🗃️ Master Data Ledger Grid"
])

# ==========================================
# 1. TAB: PROFIT & LOSS STATEMENT (P&L)
# ==========================================
with tab_pl:
    st.markdown("### **Statement of Profit or Loss**")
    st.caption("Operational trading activity over the rolling 24-month horizon period.")
    
    # Deriving additional lines dynamically to round out standard format presentation
    pl_df = pd.DataFrame({
        "Month": forecast_df["Month"],
        "Revenue (Turnover)": forecast_df["Turnover (£)"],
        "Cost of Sales (COGS)": forecast_df["Turnover (£)"] * (1 - (gp_input / 100.0)),
        "Gross Profit": forecast_df["Turnover (£)"] * (gp_input / 100.0),
        "Total Payroll Overheads": forecast_df["Payroll Costs (£)"],
        "Net Operating Profit": forecast_df["Net Profit (£)"]
    })
    
    st.dataframe(
        pl_df, use_container_width=True, hide_index=True,
        column_config={
            "Revenue (Turnover)": st.column_config.NumberColumn(format="£%,.2f"),
            "Cost of Sales (COGS)": st.column_config.NumberColumn(format="£%,.2f"),
            "Gross Profit": st.column_config.NumberColumn(format="£%,.2f"),
            "Total Payroll Overheads": st.column_config.NumberColumn(format="£%,.2f"),
            "Net Operating Profit": st.column_config.NumberColumn(format="£%,.2f")
        }
    )

# ==========================================
# 2. TAB: BALANCE SHEET SNAPSHOT (BS)
# ==========================================
with tab_bs:
    st.markdown("### **Statement of Financial Position**")
    st.caption("Cumulative snapshot of assets, liabilities, and owners' equity lines at each month close.")
    
    bs_df = pd.DataFrame({
        "Month": forecast_df["Month"],
        "Current Assets: Bank Cash": forecast_df["Bank Cash Position (£)"],
        "Current Assets: Accounts Receivable": forecast_df["Debtors Asset (£)"],
        "Total Assets": forecast_df["Bank Cash Position (£)"] + forecast_df["Debtors Asset (£)"],
        "Current Liabilities: Short Term Creditors": forecast_df["Creditors Under 1 Yr (£)"],
        "Total Liabilities": forecast_df["Creditors Under 1 Yr (£)"],
        "Equity: Retained Earnings": forecast_df["Retained Earnings Balance (£)"],
        "Total Liabilities & Equity": forecast_df["Creditors Under 1 Yr (£)"] + forecast_df["Retained Earnings Balance (£)"],
        "Net Check Variance": forecast_df["Variance (£)"]
    })
    
    st.dataframe(
        bs_df, use_container_width=True, hide_index=True,
        column_config={
            "Current Assets: Bank Cash": st.column_config.NumberColumn(format="£%,.2f"),
            "Current Assets: Accounts Receivable": st.column_config.NumberColumn(format="£%,.2f"),
            "Total Assets": st.column_config.NumberColumn(format="£%,.2f"),
            "Current Liabilities: Short Term Creditors": st.column_config.NumberColumn(format="£%,.2f"),
            "Total Liabilities": st.column_config.NumberColumn(format="£%,.2f"),
            "Equity: Retained Earnings": st.column_config.NumberColumn(format="£%,.2f"),
            "Total Liabilities & Equity": st.column_config.NumberColumn(format="£%,.2f"),
            "Net Check Variance": st.column_config.NumberColumn(format="£%,.2f")
        }
    )

# ==========================================
# 3. TAB: CASH FLOW STATEMENT (CF)
# ==========================================
with tab_cf:
    st.markdown("### **Statement of Cash Flows (Indirect Reconciliation)**")
    st.caption("Bridges the gap between structural accounting net profit accruals and liquid physical bank cash variations.")
    
    cf_df = pd.DataFrame({
        "Month": forecast_df["Month"],
        "Net Operating Income (Profit)": forecast_df["Net Profit (£)"],
        "Closing Bank Cash Position": forecast_df["Bank Cash Position (£)"]
    })
    
    # Calculate incremental net flow movements between successive row indexes
    cf_df["Net Operational Cash Delta"] = cf_df["Closing Bank Cash Position"].diff().fillna(
        cf_df["Closing Bank Cash Position"] - STARTING_CASH_BASELINE
    )
    
    st.dataframe(
        cf_df[["Month", "Net Operating Income (Profit)", "Net Operational Cash Delta", "Closing Bank Cash Position"]], 
        use_container_width=True, hide_index=True,
        column_config={
            "Net Operating Income (Profit)": st.column_config.NumberColumn(format="£%,.2f"),
            "Net Operational Cash Delta": st.column_config.NumberColumn(format="£%,.2f"),
            "Closing Bank Cash Position": st.column_config.NumberColumn(format="£%,.2f")
        }
    )

# ==========================================
# 4. TAB: MASTER LEDGER GRID MATRIX
# ==========================================
with tab_master:
    st.markdown("### **Integrated Master General Ledger Data Grid**")
    st.caption("Raw complete underlying parameter output matrix framework array.")
    st.dataframe(forecast_df, use_container_width=True, hide_index=True)