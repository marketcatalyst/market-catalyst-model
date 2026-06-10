# ui_skin/pages/3_📊_forecast.py
import sys
from pathlib import Path

# --- 1. CRITICAL PATH RESOLUTION ---
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="STRATA Forecast Ledger")

# --- 2. SECURITY GATEKEEPER CONSTRAINT ---
if "authenticated" not in st.session_state or not st.session_state["authenticated"] or "baseline_inputs" not in st.session_state:
    st.error("🔒 **Access Denied: Unauthorized Endpoints Locked**")
    st.info("This environment is shielded by an enterprise security framework. You must log in via the main portal to open this workspace.")
    if st.button("Return to Portal Landing Page", use_container_width=True):
        st.switch_page("home.py")
    st.stop()

from ui_skin.core_engine.master_model import generate_integrated_3way_forecast

st.title("📊 Integrated Three-Way Financial Forecast")
st.caption("60-Month Whole-Pound Ledger: Income Statement, Balance Sheet Accruals, and Cash Runway Projections")
st.markdown("---")

# --- 3. LIVE CALCULATIONS RUNTIME ---
inputs_package = st.session_state["baseline_inputs"]

# Generate the master computation matrix from our single source of truth
try:
    forecast_matrix = generate_integrated_3way_forecast(inputs_package, overrides={})
    months = forecast_matrix.index
    
    # --- 4. EXECUTIVE SUMMARY METRICS ---
    final_cash = forecast_matrix["Cash Reserves (£)"].iloc[-1]
    peak_debt_service = forecast_matrix["Debt Service Cash Outflow (£)"].max()
    total_revenue_projected = forecast_matrix["Revenue (£)"].sum()
    
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric(label="M60 Target Cash Reserves", value=f"£{final_cash:,.0f}")
    with metric_col2:
        st.metric(label="Peak Monthly Debt Service Obligation", value=f"£{peak_debt_service:,.0f}", delta="Fixed Liability Outflow", delta_color="inverse")
    with metric_col3:
        st.metric(label="60-Month Cumulative Gross Turnover", value=f"£{total_revenue_projected:,.0f}")
        
    st.markdown("---")
    
    # --- 5. LEDGER TAB COMPONENT ARCHITECTURE ---
    tab_pl, tab_cash, tab_tax_debt = st.tabs(["📈 Profit & Loss Statement", "💰 Cash Flow Runway", "🏛️ HMRC Tax & Debt Ledgers"])
    
    with tab_pl:
        st.subheader("Income Statement Projections")
        pl_display = pd.DataFrame({
            "Gross Revenue (£)": forecast_matrix["Revenue (£)"],
            "Cost of Goods Sold (£)": forecast_matrix["COGS (£)"],
            "Operating Expenses (£)": forecast_matrix["Opex (£)"],
            "EBIT (Operating Profit) (£)": forecast_matrix["EBIT (£)"],
            "Interest Overhead (£)": forecast_matrix["Interest Expense (£)"]
        }, index=months).T
        
        st.dataframe(
            pl_display, use_container_width=True,
            column_config={m: st.column_config.NumberColumn(format="£%,.0f") for m in months}
        )
        
    with tab_cash:
        st.subheader("Cash Positioning Timeline")
        st.caption("Reflects trading profits, location-specific VAT collections, and your contractual loan repayments.")
        
        # Display our whole-pound cash ledger chart
        st.line_chart(forecast_matrix["Cash Reserves (£)"], color="#2E7D32")
        
        cash_display = pd.DataFrame({
            "Net Trading Cash Flow (£)": (forecast_matrix["EBIT (£)"] * 0.85),
            "Debt Service Outflow (£)": forecast_matrix["Debt Service Cash Outflow (£)"],
            "Quarterly VAT Cash Settled (£)": forecast_matrix["VAT Cash Outflow (£)"],
            "Closing Bank Balance (£)": forecast_matrix["Cash Reserves (£)"]
        }, index=months).T
        
        st.dataframe(
            cash_display, use_container_width=True,
            column_config={m: st.column_config.NumberColumn(format="£%,.0f") for m in months}
        )
        
    with tab_tax_debt:
        st.subheader("HMRC Statutory Obligations & Corporate Debt Balances")
        st.markdown("Track rolling corporate tax provisions, quarterly VAT liability hold accounts, and outstanding debt amortization sweeps.")
        
        tax_debt_display = pd.DataFrame({
            "Outstanding Debt Balance (£)": forecast_matrix["Outstanding Debt Balance (£)"],
            "Monthly Debt Cash Outflow (£)": forecast_matrix["Debt Service Cash Outflow (£)"],
            "HMRC Corp Tax Provision BS (£)": forecast_matrix["Tax Liability BS (£)"],
            "HMRC Rolling VAT Hold BS (£)": forecast_matrix["VAT Liability BS (£)"]
        }, index=months).T
        
        st.dataframe(
            tax_debt_display, use_container_width=True,
            column_config={m: st.column_config.NumberColumn(format="£%,.0f") for m in months}
        )
        
except Exception as e:
    st.error(f"Execution Error: Downstream matrices could not compile.")
    st.info("Please ensure your operational attributes are fully synchronized on the Data Ingestion Page.")