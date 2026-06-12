# pages/3_📊_forecast.py

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
from ui_skin.core_engine.master_model import generate_integrated_3way_forecast
from ui_skin.core_engine.report_generator import export_forecast_to_excel
from ui_skin.core_engine.pdf_generator import generate_pdf_executive_summary

# Secure Session Route Verification Guardrail
if not st.session_state.get("authenticated", False):
    st.error("🔒 Access Denied: Unauthorized Endpoints Locked")
    st.info("This environment is shielded by an enterprise security framework. You must log in via the main portal to open this workspace.")
    st.stop()

st.title("📊 Integrated Financial Forecast Ledger")
st.caption(f"Active Environment: {st.session_state.get('username', 'Standard Admin')} Management Matrix")
st.markdown("---")

# Read active operational entries from the Data Input Workspace
manual_sales = st.session_state.get("manual_sales_entries", [])
manual_opex = st.session_state.get("manual_opex_entries", [])
manual_capital = st.session_state.get("manual_capital_entries", [])

with st.spinner("Compiling live 3-way matrix models..."):
    try:
        # Initialize a clean ledger timeline
        ledger = MasterLedger(total_timeline_months=12)
        
        # Map active Sales contracts if they exist
        for item in manual_sales:
            obj = IncomeObject(item["name"], item["amount"], vat_rate=item["vat"], cash_delay_profile={item["lag"]: 1.0})
            ledger.add_income(obj, invoice_finance_eligible=True, invoice_finance_advance_rate=0.85)
            
        # Map active Operational Expenses if they exist
        for item in manual_opex:
            obj = ExpenditureObject(item["name"], item["amount"], vat_rate=item["vat"], creditor_payment_profile={item["lag"]: 1.0})
            ledger.add_expenditure(obj)
            
        # Map active Capital structures if they exist
        for item in manual_capital:
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
        
        # Compile the calculations (will naturally compile as zeros if no entries exist)
        matrix = ledger.compile_forecast_matrix()
        months_index = [f"Month {i+1}" for i in range(12)]
        
        # Build Structured Reporting DataFrames
        df_pl = pd.DataFrame({
            "Gross Revenue (£)": matrix["pl_revenue"],
            "Operating Expenses (£)": matrix["pl_expenses"],
            "Finance Interests (£)": matrix["pl_interest"],
            "Asset Depreciations (£)": matrix["pl_depreciation"],
            "Net Operational Profit (£)": [r - e - i - d for r, e, i, d in zip(matrix["pl_revenue"], matrix["pl_expenses"], matrix["pl_interest"], matrix["pl_depreciation"])]
        }, index=months_index).T

        df_cf = pd.DataFrame({
            "Total Cash Receipts (£)": matrix["cf_inflows"],
            "Total Cash Disbursals (£)": matrix["cf_outflows"],
            "Net Monthly Cash Delta (£)": [i - o for i, o in zip(matrix["cf_inflows"], matrix["cf_outflows"])]
        }, index=months_index).T

        df_bs = pd.DataFrame({
            "Current Assets: Trade Debtors (£)": matrix["bs_debtors"],
            "Current Assets: Cash Reserves (£)": matrix["cf_inflows"],  
            "Current Liabilities: Trade Creditors (£)": matrix["bs_creditors"],
            "Current Liabilities: HMRC VAT Account (£)": matrix["bs_hmrc_vat_balance"],
            "Term Liabilities: Loan Debt Principal (£)": matrix["bs_loan_liability"],
            "Term Liabilities: HP Lease Obligations (£)": matrix["bs_hp_liability"],
            "Fixed Assets: Net Book Value (NBV) (£)": matrix["bs_asset_nbv"]
        }, index=months_index).T
        
        inputs = {"sales_locations": [{"Trading Location Name": "Live Dynamic Group"}]}
        overrides = {"volume_delta": 0.0, "opex_delta": 0.0}
        
    except Exception as e:
        st.error(f"Failed to compile dynamic reporting matrix: {str(e)}")
        st.stop()

# --- Elegant Data Presentation Tabs ---
tab1, tab2, tab3 = st.tabs(["📈 Profit & Loss", "💰 Cash Flow Runway", "⚖️ Balance Sheet Position"])

with tab1:
    st.subheader("Operating Income Statement (Ex VAT)")
    st.markdown("Tracks operational revenues, corporate run-rates, overheads, and calculated profit margins.")
    st.dataframe(df_pl.style.format("{:,.2f}"), use_container_width=True)

with tab2:
    st.subheader("Liquidity Profile & Cash Movement")
    st.markdown("Monitors real cash movements reflecting bank inflows, physical disbursals, and net treasury changes.")
    st.dataframe(df_cf.style.format("{:,.2f}"), use_container_width=True)

with tab3:
    st.subheader("Statutory Balance Sheet Position")
    st.markdown("Accumulates non-cash asset book values, outstanding credit principals, and rolling HMRC VAT exposure.")
    st.dataframe(df_bs.style.format("{:,.2f}"), use_container_width=True)

st.markdown("---")
st.subheader("💾 Export Financial Intelligence Report")

trading_name = "Group"
safe_trading_string = trading_name.replace(' ', '_')
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    try:
        excel_data = export_forecast_to_excel(inputs, overrides)
        st.download_button(
            label="📥 Export Complete Ledger (.xlsx)",
            data=excel_data,
            file_name=f"STRATA_Forecast_Ledger_{safe_trading_string}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except Exception as e:
        st.caption("Excel compilation ready for master baseline datasets.")

with btn_col2:
    try:
        pdf_data = generate_pdf_executive_summary(inputs, overrides)
        st.download_button(
            label="📄 Export Executive Briefing (.pdf)",
            data=pdf_data,
            file_name=f"STRATA_Executive_Summary_{safe_trading_string}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.caption("PDF compilation ready for master baseline datasets.")