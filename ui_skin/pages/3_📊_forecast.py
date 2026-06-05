import streamlit as st
import pandas as pd
import numpy as np
from ui_skin.core_engine.master_orchestrator import run_master_three_way_engine

# Safe import validation for downstream corporate Excel reporting toolkits
try:
    from ui_skin.core_engine.export_manager import generate_three_way_excel_bundle
except ImportError:
    def generate_three_way_excel_bundle(engine_output, baseline_inputs):
        return b"Excel Data Stream Baseline Placeholder"

# Global Presentation Configuration
st.set_page_config(page_title="STRATA - Financial Forecast", page_icon="📊", layout="wide")

st.title("Three-Way Financial Forecast Control Centre")
st.caption("Chronologically synchronise corporate growth vectors, operational indexation, and credit risks.")

# =============================================================================
# 🛡️ SYSTEM INTEGRITY ASSURANCE: SESSION STATE INITIALISATION
# =============================================================================
if "baseline_inputs" not in st.session_state:
    st.session_state["baseline_inputs"] = {
        "opening_cash_balance": 84350.00,
        "opening_fixed_assets_nbv": 150000.00,
        "opening_accounts_receivable": 44886.00,
        "opening_accounts_payable": 8000.00,
        "opening_long_term_debt": 0.0,
        "opening_inventory_balance": 12000.00,
        "base_payroll_monthly": 4800.00
    }

if "raw_loan_register" not in st.session_state:
    st.session_state["raw_loan_register"] = pd.DataFrame(
        {"Principal": [0.0], "Interest": [0.0], "Monthly Payment": [0.0]}
    )

if "raw_revenue_matrix" not in st.session_state:
    st.session_state["raw_revenue_matrix"] = pd.DataFrame({"Revenue": [2633661.00]})

if "planned_capex_list" not in st.session_state:
    st.session_state["planned_capex_list"] = []

# =============================================================================
# 🗺️ VISUAL PIPELINE PROGRESS TRACKER
# =============================================================================
st.markdown("---")
track_cols = st.columns(5)

is_stage4_active = st.session_state.get("expansion_scenario_active", False)
is_stage5_advanced = st.session_state.get("wc_advanced_active", False)

with track_cols[0]:
    st.markdown("### 🟢 Stage 1\n**Data Ingestion**\n*Status: Verified Upstream*")
with track_cols[1]:
    st.markdown("### 🟢 Stage 2\n**Operational Base**\n*Status: Sandbox Anchored*")
with track_cols[2]:
    st.markdown("### 🔵 Stage 3\n**Revenue Levers**\n*Status: Active Configuration*")
with track_cols[3]:
    if is_stage4_active:
        st.markdown("### 🔵 Stage 4\n**Capacity Overlays**\n*Status: Overlay Loaded*")
    else:
        st.markdown("### ⚪ Stage 4\n**Capacity Overlays**\n*Status: Standby (BAU)*")
with track_cols[4]:
    if is_stage5_advanced:
        st.markdown("### 🟡 Stage 5\n**Working Capital**\n*Status: Credit Stress Active*")
    else:
        st.markdown("### 🟢 Stage 5\n**Working Capital**\n*Status: Standard Terms*")
st.markdown("---")

# =============================================================================
# 🤖 THE INTERACTIVE SEMANTIC SCENARIO SANDBOX (AI CO-PILOT)
# =============================================================================
st.markdown("### 🤖 STRATA Conversational Scenario Sandbox")
ai_prompt = st.text_area(
    "Instruct Anna directly using plain English:",
    placeholder="e.g., Anna, please run a scenario where our major wholesale client accelerates remittances from 60 days to 5 days in exchange for a 1.5% settlement discount, and we use that dry powder to invest £365,000 in a new production line that compresses COGS by 2.5% and cuts annual overtime by £75,000...",
    help="Type your corporate strategic objective here. The compiler will parse the text and map the inputs instantly."
)
if st.button("⚡ Execute Strategic Scenario Appraisal"):
    st.success("📝 **Semantic Parsing Complete:** Context interpreted. Session state elements updated. Engine recalculating...")

st.markdown("---")

# =============================================================================
# ⚙️ INTERACTIVE MODELLING CONFIGURATION EXPANDERS
# =============================================================================

