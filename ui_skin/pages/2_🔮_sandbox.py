# ui_skin/pages/2_🧪_sandbox.py
import streamlit as st
import pandas as pd
import numpy as np
import core_engine.forecast_formulas as ff

st.set_page_config(layout="wide", page_title="Financial Sandbox")

st.title("🧪 Strategic Scenario Sandbox Playground")
st.caption("Isolated Risk Assessment Environment • Stress-Test Market Projections Without Changing Core Ledger Values")
st.markdown("---")

# Initialize global scenario option in session memory state
if "global_strategic_scenario" not in st.session_state:
    st.session_state.global_strategic_scenario = "Baseline Case"

st.subheader("⚙️ Select Global Forecast Strategy Path")
chosen_scenario = st.selectbox(
    "Choose active scenario track to simulate across all core statements:",
    options=["Baseline Case", "Growth Expansion Case", "Supply-Chain Stress Case"],
    index=["Baseline Case", "Growth Expansion Case", "Supply-Chain Stress Case"].index(st.session_state.global_strategic_scenario),
    key="sandbox_scenario_selector"
)

# Apply context callout boxes explaining the parameters of each scenario
if chosen_scenario == "Baseline Case":
    st.success("🟢 **Baseline Mode Active:** Mirroring your legacy WinForecast report and core multi-site rollouts exactly.")
elif chosen_scenario == "Growth Expansion Case":
    st.info("🚀 **Growth Mode Active:** Simulating a +15% surge in retail volume alongside a 5% saving on material logistics.")
elif chosen_scenario == "Supply-Chain Stress Case":
    st.warning("⚠️ **Stress-Test Mode Active:** Simulating an economic contraction that drops sales by -20% while inflating supplier costs by +10%.")

st.markdown("---")

# Sidebar configurations
st.sidebar.header("📅 Simulation Config")
sb_horizon = st.sidebar.slider("Simulation Horizon (Months)", 12, 60, 36, 12)

# Execute simulation pass
if st.button("Execute High-Speed Sandbox Simulation", use_container_width=True, type="primary"):
    st.session_state.global_strategic_scenario = chosen_scenario
    
    sandbox_df = ff.run_winforecast_replication_engine(months=sb_horizon, scenario=chosen_scenario)
    
    if sandbox_df is not None:
        st.markdown("### 📊 Scenario Trajectory Visualizations")
        chart_bytes = ff.generate_forecast_charts(sandbox_df)
        st.image(chart_bytes, caption=f"Visualized Runways for {chosen_scenario}")
        
        with st.expander("🗃️ Inspect Raw Simulation Output Ledger Data Frame", expanded=False):
            st.dataframe(sandbox_df, use_container_width=True, hide_index=True)