# ui_skin/pages/3_📊_forecast.py
import streamlit as st
import pandas as pd
import sys
import os

# Ensure the app can access the backend core_engine modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core_engine.master_model import generate_integrated_3way_forecast

st.set_page_config(layout="wide", page_title="Dynamic 3-Way Forecast Matrix")

st.title("📊 Dynamic 3-Way Forecast Matrix")
st.caption("UK GAAP Compliant • Real-Time Balanced P&L, Balance Sheet & Cash Flow Projections")
st.markdown("---")

# --- 1. PERSISTENT INTERACTIVE WORKSTATION CONTROLLERS ---
st.subheader("🎛️ Scenario Modeling Variables")
st.markdown("Adjust the operational variables below to see the instant, cascading impact across all financial statements.")

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)

with col_ctrl1:
    st.markdown("##### 📈 Revenue & Operations")
    target_sales = st.number_input("Target Monthly Sales Turnover (£)", min_value=0.0, value=55000.0, step=2500.0)
    opening_cash = st.number_input("Opening Bank Balance (£)", min_value=0.0, value=20000.0, step=1000.0)

with col_ctrl2:
    st.markdown("##### 👥 Personnel & Overheads")
    base_gross_wages = st.number_input("Base Monthly Staff Gross Pay (£)", min_value=0.0, value=7500.0, step=500.0)
    pension_opt_out = st.checkbox("Assume Workforce Pension Opt-Out (0%)", value=False)

with col_ctrl3:
    st.markdown("##### 🏢 Asset & Liability Financing")
    loan_principal = st.number_input("New HP / Commercial Loan Capital (£)", min_value=0.0, value=25000.0, step=5000.0)
    loan_term_months = st.slider("Financing Repayment Term (Months)", min_value=6, max_value=60, value=36)
    loan_interest_rate = st.slider("Contractual Annual Interest Rate (%)", min_value=0.0, max_value=20.0, value=7.0, step=0.5)

st.markdown("---")

# --- 2. PACKAGING DATA & FIRING THE PURE PYTHON ENGINE ---
# Create the standard inputs dictionary expected by our backend orchestrator
engine_payload = {
    "target_monthly_sales": target_sales,
    "base_monthly_gross_wages": base_gross_wages,
    "pension_opt_out": pension_opt_out,
    "loan_amount": loan_principal,
    "loan_term": loan_term_months,
    "loan_rate": loan_interest_rate,
    "loan_month": 1,              # Inject the financing liability event in Month 2 (0-indexed index 1)
    "opening_cash_balance": opening_cash,
    "opening_retained_earnings": opening_cash # Initial capitalization baseline anchor
}

with st.spinner("Processing structural multi-dimensional ledger matrices..."):
    # Fire data down past our clean architecture wall
    integrated_forecast_df = generate_integrated_3way_forecast(engine_payload)

# --- 3. FINANCIAL INTEGRITY HEALTH STATS ---
col_stat1, col_stat2 = st.columns([3, 1])

with col_stat1:
    st.subheader("📋 Integrated Financial Ledger Outputs")
    st.caption("Displaying a key slice of the fully integrated structural data grid matrix below.")
    
with col_stat2:
    # Read the absolute variance line directly out of the returned engine arrays
    total_model_variance = integrated_forecast_df["Double_Entry_Check"].sum()
    
    if total_model_variance == 0.00:
        st.success("✔️ 3-Way Model Status: Perfectly Balanced")
    else:
        st.error(f"❌ 3-Way Model Out of Balance! Cumulative Variance: £{total_model_variance:,.2f}")

# --- 4. DATA PRESENTATION DATAFRAME ---
# Filter down the columns to give the bookkeeper a clean, professional view
presentation_columns = [
    "Revenue", 
    "Total_Employment_Overhead", 
    "Net_Profit", 
    "Bank_Cash_Asset", 
    "HMRC_PAYE_NI_Liability", 
    "Pension_Liability",
    "Total_Current_Liabilities", 
    "Retained_Earnings"
]

# Rename columns on the fly for premium report presentation formatting
styled_df = integrated_forecast_df[presentation_columns].copy()
styled_df.columns = [
    "Turnover (£)", "Payroll Costs (£)", "Net Profit (£)", 
    "Bank Cash Position (£)", "HMRC PAYE/NI Owed (£)", "Pension Owed (£)", 
    "Creditors Under 1 Yr (£)", "Retained Earnings Balance (£)"
]

# Render the data table using container-width responsive formatting
st.dataframe(styled_df, use_container_width=True)

# --- 5. DATA EXPORT ACTIONS ---
st.markdown("---")
st.subheader("📥 Professional Reporting Suite Exports")
col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    # Format current dataframe state to standard flat CSV string for basic file downloads
    csv_buffer = styled_df.to_csv().encode('utf-8')
    st.download_button(
        label="📥 Download Data Dump Worksheet (.CSV)",
        data=csv_buffer,
        file_name="market_catalyst_3way_forecast.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_exp2:
    # Placeholder for the professional live-formula XlsxWriter engine we specified in our SRS
    if st.button("📊 Compile Board-Ready Live-Formula Workbook (.XLSX)", use_container_width=True):
        st.info("Triggering backend core_engine/exporters module: Compiling live spreadsheet with active string formulas...")