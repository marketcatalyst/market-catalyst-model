import streamlit as st
import pandas as pd
import numpy as np
# Cloud Container Path Resolution Modules
from ui_skin.core_engine.master_orchestrator import run_master_three_way_engine
from ui_skin.core_engine.export_manager import generate_three_way_excel_bundle
from ui_skin.core_engine.pdf_manager import generate_three_way_pdf_pack

st.set_page_config(layout="wide", page_title="Financial Statements Forecast")

st.title("📊 Synchronised 3-Way Financial Statements")
st.caption("60-Month Institutional Forecast Engine Backed by Proactive Working Capital Modifiers")
st.markdown("---")

# =========================================================================
# --- 1. SESSION STATE VERIFICATION & FALLBACK PROTECTION ---
# =========================================================================
if "baseline_inputs" not in st.session_state or "raw_loan_register" not in st.session_state or "raw_revenue_matrix" not in st.session_state:
    st.warning("⚠️ **Upstream Data Missing:** Active session data not detected. Please initialise your parameters on the Ingestion page first.")
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

# =========================================================================
# --- IN-CONTEXT INTERACTIVE INPUT CENTRE: STAGES 3 & 4 ---
# =========================================================================
st.header("⚙️ Operational Growth & Capacity Levers")
st.markdown(
    "Configure your core trading channel escalators and strategic capacity expansion overlays "
    "directly before executing the centralized three-way engine."
)

# Extract baseline run-rates securely from active session data for contextual display
base_inputs = st.session_state["baseline_inputs"]
baseline_retail_monthly = float(base_inputs.get("opening_accounts_receivable", 45000.00)) # Fallback context anchors
baseline_wholesale_monthly = float(base_inputs.get("opening_accounts_payable", 25000.00))

