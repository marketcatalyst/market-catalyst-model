# ui_skin/pages/1_📊_forecast.py
import streamlit as st
import pandas as pd
import numpy as np
import core_engine.forecast_formulas as ff

st.set_page_config(layout="wide", page_title="3-Way Financial Forecast")

st.title("📊 Primary 3-Way Integrated Forecast")
st.caption("Core Financial Reporting Layer • Live General Ledger Data Engine Matrix")
st.markdown("---")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("📊 Forecast Parameter Control")
sales_input = st.sidebar.slider("Target Monthly Revenue (£)", 10000.0, 500000.0, 100000.0, 5000.0, format="£%.2f")
gp_input = st.sidebar.slider("Target Gross Profit Margin (%)", 10.0, 100.0, 65.0, 0.5)
wages_input = st.sidebar.slider("Base Monthly Payroll / Wages (£)", 0.0, 100000.0, 8672.57, 500.0, format="£%.2f")

st.sidebar.markdown("---")
st.sidebar.subheader("⏳ Working Capital Timing")
debtor_days_input = st.sidebar.number_input("Debtor Days", 0, 120, 30, 5, key="f_debtor")
creditor_days_input = st.sidebar.number_input("Creditor Days", 0, 120, 30, 5, key="f_creditor")

# --- ENGINE CALL ---
forecast_df = ff.run_three_way_forecast(
    months=24, starting_cash=500000.0, starting_retained_earnings=500000.0,
    monthly_sales=sales_input, gross_profit_percent=gp_input, monthly_wages=wages_input,
    debtor_days=debtor_days_input, creditor_days=creditor_days_input
)
cumulative_variance = forecast_df["Variance (£)"].iloc[-1]

# --- DISPLAY ---
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("📋 Integrated Financial Ledger Outputs")
with col2:
    if abs(cumulative_variance) < 0.05:
        st.success("🟢 Model Balanced!")
    else:
        st.error(f"❌ Out of Balance! £{cumulative_variance:,.2f}")

st.dataframe(forecast_df, use_container_width=True, hide_index=True)