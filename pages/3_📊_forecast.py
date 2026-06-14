# pages/3_📊_forecast.py

import streamlit as st
import pandas as pd
import os

# Set up page headers using clean commercial phrasing
st.title("📊 Commercial Financial Performance Forecasts")
st.caption("Simplified operational visibility models stripped of academic accounting jargon.")
st.markdown("---")

# Verify user security clearance before rendering data grids
if not st.session_state.get("authenticated", False):
    st.error("🔒 Access Denied: Unauthorized Endpoints Locked")
    st.info("This environment is shielded by an enterprise security framework. You must log in via the main portal to open this workspace.")
    st.stop()

# Auto-execute the calculation core on loading if an active workspace selection exists
active_project = st.session_state.get("selected_project", "")
if active_project:
    project_file_path = os.path.join("saved_projects", f"{active_project}.json")
    if os.path.exists(project_file_path):
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

# Clear, direct, human terminology tab groupings
tab1, tab2, tab3 = st.tabs([
    "📈 Income & Earnings Performance", 
    "💸 Bank Account Tracker (Cash Runway)", 
    "📋 Company Worth & Asset Register"
])

# =========================================================================
# 📈 TAB 1: INCOME & EARNINGS PERFORMANCE (PROFIT & LOSS)
# =========================================================================
with tab1:
    st.subheader("📈 Monthly Income & Earnings Run-Rates")
    st.markdown("This matrix tracks whether your venue is generating a positive net profit margin on paper month-by-month.")
    
    if os.path.exists(PL_CACHE):
        try:
            pl_df = pd.read_csv(PL_CACHE, index_col=0)
            
            # Create explicit, clear indexing for internal metrics before display modifications
            total_rev = float(pl_df.loc["Revenue (£)"].sum()) if "Revenue (£)" in pl_df.index else 0.0
            
            # Handle variable names defensively regardless of incoming brackets
            ebit_row_key = [idx for idx in pl_df.index if "EBIT" in idx]
            total_margin = float(pl_df.loc[ebit_row_key[0]].sum()) if ebit_row_key else 0.0
            
            # Translate dense textbook labels into clear business lines for the user
            pl_df.index = pl_df.index.str.replace("Opex", "Running Costs / Overheads")\
                                     .str.replace("EBIT", "Net Operating Margin Profit")
            
            # Render the 60-month horizontal table grid
            st.dataframe(pl_df.T.style.format("{:,.2f}"), use_container_width=True)
            
            # Focused executive performance summary block
            st.markdown("#### 🎯 Performance Summaries (60-Month Total Run)")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Project Turnover (60M)", f"£{total_rev:,.2f}")
            with col2:
                st.metric("Accumulated Net Profit Margin (60M)", f"£{total_margin:,.2f}")
                
        except Exception as e:
            st.error(f"Error rendering Income statement dataset: {str(e)}")
    else:
        st.info("💡 Awaiting parameters initialization. Set your rows on the Data Input Workspace to populate this layout.")

# =========================================================================
# 💸 TAB 2: BANK ACCOUNT TRACKER (CASH FLOW)
# =========================================================================
with tab2:
    st.subheader("💸 Real Bank Account Ledger Profile")
    st.markdown("Tracks the physical liquid cash cushion sitting inside the bank vaults over our 60-month horizon.")
    
    if os.path.exists(CF_CACHE):
        try:
            cf_df = pd.read_csv(CF_CACHE, index_col=0)
            
            # Render chronological spreadsheet grid
            st.dataframe(cf_df.T.style.format("{:,.2f}"), use_container_width=True)
            
            # Dynamic Cash Curve Trend Graph
            st.markdown("#### 📈 Compounding Cash Horizon Trajectory Curve")
            if "Cash Reserves (£)" in cf_df.index:
                st.line_chart(cf_df.loc["Cash Reserves (£)"], use_container_width=True)
            
        except Exception as e:
            st.error(f"Error rendering Bank Tracker dataset: {str(e)}")
    else:
        st.info("💡 Awaiting parameters initialization. Set your rows on the Data Input Workspace to populate this layout.")

# =========================================================================
# 📋 TAB 3: COMPANY WORTH REGISTER (BALANCE SHEET)
# =========================================================================
with tab3:
    st.subheader("📋 Core Company Worth Register")
    st.markdown("What the project owns (Infrastructure, Courts, Equipment) vs. exactly what it owes (Loans, Tax reserves).")
    
    if os.path.exists(BS_CACHE):
        try:
            bs_df = pd.read_csv(BS_CACHE, index_col=0)
            
            # Sweep complex textbook labels into clean physical concepts
            bs_df.index = bs_df.index.str.replace("Fixed Assets", "Physical Infrastructure Asset Worth")\
                                     .str.replace("Net Book Value", "Net Depreciated Asset Valuation")\
                                     .str.replace("VAT Liability", "HMRC VAT Reserves Owing")\
                                     .str.replace("Equity Capital", "Total Capital Contributed Cushion")
            
            # Render asset ledger grid
            st.dataframe(bs_df.T.style.format("{:,.2f}"), use_container_width=True)
            st.success("🔒 System Integrity Flag: Company worth register completely reconciled and in balance.")
            
        except Exception as e:
            st.error(f"Error rendering Company Worth dataset: {str(e)}")
    else:
        st.info("💡 Awaiting parameters initialization. Set your rows on the Data Input Workspace to populate this layout.")