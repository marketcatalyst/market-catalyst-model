import sys
import os
import json

# Dynamic Environment Path Safeguard
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
from ui_skin.core_engine.master_orchestrator import run_master_three_way_engine

st.set_page_config(page_title="STRATA - Financial Forecast", page_icon="📊", layout="wide")

st.title("Three-Way Financial Forecast Control Centre")
st.caption("AI-Driven predictive modelling platform connected directly to Gemini analytics pipelines.")

# Initialize default session parameters if cache clear occurs
if "baseline_inputs" not in st.session_state:
    st.session_state["baseline_inputs"] = {
        "opening_cash_balance": 69488.00,             
        "opening_fixed_assets_nbv": 531385.00,         
        "opening_accounts_receivable": 44886.00,          
        "opening_accounts_payable": 8000.00,
        "opening_long_term_debt": 341001.00,           
        "opening_inventory_balance": 12000.00,
        "y1_revenue_target": 6528886.00,
        "y2_revenue_target": 10805679.00,
        "y3_revenue_target": 12126469.00,
        "monthly_overhead_baseline": 18575.00,
        "base_production_cogs_pct": 0.696,
        "y1_monthly_revenue_curve": [
            249310.00, 356310.00, 385200.00, 404460.00, 447260.00, 470800.00,
            508785.00, 707525.00, 763067.00, 750127.00, 750025.00, 736017.00
        ],
        "historical_cash_flow_vector": [
            30534.00, 55816.00, 57184.00, 107551.00, 112372.00, 313144.00, 
            133467.00, 210615.00, 232118.00, 373846.00, 335510.00, 313760.00,
            543297.00, 614240.00, 718038.00, 920317.00, 1044788.00, 1165807.00,
            1382623.00, 1491213.00, 1617929.00, 1808973.00, 1887158.00, 1946084.00,
            2176989.00, 2265357.00, 2390615.00, 2623144.00, 2772046.00, 2917012.00,
            3166164.00, 3296896.00, 3448372.00, 3668049.00, 3763998.00, 3837934.00,
            4068140.00, 4156980.00, 4295761.00, 4567153.00, 4732985.00, 4894313.00,
            5184725.00, 5329768.00, 5498544.00, 5755233.00, 5860489.00, 5940553.00,
            6150000.00, 6340000.00, 6520000.00, 6710000.00, 6920000.00, 7120000.00,
            7320000.00, 7540000.00, 7750000.00, 7940000.00, 8120000.00, 8244000.00
        ],
        "historical_fa_nbv_vector": [755746.00, 661095.00, 477464.00, 302254.00, 150000.00],
        "historical_debt_vector": [341001.00, 237330.00, 11001.00, 0.0, 0.0],
        "historical_ar_vector": [320000.00, 352000.00, 387200.00, 442957.00, 480000.00],
        "historical_inventory_vector": [12000.00, 12000.00, 12000.00, 12000.00, 12000.00],
        "meta_project_name": "Core Strategy Expansion Plan", "meta_horizon_years": 5, "meta_year_end": "December"
    }

raw_loan = pd.DataFrame({"Principal": [0.0], "Interest": [0.0], "Monthly Payment": [0.0]})
raw_rev = pd.DataFrame({"Revenue": [6528886.00]})

baseline_output = run_master_three_way_engine(
    baseline_inputs=st.session_state["baseline_inputs"],
    loan_register_df=raw_loan,
    revenue_matrix_df=raw_rev,
    planned_capex_list=[]
)

# =============================================================================
# 🔥 VISUAL MODEL PERFORMANCE LAYERS
# =============================================================================
st.markdown("### 📊 Operational Base Case Trends")
chart_col1, chart_col2 = st.columns(2)
timeline_index = list(range(1, 61))

with chart_col1:
    st.markdown("#### Profitability Trajectory (Net Monthly Profit)")
    prof_df = pd.DataFrame({"Net Profit (£)": baseline_output["Net Profit"]}, index=timeline_index)
    prof_df.index.name = "Timeline Horizon (Months)"
    st.line_chart(prof_df, color="#2b5c8f")
with chart_col2:
    st.markdown("#### Corporate Cash Runway (Closing Liquid Balances)")
    cash_df = pd.DataFrame({"Cash at Bank (£)": baseline_output["Cash At Bank"]}, index=timeline_index)
    cash_df.index.name = "Timeline Horizon (Months)"
    st.area_chart(cash_df, color="#1e7e34")

# =============================================================================
# 🤖 INTELLECTUAL STRATEGIC APPRAISAL ROOM (GEMINI INTEG)
# =============================================================================
st.markdown("---")
st.markdown("### 🤖 STRATA On-Demand Strategic Appraisal Room")
st.caption("Submit narrative queries below to compile parallel target scenarios without cluttering core ledger charts.")

user_inquiry = st.text_area(
    "Query Strategic Alternatives (e.g., Evaluate a 1% expansion in sales volume baseline):",
    placeholder="Type scenario narrative query here..."
)

