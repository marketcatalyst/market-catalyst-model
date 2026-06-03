# ui_skin/pages/3_📊_forecast.py
import streamlit as st
import pandas as pd
import numpy as np

# Native Workspace Root Import relative to Streamlit Cloud container execution context
import core_engine.forecast_formulas as ff

st.set_page_config(layout="wide", page_title="3-Way Financial Forecast")

st.title("📊 Primary 3-Way Integrated Forecast")
st.caption("Core Financial Reporting Layer • Professional Multi-Statement Ledger Framework")
st.markdown("---")

# --- SIDEBAR Horizon Timeline Configuration ---
st.sidebar.header("📅 Timeline Horizon Configuration")
horizon_months = st.sidebar.slider("Forecast Horizon Runway (Months)", 12, 60, 36, 12)
st.sidebar.markdown("---")

# Execute the advanced multi-site replication engine loop
forecast_df = ff.run_winforecast_replication_engine(months=horizon_months)

# ==========================================
# RENDER STATEMENT VIEWS
# ==========================================
if forecast_df is not None:
    cumulative_variance = forecast_df["Variance Check (£)"].iloc[-1]
    
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
        
    # --- TAB 1: PROFIT & LOSS ---
    with tab_pl:
        st.markdown(f"### **Statement of Profit or Loss ({horizon_months}-Month Runway)**")
        pl_rows = {
            "Turnover (£)": "Revenue (Turnover Summary)", 
            "Direct Costs (£)": "  Less: Operating Cost of Sales (Direct COGS)",
            "Depreciation Expense (£)": "  Less: Non-Cash Asset Impairments (Depreciation)",
            "Net Profit (£)": "Net Operating Profit / (Loss) Retained Earnings"
        }
        st.data_editor(create_accounting_statement(forecast_df, pl_rows), use_container_width=True, hide_index=True, key="pl_view_editor")

    # --- TAB 2: BALANCE SHEET ---
    with tab_bs:
        st.markdown(f"### **Statement of Financial Position ({horizon_months}-Month Snapshot)**")
        bs_rows = {
            "Fixed Asset NBV (£)": "Non-Current Assets: Fixed Assets Carrying NBV",
            "Bank Cash Position (£)": "Current Assets: Bank Liquidity Clearing Balance", 
            "Accounts Payable & Debt (£)": "Current Liabilities: Accounts Payable & Loan Obligations", 
            "Retained Earnings (£)": "Capital & Reserves: Accumulated Retained Earnings Pool", 
            "Variance Check (£)": "Double-Entry Validation Variance"
        }
        st.data_editor(create_accounting_statement(forecast_df, bs_rows), use_container_width=True, hide_index=True, key="bs_view_editor")
        
    # --- TAB 3: CASH FLOW (ADVANCED ACCRUAL-TO-CASH RECONCILIATION BRIDGE) ---
    with tab_cf:
        st.markdown(f"### **Statement of Cash Flows ({horizon_months}-Month Indirect Reconciliation)**")
        st.markdown("This schedule bridges accrued accounting profits directly to physical liquid bank cash movements.")
        st.markdown("---")
        
        cf_bridge_rows = {
            "Bridge: Net Profit": "Net Operating Profit / (Loss) (Accrued P&L Base)",
            "Bridge: Depreciation": "  Add Back: Non-Cash Asset Depreciation Charges",
            "Bridge: Operating CF": "👉 NET CASH FLOW FROM OPERATING ACTIVITIES",
            "Bridge: Investing CF": "📁 Net Cash Outflows for Capital Expenditures (Investing CapEx)",
            "Bridge: Financing CF": "🏦 Net Cash Flow Movements from Financing Events",
            "Bridge: Net Movement": "🎯 NET PERIODIC CASH FLOW INCREASE / (DECREASE)",
            "Bank Cash Position (£)": "💰 CLOSING LIQUID BANK CASH POSITION"
        }
        st.data_editor(create_accounting_statement(forecast_df, cf_bridge_rows), use_container_width=True, hide_index=True, key="cf_bridge_view_editor")
        
    # --- TAB 4: MASTER DATA LEDGER GRID ---
    with tab_master:
        st.markdown("### **Master Data Ledger Grid (Horizontal Time-Series Matrix View)**")
        master_transposed = forecast_df.set_index("Month").T.reset_index().rename(columns={"index": "Database Structural Field"})
        st.data_editor(master_transposed, use_container_width=True, hide_index=True, key="master_grid_editor")

    # ==========================================
    # 📥 EXPORT PANEL
    # ==========================================
    st.markdown("---")
    st.subheader("📊 Executive Data Visualization & Reporting Suite")
    
    chart_bytes = ff.generate_forecast_charts(forecast_df)
    st.image(chart_bytes, caption="Dynamic 3-Way Forecasting Performance Dashboard Chart")