# Interlocking Frictionless Inputs Layout
with st.container(border=True):
    rev_tab, exp_tab = st.tabs(["📈 Stage 3: Multi-Channel Revenue Modelling", "🔮 Stage 4: Strategic Capacity Expansions"])
    
    with rev_tab:
        st.markdown("#### 🎛️ Core Trading Channel Growth Vectors")
        col_ret, col_whl = st.columns(2, gap="large")
        
        with col_ret:
            with st.container(border=True):
                st.markdown("🔹 **Direct Retail Counter Sales (65% GP Baseline Target)**")
                st.metric(label="Ingested Starting Baseline", value=f"£{baseline_retail_monthly:,.0f}/mo")
                c1, c2 = st.columns(2)
                with c1:
                    ret_vol = st.number_input("Annual Volume Growth (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5, format="%.1f", key="ret_vol_key") / 100.0
                with c2:
                    ret_prc = st.number_input("Annual Price Ramp (%)", min_value=0.0, max_value=50.0, value=2.5, step=0.5, format="%.1f", key="ret_prc_key") / 100.0
                    
        with col_whl:
            with st.container(border=True):
                st.markdown("🔹 **B2B Wholesale Accounts (40% GP Baseline Target)**")
                st.metric(label="Ingested Starting Baseline", value=f"£{baseline_wholesale_monthly:,.0f}/mo")
                c3, c4 = st.columns(2)
                with c3:
                    whl_vol = st.number_input("Annual Volume Growth (%)", min_value=0.0, max_value=100.0, value=12.0, step=0.5, format="%.1f", key="whl_vol_key") / 100.0
                with c4:
                    whl_prc = st.number_input("Annual Price Ramp (%)", min_value=0.0, max_value=50.0, value=0.0, step=0.5, format="%.1f", key="whl_prc_key") / 100.0
                    
        # Update session states dynamically for master orchestrator lookup
        st.session_state["retail_annual_volume_growth"] = ret_vol
        st.session_state["retail_annual_price_ramp"] = ret_prc
        st.session_state["wholesale_annual_volume_growth"] = whl_vol
        st.session_state["wholesale_annual_price_ramp"] = whl_prc

    with exp_tab:
        st.markdown("#### 🏬 Physical Footprint & Step-Cost Modifiers")
        expansion_active = st.toggle("Activate Strategic Footprint Expansion Scenario", value=False, key="expansion_active_key")
        st.session_state["expansion_scenario_active"] = expansion_active
        
        if expansion_active:
            exp_c1, exp_c2 = st.columns(2, gap="medium")
            with exp_c1:
                st.session_state["expansion_month"] = st.number_input("Launch Timeline Trigger (Month)", min_value=1, max_value=48, value=13, step=1)
                st.session_state["incremental_revenue_start"] = st.number_input("Target Expansion Monthly Revenue Base (£)", min_value=0.0, value=20000.00, step=1000.00)
                st.session_state["expansion_cogs_pct"] = st.number_input("Expansion Specific COGS (%)", min_value=0.0, max_value=100.0, value=40.0, step=1.0) / 100.0
            with exp_c2:
                st.session_state["incremental_rent"] = st.number_input("Incremental Facility Rent & Rates (£/mo)", min_value=0.0, value=2500.00, step=100.00)
                st.session_state["incremental_insurance"] = st.number_input("Incremental Site Risk Premium (£/mo)", min_value=0.0, value=500.00, step=50.00)
                st.session_state["logistics_overtime_premium"] = st.number_input("Logistics Route Overtime Load (£/mo)", min_value=0.0, value=750.00, step=50.00)
        else:
            st.info("Currently processing business-as-usual core metrics. Toggle the switch above to inject expansion adjustments.")

st.markdown("---")

# =========================================================================
# --- 2. EXECUTE MASTER PIPELINE CALCULATIONS ---
# =========================================================================
with st.spinner("Re-consolidating multi-source dynamic matrix models..."):
    engine_output = run_master_three_way_engine(
        baseline_inputs=st.session_state["baseline_inputs"],
        loan_register_df=st.session_state["raw_loan_register"],
        revenue_matrix_df=st.session_state["raw_revenue_matrix"],
        planned_capex_list=planned_capex_list,
        total_months=60
    )

# =========================================================================
# --- 3. THE SIDE-BY-SIDE CORPORATE EXPORT CONTROLLER PANEL ---
# =========================================================================
col_lbl, col_btn_xl, col_btn_pdf = st.columns([2, 1, 1])
with col_lbl:
    st.write("💡 **Ready for Stakeholder Review?** Compile and download this current balanced matrix run directly into production-ready corporate outputs.")

with col_btn_xl:
    excel_data_stream = generate_three_way_excel_bundle(
        engine_output=engine_output,
        baseline_inputs=st.session_state["baseline_inputs"]
    )
    st.download_button(
        label="📥 Download Excel Model",
        data=excel_data_stream,
        file_name="STRATA_60M_Three_Way_Forecast.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with col_btn_pdf:
    pdf_data_stream = generate_three_way_pdf_pack(
        engine_output=engine_output,
        baseline_inputs=st.session_state["baseline_inputs"]
    )
    st.download_button(
        label="📄 Download PDF Pack",
        data=pdf_data_stream,
        file_name="STRATA_Executive_Financial_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )

st.markdown("---")

# =========================================================================
# --- 4. UX VIEW INTERVAL SELECTOR ---
# =========================================================================
view_interval = st.radio(
    "Select Reporting View Profile Interval:",
    ["📅 Detailed 60-Month Rolling Schedule", "📆 5-Year Annualised Summary Deck"],
    horizontal=True
)
st.markdown("---")

# =========================================================================
# --- 5. PREPARE PRESENTATION METRIC TIMELINES ---
# =========================================================================
if "Detailed" in view_interval:
    columns_layout = [f"Month {i}" for i in range(1, 61)]
    
    # Map arrays straight out of the engine outputs
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
    # Build 5-Year Annualised Aggregations
    columns_layout = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    
    # Flow Statements (Summation over rolling 12-month buckets)
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
    
    # Stock Closing Positions (Snapshot at index 11, 23, 35, 47, 59)
    cash_at_bank = np.array([engine_output["Cash At Bank"][(i*12)+11] for i in range(5)])
    fa_nbv = np.array([engine_output["Fixed Asset NBV"][(i*12)+11] for i in range(5)])
    inv_bs = np.array([engine_output["Inventory Asset BS"][(i*12)+11] for i in range(5)])
    ar_bs = np.array([engine_output["Accounts Receivable BS"][(i*12)+11] for i in range(5)])
    debt_bs = np.array([engine_output["Outstanding Debt"][(i*12)+11] for i in range(5)])
    tax_bs = np.array([engine_output["Tax Liability BS"][(i*12)+11] for i in range(5)])

# =========================================================================
# --- 6. RENDERING THE INTERACTIVE REPORTING TABS ---
# =========================================================================
tab_pl, tab_cf, tab_bs = st.tabs(["📈 Profit & Loss Statement", "💸 Cash Flow Statement", "⚖️ Balance Sheet Position"])

with tab_pl:
    st.markdown("### **Income Statement (P&L)**")
    ebitda = rev - cogs - overheads
    operating_profit = ebitda - depr - interest
    
    pl_data = {
        "Gross Revenue Turnover (£)": rev,
        "Direct Raw Material Purchases (£)": -purchases,
        "Add/Less: Capitalised Stock Movement (£)": stock_mov,
        "**TOTAL COST OF GOODS SOLD (COGS) (£)**": -cogs,
        "Administrative Overheads (£)": -overheads,
        "**OPERATIONAL EBITDA (£)**": ebitda,
        "Book Depreciation Expense (£)": -depr,
        "Finance Costs / Interest Expense (£)": -interest,
        "**OPERATING PROFIT (EBIT) (£)**": operating_profit,
        "Statutory Corporation Tax Provision (£)": -tax_exp,
        "***NET PROFIT AFTER TAX (EAT) (£)***": net_profit
    }
    # SYSTEM UPGRADE: Styled to display integers rounded to the nearest £1
    st.dataframe(pd.DataFrame(pl_data, index=columns_layout).T.style.format("£{:,.0f}"), use_container_width=True)

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
    # SYSTEM UPGRADE: Styled to display integers rounded to the nearest £1
    st.dataframe(pd.DataFrame(cf_data, index=columns_layout).T.style.format("£{:,.0f}"), use_container_width=True)

with tab_bs:
    st.markdown("### **Statement of Financial Position (Balance Sheet)**")
    
    # Extract baseline positions from active session state configurations
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
        
        running_re = re_seed
        timeline_re = np.zeros(60)
        for m in range(60):
            running_re += engine_output["Net Profit"][m]
            timeline_re[m] = running_re
            
        total_assets = fa_nbv + cash_at_bank + inv_bs + ar_bs
        total_liabilities = debt_bs + tax_bs + timeline_ap
    else:
        # Prepend opening balance sheet b/f column headers explicitly
        bs_columns = ["Opening b/f"] + columns_layout
        timeline_ap = np.full(6, ap_seed)
        
        # Build annualised rolling equity reserves starting from baseline seed
        timeline_re = np.zeros(6)
        timeline_re[0] = re_seed
        running_re = re_seed
        for i in range(5):
            running_re += net_profit[i]
            timeline_re[i+1] = running_re
            
        # Insert initial starting figures at array index positions 0
        fa_nbv = np.insert(fa_nbv, 0, fa_seed)
        inv_bs = np.insert(inv_bs, 0, inv_seed)
        ar_bs = np.insert(ar_bs, 0, ar_seed)
        cash_at_bank = np.insert(cash_at_bank, 0, cash_seed)
        debt_bs = np.insert(debt_bs, 0, debt_seed)
        tax_bs = np.insert(tax_bs, 0, 0.0)
        
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
    
    # SYSTEM UPGRADE: Styled to display integers rounded to the nearest £1
    st.dataframe(pd.DataFrame(bs_data, index=bs_columns).T.style.format("£{:,.0f}"), use_container_width=True)

    # --- THREE-WAY LEDGER EQUILIBRIUM GUARDRAIL ---
    numerical_variance = np.abs(net_assets - timeline_re)
    unbalanced_instances = np.where(numerical_variance > 0.05)[0]
    
    if len(unbalanced_instances) == 0:
        st.success("⚖️ **Ledger Equilibrium Verified:** The Balance Sheet scales and balances perfectly across all selected reporting intervals.")
    else:
        st.error(f"⚠️ **Ledger Disbalance Warning:** Numerical variance detected inside interval index positions: {unbalanced_instances}")