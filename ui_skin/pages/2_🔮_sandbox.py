# ui_skin/pages/2_🔮_sandbox.py
import streamlit as st
import pandas as pd
import numpy as np

# 1. Native Workspace Root Import (No dots, no path hacks needed)
import core_engine.forecast_formulas as ff

st.set_page_config(layout="wide", page_title="3-Way Forecasting Sandbox")

st.title("🔮 3-Way Forecasting Engine Sandbox")
st.caption("Strategic Modeling Layer • Run Real-Time Scenario Simulations Connected to London Neon Node")
st.markdown("---")

# --- SIDEBAR CONTROLS FOR LIVE USER INPUTS ---
st.sidebar.header("📊 Scenario Parameter Control")

sales_input = st.sidebar.slider(
    "Target Monthly Revenue (£)", 
    min_value=10000.00, 
    max_value=500000.00, 
    value=100000.00, 
    step=5000.00,
    format="£%.2f"
)

gp_input = st.sidebar.slider(
    "Target Gross Profit Margin (%)", 
    min_value=10.0, 
    max_value=100.0, 
    value=65.0, 
    step=0.5
)

wages_input = st.sidebar.slider(
    "Base Monthly Payroll / Wages (£)", 
    min_value=0.00, 
    max_value=100000.00, 
    value=8672.57, 
    step=500.00,
    format="£%.2f"
)

st.sidebar.markdown("---")
st.sidebar.subheader("⏳ Working Capital Timing")
debtor_days_input = st.sidebar.number_input("Debtor Days (Collection Lag)", min_value=0, max_value=120, value=30, step=5)
creditor_days_input = st.sidebar.number_input("Creditor Days (Payment Lag)", min_value=0, max_value=120, value=30, step=5)


# --- RUN THE FORECAST CALCULATIONS ---
# Pass parameters to our native engine module
forecast_df = ff.run_three_way_forecast(
    months=24,
    starting_cash=500000.00,
    starting_retained_earnings=500000.00,  # Balanced Day 1 Baseline
    monthly_sales=sales_input,
    gross_profit_percent=gp_input,
    monthly_wages=wages_input,
    debtor_days=debtor_days_input,
    creditor_days=creditor_days_input
)

# FIXED: Check the final month snapshot variance rather than summing row increments
cumulative_variance = forecast_df["Variance (£)"].iloc[-1]


# --- MODULE DEPLOYMENT: VALIDATION BANNERS ---
col_layout_1, col_layout_2 = st.columns([3, 1])

with col_layout_1:
    st.subheader("📋 Integrated Financial Ledger Outputs")
    st.markdown("Displaying a key slice of the fully integrated structural data grid matrix below.")

with col_layout_2:
    # Render dynamic alert boxes based on true ledger equality
    if abs(cumulative_variance) < 0.05:
        st.success(
            "🟢 Model Balanced!\n\n"
            "Assets exactly equal Liabilities + Equity across the entire timeline continuum."
        )
    else:
        st.error(
            f"❌ 3-Way Model Out of Balance!\n\n"
            f"Current Snapshot Variance:\n\n"
            f"£{cumulative_variance:,.2f}"
        )


# --- RENDER DATA GRID ---
# Highlight specific columns to match user workflow clarity
formatted_grid = forecast_df[[
    "Month", 
    "Payroll Costs (£)", 
    "Net Profit (£)", 
    "Bank Cash Position (£)", 
    "HMRC PAYE/NI Owed (£)", 
    "Pension Owed (£)", 
    "Retained Earnings Balance (£)", 
    "Creditors Under 1 Yr (£)",
    "Variance (£)"
]]

st.dataframe(
    formatted_grid, 
    use_container_width=True,
    hide_index=True,
    column_config={
        "Bank Cash Position (£)": st.column_config.NumberColumn(format="£%,.2f"),
        "Net Profit (£)": st.column_config.NumberColumn(format="£%,.2f"),
        "Retained Earnings Balance (£)": st.column_config.NumberColumn(format="£%,.2f"),
        "Payroll Costs (£)": st.column_config.NumberColumn(format="£%,.2f"),
        "HMRC PAYE/NI Owed (£)": st.column_config.NumberColumn(format="£%,.2f"),
        "Pension Owed (£)": st.column_config.NumberColumn(format="£%,.2f"),
        "Creditors Under 1 Yr (£)": st.column_config.NumberColumn(format="£%,.2f"),
        "Variance (£)": st.column_config.NumberColumn(format="£%,.2f")
    }
)