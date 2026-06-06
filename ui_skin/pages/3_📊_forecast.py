import sys
from pathlib import Path
import io  # <-- Added to handle secure file buffers

# --- 🛡️ CRITICAL PATH RESOLUTION FIX ---
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

import streamlit as st
import pandas as pd
import numpy as np
import google.generativeai as genai
import altair as alt
from ui_skin.core_engine.master_orchestrator import run_master_three_way_engine

# Page Configuration
st.set_page_config(page_title="AI Strategic Appraisal Room", page_icon="📊", layout="wide")

st.title("📊 AI Strategic Appraisal Room")
st.caption("Formulate alternative operational scenarios and generate independent corporate executive briefings.")

# --- 🔑 SECURITY GUARDRAIL: SECRET KEY VALIDATION ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("API Error: GEMINI_API_KEY is missing from your Streamlit secrets configurations.")
    st.stop()

# Initialize the Gemini SDK layout using the root context token
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- CORE DATA FALLBACK HYDRATION ---
if "baseline_inputs" not in st.session_state:
    st.session_state.baseline_inputs = {
        "opening_cash_balance": 69488.00,
        "y1_revenue_target": 6528886.00,
        "y2_revenue_target": 10805679.00,
        "y3_revenue_target": 12126469.00,
        "monthly_overhead_baseline": 18575.00,
        "base_production_cogs_pct": 0.696,
        "historical_cash_flow_vector": [69488.00 + (i * 138551.05) for i in range(59)] + [8244000.00],
        "historical_fa_nbv_vector": [531385.00] * 5,
        "historical_debt_vector": [341001.00] * 5,
        "historical_ar_vector": [44886.00] * 5,
        "historical_inventory_vector": [12000.00] * 5
    }

# --- 🔄 INTERACTIVE UX SIDEBAR & ESCAPE HATCH ---
st.sidebar.header("Operational Scenario Controls")

if st.sidebar.button("🔄 Reset to Operational Baseline"):
    st.session_state.vol_slider = 0.0
    st.session_state.price_slider = 0.0
    if "user_query_text" in st.session_state:
        st.session_state.user_query_text = ""
    st.rerun()

st.sidebar.markdown("---")

vol_growth = st.sidebar.slider(
    "Sales Volume Growth Override", 
    0.0, 0.50, 0.0, step=0.05, 
    key="vol_slider",
    help="Simulate uniform annual demand expansion."
)

price_ramp = st.sidebar.slider(
    "Price Ramp Override", 
    0.0, 0.20, 0.0, step=0.01, 
    key="price_slider",
    help="Simulate localized product price increases."
)

overrides = {
    "retail_annual_volume_growth": vol_growth,
    "retail_annual_price_ramp": price_ramp,
    "expansion_scenario_active": False
}

# Execute parallel simulation runs inside the dynamic cash engine
base_outputs = run_master_three_way_engine(st.session_state.baseline_inputs, None, None, None, overrides={})
scenario_outputs = run_master_three_way_engine(st.session_state.baseline_inputs, None, None, None, overrides=overrides)

# --- 📈 METRIC APPRAISAL CARD TILES ---
col1, col2 = st.columns(2)

with col1:
    st.metric(label="Base Case Year 5 Cash Balance", value=f"£{int(base_outputs['Cash At Bank'][-1]):,}")
    cash_delta = int(scenario_outputs['Cash At Bank'][-1] - base_outputs['Cash At Bank'][-1])
    st.metric(label="Scenario Year 5 Cash Balance", value=f"£{int(scenario_outputs['Cash At Bank'][-1]):,}", delta=f"£{cash_delta:,}")

with col2:
    base_peak_profit = np.max(base_outputs["Net Profit"])
    scen_peak_profit = np.max(scenario_outputs["Net Profit"])
    profit_delta = int(scen_peak_profit - base_peak_profit)
    st.metric(label="Base Case Peak Monthly Profit", value=f"£{int(base_peak_profit):,}/mo")
    st.metric(label="Scenario Peak Monthly Profit", value=f"£{int(scen_peak_profit):,}/mo", delta=f"£{profit_delta:,}")

