# ui_skin/pages/4_🛡️_compliance.py
import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# Ensure the app can access our core engine directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core_engine.database import get_db_connection

st.set_page_config(layout="wide", page_title="HMRC Pre-Submission Compliance Audit")

st.title("🛡️ Pre-Submission Audit & Risk Profiler")
st.caption("Algorithmic Risk Screening Engine • Simulating HMRC Connect System Data Anomaly Rules")
st.markdown("---")

st.markdown("""
### Automated Risk Analysis & Diagnostic Log
Before exporting financial models for bank lending presentations, board reviews, or HMRC filings, 
the system scans your generated datasets for statistical anomalies, rounding bias, and structural variance.
""")

# --- MOCKING DATASET ENTRIES FOR THE SCREENING DEMO ---
# In a fully wired environment, this would pull directly from your active session_state forecast arrays
sample_ledger_amounts = [
    1045.20, 189.50, 1102.00, 4500.00, 1250.00, 195.00, 240.00, 115.60, 310.00, 
    1450.00, 1800.00, 120.00, 560.00, 130.00, 175.00, 2100.00, 1150.00, 140.00
]

# --- 1. THE BENFORD'S LAW LEDGER DIGITAL SCREEN ---
st.subheader("🔢 Metric 1: Benford's Law Digit Frequency Distribution")
st.markdown("""
HMRC screening algorithms use Benford's Law to analyze the frequency of leading digits in ledger transactions. 
Fabricated, over-rounded, or artificially smoothed numbers typically violate this natural curve.
""")

def execute_benfords_digit_analysis(transactions):
    """
    Computes observed vs expected leading digit frequencies to spot data fabrication anomalies.
    """
    first_digits = [int(str(abs(amt))[0]) for amt in transactions if amt != 0]
    if not first_digits:
        return 0.0, "PASS"
        
    observed_counts = np.bincount(first_digits)[1:10]
    observed_frequencies = observed_counts / len(first_digits)
    
    # Standard statistical distribution parameters according to Benford's formula
    expected_frequencies = np.log10(1 + 1.0 / np.arange(1, 10))
    
    # Pad observed frequencies if trailing digits didn't appear in small sample size
    if len(observed_frequencies) < 9:
        observed_frequencies = np.pad(observed_frequencies, (0, 9 - len(observed_frequencies)), 'constant')
        
    # Calculate absolute total deviation variance
    total_statistical_deviation = np.sum(np.abs(observed_frequencies - expected_frequencies))
    
    risk_label = "🟢 PASS (Low Risk)" if total_statistical_deviation < 0.25 else "🔴 HIGH RISK (Anomalous Distribution)"
    return total_statistical_deviation, risk_label

deviation_score, status_result = execute_benfords_digit_analysis(sample_ledger_amounts)

col_b1, col_b2 = st.columns([1, 2])
with col_b1:
    st.metric(label="Ledger Integrity Status", value=status_result)
    st.caption(f"Calculated statistical deviation factor: {deviation_score:.4f}")
with col_b2:
    if "PASS" in status_result:
        st.success("✔️ **Audit Note:** The distribution of numerical digits in the ledger entries falls within normal, organic limits. There is no structural sign of manual data manipulation or synthetic rounding bias.")
    else:
        st.error("⚠️ **Audit Alarm:** First-digit frequencies deviate sharply from Benford's Law parameters. This pattern indicates an unusually high presence of rounded placeholder inputs, which frequently triggers automated tax enforcement flags.")

st.markdown("---")

# --- 2. THE SIC CODE BENCHMARK VARIANCE SCREEN ---
st.subheader("📊 Metric 2: Sub-Sector Performance Variance Guardrail")
st.markdown("""
This module cross-references your current forecast metrics with the standard operating baselines 
stored inside your **market-catalyst-model** project database on Neon.
""")

try:
    conn = get_db_connection()
    df_sic_lookup = pd.read_sql("SELECT sic_code, sector_name, target_gross_profit_percent FROM uk_sic_benchmarks;", conn)
    conn.close()
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        selected_code = st.selectbox("Anchor Audit SIC Code Profile", options=df_sic_lookup["sic_code"].values)
        modeled_gp_margin = st.slider("Current Forecast Model Stated Gross Profit Margin (%)", 10.0, 95.0, 72.0)
        
    with col_v2:
        benchmark_target_gp = float(df_sic_lookup[df_sic_lookup["sic_code"] == selected_code]["target_gross_profit_percent"].values[0])
        variance_delta = modeled_gp_margin - benchmark_target_gp
        
        st.metric(
            label="Variance vs Standard UK Peer Average", 
            value=f"{variance_delta:+.1f}%",
            delta=f"Database Target: {benchmark_target_gp}%"
        )
        
        # Traffic-light rule logic processing based on variance severity margins
        if abs(variance_delta) <= 5.0:
            st.success("🟢 **Low Audit Risk:** Stated forecast margins sit within a standard tollerance band of your sub-sector baseline.")
        elif abs(variance_delta) <= 15.0:
            st.warning("🟡 **Medium Risk Warning:** Gross Profit margins are uncharacteristically high or low compared to sector peers. Ensure you have clear, granular transactional proof to justify this operational run-rate during external funding due diligence.")
        else:
            st.error("🔴 **High Risk Anomaly:** Stated margin variations sit multiple standard deviations outside standard UK benchmarks. This dramatic outperformance is a classic indicator for automated data auditing flags inside HMRC's Connect database engine.")
            
except Exception:
    st.info("💡 Complete your Neon database deployment and configuration secrets to unlock live sub-sector benchmarking reviews.")