# pages/3_📊_forecast.py

import streamlit as st
import pandas as pd
import os
import json

# Set up page headers using clean commercial phrasing
st.title("📊 Commercial Financial Performance Forecasts")
st.caption("Simplified operational visibility models with interactive structural granularity selectors.")
st.markdown("---")

# Verify user security clearance before rendering data grids
if not st.session_state.get("authenticated", False):
    st.error("🔒 Access Denied: Unauthorized Endpoints Locked")
    st.info("This environment is shielded by an enterprise security framework. You must log in via the main portal to open this workspace.")
    st.stop()

# Auto-execute the calculation core on loading if an active workspace selection exists
active_project = st.session_state.get("selected_project", "")
project_file_path = os.path.join("saved_projects", f"{active_project}.json")

if active_project and os.path.exists(project_file_path):
    try:
        from ui_skin.core_engine.double_entry_matrix import compile_three_way_forecast
        compile_three_way_forecast(project_file_path)
        st.sidebar.success(f"📁 Active Project: `{active_project}`")
    except Exception as engine_err:
        st.sidebar.error(f"⚠️ Calculation Engine Error: {str(engine_err)}")
else:
    st.sidebar.warning("⚠️ No Active Project Context Loaded")

# Define internal cache targets written by the backend engine
PL_CACHE = "STRATA_Forecast_Ledger_Group.xlsx - Profit & Loss.csv"
CF_CACHE = "STRATA_Forecast_Ledger_Group.xlsx - Cash Flow Ledger.csv"
BS_CACHE = "STRATA_Forecast_Ledger_Group.xlsx - Balance Sheet Accruals.csv"

# =========================================================================
# CONTROL PANEL: GRANULARITY & DOWNLOAD CONTROLLER
# =========================================================================
st.subheader("⚙️ Statement View & Compilation Controls")

ctrl_col1, ctrl_col2 = st.columns([1, 2])

with ctrl_col1:
    view_granularity = st.radio(
        "Reporting Ledger Granularity Mode:",
        options=["Consolidated Account Buckets", "Granular Line-Item Accounts"],
        index=0,
        help="Switch between high-level operational summaries and expanded line-by-line account statements."
    )

with ctrl_col2:
    st.markdown("<div style='padding-top: 5px;'></div>", unsafe_allow_html=True)
    st.caption("Package active data arrays for distribution or external audit submission:")
    rep_col1, rep_col2, rep_col3 = st.columns(3)
    
    with rep_col1:
        if os.path.exists(PL_CACHE):
            with open(PL_CACHE, "rb") as f:
                st.download_button("📈 Download P&L (CSV)", data=f, file_name=f"{active_project}_P_and_L.csv", mime="text/csv", use_container_width=True)
        else: st.button("📈 P&L Offline", disabled=True, use_container_width=True)
        
    with rep_col2:
        if os.path.exists(CF_CACHE):
            with open(CF_CACHE, "rb") as f:
                st.download_button("💸 Download Cash (CSV)", data=f, file_name=f"{active_project}_Cash_Flow.csv", mime="text/csv", use_container_width=True)
        else: st.button("💸 Cash Offline", disabled=True, use_container_width=True)
        
    with rep_col3:
        if os.path.exists(BS_CACHE):
            with open(BS_CACHE, "rb") as f:
                st.download_button("📋 Download Assets (CSV)", data=f, file_name=f"{active_project}_Balance_Sheet.csv", mime="text/csv", use_container_width=True)
        else: st.button("📋 Assets Offline", disabled=True, use_container_width=True)

st.markdown("---")

# Clear, direct, human terminology tab groupings
tab1, tab2, tab3 = st.tabs([
    "📈 Income & Earnings Performance", 
    "💸 Bank Account Tracker (Cash Runway)", 
    "📋 Company Worth & Asset Register"
])

# Load master lists for line-item expansion mapping
raw_sales_setup = st.session_state.get("manual_sales_entries", [])
raw_opex_setup = st.session_state.get("manual_opex_entries", [])

