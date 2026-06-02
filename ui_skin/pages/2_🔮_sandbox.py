# ui_skin/pages/2_🧪_sandbox.py
import streamlit as st
import pandas as pd
import numpy as np

# Native Workspace Root Import relative to Streamlit Cloud container execution context
import core_engine.forecast_formulas as ff

st.set_page_config(layout="wide", page_title="Financial Sandbox")

st.title("🧪 Financial Sandbox & Scenario Playground")
st.caption("Isolated Simulation Environment • Stress-Test Assumptions Without Affecting Production Ledgers")
st.markdown("---")

# ==========================================
# 📊 1. THE SANDBOX TRIAL BALANCE SCRATCHPAD
# ==========================================
st.subheader("📋 Sandbox Trial Balance Scratchpad")
st.markdown("Modify these baseline starting account pools to mock up an entirely alternative starting business profile:")

# Initialize a separate sandbox-isolated trial balance so it doesn't overwrite live ingestion data
if "sandbox_tb_matrix" not in st.session_state:
    st.session_state.sandbox_tb_matrix = pd.DataFrame({
        "Account Code": ["1000", "5000", "7000", "7100"],
        "Account Name": ["General Sales Revenue Pool", "Direct Cost of Sales (COGS)", "Gross Staff Wages Ledger", "Indirect Operational Overheads (OpEx)"],
        "Accounting Allocation Bucket": ["Revenue", "Direct Expenses (COGS)", "Gross Wages", "Indirect Overheads (OpEx)"],
        "Base Monthly Amount (£)": [120000.00, 42000.00, 15000.00, 18000.00]
    })

edited_sandbox_tb = st.data_editor(
    st.session_state.sandbox_tb_matrix,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Account Code": st.column_config.TextColumn("Account Code", disabled=True),
        "Account Name": st.column_config.TextColumn("Account Description Name", disabled=True),
        "Accounting Allocation Bucket": st.column_config.TextColumn("Ledger Target Allocation", disabled=True),
        "Base Monthly Amount (£)": st.column_config.NumberColumn("Scratchpad Base Value (£)", format="£%,.2f", min_value=0.00)
    },
    key="sandbox_tb_grid_editor"
)

st.markdown("---")

# ==========================================
# 🎛️ 2. THE DYNAMIC OPERATION OVERRIDE SLIDERS
# ==========================================
st.subheader("🎛️ Operational Stress-Testing Sliders")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### **📈 Revenue & Cost Scalers**")
    sb_sales = st.slider("Simulated Base Monthly Revenue (£)", 10000.0, 500000.0, float(edited_sandbox_tb.iloc[0]["Base Monthly Amount (£)"]), 5000.0, format="£%.2f")
    sb_cogs_val = float(edited_sandbox_tb.iloc[1]["Base Monthly Amount (£)"])
    sb_calculated_gp = ((sb_sales - sb_cogs_val) / sb_sales * 100.0) if sb_sales > 0 else 65.0
    sb_gp_margin = st.slider("Simulated Gross Profit Margin (%)", 10.0, 100.0, float(sb_calculated_gp), 0.5)
    sb_opex = st.slider("Simulated Base Operating Overheads (£)", 0.0, 100000.0, float(edited_sandbox_tb.iloc[3]["Base Monthly Amount (£)"]), 1000.0, format="£%.2f")
    sb_wages = st.slider("Simulated Base Gross Payroll Costs (£)", 0.0, 100000.0, float(edited_sandbox_tb.iloc[2]["Base Monthly Amount (£)"]), 500.0, format="£%.2f")

with col_right:
    st.markdown("### **⏳ Working Capital Credit Timing Lags**")
    sb_debtor_days = st.number_input("Simulated Debtor Collection Days (Asset Lag)", 0, 120, 30, 5)
    sb_creditor_days = st.number_input("Simulated Creditor Payment Days (Liability Lag)", 0, 120, 45, 5)
    
    st.markdown("### **📅 Forecast Horizon Extension**")
    sb_horizon = st.slider("Simulation Runway Window (Months)", 12, 60, 36, 12, key="sb_horizon_slider")

st.markdown("---")

# ==========================================
# 🚀 3. RUNNING THE SANDBOX GRAPH ENGINE
# ==========================================
if st.button("Execute High-Speed Sandbox Simulation", use_container_width=True, type="primary"):
    st.session_state.sandbox_tb_matrix = edited_sandbox_tb
    
    # Generate the projection dataframe by feeding our sandbox parameters into our multi-statement engine logic
    sandbox_df = ff.run_three_way_forecast(
        months=sb_horizon,
        starting_cash=250000.00,  # Controlled sandbox starting cash position
        starting_retained_earnings=250000.00,
        monthly_sales=sb_sales,
        opex_input=sb_opex,
        gross_profit_percent=sb_gp_margin,
        monthly_wages=sb_wages,
        debtor_days=sb_debtor_days,
        creditor_days=sb_creditor_days
    )
    
    if sandbox_df is not None:
        st.success("🎯 Simulation calculation pass complete! Review the resulting trajectory profiles below:")
        
        # Display high-level visual charts
        chart_bytes = ff.generate_forecast_charts(sandbox_df)
        st.image(chart_bytes, caption="Sandbox Scenario Trajectory Outputs")
        
        # Display a quick flat data ledger view
        with st.expander("🗃️ Inspect Raw Simulation Output Ledger Data Frame", expanded=False):
            st.dataframe(sandbox_df, use_container_width=True, hide_index=True)