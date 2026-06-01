# ui_skin/home.py
import streamlit as st
import pandas as pd
import sys
import os

# This line ensures your app can see the core_engine folder upstairs
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_engine.database import get_db_connection, initialize_database_tables, seed_initial_benchmarks

# --- Page Layout Configuration ---
st.set_page_config(layout="wide", page_title="Market Catalyst Forecasting Suite")

# --- Initialize Database Connections on Startup ---
try:
    initialize_database_tables()
    seed_initial_benchmarks()
    db_status = "🟢 Connected to Neon Serverless Postgres (market-catalyst-model)"
except Exception as e:
    db_status = f"🔴 Database Connection Standby: {str(e)}"

# --- Main Dashboard Header ---
st.title("🚀 Market Catalyst Financial Forecasting Engine")
st.caption(f"Framework Status: {db_status}")
st.markdown("---")

# --- Introduction & Core Purpose Banner ---
st.markdown("""
### Welcome to the Next-Generation 3-Way Forecasting Suite
This platform is custom-built to handle complex **UK GAAP (FRS 102/105)** accounting projections—even when client historical records are completely fragmented or 'thin on the ground'. 

By decoupling your financial mathematics from this user interface screen, the core forecasting engine runs lightning-fast behind the scenes, tracking precise statutory payroll allocations, rolling 12-month short/long-term debt splits, and proactive tax-planning triggers.
""")

st.markdown("---")

# --- Sectoral Benchmarking Quick-Look Matrix ---
st.subheader("📚 Global Sectoral Benchmarking Repository")
st.markdown("""
Before starting a projection, review the standard operational averages below. These targets are pulled 
live from your isolated Neon cloud environment to help reconstruct missing client records or spot anomalies 
that could trigger automated HMRC review flags.
""")

# Fetch benchmarks from the database to show on the dashboard
try:
    conn = get_db_connection()
    query = "SELECT sic_code, sector_name, sub_sector_detail, target_gross_profit_percent, typical_debtor_days, typical_creditor_days FROM uk_sic_benchmarks;"
    df_benchmarks = pd.read_sql(query, conn)
    conn.close()
    
    # Rename columns to look highly professional on the UI grid
    df_benchmarks.columns = ["UK SIC Code", "Industry Sector", "Sub-Sector Focus", "Target GP %", "Standard Debtor Days", "Standard Creditor Days"]
    
    # Display the live table cleanly inside the Streamlit view layer
    st.data_editor(df_benchmarks, use_container_width=True, disabled=True)
    
except Exception:
    st.warning("⚠️ Baseline Benchmarks currently running on local fallback configurations. Ensure your database secrets are complete.")

# --- Workflow Guide Footnote ---
st.markdown("---")
st.subheader("🛠️ Professional Bookkeeping Workflow Navigation")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info("### 1. Ingestion\nScrape bank trial balances or map incomplete chart of accounts records cleanly.")
with col2:
    st.info("### 2. Sandbox\nApply linear regressions or sector averages to cleanly plug historical data gaps.")
with col3:
    st.info("### 3. Forecast\nAdjust unit drivers, track live payroll, and monitor dynamic debt amortization.")
with col4:
    st.info("### 4. Compliance\nRun automated Benford's Law screens and pre-submission audit risk checks.")