# ui_skin/pages/3_📊_forecast.py
import streamlit as st
import pandas as pd
import io
from core_engine.master_model import generate_integrated_3way_forecast

st.set_page_config(layout="wide", page_title="3-Way Financial Forecast")

st.title("📊 Primary 3-Way Integrated Forecast")
st.caption("Core Financial Reporting Layer • Professional Multi-Statement Ledger Framework")
st.markdown("---")

# --- SIDEBAR Horizon Timeline Configuration ---
st.sidebar.header("📅 Timeline Horizon Configuration")
horizon_months = st.sidebar.slider("Forecast Horizon Runway (Months)", 12, 60, 60, 12)
st.sidebar.markdown("---")

# Read global scenario tracking option from common session state
active_scenario_setting = st.session_state.get("global_strategic_scenario", "Baseline Case")
st.sidebar.info(f"Active Strategy Track: **{active_scenario_setting}**")

# --- 1. Dynamic Baseline Inputs Package Builder ---
# This page pulls default parameters to feed the central engine pass
inputs_package = {
    "target_monthly_sales": 50000.0,
    "base_monthly_gross_wages": 12000.0,
    "pension_opt_out": False,
    "direct_costs_monthly": 22000.0,
    "admin_overheads_monthly": 8000.0,
    "directors_salaries_monthly": 5000.0,
    "opening_cash_balance": 15000.0,
    "opening_retained_earnings": 15000.0,
    
    # Empty default CapEx slots to keep the background loop happy
    "planned_asset_cost": 0.0,
    "planned_asset_purchase_month_index": -1,
    "planned_asset_uel_months": 36,
    "planned_asset_residual_value": 0.0,
    "planned_asset_tax_code": "WDA_MAIN",
    "planned_asset_systemic_multiplier": 1.0
}

# Apply global macro scenario mutations automatically if switched on from Sandbox
if active_scenario_setting == "Growth Expansion Case":
    inputs_package["target_monthly_sales"] = 50000.0 * 1.15
elif active_scenario_setting == "Supply-Chain Stress Case":
    inputs_package["target_monthly_sales"] = 50000.0 * 0.80

# --- 2. Fire the Core Upgraded Master Engine ---
forecast_matrix_full = generate_integrated_3way_forecast(inputs_package)

# Slice row horizons to match user selected timeline configuration slider
forecast_df = forecast_matrix_full.iloc[:horizon_months].copy()

