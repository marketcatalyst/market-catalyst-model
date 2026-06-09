# ui_skin/pages/3_📊_forecast.py
import sys
from pathlib import Path

# --- 1. CRITICAL PATH RESOLUTION ---
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

import streamlit as st
import pandas as pd
import numpy as np
import io
import google.generativeai as genai

st.set_page_config(layout="wide", page_title="STRATA AI Strategy Room")

# --- 2. SECURITY GUARDRAIL & INITIALIZATION ---
if "GEMINI_API_KEY" not in st.secrets:
    st.error("❌ Configuration Error: 'GEMINI_API_KEY' is missing from the top of your local .streamlit/secrets.toml file.")
    st.stop()

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

st.title("📊 AI Strategic Appraisal Room")
st.caption("Parallel Multi-Scenario Simulation, Dual-Grained Reporting, & Executive Narrative Synth")
st.markdown("---")

# --- 3. SESSION STATE INTEGRITY CONTRACT ---
if "baseline_inputs" not in st.session_state:
    st.warning("📋 No active ingestion contract detected. Seeding workspace memory with fallback WinForecast benchmark profiles.")
    fallback_records = [
        {"Account Code": "0020", "Account Group": "Fixed Assets", "Account Name": "Operational Plant & Heavy Ovens Gross Cost", "Net Balance (£)": 150000.00, "Assigned Platform Destination": "Fixed Assets Gross Cost"},
        {"Account Code": "0040", "Account Group": "Fixed Assets", "Account Name": "Company Delivery Fleet Vehicles", "Net Balance (£)": 381385.00, "Assigned Platform Destination": "Fixed Assets Gross Cost"},
        {"Account Code": "1200", "Account Group": "Current Assets", "Account Name": "Barclays Commercial Current A/C", "Net Balance (£)": 69488.00, "Assigned Platform Destination": "Liquid Bank Cash Base"},
        {"Account Code": "1100", "Account Group": "Current Assets", "Account Name": "Trade Debtors Control Ledger", "Net Balance (£)": 44886.00, "Assigned Platform Destination": "Trade Accounts Receivable (AR)"},
        {"Account Code": "2200", "Account Group": "Current Liabilities", "Account Name": "Trade Creditors Control Ledger", "Net Balance (£)": -8000.00, "Assigned Platform Destination": "Trade Accounts Payable (AP)"},
        {"Account Code": "2150", "Account Group": "Long-Term Liabilities", "Account Name": "Development Bank of Wales (DBW) Term Loan", "Net Balance (£)": -130176.00, "Assigned Platform Destination": "Outstanding Debt Obligations"},
        {"Account Code": "3000", "Account Group": "Equity Reserve", "Account Name": "Prior Year Accumulated Retained Profits", "Net Balance (£)": 82005.00, "Assigned Platform Destination": "Retained Earnings Reserve"}
    ]
    st.session_state["baseline_inputs"] = {
        "opening_cash_balance": 69488.00,
        "opening_fixed_assets_nbv": 531385.00,
        "opening_accounts_receivable": 44886.00,
        "opening_accounts_payable": 8000.00,
        "opening_long_term_debt": 130176.00,
        "opening_retained_earnings": 82005.00,
        "granular_ledger_records": fallback_records,
        "admin_overheads_monthly": 18575.00,
        "base_monthly_gross_wages": 12000.00,
        "directors_salaries_monthly": 5150.00,
        "pension_opt_out": False,
        "y1_monthly_revenue_curve": [249310.0, 356310.0, 385200.0, 404460.0, 447260.0, 470800.0, 508785.0, 707525.0, 763067.0, 750127.0, 750025.0, 736017.0],
    }

inputs = st.session_state["baseline_inputs"]
granular_records = inputs.get("granular_ledger_records", [])

# --- 4. SIDEBAR MANAGEMENT CONTROLS ---
st.sidebar.header("🎛️ Live Scenario Sensitivities")
volume_delta = st.sidebar.slider("Sales Volume Modifier (%)", min_value=-50.0, max_value=50.0, value=0.0, step=5.0) / 100.0
opex_delta = st.sidebar.slider("Overhead Inflation Pressure (%)", min_value=-20.0, max_value=50.0, value=0.0, step=2.5) / 100.0

# --- 5. REPORTING DEPTH CONTROLLER CONTROLS ---
st.markdown("### **Step 1: Financial Matrix Granularity Controls**")
col_view, col_export = st.columns([2, 1])

with col_view:
    report_depth = st.selectbox(
        "Select Active Data Presentation Depth:",
        options=["Summary Level (Executive Dashboard Summary)", "Granular Detail Level (WinForecast Account Appendix)"],
        help="Summary Level groups accounts into standard three-way layout lines. Granular maps out every individual ledger code sequentially."
    )

# --- 6. CORE 60-MONTH COMPUTATION ENGINE ---
months = [f"M{i:02d}" for i in range(1, 61)]

simulated_revenue = [float(r * (1.0 + volume_delta)) for r in (inputs["y1_monthly_revenue_curve"] * 5)[:60]]
simulated_cogs = [r * 0.40 for r in simulated_revenue]
simulated_opex = [(inputs["admin_overheads_monthly"] + inputs["base_monthly_gross_wages"] + inputs["directors_salaries_monthly"]) * (1.0 + opex_delta)] * 60

simulated_cash = []
current_cash = inputs["opening_cash_balance"]
for i in range(60):
    net_monthly_profit = simulated_revenue[i] - simulated_cogs[i] - simulated_opex[i]
    current_cash += net_monthly_profit * 0.85
    simulated_cash.append(current_cash)

