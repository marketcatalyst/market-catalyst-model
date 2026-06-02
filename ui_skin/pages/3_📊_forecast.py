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
        
    # --- TAB 3: CASH FLOW ---
    with tab_cf:
        st.markdown(f"### **Statement of Cash Flows ({horizon_months}-Month Runway)**")
        cf_working = forecast_df[["Month", "Net Profit (£)", "Bank Cash Position (£)"]].copy()
        
        # Calculate periodic movement differences against the opening cash baseline (£69,488.00)
        cf_working["Net Cash Flow Movement"] = cf_working["Bank Cash Position (£)"].diff().fillna(cf_working["Bank Cash Position (£)"] - 69488.00)
        
        cf_rows = {
            "Net Profit (£)": "Net Profit from Operations (Accrued P&L)", 
            "Net Cash Flow Movement": "Net Periodic Cash Inflow / (Outflow)", 
            "Bank Cash Position (£)": "Closing Liquidity Bank Balance"
        }
        st.data_editor(create_accounting_statement(cf_working, cf_rows), use_container_width=True, hide_index=True, key="cf_view_editor")
        
    # --- TAB 4: MASTER DATA LEDGER GRID (HORIZONTAL TRANSPOSED LOOKUP) ---
    with tab_master:
        st.markdown("### **Master Data Ledger Grid (Horizontal Time-Series Matrix View)**")
        
        # Set the tracking month index as the index before running transposition (.T) to align months on columns
        master_transposed = forecast_df.set_index("Month").T.reset_index().rename(columns={"index": "Database Structural Field"})
        st.data_editor(master_transposed, use_container_width=True, hide_index=True, key="master_grid_editor")

    # ==========================================
    # 📥 THE STRATEGIC EXPORT PANEL
    # ==========================================
    st.markdown("---")
    st.subheader("📊 Executive Data Visualization & Reporting Suite")
    
    chart_bytes = ff.generate_forecast_charts(forecast_df)
    st.image(chart_bytes, caption="Dynamic 3-Way Forecasting Macro Performance Dashboard Chart Output")
    
    st.markdown("---")
    st.markdown("### **📥 Downstream Document Export Gateway**")
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    
    with col_dl1:
        xlsx_data = ff.convert_df_to_excel(forecast_df)
        st.download_button(
            label="📁 Download Multi-Tab Excel Workpack (.xlsx)",
            data=xlsx_data,
            file_name="market_catalyst_winforecast_replication_pack.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with col_dl2:
        csv_data = forecast_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download Raw Consolidated Data (.csv)",
            data=csv_data,
            file_name="market_catalyst_flat_replication_ledger.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_dl3:
        st.button(
            "📋 Compile PDF Executive Management Report",
            on_click=lambda: st.toast("🛠️ Generating ReportLab print canvas matrix...", icon="📋"),
            use_container_width=True
        )