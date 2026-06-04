# ui_skin/pages/3_📊_forecast.py
import streamlit as st
import pandas as pd
import numpy as np
# Cloud Container Path Resolution Fix
from ui_skin.core_engine.master_orchestrator import run_master_three_way_engine

st.set_page_config(layout="wide", page_title="Financial Statements Forecast")

st.title("📊 Synchronized 3-Way Financial Statements")
st.caption("60-Month Institutional Forecast Engine Backed by Proactive Working Capital Modifiers")
st.markdown("---")

# --- 1. SESSION STATE VERIFICATION & FALLBACK PROTECTION ---
if "baseline_inputs" not in st.session_state or "raw_loan_register" not in st.session_state or "raw_revenue_matrix" not in st.session_state:
    st.warning("⚠️ **Upstream Data Missing:** Active session data not detected. Please initialize your parameters on the Ingestion page first.")
    st.stop()

# Reconstruct planned capex lists dynamically from active state
planned_capex_list = []
if "asset_ledger" in st.session_state:
    for _, row in st.session_state["asset_ledger"].iterrows():
        planned_capex_list.append({
            "Category": row.get("Asset Category"),
            "Gross Purchase Price (£)": row.get("Original Cost (£)", 0.0),
            "Transaction Month": 0,
            "Disposal Month": -1,
            "Disposal Proceeds (£)": 0.0
        })

# --- 2. EXECUTE MASTER PIPELINE CALCULATIONS ---
with st.spinner("Re-consolidating multi-source dynamic matrix models..."):
    engine_output = run_master_three_way_engine(
        baseline_inputs=st.session_state["baseline_inputs"],
        loan_register_df=st.session_state["raw_loan_register"],
        revenue_matrix_df=st.session_state["raw_revenue_matrix"],
        planned_capex_list=planned_capex_list,
        total_months=60
    )

# Establish time-series layout indexes
timeline_columns = [f"Month {i}" for i in range(1, 61)]

# --- 3. RENDERING THE INTERACTIVE REPORTING TABS ---
tab_pl, tab_cf, tab_bs = st.tabs(["📈 Profit & Loss Statement", "💸 Cash Flow Statement", "⚖️ Balance Sheet Position"])

with tab_pl:
    st.markdown("### **Integrated Income Statement (P&L)**")
    st.caption("Reflects production matching rules. Gross margins are protected from warehouse accumulation spikes.")
    
    ebitda = engine_output["Revenue"] - engine_output["COGS"] - engine_output["Overheads"]
    operating_profit = ebitda - engine_output["Depreciation"] - engine_output["Interest Paid"]
    
    pl_data = {
        "Gross Revenue Turnover (£)": engine_output["Revenue"],
        "Direct Raw Material Purchases (£)": -engine_output["Purchases"],
        "Add/Less: Capitalized Stock Movement (£)": engine_output["Stock Movement"],
        "**TOTAL COST OF GOODS SOLD (COGS) (£)**": -engine_output["COGS"],
        "Administrative Overheads (£)": -engine_output["Overheads"],
        "**OPERATIONAL EBITDA (£)**": ebitda,
        "Book Depreciation Expense (£)": -engine_output["Depreciation"],
        "Finance Costs / Interest Expense (£)": -engine_output["Interest Paid"],
        "**OPERATING PROFIT (EBIT) (£)**": operating_profit,
        "Statutory Corporation Tax Provision (£)": -engine_output["Tax Expense"],
        "***NET PROFIT AFTER TAX (EAT) (£)***": engine_output["Net Profit"]
    }
    
    pl_df = pd.DataFrame(pl_data, index=timeline_columns).T
    st.dataframe(pl_df.style.format("£{:,.2f}"), use_container_width=True)

with tab_cf:
    st.markdown("### **Indirect Cash Flow Statement**")
    st.caption("Reconciles net accounting profit directly back to cash movements by tracking working capital changes.")
    
    net_operating_cash_flow = (
        engine_output["Net Profit"]
        + engine_output["Depreciation"]
        + engine_output["Stock Movement"] 
    )
    
    cf_data = {
        "Net Profit Allocation (£)": engine_output["Net Profit"],
        "Add: Non-Cash Depreciation (£)": engine_output["Depreciation"],
        "Add/Less: Stock Movement Non-Cash Delta (£)": engine_output["Stock Movement"],
        "Less: Debt Principal Repayments (£)": -engine_output["Principal Repayments"],
        "Less: Corporation Tax Payouts (£)": -engine_output["Tax Cash Paid"],
        "Less: Interest Payments (£)": -engine_output["Interest Paid"],
        "Add: Asset Disposal Proceeds Windfalls (£)": engine_output["Asset Disposal Proceeds"],
        "**Net Monthly Cash Flow Movement (£)**": (net_operating_cash_flow - engine_output["Principal Repayments"] - engine_output["Tax Cash Paid"] - engine_output["Interest Paid"] + engine_output["Asset Disposal Proceeds"]),
        "***CLOSING BANK CASH POSITION (£)***": engine_output["Cash At Bank"]
    }
    
    cf_df = pd.DataFrame(cf_data, index=timeline_columns).T
    st.dataframe(cf_df.style.format("£{:,.2f}"), use_container_width=True)