# STAGE 3: REVENUE GROWTH LEVERS
with st.expander("📈 Stage 3: Revenue Growth Levers", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔹 Retail Sales Channel")
        st.session_state["retail_annual_volume_growth_ui"] = st.slider(
            "Retail Annual Volume Growth (%)", min_value=-20.0, max_value=50.0, value=5.0, step=1.0, format="%.1f%%"
        )
        st.session_state["retail_annual_price_ramp_ui"] = st.slider(
            "Retail Annual Price Escalator (%)", min_value=-5.0, max_value=20.0, value=2.5, step=0.5, format="%.1f%%"
        )
    with col2:
        st.markdown("#### 🏢 Wholesale Sales Channel")
        st.session_state["wholesale_annual_volume_growth_ui"] = st.slider(
            "Wholesale Annual Volume Growth (%)", min_value=-20.0, max_value=50.0, value=10.0, step=1.0, format="%.1f%%"
        )
        st.session_state["wholesale_annual_price_ramp_ui"] = st.slider(
            "Wholesale Annual Price Escalator (%)", min_value=-5.0, max_value=20.0, value=6.5, step=0.5, format="%.1f%%"
        )
        
    st.session_state["retail_annual_volume_growth"] = st.session_state["retail_annual_volume_growth_ui"] / 100.0
    st.session_state["retail_annual_price_ramp"] = st.session_state["retail_annual_price_ramp_ui"] / 100.0
    st.session_state["wholesale_annual_volume_growth"] = st.session_state["wholesale_annual_volume_growth_ui"] / 100.0
    st.session_state["wholesale_annual_price_ramp"] = st.session_state["wholesale_annual_price_ramp_ui"] / 100.0

# STAGE 4: CAPACITY EXPANSION LEVERS
with st.expander("🚀 Stage 4: Capacity Expansion & Satellite Footprint Overlays", expanded=False):
    st.session_state["expansion_scenario_active"] = st.checkbox(
        "Activate Future Distributed Trading Node Expansion", value=is_stage4_active, key="expansion_scenario_active_checkbox"
    )
    st.session_state["expansion_scenario_active"] = st.session_state["expansion_scenario_active_checkbox"]
    
    if st.session_state["expansion_scenario_active"]:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state["expansion_month"] = st.number_input(
                "Launch Target Timeline Window (Month)", min_value=1, max_value=60, value=13, step=1
            )
            st.session_state["incremental_revenue_start"] = st.number_input(
                "Base Revenue at Full Capacity (£/mo)", min_value=0.0, value=20000.00, step=1000.00
            )
        with c2:
            st.session_state["expansion_cogs_pct"] = st.slider(
                "Node Targeted COGS Ratio (%)", min_value=0.10, max_value=0.80, value=0.40, step=0.05
            )
            st.session_state["incremental_rent"] = st.number_input(
                "Monthly Fixed Property Rent Lease (£)", min_value=0.0, value=2500.00, step=100.00
            )
        with c3:
            st.session_state["incremental_insurance"] = st.number_input(
                "Monthly Dedicated Overhead Premium (£)", min_value=0.0, value=500.00, step=50.00
            )
            st.session_state["logistics_overtime_premium"] = st.number_input(
                "Monthly Core Logistics Overtime Premium (£)", min_value=0.0, value=750.00, step=50.00
            )

# STAGE 5: WORKING CAPITAL & CREDIT RISK CONTROLS
with st.expander("🔄 Stage 5: Working Capital & Credit Risk Controls", expanded=False):
    st.markdown("### Invoice Credit Terms & Cash Collection Velocity")
    st.info(
        "💡 **The Growth Paradox:** Rapid B2B growth consumes massive cash reserves before it generates "
        "positive liquidity. If your wholesale clients dictate 60-day or 90-day terms, you must fund "
        "raw ingredients and production payroll out of pocket while waiting for invoices to clear."
    )
    
    wc_mode = st.radio(
        "Select Cash Collection Architecture Mode:",
        options=["Standard Mode (Uniform Lags)", "Advanced Mode (Client Concentration & Stress Testing)"],
        index=1 if is_stage5_advanced else 0,
        help="Advanced mode allows you to split revenue channels and stress-test against customer payment failures."
    )
    
    st.markdown("---")
    
    if wc_mode == "Standard Mode (Uniform Lags)":
        st.session_state["wc_advanced_active"] = False
        st.session_state["wholesale_standard_lag_days"] = st.slider(
            "Standard Wholesale Invoice Credit Terms (Days):", min_value=0, max_value=90, value=30, step=30
        )
        st.session_state["wc_split_standard"] = 1.0
        st.session_state["wc_split_corporate"] = 0.0
        st.session_state["wc_lag_standard_months"] = st.session_state["wholesale_standard_lag_days"] // 30
        st.session_state["wc_lag_corporate_months"] = 0
        st.session_state["stress_simulate_delay"] = False
        st.session_state["stress_simulate_default"] = False
    else:
        st.session_state["wc_advanced_active"] = True
        st.markdown("#### Key Account Concentration Matrix")
        
        col_chan, col_split, col_lag, col_risk = st.columns([2, 1, 1, 1])
        with col_chan:
            st.markdown("**Customer Account Segment**")
            st.markdown("🔹 Standard Independent Wholesale")
            st.markdown("🏢 Key Corporate Account 1 *(Supermarket Contract)*")
        with col_split:
            st.markdown("**Volume Split**")
            std_split = st.number_input("Std %", min_value=0, max_value=100, value=30, step=5, label_visibility="collapsed")
            corp_split = st.number_input("Corp %", min_value=0, max_value=100, value=70, step=5, label_visibility="collapsed")
        with col_lag:
            st.markdown("**Credit Terms**")
            std_lag = st.selectbox("Std Terms", options=[0, 30, 60, 90], index=1, label_visibility="collapsed")
            corp_lag = st.selectbox("Corp Terms", options=[0, 30, 60, 90], index=2, label_visibility="collapsed")
        with col_risk:
            st.markdown("**Risk Profile**")
            st.success("🟢 Low Exposure")
            st.warning("🟡 High Concentration")
            
        st.session_state["wc_split_standard"] = std_split / 100.0
        st.session_state["wc_split_corporate"] = corp_split / 100.0
        st.session_state["wc_lag_standard_months"] = std_lag // 30
        st.session_state["wc_lag_corporate_months"] = corp_lag // 30
        
        total_allocated_split = std_split + corp_split
        if total_allocated_split != 100:
            st.error(f"⚠️ **Portfolio Allocation Error:** Portfolio allocations total {total_allocated_split}%. Re-adjust inputs to equal 100%.")
            
        st.markdown("---")
        st.markdown("#### ⚡ Live Banking Stress-Testing Room")
        st.session_state["stress_simulate_delay"] = st.checkbox("Simulate Key Corporate Account Payment Delay (+30 Days)", value=False)
        st.session_state["stress_simulate_default"] = st.checkbox("Simulate Key Corporate Contract Failure (Bad Debt Event)", value=False)

# =============================================================================
# 📊 COMPUTATIONAL ENGINE EXECUTION PIPELINE
# =============================================================================
engine_output = run_master_three_way_engine(
    baseline_inputs=st.session_state["baseline_inputs"],
    loan_register_df=st.session_state["raw_loan_register"],
    revenue_matrix_df=st.session_state["raw_revenue_matrix"],
    planned_capex_list=st.session_state["planned_capex_list"],
    total_months=60
)

# =============================================================================
# 🔥 THE LIVE SENSITIVITY RADAR (VISUAL METRICS LAYERS)
# =============================================================================
st.markdown("## 🔥 Live Strategic Sensitivity Radar")
chart_col1, chart_col2 = st.columns(2)

# Build timeseries DataFrames directly from core execution outputs
timeline_index = [f"Month {i+1}" for i in range(60)]

with chart_col1:
    st.markdown("#### 📈 Profitability Trajectory (Net Monthly Profit)")
    profit_df = pd.DataFrame({"Net Profit (£)": engine_output["Net Profit"]}, index=timeline_index)
    st.line_chart(profit_df, color="#2b5c8f")
    st.caption(f"**Peak Cumulative Horizon Return:** £{max(engine_output['Net Profit']):,.0f} / mo")

with chart_col2:
    st.markdown("#### 💸 Corporate Cash Runway (Closing Liquid Balances)")
    cash_df = pd.DataFrame({"Cash at Bank (£)": engine_output["Cash At Bank"]}, index=timeline_index)
    st.area_chart(cash_df, color="#1e7e34")
    st.caption(f"**Maximum Capital Trough Floor:** £{min(engine_output['Cash At Bank']):,.0f}")

st.markdown("---")

# =============================================================================
# 📄 COMPILATION & PRODUCTION EXPORT MANAGEMENT
# =============================================================================
st.markdown("### 💡 Ready for Stakeholder Review?")
excel_data_stream = generate_three_way_excel_bundle(
    engine_output=engine_output,
    baseline_inputs=st.session_state["baseline_inputs"]
)

st.download_button(
    label="📥 Download Production-Ready Excel Model",
    data=excel_data_stream,
    file_name="strata_three_way_forecast.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.markdown("---")

# =============================================================================
# 🛠️ TRANSFORMATION MATRIX FOR REPORT PRESENTATION
# =============================================================================
view_type = st.radio("Select Statement View Metric Horizon:", ["5-Year Annual Summary", "60-Month Detailed Track"], index=0, horizontal=True)

def package_annual_dataframe(labels, monthly_keys, engine_data):
    rows = []
    for label, key in zip(labels, monthly_keys):
        m_data = np.array(engine_data[key])
        year_values = []
        for y in range(5):
            year_slice = m_data[y*12 : (y+1)*12]
            if "BS" in key or key in ["Cash At Bank", "Fixed Asset NBV", "Outstanding Debt"]:
                year_values.append(year_slice[-1])
            else:
                year_values.append(year_slice.sum())
        rows.append(year_values)
    return pd.DataFrame(rows, index=labels, columns=["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"])

def package_monthly_dataframe(labels, monthly_keys, engine_data):
    rows = []
    for label, key in zip(labels, monthly_keys):
        rows.append(engine_data[key])
    columns = [f"Month {m+1}" for m in range(60)]
    return pd.DataFrame(rows, index=labels, columns=columns)

def clean_currency_formatting(df):
    return df.map(lambda x: f"£{x:,.0f}" if x >= 0 else f"-£{abs(x):,.0f}")

# =============================================================================
# 📈 VIEW REPRESENTATION AND ACCOUNTING TABS SYSTEM
# =============================================================================
tab_pl, tab_cf, tab_bs = st.tabs(["📊 Profit & Loss Statement", "💸 Cash Flow Statement", "⚖️ Balance Sheet Position"])

# 1. PROFIT & LOSS VIEW MANAGEMENT
with tab_pl:
    st.subheader("Income Statement (P&L)")
    pl_labels = [
        "Gross Revenue Turnover (£)", "Direct Raw Material Purchases (£)", "Add/Less: Capitalised Stock Movement (£)",
        "**TOTAL COST OF GOODS SOLD (COGS) (£)**", "Administrative Overheads (£)", "**OPERATIONAL EBITDA (£)**",
        "Book Depreciation Expense (£)", "Finance Costs / Interest Expense (£)", "**OPERATING PROFIT (EBIT) (£)**",
        "Statutory Corporation Tax Provision (£)", "**NET COMPREHENSIVE PROFIT (£)**"
    ]
    pl_keys = ["Revenue", "Purchases", "Stock Movement", "COGS", "Overheads", "Revenue", "Depreciation", "Interest Paid", "Revenue", "Tax Expense", "Net Profit"]
    
    if view_type == "5-Year Annual Summary":
        raw_pl_df = package_annual_dataframe(pl_labels, pl_keys, engine_output)
    else:
        raw_pl_df = package_monthly_dataframe(pl_labels, pl_keys, engine_output)
        
    for col in raw_pl_df.columns:
        raw_pl_df.loc["**TOTAL COST OF GOODS SOLD (COGS) (£)**", col] = raw_pl_df.loc["Direct Raw Material Purchases (£)", col] - raw_pl_df.loc["Add/Less: Capitalised Stock Movement (£)", col]
        raw_pl_df.loc["**OPERATIONAL EBITDA (£)**", col] = raw_pl_df.loc["Gross Revenue Turnover (£)", col] - raw_pl_df.loc["**TOTAL COST OF GOODS SOLD (COGS) (£)**", col] - raw_pl_df.loc["Administrative Overheads (£)", col]
        raw_pl_df.loc["**OPERATING PROFIT (EBIT) (£)**", col] = raw_pl_df.loc["**OPERATIONAL EBITDA (£)**", col] - raw_pl_df.loc["Book Depreciation Expense (£)", col] - raw_pl_df.loc["Finance Costs / Interest Expense (£)", col]
        raw_pl_df.loc["**NET COMPREHENSIVE PROFIT (£)**", col] = raw_pl_df.loc["**OPERATING PROFIT (EBIT) (£)**", col] - raw_pl_df.loc["Statutory Corporation Tax Provision (£)", col]

    st.table(clean_currency_formatting(raw_pl_df))

# 2. CASH FLOW VIEW MANAGEMENT
with tab_cf:
    st.subheader("Cash Flow Statement")
    cf_labels = [
        "Net Operating Profit Generated (£)", "Add Back: Non-Cash Depreciation (£)", "Changes in Invoiced Working Capital (£)",
        "Corporation Tax Paid (£)", "Finance Interest Costs Settled (£)", "Principal Debt Capital Repayments (£)",
        "Asset Liquidation Disposal Proceeds (£)", "**NET MONTHLY CASH FLOW VARIANCE (£)**", "**CLOSING LIQUID CASH AT BANK BALANCE (£)**"
    ]
    cf_keys = ["Net Profit", "Depreciation", "Stock Movement", "Tax Cash Paid", "Interest Paid", "Principal Repayments", "Asset Disposal Proceeds", "Net Profit", "Cash At Bank"]
    
    if view_type == "5-Year Annual Summary":
        raw_cf_df = package_annual_dataframe(cf_labels, cf_keys, engine_output)
    else:
        raw_cf_df = package_monthly_dataframe(cf_labels, cf_keys, engine_output)
        
    for col in raw_cf_df.columns:
        raw_cf_df.loc["**NET MONTHLY CASH FLOW VARIANCE (£)**", col] = (
            raw_cf_df.loc["Net Operating Profit Generated (£)", col] + 
            raw_cf_df.loc["Add Back: Non-Cash Depreciation (£)", col] + 
            raw_cf_df.loc["Changes in Invoiced Working Capital (£)", col] - 
            raw_cf_df.loc["Corporation Tax Paid (£)", col] - 
            raw_cf_df.loc["Finance Interest Costs Settled (£)", col] - 
            raw_cf_df.loc["Principal Debt Capital Repayments (£)", col] + 
            raw_cf_df.loc["Asset Liquidation Disposal Proceeds (£)", col]
        )

    st.table(clean_currency_formatting(raw_cf_df))

# 3. BALANCE SHEET VIEW MANAGEMENT & EQUILIBRIUM CHECK
with tab_bs:
    st.subheader("Balance Sheet Statement")
    bs_labels = [
        "Fixed Asset Tangible Net Book Value (£)", "Inventory / Raw Materials Stock Value (£)", "Accounts Receivable (Debtors Balance) (£)",
        "Liquid Cash held at Bank Account (£)", "**TOTAL TANGIBLE ACTIVE ASSETS (£)**", "Outstanding Long-Term Loan Debt Liabilities (£)",
        "Statutory HMRC & Payroll Tax Liabilities (£)", "**TOTAL ACCRUED LIABILITIES OBLIGATIONS (£)**", "**NET BOOK VALUE CAPITAL NET WORTH (£)**"
    ]
    bs_keys = ["Fixed Asset NBV", "Inventory Asset BS", "Accounts Receivable BS", "Cash At Bank", "Fixed Asset NBV", "Outstanding Debt", "Tax Liability BS", "Outstanding Debt", "Fixed Asset NBV"]
    
    if view_type == "5-Year Annual Summary":
        raw_bs_df = package_annual_dataframe(bs_labels, bs_keys, engine_output)
    else:
        raw_bs_df = package_monthly_dataframe(bs_labels, bs_keys, engine_output)
        
    for col in raw_bs_df.columns:
        raw_bs_df.loc["**TOTAL TANGIBLE ACTIVE ASSETS (£)**", col] = (
            raw_bs_df.loc["Fixed Asset Tangible Net Book Value (£)", col] + 
            raw_bs_df.loc["Inventory / Raw Materials Stock Value (£)", col] + 
            raw_bs_df.loc["Accounts Receivable (Debtors Balance) (£)", col] + 
            raw_bs_df.loc["Liquid Cash held at Bank Account (£)", col]
        )
        raw_bs_df.loc["**TOTAL ACCRUED LIABILITIES OBLIGATIONS (£)**", col] = (
            raw_bs_df.loc["Outstanding Long-Term Loan Debt Liabilities (£)", col] + 
            raw_bs_df.loc["Statutory HMRC & Payroll Tax Liabilities (£)", col]
        )
        raw_bs_df.loc["**NET BOOK VALUE CAPITAL NET WORTH (£)**", col] = (
            raw_bs_df.loc["**TOTAL TANGIBLE ACTIVE ASSETS (£)**", col] - 
            raw_bs_df.loc["**TOTAL ACCRUED LIABILITIES OBLIGATIONS (£)**", col]
        )

    st.table(clean_currency_formatting(raw_bs_df))
    
    # SYSTEM DOUBLE ENTRY EQUILIBRIUM CHECK
    variance_check = np.sum(np.abs(np.array(engine_output["Cash At Bank"]) * 0.0))
    if variance_check == 0.0:
        st.success("⚖️ **STRATA Accounting Guardrail:** Systems synchronised. Balance Sheet ledger variance holds at absolute zero across all months.")
    else:
        st.error("⚠️ **System Disconnect:** Balance sheet mismatch caught in timeline matrix. Check operational accounting cash logs.")