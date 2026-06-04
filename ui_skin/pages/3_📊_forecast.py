# ui_skin/pages/3_📊_forecast.py
import streamlit as st
import pandas as pd
import numpy as np
from ui_skin.core_engine.master_orchestrator import run_master_three_way_engine

st.set_page_config(layout="wide", page_title="Financial Statements Forecast")

st.title("📊 Synchronized 3-Way Financial Statements")
st.caption("60-Month Institutional Forecast Engine Backed by Proactive Working Capital Modifiers")
st.markdown("---")

# --- 1. SESSION STATE VERIFICATION ---
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

# --- 2. EXECUTE MASTER CALCULATIONS ---
with st.spinner("Re-consolidating multi-source dynamic matrix models..."):
    engine_output = run_master_three_way_engine(
        baseline_inputs=st.session_state["baseline_inputs"],
        loan_register_df=st.session_state["raw_loan_register"],
        revenue_matrix_df=st.session_state["raw_revenue_matrix"],
        planned_capex_list=planned_capex_list,
        total_months=60
    )

# --- 3. UX VIEW INTERVAL SELECTOR ---
view_interval = st.radio(
    "Select Reporting View Profile Interval:",
    ["📅 Detailed 60-Month Rolling Schedule", "📆 5-Year Annualized Summary Deck"],
    horizontal=True
)
st.markdown("---")

# --- 4. PREPARE PRESENTATION METRIC TIMELINES ---
if "Detailed" in view_interval:
    columns_layout = [f"Month {i}" for i in range(1, 61)]
    
    # Map arrays straight out of the engine
    rev = engine_output["Revenue"]
    purchases = engine_output["Purchases"]
    stock_mov = engine_output["Stock Movement"]
    cogs = engine_output["COGS"]
    overheads = engine_output["Overheads"]
    depr = engine_output["Depreciation"]
    interest = engine_output["Interest Paid"]
    tax_exp = engine_output["Tax Expense"]
    net_profit = engine_output["Net Profit"]
    
    principal = engine_output["Principal Repayments"]
    tax_paid = engine_output["Tax Cash Paid"]
    proceeds = engine_output["Asset Disposal Proceeds"]
    cash_at_bank = engine_output["Cash At Bank"]
    
    fa_nbv = engine_output["Fixed Asset NBV"]
    inv_bs = engine_output["Inventory Asset BS"]
    ar_bs = engine_output["Accounts Receivable BS"]
    debt_bs = engine_output["Outstanding Debt"]
    tax_bs = engine_output["Tax Liability BS"]
    
else:
    # Build 5-Year Annualized Aggregations
    columns_layout = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    
    # Flow Statements (Summation over 12-month buckets)
    rev = np.array([np.sum(engine_output["Revenue"][i*12:(i+1)*12]) for i in range(5)])
    purchases = np.array([np.sum(engine_output["Purchases"][i*12:(i+1)*12]) for i in range(5)])
    stock_mov = np.array([np.sum(engine_output["Stock Movement"][i*12:(i+1)*12]) for i in range(5)])
    cogs = np.array([np.sum(engine_output["COGS"][i*12:(i+1)*12]) for i in range(5)])
    overheads = np.array([np.sum(engine_output["Overheads"][i*12:(i+1)*12]) for i in range(5)])
    depr = np.array([np.sum(engine_output["Depreciation"][i*12:(i+1)*12]) for i in range(5)])
    interest = np.array([np.sum(engine_output["Interest Paid"][i*12:(i+1)*12]) for i in range(5)])
    tax_exp = np.array([np.sum(engine_output["Tax Expense"][i*12:(i+1)*12]) for i in range(5)])
    net_profit = np.array([np.sum(engine_output["Net Profit"][i*12:(i+1)*12]) for i in range(5)])
    
    principal = np.array([np.sum(engine_output["Principal Repayments"][i*12:(i+1)*12]) for i in range(5)])
    tax_paid = np.array([np.sum(engine_output["Tax Cash Paid"][i*12:(i+1)*12]) for i in range(5)])
    proceeds = np.array([np.sum(engine_output["Asset Disposal Proceeds"][i*12:(i+1)*12]) for i in range(5)])
    
    # Closing positions (Snapshot at index 11, 23, 35, 47, 59)
    cash_at_bank = np.array([engine_output["Cash At Bank"][(i*12)+11] for i in range(5)])
    fa_nbv = np.array([engine_output["Fixed Asset NBV"][(i*12)+11] for i in range(5)])
    inv_bs = np.array([engine_output["Inventory Asset BS"][(i*12)+11] for i in range(5)])
    ar_bs = np.array([engine_output["Accounts Receivable BS"][(i*12)+11] for i in range(5)])
    debt_bs = np.array([engine_output["Outstanding Debt"][(i*12)+11] for i in range(5)])
    tax_bs = np.array([engine_output["Tax Liability BS"][(i*12)+11] for i in range(5)])

# --- 5. RENDERING THE INTERACTIVE REPORTING TABS ---
tab_pl, tab_cf, tab_bs = st.tabs(["📈 Profit & Loss Statement", "💸 Cash Flow Statement", "⚖️ Balance Sheet Position"])

with tab_pl:
    st.markdown("### **Income Statement (P&L)**")
    ebitda = rev - cogs - overheads
    operating_profit = ebitda - depr - interest
    
    pl_data = {
        "Gross Revenue Turnover (£)": rev,
        "Direct Raw Material Purchases (£)": -purchases,
        "Add/Less: Capitalized Stock Movement (£)": stock_mov,
        "**TOTAL COST OF GOODS SOLD (COGS) (£)**": -cogs,
        "Administrative Overheads (£)": -overheads,
        "**OPERATIONAL EBITDA (£)**": ebitda,
        "Book Depreciation Expense (£)": -depr,
        "Finance Costs / Interest Expense (£)": -interest,
        "**OPERATING PROFIT (EBIT) (£)**": operating_profit,
        "Statutory Corporation Tax Provision (£)": -tax_exp,
        "***NET PROFIT AFTER TAX (EAT) (£)***": net_profit
    }
    st.dataframe(pd.DataFrame(pl_data, index=columns_layout).T.style.format("£{:,.2f}"), use_container_width=True)

