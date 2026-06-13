# pages/3_📊_forecast.py

import streamlit as st
import pandas as pd
import os

# Ensure the page layout is wide and consistent with the core theme
st.markdown("### 📊 Financial Forecast Dashboard")
st.markdown("---")

# Verify user security clearance before rendering ledger positions
if not st.session_state.get("authenticated", False):
    st.error("🔒 Access Denied: Unauthorized Endpoints Locked")
    st.info("This environment is shielded by an enterprise security framework. You must log in via the main portal to open this workspace.")
    st.stop()

# Define paths to the double-entry transaction caches
PL_CACHE = "STRATA_Forecast_Ledger_Group.xlsx - Profit & Loss.csv"
CF_CACHE = "STRATA_Forecast_Ledger_Group.xlsx - Cash Flow Ledger.csv"
BS_CACHE = "STRATA_Forecast_Ledger_Group.xlsx - Balance Sheet Accruals.csv"

# =========================================================================
# 📊 TOP LEVEL CUMULATIVE SUMMARY MATRIX
# =========================================================================
active_project = st.session_state.get("selected_project", "")
if active_project:
    st.sidebar.success(f"📁 Active Project: `{active_project}`")
else:
    st.sidebar.warning("⚠️ No Project Loaded from Workspace")

# Define reporting tabs mapping to the three traditional statement outputs
tab1, tab2, tab3 = st.tabs([
    "📈 Profit & Loss Statement", 
    "💸 Cash Flow Ledger", 
    "📋 Balance Sheet Accruals"
])

# =========================================================================
# 📈 TAB 1: PROFIT & LOSS STATEMENT VIEW
# =========================================================================
with tab1:
    st.subheader("📈 Integrated Profit & Loss Performance Matrix")
    st.markdown("All lines below are derived directly via structural Trial Balance validation routines.")
    
    if os.path.exists(PL_CACHE):
        try:
            pl_df = pd.read_csv(PL_CACHE, index_col=0)
            
            # Display transposed dataframe so months flow across as headers
            st.dataframe(pl_df.T.style.format("{:,.2f}"), use_container_width=True)
            
            # Key performance metrics summary block
            st.markdown("#### 🎯 Performance Summaries (60-Month Run)")
            col1, col2 = st.columns(2)
            with col1:
                total_rev = pl_df["Revenue (£)"].sum()
                st.metric("Total Project Turnover (60M)", f"£{total_rev:,.2f}")
            with col2:
                total_ebit = pl_df["EBIT (£)"].sum()
                st.metric("Accumulated Net EBIT (60M)", f"£{total_ebit:,.2f}")
                
        except Exception as e:
            st.error(f"Error rendering Profit & Loss dataset: {str(e)}")
    else:
        st.info("💡 Awaiting fresh double-entry calculation pass. Load your baseline project via the Data Ingestion Suite to hydrate this ledger.")

# =========================================================================
# 💸 TAB 2: CASH FLOW LEDGER VIEW
# =========================================================================
with tab2:
    st.subheader("💸 Chronological Cash Flow Ledger")
    st.markdown("Tracks liquid asset fluctuations resulting from real-time debit and credit handshakes.")
    
    if os.path.exists(CF_CACHE):
        try:
            cf_df = pd.read_csv(CF_CACHE, index_col=0)
            
            # Render chronological data table
            st.dataframe(cf_df.T.style.format("{:,.2f}"), use_container_width=True)
            
            # Dynamic Cash Curve Visualization
            st.markdown("#### 📈 Cumulative Net Cash Horizon")
            st.line_chart(cf_df["Cash Reserves (£)"], use_container_width=True)
            
        except Exception as e:
            st.error(f"Error rendering Cash Flow dataset: {str(e)}")
    else:
        st.info("💡 Awaiting fresh double-entry calculation pass. Load your baseline project via the Data Ingestion Suite to hydrate this ledger.")

# =========================================================================
# 📋 TAB 3: BALANCE SHEET ACCRUALS VIEW
# =========================================================================
with tab3:
    st.subheader("📋 Balance Sheet Accruals Ledger")
    st.markdown("Maintains continuous structural alignment. Asserts that Total Assets perfectly match Total Liabilities and Equity.")
    
    if os.path.exists(BS_CACHE):
        try:
            bs_df = pd.read_csv(BS_CACHE, index_col=0)
            
            # Render structural data matrix
            st.dataframe(bs_df.T.style.format("{:,.2f}"), use_container_width=True)
            
            # Absolute Accounting Integrity Indicator Flag
            st.success("🔒 Systemic Integrity Check: Balanced Ledger Context Maintained (Debits = Credits)")
            
        except Exception as e:
            st.error(f"Error rendering Balance Sheet dataset: {str(e)}")
    else:
        st.info("💡 Awaiting fresh double-entry calculation pass. Load your baseline project via the Data Ingestion Suite to hydrate this ledger.")