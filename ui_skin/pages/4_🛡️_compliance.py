# ui_skin/pages/4_🛡️_compliance.py
import streamlit as st
import pandas as pd
import numpy as np
from core_engine.master_model import generate_integrated_3way_forecast

st.set_page_config(layout="wide", page_title="HMRC Pre-Submission Compliance Audit")

st.title("🛡️ Pre-Submission Audit & Risk Profiler")
st.caption("Algorithmic Risk Screening Engine • Simulating HMRC Connect System Data Anomaly Rules")
st.markdown("---")

st.markdown("""
### Automated Risk Analysis & Diagnostic Log
Before exporting financial models for bank lending presentations, board reviews, or HMRC filings, 
the system scans your generated datasets for statistical anomalies, rounding bias, and structural variance.
""")

# --- 1. LIVE SESSION STATE INTENDED INGESTION ---
# Gracefully extract parameters from the global cache with rock-solid fallbacks
baseline = st.session_state.get("baseline_inputs", {
    "nominal_seasonal_sales_base": 50000.0,
    "fixed_contractual_sales_base": 5000.0,
    "nominal_cogs_base": 22000.0,
    "base_monthly_gross_wages": 12000.0,
    "admin_overheads_monthly": 8000.0,
    "directors_salaries_monthly": 5000.0,
    "pension_opt_out": False,
    "seasonality_weights": [1.0] * 12,
    "opening_cash_balance": 20000.0,
    "opening_fixed_assets_nbv": 150000.0,
    "opening_accounts_receivable": 10000.0,
    "opening_accounts_payable": 8000.0,
    "opening_long_term_debt": 50000.0,
    "opening_retained_earnings": 122000.0
})

sic_profile = st.session_state.get("selected_sic_profile", {
    "sic_code": "10710",
    "industry_title": "Manufacture of bread, fresh pastry goods and cakes",
    "target_gross_margin_pct": 45.0,
    "max_allowable_labor_pct": 35.0
})

active_scenario = st.session_state.get("global_strategic_scenario", "Baseline Case")

# Apply active macro scenario variations from Sandbox if selected
inputs_package = baseline.copy()
if active_scenario == "Growth Expansion Case":
    inputs_package["nominal_seasonal_sales_base"] *= 1.15
elif active_scenario == "Supply-Chain Stress Case":
    inputs_package["nominal_seasonal_sales_base"] *= 0.80

# --- 2. EXECUTE THE UNIFIED FINANCIAL RUN-RATE ---
forecast_df = generate_integrated_3way_forecast(inputs_package)

# --- 3. DYNAMIC BENFORD'S LAW DATA EXTRACTION ---
# Instead of hardcoded numbers, pull every dynamic calculation result from the active 3-way matrix
columns_to_scan = [
    "Turnover (£)", "Direct Costs (£)", "Admin Overheads (£)", 
    "Depreciation Expense (£)", "Net Profit (£)", "Bank Cash Position (£)", 
    "Fixed Asset NBV (£)", "Accounts Payable & Debt (£)", "Retained Earnings (£)"
]

# Flatten every single calculated value in the table into a pure numeric evaluation array
live_ledger_amounts = forecast_df[columns_to_scan].to_numpy().flatten()

# --- BENFORD'S LAW DIGIT ALGORITHMIC FILTER ---
st.subheader("🔢 Metric 1: Benford's Law Digit Frequency Distribution")
st.markdown("""
HMRC screening algorithms use Benford's Law to analyze the frequency of leading digits in ledger transactions. 
Fabricated, over-rounded, or artificially smoothed numbers typically violate this natural curve.
""")