with tab_cf:
    st.markdown("### **Indirect Cash Flow Statement**")
    net_operating_cash_flow = net_profit + depr + stock_mov
    
    cf_data = {
        "Net Profit Allocation (£)": net_profit,
        "Add: Non-Cash Depreciation (£)": depr,
        "Add/Less: Stock Movement Non-Cash Delta (£)": stock_mov,
        "Less: Debt Principal Repayments (£)": -principal,
        "Less: Corporation Tax Payouts (£)": -tax_paid,
        "Less: Interest Payments (£)": -interest,
        "Add: Asset Disposal Proceeds Windfalls (£)": proceeds,
        "**Net Annual Cash Flow Movement (£)**": (net_operating_cash_flow - principal - tax_paid - interest + proceeds),
        "***CLOSING BANK CASH POSITION (£)***": cash_at_bank
    }
    st.dataframe(pd.DataFrame(cf_data, index=columns_layout).T.style.format("£{:,.2f}"), use_container_width=True)

with tab_bs:
    st.markdown("### **Statement of Financial Position (Balance Sheet)**")
    
    # Extract baseline positions
    cash_seed = float(st.session_state["baseline_inputs"].get("opening_cash_balance", 69488.0))
    fa_seed = float(st.session_state["baseline_inputs"].get("opening_fixed_assets_nbv", 150000.0))
    ar_seed = float(st.session_state["baseline_inputs"].get("opening_accounts_receivable", 44886.0))
    ap_seed = float(st.session_state["baseline_inputs"].get("opening_accounts_payable", 8000.0))
    debt_seed = float(st.session_state["baseline_inputs"].get("opening_long_term_debt", 0.0))
    inv_seed = engine_output["Inventory Asset BS"][0]
    re_seed = (cash_seed + fa_seed + ar_seed + inv_seed) - (debt_seed + ap_seed)
    
    if "Detailed" in view_interval:
        bs_columns = columns_layout
        timeline_ap = np.full(60, ap_seed)
        
        timeline_re = np.zeros(60)
        running_re = re_seed
        for m in range(60):
            running_re += engine_output["Net Profit"][m]
            timeline_re[m] = running_re
            
        total_assets = fa_nbv + cash_at_bank + inv_bs + ar_bs
        total_liabilities = debt_bs + tax_bs + timeline_ap
    else:
        # Append "Opening b/f" column explicitly to match layout requests
        bs_columns = ["Opening b/f"] + columns_layout
        timeline_ap = np.full(6, ap_seed)
        
        # Build annualized rolling equity positions starting from b/f seed
        timeline_re = np.zeros(6)
        timeline_re[0] = re_seed
        running_re = re_seed
        for i in range(5):
            running_re += net_profit[i]
            timeline_re[i+1] = running_re
            
        # Prepend opening parameters to the year-end snapshots
        fa_nbv = np.insert(fa_nbv, 0, fa_seed)
        inv_bs = np.insert(inv_bs, 0, inv_seed)
        ar_bs = np.insert(ar_bs, 0, ar_seed)
        cash_at_bank = np.insert(cash_at_bank, 0, cash_seed)
        debt_bs = np.insert(debt_bs, 0, debt_seed)
        tax_bs = np.insert(tax_bs, 0, 0.0) # Assume 0 opening deferred tax
        
        total_assets = fa_nbv + cash_at_bank + inv_bs + ar_bs
        total_liabilities = debt_bs + tax_bs + timeline_ap

    net_assets = total_assets - total_liabilities
    
    bs_data = {
        "Non-Current Assets: Fixed Assets NBV (£)": fa_nbv,
        "Current Assets: Warehouse Inventory Pool (£)": inv_bs,
        "Current Assets: Accounts Receivable (AR) (£)": ar_bs,
        "Current Assets: Liquid Cash Base (£)": cash_at_bank,
        "**TOTAL STRUCTURAL ASSETS (£)**": total_assets,
        "Non-Current Liabilities: Outstanding Debt (£)": -debt_bs,
        "Current Liabilities: Deferred Tax Reserve (£)": -tax_bs,
        "Current Liabilities: Accounts Payable (AP) (£)": -timeline_ap,
        "**TOTAL STRUCTURAL LIABILITIES (£)**": -total_liabilities,
        "***NET NET ASSETS CAPITAL (£)***": net_assets,
        "Equity: Accumulated Retained Reserves (£)": timeline_re,
        "**TOTAL CAPITAL AND RESERVES MATCH (£)**": timeline_re
    }
    
    st.dataframe(pd.DataFrame(bs_data, index=bs_columns).T.style.format("£{:,.2f}"), use_container_width=True)

    # --- THREE-WAY LEDGER EQUILIBRIUM GUARDRAIL ---
    numerical_variance = np.abs(net_assets - timeline_re)
    unbalanced_instances = np.where(numerical_variance > 0.05)[0]
    
    if len(unbalanced_instances) == 0:
        st.success("⚖️ **Ledger Equilibrium Verified:** The Balance Sheet scales and balances perfectly across all selected reporting intervals.")
    else:
        st.error(f"⚠️ **Ledger Disbalance Warning:** Numerical variance detected inside interval index positions: {unbalanced_instances}")