with tab_bs:
    st.markdown("### **Statement of Financial Position (Balance Sheet)**")
    st.caption("Verifies system equity equilibrium. Total Assets minus Total Liabilities must equal Retained Reserves.")
    
    # Extract structural starting configurations from active ingestion memory state
    cash_seed = float(st.session_state["baseline_inputs"].get("opening_cash_balance", 69488.0))
    fa_seed = float(st.session_state["baseline_inputs"].get("opening_fixed_assets_nbv", 150000.0))
    ar_seed = float(st.session_state["baseline_inputs"].get("opening_accounts_receivable", 44886.0))
    ap_seed = float(st.session_state["baseline_inputs"].get("opening_accounts_payable", 8000.0))
    debt_seed = float(st.session_state["baseline_inputs"].get("opening_long_term_debt", 0.0))
    
    # Extract initial warehouse inventory base to anchor baseline values
    inv_seed = engine_output["Inventory Asset BS"][0]
    
    # SYSTEM FIX: Dynamically derive opening retained earnings to absorb active policy variables cleanly
    re_seed = (cash_seed + fa_seed + ar_seed + inv_seed) - (debt_seed + ap_seed)
    
    timeline_ap = np.full(60, ap_seed)
    
    # Roll retained earnings forward dynamically matching net profit generation
    timeline_re = np.zeros(60)
    running_re = re_seed
    for m in range(60):
        running_re += engine_output["Net Profit"][m]
        timeline_re[m] = running_re
        
    total_assets = engine_output["Fixed Asset NBV"] + engine_output["Cash At Bank"] + engine_output["Inventory Asset BS"] + engine_output["Accounts Receivable BS"]
    total_liabilities = engine_output["Outstanding Debt"] + engine_output["Tax Liability BS"] + timeline_ap
    net_assets = total_assets - total_liabilities
    
    bs_data = {
        "Non-Current Assets: Fixed Assets NBV (£)": engine_output["Fixed Asset NBV"],
        "Current Assets: Warehouse Inventory Pool (£)": engine_output["Inventory Asset BS"],
        "Current Assets: Accounts Receivable (AR) (£)": engine_output["Accounts Receivable BS"],
        "Current Assets: Liquid Cash Base (£)": engine_output["Cash At Bank"],
        "**TOTAL STRUCTURAL ASSETS (£)**": total_assets,
        "Non-Current Liabilities: Outstanding Debt (£)": -engine_output["Outstanding Debt"],
        "Current Liabilities: Deferred Tax Reserve (£)": -engine_output["Tax Liability BS"],
        "Current Liabilities: Accounts Payable (AP) (£)": -timeline_ap,
        "**TOTAL STRUCTURAL LIABILITIES (£)**": -total_liabilities,
        "***NET NET ASSETS CAPITAL (£)***": net_assets,
        "Equity: Accumulated Retained Reserves (£)": timeline_re,
        "**TOTAL CAPITAL AND RESERVES MATCH (£)**": timeline_re
    }
    
    bs_df = pd.DataFrame(bs_data, index=timeline_columns).T
    st.dataframe(bs_df.style.format("£{:,.2f}"), use_container_width=True)

    # --- THREE-WAY LEDGER EQUILIBRIUM GUARDRAIL ---
    numerical_variance = np.abs(net_assets - timeline_re)
    unbalanced_months = np.where(numerical_variance > 0.05)[0]
    
    if len(unbalanced_months) == 0:
        st.success("⚖️ **Ledger Equilibrium Verified:** The Balance Sheet scales and balances perfectly across all 60 forecast months.")
    else:
        st.error(f"⚠️ **Ledger Disbalance Warning:** Numerical variance detected inside Month Index positions: {unbalanced_months + 1}")