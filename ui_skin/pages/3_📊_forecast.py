# ui_skin/pages/3_📊_forecast.py
import streamlit as st
import pandas as pd
import numpy as np
from core_engine.master_orchestrator import run_master_three_way_engine

st.set_page_config(layout="wide", page_title="Financial Statements Forecast")

st.title("📊 Synchronized 3-Way Financial Statements")
st.caption("60-Month Institutional Forecast Engine Powered by Real-Time Ingestion Channels")
st.markdown("---")

# --- 1. SESSION STATE VERIFICATION & FALLBACK PROTECTION ---
if "baseline_inputs" not in st.session_state or "raw_loan_register" not in st.session_state or "raw_revenue_matrix" not in st.session_state:
    st.warning("⚠️ **Upstream Data Missing:** Active session data not detected. Please initialize the pipeline on the Ingestion page first.")
    st.stop()

# Gracefully build the CapEx list from the asset ledger state or provide an empty placeholder array
planned_capex_list = []
if "asset_ledger" in st.session_state:
    for _, row in st.session_state["asset_ledger"].iterrows():
        planned_capex_list.append({
            "Category": row.get("Asset Category"),
            "Gross Purchase Price (£)": row.get("Original Cost (£)", 0.0),
            "Transaction Month": 0, # Seeding as legacy opening position
            "Disposal Month": -1,
            "Disposal Proceeds (£)": 0.0
        })

# --- 2. EXECUTE MASTER ENGINE RECONCILIATION ---
with st.spinner("Executing structural multi-engine consolidation loops..."):
    engine_output = run_master_three_way_engine(
        baseline_inputs=st.session_state["baseline_inputs"],
        loan_register_df=st.session_state["raw_loan_register"],
        revenue_matrix_df=st.session_state["raw_revenue_matrix"],
        planned_capex_list=planned_capex_list,
        total_months=60
    )

# Establish uniform chronological timeline headers (Month 1 to Month 60)
timeline_columns = [f"Month {i}" for i in range(1, 61)]

# --- 3. CONSTRUCT INTERACTIVE REPORTING TABS ---
tab_pl, tab_cf, tab_bs = st.tabs(["📈 Profit & Loss Statement", "💸 Cash Flow Statement", "⚖️ Balance Sheet Position"])

with tab_pl:
    st.markdown("### **Integrated Income Statement (P&L)**")
    st.caption("Tracks operational revenue, overhead splits, and non-cash depreciation adjustments.")
    
    ebitda = engine_output["Revenue"] - engine_output["COGS"] - engine_output["Overheads"]
    operating_profit = ebitda - engine_output["Depreciation"] - engine_output["Interest Paid"]
    
    pl_data = {
        "Revenue (£)": engine_output["Revenue"],
        "Cost of Sales (COGS) (£)": -engine_output["COGS"],
        "Administrative Overheads (£)": -engine_output["Overheads"],
        "**EBITDA (£)**": ebitda,
        "Book Depreciation Expense (£)": -engine_output["Depreciation"],
        "Finance Costs (Interest) (£)": -engine_output["Interest Paid"],
        "**Operating Profit (EBIT) (£)**": operating_profit,
        "Statutory Corporation Tax (£)": -engine_output["Tax Expense"],
        "***NET PROFIT AFTER TAX (£)***": engine_output["Net Profit"]
    }
    
    pl_df = pd.DataFrame(pl_data, index=timeline_columns).T
    st.dataframe(pl_df.style.format("£{:,.2f}"), use_container_width=True)

with tab_cf:
    st.markdown("### **Indirect Cash Flow Statement**")
    st.caption("Reconciles net accounting profit back to true liquid bank cash movements.")
    
    net_cash_flow = (
        engine_output["Net Profit"] 
        + engine_output["Depreciation"] 
        - engine_output["Principal Repayments"] 
        - engine_output["Tax Cash Paid"] 
        + engine_output["Asset Disposal Proceeds"]
    )
    
    cf_data = {
        "Net Profit Allocation (£)": engine_output["Net Profit"],
        "Add: Non-Cash Depreciation (£)": engine_output["Depreciation"],
        "Less: Debt Principal Repayments (£)": -engine_output["Principal Repayments"],
        "Less: Corporation Tax Settlements (£)": -engine_output["Tax Cash Paid"],
        "Add: Asset Disposal Windfalls (£)": engine_output["Asset Disposal Proceeds"],
        "**Net Monthly Cash Flow Movement (£)**": net_cash_flow,
        "***CLOSING BANK CASH CLEARING (£)***": engine_output["Cash At Bank"]
    }
    
    cf_df = pd.DataFrame(cf_data, index=timeline_columns).T
    st.dataframe(cf_df.style.format("£{:,.2f}"), use_container_width=True)

with tab_bs:
    st.markdown("### **Statement of Financial Position (Balance Sheet)**")
    st.caption("Confirms double-entry ledger balance state. Net assets must equal equity pools.")
    
    # Calculate closing balances based on initial seeds
    ar_seed = float(st.session_state["baseline_inputs"].get("opening_accounts_receivable", 44886.0))
    ap_seed = float(st.session_state["baseline_inputs"].get("opening_accounts_payable", 8000.0))
    re_seed = float(st.session_state["baseline_inputs"].get("opening_retained_earnings", -82005.0))
    
    timeline_ar = np.full(60, ar_seed)
    timeline_ap = np.full(60, ap_seed)
    
    # Accumulate retained earnings from monthly profit run-rates
    timeline_re = np.zeros(60)
    running_re = re_seed
    for m in range(60):
        running_re += engine_output["Net Profit"][m]
        timeline_re[m] = running_re
        
    total_assets = engine_output["Fixed Asset NBV"] + engine_output["Cash At Bank"] + timeline_ar
    total_liabilities = engine_output["Outstanding Debt"] + engine_output["Tax Liability BS"] + timeline_ap
    net_assets = total_assets - total_liabilities
    
    bs_data = {
        "Non-Current Assets: Fixed Assets NBV (£)": engine_output["Fixed Asset NBV"],
        "Current Assets: Liquid Cash Base (£)": engine_output["Cash At Bank"],
        "Current Assets: Accounts Receivable (£)": timeline_ar,
        "**TOTAL CORPORATE ASSETS (£)**": total_assets,
        "Non-Current Liabilities: Long-Term Debt (£)": -engine_output["Outstanding Debt"],
        "Current Liabilities: Deferred Tax Reserve (£)": -engine_output["Tax Liability BS"],
        "Current Liabilities: Accounts Payable (£)": -timeline_ap,
        "**TOTAL CORPORATE LIABILITIES (£)**": -total_liabilities,
        "***NET NET ASSETS POSITION (£)***": net_assets,
        "Equity: Accumulated Retained Reserves (£)": timeline_re,
        "**TOTAL CORPORATE EQUITY MATCH (£)**": timeline_re
    }
    
    bs_df = pd.DataFrame(bs_data, index=timeline_columns).T
    st.dataframe(bs_df.style.format("£{:,.2f}"), use_container_width=True)

    # --- DOUBLE ENTRY BALANCING VERIFICATION GUARDRAIL ---
    unbalanced_months = np.where(np.abs(net_assets - timeline_re) > 0.05)[0]
    if len(unbalanced_months) == 0:
        st.success("⚖️ **Ledger Equilibrium Verified:** The Balance Sheet scales and balances perfectly across all 60 forecast months.")
    else:
        st.error(f"⚠️ **Structural Disbalance Warning:** Numerical variance detected in Month Index positions: {unbalanced_months + 1}")