# ui_skin/pages/2_🔮_sandbox.py
import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# Ensure the app can access our core engine folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core_engine.database import get_db_connection

st.set_page_config(layout="wide", page_title="The Bookkeeper's Data Sandbox")

st.title("🔮 The Bookkeeper's Data Sandbox")
st.caption("Reconstruct missing ledger entries, apply sector benchmarks, and smooth timeline anomalies")
st.markdown("---")

# --- TOOL 1: THE ACCRUAL & PREPAYMENT SMOOTHER ---
st.subheader("⏱️ Tool 1: Lump-Sum Expense Smoother (Prepayments/Accruals)")
st.markdown("""
If you spot a massive, isolated overhead cash payment in the client's history that distorts their true monthly run-rate, 
use this tool to convert it into a smooth accounting prepayment.
""")

col_sm1, col_sm2, col_sm3 = st.columns(3)
with col_sm1:
    raw_payment = st.number_input("Detected Lump-Sum Cash Outflow (£)", min_value=0.0, value=12000.0, step=1000.0)
with col_sm2:
    spread_months = st.slider("Accounting Usage Horizon (Months)", min_value=3, max_value=24, value=12)
with col_sm3:
    target_overhead_line = st.text_input("Target P&L Overhead Account Line", value="Rent & Rates")

calculated_monthly_charge = raw_payment / spread_months
st.info(f"⚙️ **Engine Action:** The cash outflow remains concentrated in Month 1, but the P&L will recognize **£{calculated_monthly_charge:,.2f}** per month across Month 1 to Month {spread_months}, holding the balance safely inside the *Prepayments Asset* account.")

st.markdown("---")

# --- TOOL 2: SECTOR BENCHMARK RECONSTRUCTION ---
st.subheader("📊 Tool 2: Sector Margin Fallback (GP & Working Capital Triangulation)")
st.markdown("""
When a client has intact sales records but their cost receipts or invoicing records are fragmented, 
you can pull standard UK SIC benchmarks straight from your Neon database to back-calculate the Cost of Sales line.
""")

# Fetch our live sector codes from Neon to fill the dropdown menu
try:
    conn = get_db_connection()
    df_sic = pd.read_sql("SELECT sic_code, sector_name, target_gross_profit_percent FROM uk_sic_benchmarks;", conn)
    conn.close()
    
    sector_options = [f"{row['sic_code']} - {row['sector_name']} (Target: {row['target_gross_profit_percent']}%)" for _, row in df_sic.iterrows()]
    selected_sector_string = st.selectbox("Select Client UK SIC Sub-Sector Code", options=sector_options)
    
    # Extract the raw values based on user dropdown selection
    selected_sic = selected_sector_string.split(" - ")[0]
    target_gp_percent = float(df_sic[df_sic['sic_code'] == selected_sic]['target_gross_profit_percent'].values[0])
    implied_cos_percent = 100.0 - target_gp_percent
    
    col_recon1, col_recon2 = st.columns(2)
    with col_recon1:
        known_revenue = st.number_input("Known Monthly Revenue Baseline (£)", min_value=0.0, value=50000.0, step=5000.0)
    with col_recon2:
        st.metric(label="Inferred Cost of Sales Target", value=f"£{(known_revenue * (implied_cos_percent / 100)):,.2f}", 
                  delta=f"Based on standard {implied_cos_percent}% implied cost ratio")
        
except Exception:
    st.error("⚠️ Unable to pull live SIC parameters. Check that your Neon connection secrets are set up correctly.")

st.markdown("---")

# --- TOOL 3: STATISTICAL TREND REGRESSION ---
st.subheader("📈 Tool 3: Quantitative Trend Imputation")
st.markdown("""
Where historical quarters are missing, the sandbox runs a linear regression trend pass. 
Input the fragments of historical monthly revenue you have below, and the system will instantly calculate the growth trajectory.
""")

# Provide an editable spreadsheet for entering known historical fragments
historical_data_template = {
    "Historical Month Index": [1, 2, 3, 4, 5, 6],
    "Recorded Revenue Input (£)": [42000.0, 44500.0, np.nan, 46000.0, np.nan, 49000.0] # np.nan represents missing data points
}
df_historical = pd.DataFrame(historical_data_template)

col_reg1, col_reg2 = st.columns([1, 1])

with col_reg1:
    st.markdown("**Editable Input Fragment Grid**")
    st.caption("Leave missing months completely blank or set them to 0.")
    edited_hist_df = st.data_editor(df_historical, num_rows="dynamic", use_container_width=True)

with col_reg2:
    st.markdown("**Reconstructed Linear Trendline Output**")
    
    # Clean out missing rows or NaN items to perform our linear regression math pass
    clean_df = edited_hist_df.dropna()
    clean_df = clean_df[clean_df["Recorded Revenue Input (£)"] > 0]
    
    if len(clean_df) >= 2:
        X = clean_df["Historical Month Index"].values
        y = clean_df["Recorded Revenue Input (£)"].values
        
        # Calculate standard linear regression variables: y = mx + c
        slope, intercept = np.polyfit(X, y, 1)
        
        # Generate the complete reconstructed trend vector
        reconstructed_months = list(range(1, 7))
        reconstructed_values = [round((slope * x) + intercept, 2) for x in reconstructed_months]
        
        df_output_trend = pd.DataFrame({
            "Month": [f"Month {m}" for m in reconstructed_months],
            "Inferred Revenue Base (£)": reconstructed_values
        })
        
        st.dataframe(df_output_trend, use_container_width=True, hide_index=True)
        st.success(f"📈 Regression Match Complete! Calculated growth trajectory: **£{slope:,.2f} per month**.")
    else:
        st.warning("📥 Type at least two known historical data points in the grid to activate the trend calculation pass.")