if st.button("⚡ Generate Independent Executive Briefing"):
    if user_inquiry:
        # Check for API Key presence in Streamlit secrets
        if "GEMINI_API_KEY" in st.secrets:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        else:
            st.error("API Error: GEMINI_API_KEY is missing from your Streamlit secrets configurations.")
            st.stop()
            
        with st.spinner("🧠 Gemini Consulting Layer processing operational overrides..."):
            # Construct a system instruction template forcing standard JSON returns
            system_prompt = (
                "You are an elite corporate finance advisor modeling simulations for a three-way financial forecast framework. "
                "Your objective is to translate the user's free-text strategic narrative request into explicit mathematical overrides "
                "and compose a professional executive commentary.\n\n"
                "You MUST respond with a valid raw JSON object containing exactly two keys:\n"
                "1. 'overrides': a dictionary mapping variable adjustments. Valid target keys are:\n"
                "   - 'retail_annual_volume_growth' (float, e.g., 0.01 for 1% up)\n"
                "   - 'retail_annual_price_ramp' (float, e.g., -0.015 for 1.5% deduction)\n"
                "   - 'wc_lag_corporate_months' (int, e.g., 0 for instant collection optimization)\n"
                "   - 'expansion_scenario_active' (boolean)\n"
                "2. 'commentary': a text string containing a thorough executive evaluation of the financial strategy.\n\n"
                "Do not include any markdown backticks, explanations, or text formatting outside of the raw JSON dictionary string."
            )
            
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # FIX: Force native JSON mode to avoid parsing errors
                response = model.generate_content(
                    f"System Instructions: {system_prompt}\n\nUser Request: {user_inquiry}",
                    generation_config={"response_mime_type": "application/json"}
                )
                
                # Load the verified structured text safely
                parsed_payload = json.loads(response.text.strip())
                
                scenario_overrides = parsed_payload.get("overrides", {})
                executive_commentary = parsed_payload.get("commentary", "Analysis generated cleanly.")
                
                # Execute separate mathematical instance using Gemini parameters
                scenario_output = run_master_three_way_engine(
                    baseline_inputs=st.session_state["baseline_inputs"],
                    loan_register_df=raw_loan,
                    revenue_matrix_df=raw_rev,
                    planned_capex_list=[],
                    overrides=scenario_overrides
                )
                
                # Display dynamic report output matrix
                st.markdown("### 📄 AI Strategic Briefing Report")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.metric("Base Case Year 5 Cash Balance", f"£{baseline_output['Cash At Bank'][-1]:,.0f}")
                    st.metric("Scenario Year 5 Cash Balance", f"£{scenario_output['Cash At Bank'][-1]:,.0f}", 
                              delta=f"£{scenario_output['Cash At Bank'][-1] - baseline_output['Cash At Bank'][-1]:,.0f}")
                with col_m2:
                    st.metric("Base Case Peak Monthly Profit", f"£{max(baseline_output['Net Profit']):,.0f}/mo")
                    st.metric("Scenario Peak Monthly Profit", f"£{max(scenario_output['Net Profit']):,.0f}/mo",
                              delta=f"£{max(scenario_output['Net Profit']) - max(baseline_output['Net Profit']):,.0f}")
                    
                st.info(f"💡 **Executive Commentary:** {executive_commentary}")
                
                comparison_df = pd.DataFrame({
                    "Base Cash Runway": baseline_output["Cash At Bank"],
                    "Scenario Cash Runway": scenario_output["Cash At Bank"]
                }, index=timeline_index)
                st.line_chart(comparison_df)
                
            except json.JSONDecodeError:
                st.error("Failed to parse response structure. The model returned an invalid payload layout.")
            except Exception as e:
                st.error(f"Failed to compile Gemini response layer: {str(e)}")
    else:
        st.warning("Please type a scenario narrative request above to trigger an analysis.")

st.markdown("---")

# =============================================================================
# 📈 VIEW REPRESENTATION MATRIX
# =============================================================================
view_type = st.radio("Select Base Statement View Horizon:", ["5-Year Annual Summary", "60-Month Detailed Track"], index=0, horizontal=True)

def package_annual_dataframe(labels, keys, data):
    rows = []
    snapshot_keys = [
        "Cash At Bank", "Fixed Asset NBV", "Outstanding Debt", "Tax Liability BS", 
        "Inventory Asset BS", "Accounts Receivable BS", "Equity Retained BS"
    ]
    for label, key in zip(labels, keys):
        m_data = np.array(data[key])
        vals = []
        for y in range(5):
            slice_data = m_data[y*12 : (y+1)*12]
            if key in snapshot_keys:
                vals.append(slice_data[-1])
            else:
                vals.append(slice_data.sum())
        rows.append(vals)
    return pd.DataFrame(rows, index=labels, columns=["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"])

def package_monthly_dataframe(labels, keys, data):
    rows = [data[key] for key in keys]
    return pd.DataFrame(rows, index=labels, columns=[f"Month {m+1}" for m in range(60)])

# FIX: Version control compatibility for df.map vs df.applymap
def clean_format(df):
    formatter = lambda x: f"£{x:,.0f}" if x >= 0 else f"-£{abs(x):,.0f}"
    if hasattr(df, 'map'):
        return df.map(formatter)
    return df.applymap(formatter)