# ==========================================
# RENDER STATEMENT VIEWS
# ==========================================
if forecast_df is not None:
    # Read the balance sheet verification value directly from our new schema column
    cumulative_variance = forecast_df["Double_Entry_Check"].iloc[-1]
    
    col_layout_1, col_layout_2 = st.columns([3, 1])
    with col_layout_1:
        st.subheader(f"📋 Conventional Statements ({active_scenario_setting})")
    with col_layout_2:
        if abs(cumulative_variance) < 0.05:
            st.success("🟢 Model Balanced!")
        else:
            st.error(f"❌ Balance Sheet Out of Sync! £{cumulative_variance:,.2f}")
            
    st.markdown("---")
    tab_pl, tab_bs, tab_cf, tab_master = st.tabs([
        "📈 Profit & Loss (P&L)", "⚖️ Balance Sheet (BS)", "💸 Cash Flow Statement (CF)", "🗃️ Master Data Ledger Grid"
    ])
    
    def create_accounting_statement(df: pd.DataFrame, row_mapping: dict) -> pd.DataFrame:
        statement_df = df[list(row_mapping.keys())].rename(columns=row_mapping)
        statement_df.index = df["Month"]
        return statement_df.T.reset_index().rename(columns={"index": "Financial Line Item"})
        
    # --- TAB 1: PROFIT & LOSS ---
    with tab_pl:
        st.markdown(f"### **Statement of Profit or Loss ({horizon_months}-Month Runway)**")
        pl_rows = {
            "Turnover (£)": "Revenue (Turnover Summary)", 
            "Direct Costs (£)": "  Less: Operating Cost of Sales (Direct COGS)",
            "Admin Overheads (£)": "  Less: Administrative Overheads",
            "Directors Salaries (£)": "  Less: Directors' Salaries",
            "Depreciation Expense (£)": "  Less: Non-Cash Asset Impairments (Depreciation)",
            "Net Profit (£)": "Net Operating Profit / (Loss) Retained Earnings"
        }
        st.data_editor(create_accounting_statement(forecast_df, pl_rows), use_container_width=True, hide_index=True, key="pl_view_editor")

    # --- TAB 2: BALANCE SHEET ---
    with tab_bs:
        st.markdown(f"### **Statement of Financial Position ({horizon_months}-Month Snapshot)**")
        bs_rows = {
            "Fixed Asset NBV (£)": "Non-Current Assets: Fixed Assets Carrying NBV",
            "Bank Cash Position (£)": "Current Assets: Bank Liquidity Clearing Balance", 
            "Accounts Payable & Debt (£)": "Current Liabilities: Accounts Payable & Loan Obligations", 
            "Retained Earnings (£)": "Capital & Reserves: Accumulated Retained Earnings Pool"
        }
        st.data_editor(create_accounting_statement(forecast_df, bs_rows), use_container_width=True, hide_index=True, key="bs_view_editor")
        
    # --- TAB 3: CASH FLOW STATEMENT ---
    with tab_cf:
        st.markdown(f"### **Statement of Cash Flows ({horizon_months}-Month Indirect Reconciliation)**")
        st.markdown("---")
        cf_bridge_rows = {
            "Bridge: Net Profit": "Net Operating Profit / (Loss) (Accrued P&L Base)",
            "Bridge: Depreciation": "  Add Back: Non-Cash Asset Depreciation Charges",
            "Bridge: Operating CF": "👉 NET CASH FLOW FROM OPERATING ACTIVITIES",
            "Bridge: Investing CF": "📁 Net Cash Outflows for Capital Expenditures (Investing CapEx)",
            "Bridge: Financing CF": "🏦 Net Cash Flow Movements from Financing Events",
            "Bridge: Net Movement": "🎯 NET PERIODIC CASH FLOW INCREASE / (DECREASE)",
            "Bank Cash Position (£)": "💰 CLOSING LIQUID BANK CASH POSITION"
        }
        st.data_editor(create_accounting_statement(forecast_df, cf_bridge_rows), use_container_width=True, hide_index=True, key="cf_bridge_view_editor")
        
    # --- TAB 4: MASTER DATA LEDGER GRID ---
    with tab_master:
        st.markdown("### **Master Data Ledger Grid (Horizontal Time-Series Matrix View)**")
        master_transposed = forecast_df.set_index("Month").T.reset_index().rename(columns={"index": "Database Structural Field"})
        st.data_editor(master_transposed, use_container_width=True, hide_index=True, key="master_grid_editor")

    # ==========================================
    # 📥 THE STRATEGIC EXPORT PANEL
    # ==========================================
    st.markdown("---")
    st.subheader("📊 Executive Data Visualisation Suite")
    
    # Modernised Interactive Dashboard Chart Layout
    st.line_chart(forecast_df[["Turnover (£)", "Net Profit (£)", "Bank Cash Position (£)"]], y_label="Value (£)")
    
    st.markdown("---")
    st.markdown("### **📥 Downstream Document Export Gateway**")
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    
    with col_dl1:
        # Decoupled Excel Converter utility run natively inside the page memory space
        output_buffer = io.BytesIO()
        with pd.ExcelWriter(output_buffer, engine='openpyxl') as writer:
            forecast_df.to_excel(writer, sheet_name='Financial Forecast', index=False)
        xlsx_data = output_buffer.getvalue()
        
        st.download_button(
            label="📁 Download Multi-Tab Excel Workpack (.xlsx)",
            data=xlsx_data,
            file_name="market_catalyst_forecast_pack.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with col_dl2:
        csv_data = forecast_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download Raw Consolidated Data (.csv)",
            data=csv_data,
            file_name="market_catalyst_flat_ledger.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_dl3:
        st.markdown("##### **PDF Landscape Export Configuration**")
        pdf_year = st.selectbox(
            "Select Targeted Year for 12-Month Print Pack:",
            options=[1, 2, 3],
            format_func=lambda x: f"Year {x} (Months {(x-1)*12 + 1} to {x*12})",
            key="pdf_year_selector_widget"
        )
        
        import core_engine.report_generator as rg
        pdf_report_bytes = rg.compile_pdf_executive_report(
            forecast_df=forecast_df, 
            scenario_name=active_scenario_setting,
            selected_year=pdf_year
        )
        
        st.download_button(
            label=f"📋 Download Year {pdf_year} PDF Pack (.pdf)",
            data=pdf_report_bytes,
            file_name=f"AHOTG_Year_{pdf_year}_Financial_Forecast_{active_scenario_setting.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )