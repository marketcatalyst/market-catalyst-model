# pages/2_🔮_sandbox.py

import os
import sys
import streamlit as st
import pandas as pd
from pathlib import Path

# Absolute project path resolution to handle multi-page layout shifts smoothly
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from engine.income import IncomeObject
from engine.expenditure import ExpenditureObject
from engine.assets import AssetObject
from engine.finance import LoanObject, HirePurchaseObject
from engine.ledger import MasterLedger

# --- 🛡️ SECURITY BYPASS TIER ---
st.session_state["authenticated"] = True
st.session_state["username"] = "Market Catalyst"

if "manual_sales_entries" not in st.session_state:
    st.session_state.manual_sales_entries = []
if "manual_opex_entries" not in st.session_state:
    st.session_state.manual_opex_entries = []
if "manual_capital_entries" not in st.session_state:
    st.session_state.manual_capital_entries = []

st.title("🔮 Multi-Variant Scenario Sandbox")
st.caption("Systems-Thinking Scratchpad • Test Asset Deviations & High-Impact Projections")
st.markdown("---")

# --- ⚙️ VARIANT OVERRIDE SLIDERS ---
st.subheader("🎛️ Scenario Stress Testing Controls")
st.markdown("Adjust these parameters to model potential deviations against your baseline input ledger:")

col1, col2 = st.columns(2)
with col1:
    sandbox_volume_delta = st.slider("Revenue Volume Delta / Growth Spike (%)", min_value=-50, max_value=100, value=0, step=5)
    st.session_state["sandbox_volume_delta"] = sandbox_volume_delta / 100.0
with col2:
    sandbox_opex_delta = st.slider("Operational Overhead Cost Escalation (%)", min_value=-30, max_value=100, value=0, step=5)
    st.session_state["sandbox_opex_delta"] = sandbox_opex_delta / 100.0

st.markdown("---")

# --- ⚙️ MASTER MODEL SCENARIO COMPILER ---
with st.spinner("Compiling sandbox variant projections..."):
    try:
        ledger = MasterLedger(total_timeline_months=12)
        
        # FIXED: Removed the hardcoded £20k / £8k baseline buffers completely.
        # The engine will map custom data lines or evaluate naturally as clean zeros.
        for item in st.session_state.manual_sales_entries:
            adjusted_amount = item["amount"] * (1.0 + st.session_state["sandbox_volume_delta"])
            obj = IncomeObject(item["name"], adjusted_amount, vat_rate=item["vat"], cash_delay_profile={item["lag"]: 1.0})
            ledger.add_income(obj, invoice_finance_eligible=True, invoice_finance_advance_rate=0.85)
            
        for item in st.session_state.manual_opex_entries:
            adjusted_cost = item["amount"] * (1.0 + st.session_state["sandbox_opex_delta"])
            obj = ExpenditureObject(item["name"], adjusted_cost, vat_rate=item["vat"], creditor_payment_profile={item["lag"]: 1.0})
            ledger.add_expenditure(obj)
            
        for item in st.session_state.manual_capital_entries:
            t_type = item["type"]
            val = item["value"]
            m_idx = item["month"] - 1
            param = item["parameter"]
            
            if t_type == "Fixed Asset Purchase":
                ledger.add_asset(AssetObject(item["name"], val, depreciation_rate_annual=param/100.0, acquisition_month=m_idx))
            elif t_type == "Hire Purchase (HP) Agreement":
                ledger.add_hp(HirePurchaseObject(item["name"], asset_cost=val, deposit_paid=0.0, term_months=int(param), annual_interest_rate=0.08, agreement_month=m_idx))
            elif t_type == "New Bank Loan Injection":
                ledger.add_loan(LoanObject(item["name"], principal_advance=val, term_months=int(param), annual_interest_rate=0.075, advance_month=m_idx))
            elif t_type == "Director / Equity Inflow":
                ledger.inject_direct_capital_reserve(amount=val, target_month=m_idx)
                
        matrix = ledger.compile_forecast_matrix()
        
        # Format the arrays cleanly into a display dataframe
        months_index = [f"Month {i+1}" for i in range(12)]
        df_sandbox = pd.DataFrame({
            "Variant Revenue (£)": matrix["pl_revenue"],
            "Variant OpEx (£)": matrix["pl_expenses"],
            "Net Operational Profit (£)": [r - e - i - d for r, e, i, d in zip(matrix["pl_revenue"], matrix["pl_expenses"], matrix["pl_interest"], matrix["pl_depreciation"])],
            "Projected Cash Position (£)": matrix["cf_inflows"]
        }, index=months_index).T
        
        st.subheader("📊 Visualized Run-Rate Impact Matrix")
        st.dataframe(df_sandbox.style.format("{:,.2f}"), use_container_width=True)
        
    except Exception as e:
        st.error(f"Sandbox Engine compilation error: {str(e)}")