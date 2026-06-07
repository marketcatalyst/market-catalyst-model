# ui_skin/pages/3_📊_forecast.py
import sys
from pathlib import Path
import io

# --- CRITICAL PATH RESOLUTION ---
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
import altair as alt

# Route directly to our single source of truth matrix wheel
from ui_skin.core_engine.master_model import generate_integrated_3way_forecast

st.set_page_config(page_title="STRATA Strategy Room", page_icon="📊", layout="wide")

st.title("📊 AI Strategic Appraisal Room")
st.caption("Formulate alternative operational scenarios and generate instant executive business briefings.")
st.markdown("---")

# --- GUARDRAIL KEY CHECK ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Configuration Error: GEMINI_API_KEY is missing from your Streamlit secrets.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- CORE DATA HYDRATION FALLBACK (WinForecast Ground Truth) ---
if "baseline_inputs" not in st.session_state:
    st.warning("📋 No active ingestion data detected. Seeding app with baseline AHOTG corporate data.")
    # Fallback anchors matching your exact WinForecast spreadsheet profile
    st.session_state.baseline_inputs = {
        "opening_cash_balance": 69488.00,
        "opening_fixed_assets_nbv": 531385.00,
        "opening_accounts_receivable": 44886.00,
        "opening_accounts_payable": 8000.00,
        "opening_long_term_debt": 341001.00,
        "opening_retained_earnings": -82005.00,
        "admin_overheads_monthly": 18575.00,
        "base_monthly_gross_wages": 12000.00,
        "directors_salaries_monthly": 5150.00,
        "pension_opt_out": False,
        "seasonality_weights": [1.0] * 12,
        "y1_monthly_revenue_curve": [
            249310.00, 356310.00, 385200.00, 404460.00, 447260.00, 470800.00,
            508785.00, 707525.00, 763067.00, 750127.00, 750025.00, 736017.00
        ],
        "planned_capex_list": [
            {"Asset Class": "Fixtures", "Gross Purchase Price (£)": 120000.0, "Transaction Month": 6, "Funding Mechanism": "Upfront Cash"},
            {"Asset Class": "Bridgend", "Gross Purchase Price (£)": 48000.0, "Transaction Month": 6, "Funding Mechanism": "Upfront Cash"},
            {"Asset Class": "Cardiff", "Gross Purchase Price (£)": 30000.0, "Transaction Month": 6, "Funding Mechanism": "Upfront Cash"},
            {"Asset Class": "Penarth", "Gross Purchase Price (£)": 168000.0, "Transaction Month": 6, "Funding Mechanism": "Upfront Cash"}
        ]
    }

# --- UX SIDEBAR CONTROLS ---
st.sidebar.header("🕹️ Operational Scenario Knobs")
st.sidebar.markdown("Modify these high-level triggers to stress-test your financial model parameters in real-time.")

vol_growth = st.sidebar.slider(
    "Sales Volume Override", 
    0.0, 0.50, 0.0, step=0.05, 
    help="Simulates scaling transaction quantities. Triggers secondary payroll burdens and overtime mechanics automatically."
)
price_ramp = st.sidebar.slider(
    "Price Shift Override", 
    0.0, 0.20, 0.0, step=0.01, 
    help="Simulates altering pricing power margins upwards without changing workforce volume strain."
)

if st.sidebar.button("🔄 Reset to Baseline Projections"):
    st.session_state.vol_slider = 0.0
    st.session_state.price_slider = 0.0
    if "briefing_text" in st.session_state:
        del st.session_state.briefing_text
    st.rerun()

overrides = {
    "retail_annual_volume_growth": vol_growth,
    "retail_annual_price_ramp": price_ramp
}

# --- RUN COMPUTATIONAL Core WHEEL ---
base_matrix = generate_integrated_3way_forecast(st.session_state.baseline_inputs, overrides={})
scen_matrix = generate_integrated_3way_forecast(st.session_state.baseline_inputs, overrides=overrides)

# --- DYNAMIC SUMMARY METRICS TILES ---
col1, col2, col3 = st.columns(3)

with col1:
    cash_base_end = base_matrix["Bank Cash Position (£)"].iloc[-1]
    cash_scen_end = scen_matrix["Bank Cash Position (£)"].iloc[-1]
    cash_variance = cash_scen_end - cash_base_end
    st.metric(
        label="Closing Capital Reserves (Year 5)", 
        value=f"£{cash_scen_end:,.2f}", 
        delta=f"£{cash_variance:,.2f} vs Baseline",
        help="The total bank account balance at Month 60 after processing all rolling inputs."
    )

with col2:
    peak_tax_prov = scen_matrix["Tax Liability BS (£)"].max()
    st.metric(
        label="Peak Projected Corporate Tax Reserves", 
        value=f"£{peak_tax_prov:,.2f}",
        help="The highest accumulating tax obligation held on the Balance Sheet before quarterly/annual settlement drops out to HMRC."
    )

with col3:
    fte_strain_factor = scen_matrix["Ops_FTE_Strain"].max()
    st.metric(
        label="Workforce Load Indicator", 
        value=f"{fte_strain_factor:.1f}x Capacity",
        delta="Overtime Auto-Triggered ⚠️" if fte_strain_factor > 1.0 else "Stable Run-Rate",
        delta_color="inverse" if fte_strain_factor > 1.0 else "normal",
        help="Monitors human resource scaling. Volume spikes automatically shift labor into overtime premium tiers."
    )

