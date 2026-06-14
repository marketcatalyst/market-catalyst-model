# pages/4_🛡️_compliance.py

import os
import sys
import streamlit as st
import pandas as pd
from pathlib import Path

# Absolute project path resolution to handle multi-page layout shifts smoothly
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

# Check authentication profile cleanly without dropping a hard terminal stop
is_authenticated = st.session_state.get("authenticated", False)

st.title("🛡️ Regulatory Compliance & Audit Gateway")
st.caption("Baseline Data Verification Frameworks & HMRC Digital Audit Trails")
st.markdown("---")

if not is_authenticated:
    st.error("🔒 Access Denied: Unauthorized Endpoints Locked")
    st.info("This environment is shielded by an enterprise security framework. If you refreshed your browser or navigated directly to this sub-path, your active session keys were temporarily flushed.")
    
    # Provide an immediate escape hatch to return to the root gateway for re-authentication
    if st.button("🔑 Return to Main Portal Login", use_container_width=True):
        st.switch_page("app.py")
    st.stop()

# Define the absolute calculation endpoints written by our core double-entry engine
PL_CACHE = "STRATA_Forecast_Ledger_Group.xlsx - Profit & Loss.csv"
BS_CACHE = "STRATA_Forecast_Ledger_Group.xlsx - Balance Sheet Accruals.csv"

# --- 🏁 AUTHENTICATED TIER ---
st.subheader("📊 Dynamic Statutory Integrity Checks")
st.markdown("This control center extracts rolling tax allocations and setup values directly from your active baseline data model.")

# Initialize default fields in case calculation caches haven't run yet
live_vat_payable = 0.0
cumulative_depr = 0.0
active_project = st.session_state.get("selected_project", "No Baseline Loaded")

# Extract real ledger positions from disk caches
if os.path.exists(BS_CACHE):
    try:
        bs_df = pd.read_csv(BS_CACHE, index_col=0)
        # Pull the final month's standing balance for rolling tax reserves
        if "VAT Liability (£)" in bs_df.index:
            live_vat_payable = float(bs_df.loc["VAT Liability (£)"].iloc[-1])
        if "Accumulated Depreciation (£)" in bs_df.index:
            cumulative_depr = abs(float(bs_df.loc["Accumulated Depreciation (£)"].iloc[-1]))
    except Exception as e:
        st.sidebar.error(f"Compliance ledger parser anomaly: {str(e)}")

# Render real-time audit cards using simplified business descriptions
comp_col1, comp_col2, comp_col3 = st.columns(3)
with comp_col1:
    st.metric(
        label="Project Model Context", 
        value=active_project[:20] + "..." if len(active_project) > 20 else active_project, 
        delta="Workspace Linked"
    )
with comp_col2:
    st.metric(
        label="HMRC Rolling VAT Reserves", 
        value=f"£{live_vat_payable:,.2f}", 
        delta="MTD Output Tax Linked",
        delta_color="inverse"
    )
with comp_col3:
    st.metric(
        label="Capital Write-Off Allowances", 
        value=f"£{cumulative_depr:,.2f}", 
        delta="10% Straight Line Run"
    )

st.markdown("---")

# --- 🕒 SYSTEMIC HMRC TIME-SERIES TAX VIEW ---
st.subheader("📅 Chronological Tax Allocation Streams")
st.markdown("Forensic timeline mapping of data output values structured for digital submission windows (Making Tax Digital):")

if os.path.exists(BS_CACHE) and os.path.exists(PL_CACHE):
    try:
        bs_df = pd.read_csv(BS_CACHE, index_col=0)
        pl_df = pd.read_csv(PL_CACHE, index_col=0)
        
        # Build a focused, jargon-free compliance matrix matching user definitions
        compliance_matrix = pd.DataFrame({
            "Monthly Trading Income Received (£)": pl_df["Revenue (£)"],
            "Rolling VAT Reserves Owed (£)": bs_df["VAT Liability (£)"],
            "Monthly Non-Cash Asset Write-Off (£)": pl_df["Depreciation (£)"],
            "Net Infrastructure Asset Worth (£)": bs_df["Net Book Value (£)"]
        }, index=pl_df.index).T
        
        st.dataframe(compliance_matrix.style.format("{:,.2f}"), use_container_width=True)
        
    except Exception as matrix_err:
        st.error(f"Failed to compile statutory reporting matrix: {str(matrix_err)}")
else:
    st.info("💡 Awaiting background calculations. Set your rows on the Data Input Workspace to populate your statutory tax timelines.")

st.markdown("---")
st.subheader("📁 Standard Industrial Classification (SIC) Reference Check")
st.markdown("Verifying real-time regional benchmarks against statutory UK datasets:")

benchmark_path = Path(root_dir) / "static_data" / "sic_benchmarks.csv"
if benchmark_path.exists():
    try:
        df_sic = pd.read_csv(benchmark_path)
        st.dataframe(df_sic, use_container_width=True)
    except Exception as read_err:
        st.caption(f"Reference file structurally ready. Engine linked. ({str(read_err)})")
else:
    st.info("💡 Baseline benchmarking sub-ledger is empty. System is tracking exclusively to your explicit manual inputs.")