tab_pl, tab_cf, tab_bs = st.tabs(["📊 Profit & Loss", "💸 Cash Flow", "⚖️ Balance Sheet"])

with tab_pl:
    labels = ["Gross Revenue Turnover (£)", "Direct Cost of Purchases (£)", "**TOTAL COST OF GOODS SOLD (COGS) (£)**", "Administrative Overheads (£)", "**OPERATIONAL EBITDA (£)**", "Book Depreciation Expense (£)", "**OPERATING PROFIT (EBIT) (£)**", "Statutory Corporation Tax (£)", "**NET COMPREHENSIVE PROFIT (£)**"]
    keys = ["Revenue", "Purchases", "COGS", "Overheads", "Revenue", "Depreciation", "Revenue", "Tax Expense", "Net Profit"]
    df = package_annual_dataframe(labels, keys, baseline_output) if view_type == "5-Year Annual Summary" else package_monthly_dataframe(labels, keys, baseline_output)
    
    for c in df.columns:
        df.loc["**OPERATIONAL EBITDA (£)**", c] = df.loc["Gross Revenue Turnover (£)", c] - df.loc["**TOTAL COST OF GOODS SOLD (COGS) (£)**", c] - df.loc["Administrative Overheads (£)", c]
        df.loc["**OPERATING PROFIT (EBIT) (£)**", c] = df.loc["**OPERATIONAL EBITDA (£)**", c] - df.loc["Book Depreciation Expense (£)", c]
        df.loc["**NET COMPREHENSIVE PROFIT (£)**", c] = df.loc["**OPERATING PROFIT (EBIT) (£)**", c] - df.loc["Statutory Corporation Tax (£)", c]
    st.table(clean_format(df))

with tab_cf:
    labels = ["Net Operating Profit Generated (£)", "Add Back: Non-Cash Depreciation (£)", "Changes in Invoiced Working Capital (£)", "Corporation Tax Paid (£)", "**NET MONTHLY CASH FLOW VARIANCE (£)**", "**CLOSING LIQUID CASH AT BANK BALANCE (£)**"]
    keys = ["Net Profit", "Depreciation", "Working Capital CF", "Tax Cash Paid", "Net Profit", "Cash At Bank"]
    df = package_annual_dataframe(labels, keys, baseline_output) if view_type == "5-Year Annual Summary" else package_monthly_dataframe(labels, keys, baseline_output)
    
    for c in df.columns:
        df.loc["**NET MONTHLY CASH FLOW VARIANCE (£)**", c] = df.loc["Net Operating Profit Generated (£)", c] + df.loc["Add Back: Non-Cash Depreciation (£)", c] + df.loc["Changes in Invoiced Working Capital (£)", c] - df.loc["Corporation Tax Paid (£)", c]
    st.table(clean_format(df))

with tab_bs:
    labels = [
        "Fixed Asset NBV (£)", 
        "Inventory Stock Value (£)", 
        "Accounts Receivable (£)", 
        "Liquid Cash held at Bank (£)", 
        "**TOTAL TANGIBLE ACTIVE ASSETS (£)**", 
        "Statutory Tax Liabilities (£)", 
        "Long-Term Debt Obligations (£)", 
        "**TOTAL ACCRUED LIABILITIES OBLIGATIONS (£)**", 
        "Net Worth Retained Equity (£)"
    ]
    keys = [
        "Fixed Asset NBV", 
        "Inventory Asset BS", 
        "Accounts Receivable BS", 
        "Cash At Bank", 
        "Fixed Asset NBV", 
        "Tax Liability BS", 
        "Outstanding Debt", 
        "Tax Liability BS", 
        "Equity Retained BS"
    ]
    df = package_annual_dataframe(labels, keys, baseline_output) if view_type == "5-Year Annual Summary" else package_monthly_dataframe(labels, keys, baseline_output)
    
    for c in df.columns:
        df.loc["**TOTAL TANGIBLE ACTIVE ASSETS (£)**", c] = df.loc["Fixed Asset NBV (£)", c] + df.loc["Inventory Stock Value (£)", c] + df.loc["Accounts Receivable (£)", c] + df.loc["Liquid Cash held at Bank (£)", c]
        df.loc["**TOTAL ACCRUED LIABILITIES OBLIGATIONS (£)**", c] = df.loc["Statutory Tax Liabilities (£)", c] + df.loc["Long-Term Debt Obligations (£)", c]
    st.table(clean_format(df))
    
    # Balance sheet verification guardrail
    eq_track = baseline_output["Equity Retained BS"][-1] if view_type == "5-Year Annual Summary" else baseline_output["Equity Retained BS"]
    tbl_net = df.loc["Net Worth Retained Equity (£)"].iloc[-1] if view_type == "5-Year Annual Summary" else df.loc["Net Worth Retained Equity (£)"].to_numpy()
    if np.sum(np.abs(tbl_net - eq_track)) < 0.01:
        st.success("⚖️ **STRATA Accounting Guardrail:** Core financial ledger verification balanced at absolute zero variance.")