st.markdown("---")

# --- INTERACTIVE ALTAIR VISUAL TRAJECTORY ---
st.subheader("📈 Liquid Capital Runway Path")
st.caption("Visualizes how sandbox strategy overrides compound your bank balance compared to the hardcoded WinForecast case track.")

timeline_data = pd.DataFrame({
    "Month": range(1, 61),
    "Baseline Profile": base_matrix["Bank Cash Position (£)"].values,
    "Simulated Strategy": scen_matrix["Bank Cash Position (£)"].values
}).melt(id_vars="Month", var_name="Projection Track", value_name="Liquid Reserves (£)")

runway_chart = (
    alt.Chart(timeline_data)
    .mark_line(strokeWidth=3)
    .encode(
        x=alt.X("Month:Q", title="Trading Calendar (Months)"),
        y=alt.Y("Liquid Reserves (£):Q", title="Clearing Bank Cash Assets (£)", scale=alt.Scale(zero=False)),
        color=alt.Color("Projection Track:N", scale=alt.Scale(domain=["Baseline Profile", "Simulated Strategy"], range=["#475569", "#0F766E"]))
    )
    .properties(width="container", height=350)
)
st.altair_chart(runway_chart, use_container_width=True)

# --- THE NARRATIVE AI COMPASS (GEMINI BRIEFING LAYER) ---
st.markdown("---")
st.subheader("🧠 Gemini Conversational Strategy Director")
st.markdown("""
Type questions about this simulation model in plain language. 
The underlying intelligence layer scans the complete double-entry records to formulate a high-level briefing.
""")

user_inquiry_box = st.text_input(
    "Ask Gemini an open-ended scenario question:",
    placeholder="e.g., Why does our capital runway drop significantly around Month 6? or detail how pricing increases mitigate our labor burden..."
)

if st.button("⚡ Execute AI Corporate Appraisal"):
    if user_inquiry_box:
        with st.spinner("Reviewing time-series arrays to extract management insights..."):
            try:
                # Condense vital mathematical markers to feed Gemini without flooding token boundaries
                data_snapshot_packet = f"""
                - Opening Cash: £{st.session_state.baseline_inputs['opening_cash_balance']:,.2f}
                - Year 5 Baseline Closing Cash: £{cash_base_end:,.2f}
                - Year 5 Scenario Closing Cash: £{cash_scen_end:,.2f}
                - Selected Volume Delta: +{vol_growth * 100}%
                - Selected Price Delta: +{price_ramp * 100}%
                - Peak Asset Tax Shield Accumulation: £{peak_tax_prov:,.2f}
                - Employee Capacity Mult: {fte_strain_factor:.2f}x
                """
                
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                You are a senior elite corporate financial director explaining complex three-way integrated calculations to a non-accounting executive team.
                Review this numerical snapshot data:
                {data_snapshot_packet}
                
                The business owner is requesting an answer to this operational scenario problem: "{user_inquiry_box}"
                
                Deliver a crisp, jargon-free executive review. Explain the exact financial 'reasons why' entries behave the way they do based on the metrics. Emphasize 'Connected Costs' loops explicitly (such as how the June Month 6 loan influx triggers massive CapEx asset additions, or why volume shocks automatically cascade into staffing overtime premiums). Focus on cash conservation and strategic scaling paths.
                """
                response = model.generate_content(prompt)
                st.session_state["briefing_text"] = response.text
            except Exception as e:
                st.error(f"Intelligence Layer Connection Fault: {str(e)}")
    else:
        st.warning("Please input a business narrative prompt above to prompt the appraisal module.")

if "briefing_text" in st.session_state:
    st.info(st.session_state["briefing_text"])

# --- TECHNICAL COMPLIANCE DRILLDOWN ---
st.markdown("---")
with st.expander("🔍 View Technical Double-Entry General Ledger Arrays (Auditing Panel)"):
    st.markdown("These sheets contain the underlying calculated data structures formatted directly by the master wheel engine.")
    tab_pl, tab_cf, tab_bs = st.tabs(["Profit & Loss Flow", "Indirect Cash Movement Bridges", "Statement of Financial Position"])
    
    with tab_pl:
        st.dataframe(scen_matrix[["Turnover (£)", "Direct Costs (£)", "Admin Overheads (£)", "Depreciation Expense (£)", "Interest Paid (£)", "Tax Expense (£)", "Net Profit (£)"]].T.style.format("£{:,.2f}"), use_container_width=True)
    with tab_cf:
        st.dataframe(scen_matrix[["Bridge: Net Profit", "Bridge: Depreciation", "Bridge: Net Movement", "Bank Cash Position (£)"]].T.style.format("£{:,.2f}"), use_container_width=True)
    with tab_bs:
        st.dataframe(scen_matrix[["Bank Cash Position (£)", "Accounts Receivable BS (£)", "Fixed Asset NBV (£)", "Accounts Payable & Debt (£)", "Tax Liability BS (£)", "Retained Earnings (£)"]].T.style.format("£{:,.2f}"), use_container_width=True)