def execute_benfords_digit_analysis(transactions):
    """
    Computes observed vs expected leading digit frequencies to spot data fabrication anomalies.
    """
    first_digits = []
    for amt in transactions:
        # Strip signs, decimal points, and leading zeros to cleanly locate the true leading digit
        clean_str = str(abs(amt)).replace('.', '').lstrip('0')
        if clean_str and clean_str[0].isdigit():
            digit = int(clean_str[0])
            if digit != 0:
                first_digits.append(digit)
                
    if not first_digits:
        return 0.0, "🟢 PASS (Low Risk)"
        
    observed_counts = np.bincount(first_digits)[1:10]
    observed_frequencies = observed_counts / len(first_digits)
    
    # Standard statistical distribution parameters according to Benford's formula
    expected_frequencies = np.log10(1 + 1.0 / np.arange(1, 10))
    
    if len(observed_frequencies) < 9:
        observed_frequencies = np.pad(observed_frequencies, (0, 9 - len(observed_frequencies)), 'constant')
        
    # Calculate absolute total deviation variance
    total_statistical_deviation = np.sum(np.abs(observed_frequencies - expected_frequencies))
    
    risk_label = "🟢 PASS (Low Risk)" if total_statistical_deviation < 0.35 else "🔴 HIGH RISK (Anomalous Distribution)"
    return total_statistical_deviation, risk_label

deviation_score, status_result = execute_benfords_digit_analysis(live_ledger_amounts)

col_b1, col_b2 = st.columns([1, 2])
with col_b1:
    st.metric(label="Ledger Integrity Status", value=status_result)
    st.caption(f"Calculated statistical deviation factor: {deviation_score:.4f}")
with col_b2:
    if "PASS" in status_result:
        st.success("✔️ **Audit Note:** The distribution of numerical digits across the simulated 3-way ledger entries falls within normal, organic limits. There is no structural sign of manual data manipulation or synthetic rounding bias.")
    else:
        st.error("⚠️ **Audit Alarm:** First-digit frequencies deviate sharply from Benford's Law parameters. This pattern indicates an unusually high presence of rounded placeholder inputs, which frequently triggers automated tax enforcement flags.")

st.markdown("---")

# ==========================================
# 📊 4. THE LIVE PERFORMANCE VARIANCE SCREEN
# ==========================================
st.subheader("📊 Metric 2: Sub-Sector Performance Variance Guardrail")
st.markdown(f"This module cross-references your current live model forecast metrics directly with the active UK benchmark sector profile.")

# Extract the genuine financial performance from the dynamic 3-way data array
total_revenue_run = forecast_df["Turnover (£)"].sum()
total_cogs_run = forecast_df["Direct Costs (£)"].sum()
calculated_gp_margin = ((total_revenue_run - total_cogs_run) / total_revenue_run) * 100 if total_revenue_run > 0 else 0

col_v1, col_v2 = st.columns(2)
with col_v1:
    st.markdown(f"#### **Target Industry Focus**")
    st.info(f"🏢 **Active Profile:** SIC Code {sic_profile['sic_code']} — {sic_profile['industry_title']}")
    st.metric(label="Model-Calculated True Gross Profit Margin", value=f"{calculated_gp_margin:.2f}%")
    
with col_v2:
    benchmark_target_gp = sic_profile["target_gross_margin_pct"]
    variance_delta = calculated_gp_margin - benchmark_target_gp
    
    st.metric(
        label="Variance vs Standard UK Peer Average", 
        value=f"{variance_delta:+.2f}%",
        delta=f"Registry Target: {benchmark_target_gp:.1f}%"
    )
    
    # Traffic-light rule logic processing based on variance severity margins
    if abs(variance_delta) <= 5.0:
        st.success("🟢 **Low Audit Risk:** Stated forecast margins sit within a standard tolerance band of your sub-sector baseline.")
    elif abs(variance_delta) <= 15.0:
        st.warning("🟡 **Medium Risk Warning:** Gross Profit margins are uncharacteristically high or low compared to sector peers. Ensure you have clear, granular transactional proof to justify this operational run-rate during external funding due diligence.")
    else:
        st.error("🔴 **High Risk Anomaly:** Stated margin variations sit multiple standard deviations outside standard UK benchmarks. This dramatic variation is a classic indicator for automated data auditing flags inside HMRC's Connect database engine.")

st.markdown("---")
st.markdown("### 📊 Live Audit Ledger Diagnostics Chart")
st.line_chart(forecast_df[["Turnover (£)", "Net Profit (£)", "Bank Cash Position (£)"]])