st.markdown("---")
st.subheader("Liquid Capital Runway Projections")

comparison_df = pd.DataFrame({
    "Base Cash Runway": np.round(base_outputs["Cash At Bank"], 2),
    "Scenario Cash Runway": np.round(scenario_outputs["Cash At Bank"], 2)
})

comparison_melted = comparison_df.reset_index().melt(
    id_vars="index", var_name="Scenario", value_name="Cash Balance (£)"
)
comparison_melted.rename(columns={"index": "Month"}, inplace=True)

stable_chart = (
    alt.Chart(comparison_melted)
    .mark_line(strokeWidth=2.5)
    .encode(
        x=alt.X("Month:Q", title="Timeline Horizon (Months)"),
        y=alt.Y("Cash Balance (£):Q", title="Closing Liquid Balances (£)", scale=alt.Scale(zero=False)),
        color=alt.Color("Scenario:N", scale=alt.Scale(domain=["Base Cash Runway", "Scenario Cash Runway"], range=["#2b5c8f", "#1e7e34"]))
    )
    .properties(width="container", height=400)
)
st.altair_chart(stable_chart, use_container_width=True)

st.markdown("---")

# --- ⚡ INTELLIGENCE LAYER: GEMINI RESPONSE BRIEFING ---
user_inquiry = st.text_area(
    "Query Strategic Alternatives (e.g., Evaluate a 1% expansion in sales volume baseline):",
    placeholder="Type scenario narrative query here...",
    key="user_query_text"
)

if st.button("⚡ Generate Independent Executive Briefing"):
    if user_inquiry:
        with st.spinner("Compiling Gemini response layer..."):
            try:
                model = genai.GenerativeModel('gemini-3.5-flash')
                prompt = f"""
                You are a senior corporate finance director reviewing a 5-year three-way integrated forecast model.
                Analyze the following operational variance metrics and compile a clean executive briefing:
                Baseline Metrics:
                - Ending Year 5 Cash Position: £{base_outputs['Cash At Bank'][-1]:,.2f}
                - Highest Monthly Profit Ceiling: £{base_peak_profit:,.2f}/mo
                Simulated Alternative Case ({vol_growth * 100}% Volume Expansion, {price_ramp * 100}% Pricing Shift):
                - Ending Year 5 Cash Position: £{scenario_outputs['Cash At Bank'][-1]:,.2f}
                - Highest Monthly Profit Ceiling: £{scen_peak_profit:,.2f}/mo
                User Narrative Query Context: "{user_inquiry}"
                Provide a crisp, corporate strategic analysis discussing margins, working capital absorption speed, and cumulative cash optimization recommendations.
                """
                response = model.generate_content(prompt)
                st.info(response.text)
            except Exception as e:
                st.error(f"Failed to compile Gemini response layer: {str(e)}")
    else:
        st.warning("Please enter a scenario narrative request into the strategic prompt box to compile an executive analysis.")

# --- 📥 CORPORATE EXPORT CENTER (RESTORED) ---
st.markdown("---")
st.subheader("📥 Corporate Export Center")
st.caption("Download the active simulation matrices to your local machine for offline review.")

# Format the 60-month vectors into clean DataFrames for the spreadsheet
base_export_df = pd.DataFrame(base_outputs)
base_export_df.index = [f"Month {i+1}" for i in base_export_df.index]

scen_export_df = pd.DataFrame(scenario_outputs)
scen_export_df.index = [f"Month {i+1}" for i in scen_export_df.index]

# Write to an active memory buffer to instantly generate the Excel file
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    base_export_df.to_excel(writer, sheet_name="Baseline Tracker")
    scen_export_df.to_excel(writer, sheet_name="Strategic Scenario")

col_dl1, col_dl2 = st.columns(2)

with col_dl1:
    st.download_button(
        label="📊 Download Integrated Excel Model (.xlsx)",
        data=excel_buffer.getvalue(),
        file_name="STRATA_Strategic_Forecast.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with col_dl2:
    st.info("💡 **Legacy PDF Hook:** To restore your custom PDF generation, import the specific function from your `report_generator.py` module here.")