summary_p_and_l = pd.DataFrame([simulated_revenue, simulated_cogs, simulated_opex], columns=months, index=["Gross Revenue Turnover", "Cost of Goods Sold (COGS)", "Total Administrative Expenses"])
summary_balance_sheet = pd.DataFrame([simulated_cash, [inputs["opening_fixed_assets_nbv"]] * 60], columns=months, index=["Liquid Cash Base", "Net Tangible Fixed Assets"])

granular_rows = []
for record in granular_records:
    base_bal = abs(float(record["Net Balance (£)"]))
    dest = record["Assigned Platform Destination"]
    
    if dest == "Liquid Bank Cash Base":
        trend = simulated_cash
    elif dest == "Fixed Assets Gross Cost":
        trend = [base_bal * (0.99 ** i) for i in range(1, 61)]
    elif dest == "Trade Accounts Receivable (AR)":
        trend = [r * 0.12 for r in simulated_revenue]
    elif dest == "Outstanding Debt Obligations":
        trend = [max(0.0, base_bal - (i * 2500)) for i in range(1, 61)]
    else:
        trend = [base_bal] * 60
        
    row_data = {
        "Account Code": record["Account Code"],
        "Account Group": record["Account Group"],
        "Account Name": record["Account Name"],
        "Opening Base": float(record["Net Balance (£)"])
    }
    for idx, m in enumerate(months):
        row_data[m] = trend[idx] if float(record["Net Balance (£)"]) >= 0 else -trend[idx]
    granular_rows.append(row_data)

granular_forecast_df = pd.DataFrame(granular_rows)

# --- 7. EXCEL MEMORY BUFFER BUILDER ---
with col_export:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        summary_p_and_l.to_excel(writer, sheet_name='Summary P&L', index=True)
        summary_balance_sheet.to_excel(writer, sheet_name='Summary Balance Sheet', index=True)
        granular_forecast_df.to_excel(writer, sheet_name='Granular Account Ledger', index=False)
    
    st.markdown("<p style='margin-bottom: 24px;'></p>", unsafe_allow_html=True)
    st.download_button(
        label="📥 Download Integrated Excel Model (.xlsx)",
        data=buffer.getvalue(),
        file_name="STRATA_Granular_Three_Way_Forecast.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# --- 8. CONDITIONAL RENDERING OF DATA DEPTH VIEWS (WHOLE POUND £1 FORMATTING) ---
st.markdown("---")
if report_depth == "Summary Level (Executive Dashboard Summary)":
    st.markdown("#### 📉 **Executive Summary: Consolidated Three-Way Schedules**")
    
    st.markdown("**Profit & Loss Statement (Summary View)**")
    st.dataframe(
        summary_p_and_l,
        use_container_width=True,
        column_config={m: st.column_config.NumberColumn(format="£%,.0f") for m in months}
    )
    
    st.markdown("**Statement of Financial Position (Balance Sheet View)**")
    st.dataframe(
        summary_balance_sheet,
        use_container_width=True,
        column_config={m: st.column_config.NumberColumn(format="£%,.0f") for m in months}
    )

else:
    st.markdown("#### 🔍 **Granular Audit Appendix: Source Level Account Matrices**")
    st.markdown("##### *Line-by-Line System Attribute Track (WinForecast Target Order)*")
    
    if not granular_forecast_df.empty:
        group_order = {"Fixed Assets": 0, "Current Assets": 1, "Current Liabilities": 2, "Long-Term Liabilities": 3, "Equity Reserve": 4}
        granular_forecast_df["Sort_Order"] = granular_forecast_df["Account Group"].map(group_order)
        granular_forecast_df = granular_forecast_df.sort_values(by="Sort_Order").drop(columns=["Sort_Order"])
        
        # Build whole-pound configurations across the active time-series layout
        config_map = {m: st.column_config.NumberColumn(format="£%,.0f") for m in months}
        config_map["Opening Base"] = st.column_config.NumberColumn(format="£%,.0f")
        
        st.dataframe(
            granular_forecast_df,
            use_container_width=True,
            column_config=config_map
        )
    else:
        st.warning("No custom ledger rows cached in active application RAM.")

# --- 9. CONVERSATIONAL STRATEGY DIRECTOR ---
st.markdown("---")
st.markdown("### 🧠 **Step 2: Conversational Strategy Director**")
st.markdown("Ask our structural AI engine to interpret the systemic financial effects of your custom scenario changes.")

user_query = st.text_input(
    "Submit scenario inquiry here...",
    placeholder="e.g., How does our sales volume modifier affect our cash buffer and peak statutory corporation tax liabilities?",
    value="How does our sales volume modifier affect our cash buffer and peak statutory corporation tax liabilities?"
)

if st.button("⚡ Execute AI Corporate Appraisal"):
    ledger_context = f"Granular Ledger Count: {len(granular_records)}. Starting cash reserve position: £{inputs['opening_cash_balance']:,.2f}. Assigned Sensitivity Parameters: Volume Delta={volume_delta*100}%, Opex Inflation={opex_delta*100}%."
    
    prompt = f"""
    You are the Lead Strategic Corporate Director at STRATA Forecasting Analytics. 
    Review this background accounting ledger context and the specific user inquiry. 
    Provide a professional, concise executive briefing detailing the financial impact. 
    Focus on connected cost behaviors, liquidity runway effects, and statutory obligations.
    
    Context: {ledger_context}
    Inquiry: {user_query}
    """
    
    with st.spinner("Compiling parallel multi-year forecast matrices and synthesizing executive report..."):
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            st.markdown("#### 📑 **Automated Executive Briefing Response:**")
            st.info(response.text)
        except Exception as e:
            st.error(f"AI Generation Interrupted: {str(e)}")