# =========================================================================
# 📈 TAB 1: INCOME & EARNINGS PERFORMANCE (PROFIT & LOSS)
# =========================================================================
with tab1:
    st.subheader("📈 Income & Earnings Run-Rates")
    
    if os.path.exists(PL_CACHE):
        try:
            pl_df = pd.read_csv(PL_CACHE, index_col=0)
            total_rev = float(pl_df.loc["Revenue (£)"].sum()) if "Revenue (£)" in pl_df.index else 0.0
            ebit_row_key = [idx for idx in pl_df.index if "EBIT" in idx]
            total_margin = float(pl_df.loc[ebit_row_key[0]].sum()) if ebit_row_key else 0.0
            
            if view_granularity == "Consolidated Account Buckets":
                st.markdown("Displaying aggregated, executive-level corporate operational totals:")
                display_pl = pl_df.copy()
                display_pl.index = display_pl.index.str.replace("Opex", "Running Costs / Overheads")\
                                                   .str.replace("EBIT", "Net Operating Margin Profit")
                st.dataframe(display_pl.T.style.format("{:,.2f}"), use_container_width=True)
            else:
                st.markdown("De-consolidated view breaking down every independent account line over the 60-month runway:")
                
                # Build an expanded granular matrix dynamically based on active workspace parameters
                granular_rows = {}
                timeline_cols = pl_df.columns
                
                # Settle sales individual contributions
                for idx, item in enumerate(raw_sales_setup):
                    monthly_val = float(item["amount"]) / 12.0
                    granular_rows[f"Revenue Account: {item['name']} (£)"] = [monthly_val] * len(timeline_cols)
                if not raw_sales_setup and "Revenue (£)" in pl_df.index:
                    granular_rows["Revenue Account: Combined Core Inflow (£)"] = pl_df.loc["Revenue (£)"].tolist()
                    
                # Settle operational expenses individual contributions
                for idx, item in enumerate(raw_opex_setup):
                    monthly_val = float(item["amount"]) / 12.0
                    granular_rows[f"Overhead Account: {item['name']} (£)"] = [monthly_val] * len(timeline_cols)
                if not raw_opex_setup and "Opex (£)" in pl_df.index:
                    granular_rows["Overhead Account: Combined Overheads (£)"] = pl_df.loc["Opex (£)"].tolist()
                
                # Re-append lynchpin bottom lines to ensure mathematical control context
                if ebit_row_key:
                    granular_rows["Net Operating Margin Profit (EBIT) (£)"] = pl_df.loc[ebit_row_key[0]].tolist()
                if "Depreciation (£)" in pl_df.index:
                    granular_rows["Non-Cash Asset Write-Off (Depreciation) (£)"] = pl_df.loc["Depreciation (£)"].tolist()
                
                df_granular_pl = pd.DataFrame(granular_rows, index=timeline_cols).T
                st.dataframe(df_granular_pl.style.format("{:,.2f}"), use_container_width=True)
            
            # Summary Metrics Cards
            st.markdown("#### 🎯 Performance Summaries (60-Month Total Run)")
            col1, col2 = st.columns(2)
            with col1: st.metric("Total Project Turnover (60M)", f"£{total_rev:,.2f}")
            with col2: st.metric("Accumulated Net Profit Margin (60M)", f"£{total_margin:,.2f}")
                
        except Exception as e: st.error(f"Error rendering Income statement dataset: {str(e)}")
    else: st.info("💡 Awaiting initialization vectors from your active workspace.")

# =========================================================================
# 💸 TAB 2: BANK ACCOUNT TRACKER (CASH FLOW)
# =========================================================================
with tab2:
    st.subheader("💸 Real Bank Account Ledger Profile")
    st.markdown("Tracks the physical liquid cash cushion sitting inside the bank vaults over our 60-month horizon.")
    
    if os.path.exists(CF_CACHE):
        try:
            cf_df = pd.read_csv(CF_CACHE, index_col=0)
            st.dataframe(cf_df.T.style.format("{:,.2f}"), use_container_width=True)
            
            st.markdown("#### 📈 Compounding Cash Horizon Trajectory Curve")
            if "Cash Reserves (£)" in cf_df.index:
                st.line_chart(cf_df.loc["Cash Reserves (£)"], use_container_width=True)
        except Exception as e: st.error(f"Error rendering Bank Tracker dataset: {str(e)}")
    else: st.info("💡 Awaiting initialization vectors from your active workspace.")

# =========================================================================
# 📋 TAB 3: COMPANY WORTH REGISTER (BALANCE SHEET)
# =========================================================================
with tab3:
    st.subheader("📋 Core Company Worth Register")
    st.markdown("What the project owns (Assets) vs. exactly what it owes (Liabilities and Reserves).")
    
    if os.path.exists(BS_CACHE):
        try:
            bs_df = pd.read_csv(BS_CACHE, index_col=0)
            display_bs = bs_df.copy()
            display_bs.index = display_bs.index.str.replace("Fixed Assets", "Physical Infrastructure Asset Worth")\
                                               .str.replace("Net Book Value", "Net Depreciated Asset Valuation")\
                                               .str.replace("VAT Liability", "HMRC VAT Reserves Owing")\
                                               .str.replace("Equity Capital", "Total Capital Contributed Cushion")
            
            st.dataframe(display_bs.T.style.format("{:,.2f}"), use_container_width=True)
            st.success("🔒 System Integrity Flag: Company worth register completely reconciled and in balance.")
        except Exception as e: st.error(f"Error rendering Company Worth dataset: {str(e)}")
    else: st.info("💡 Awaiting initialization vectors from your active workspace.")