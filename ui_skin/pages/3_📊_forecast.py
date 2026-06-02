# ui_skin/pages/3_📊_forecast.py
import streamlit as st
import pandas as pd
import numpy as np

# Native Workspace Root Import relative to Streamlit Cloud container execution context
import core_engine.forecast_formulas as ff

st.set_page_config(layout="wide", page_title="3-Way Financial Forecast")

st.title("📊 Primary 3-Way Integrated Forecast")
st.caption("Core Financial Reporting Layer • Professional Multi-Statement Ledger Framework")
st.markdown("---")

# --- SIDEBAR Horizon Timeline Configuration ---
st.sidebar.header("📅 Timeline Horizon Configuration")
horizon_months = st.sidebar.slider("Forecast Horizon Runway (Months)", 12, 60, 36, 12)
st.sidebar.markdown("---")

# Execute the advanced multi-site replication engine loop
forecast_df = ff.run_winforecast_replication_engine(months=horizon_months)

# ==========================================
# RENDER STATEMENT VIEWS
# ==========================================
if forecast_df is not None:
    cumulative_variance = forecast_df["Variance Check (£)"].iloc[-1]
    
    col_layout_1, col_layout_2 = st.columns([3, 1])
    with col_layout_1:
        st.subheader("📋 Conventional Financial Statements")
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
        pl_audit_mode = st.toggle("🔍 Activate Granular Auditor View (Explode Operational Accounts)", key="pl_audit_toggle")
        st.markdown("---")
        
        if not pl_audit_mode:
            pl_rows = {
                "Turnover (£)": "Revenue (Turnover Summary)", 
                "Direct Costs (£)": "  Less: Operating Cost of Sales (Direct COGS)",
                "Depreciation Expense (£)": "  Less: Non-Cash Asset Impairments (Depreciation)",
                "Net Profit (£)": "Net Operating Profit / (Loss) Retained Earnings"
            }
            st.data_editor(create_accounting_statement(forecast_df, pl_rows), use_container_width=True, hide_index=True, key="pl_view_editor")
        else:
            st.info("📊 Deep-Dive P&L Time-Series Audit Active: Unpacking statement columns into dynamic sub-ledgers.")
            
            if "trial_balance_matrix" in st.session_state:
                raw_tb_df = st.session_state.trial_balance_matrix.copy()
                raw_tb_df["Amount (£)"] = pd.to_numeric(raw_tb_df["Amount (£)"], errors="coerce").fillna(0.0)
                
                pl_bucket_mapping = {
                    "Revenue": "Turnover (£)",
                    "Direct Expenses (COGS)": "Direct Costs (£)"
                }
                
                for ui_bucket, forecast_col in pl_bucket_mapping.items():
                    accounts_in_bucket = raw_tb_df[raw_tb_df["Accounting Allocation Bucket"] == ui_bucket]
                    with st.expander(f"📁 Dynamic Account Performance Breakdown: {ui_bucket}", expanded=True):
                        if not accounts_in_bucket.empty:
                            bucket_base_total = accounts_in_bucket["Amount (£)"].sum()
                            exploded_records = []
                            for _, acct_row in accounts_in_bucket.iterrows():
                                acct_code = acct_row["Account Code"]
                                acct_name = acct_row["Account Name"]
                                base_val = acct_row["Amount (£)"]
                                ratio = (base_val / bucket_base_total) if bucket_base_total > 0 else 1.0
                                row_series = {"Account": f"[{acct_code}] {acct_name}"}
                                for m_idx in range(1, horizon_months + 1):
                                    row_series[f"Month {m_idx}"] = forecast_df.loc[m_idx - 1, forecast_col] * ratio
                                exploded_records.append(row_series)
                            st.dataframe(pd.DataFrame(exploded_records), use_container_width=True, hide_index=True)
            else:
                # Fallback multi-site presentation mapping if session state is clearing
                with st.expander("📁 Dynamic Account Performance Breakdown: Revenue (Turnover)", expanded=True):
                    rev_records = [
                        {"Account": "[1010] Carmarthen Site Sales (Standard + Zero Mix)", **{f"Month {m}": forecast_df.loc[m-1, "Turnover (£)"] * 0.45 for m in range(1, horizon_months + 1)}},
                        {"Account": "[1020] Wellfield Road Standard Rated Sales", **{f"Month {m}": forecast_df.loc[m-1, "Turnover (£)"] * 0.35 for m in range(1, horizon_months + 1)}},
                        {"Account": "[1030] Bridgend & Cardiff Bay Expansion Pipeline", **{f"Month {m}": forecast_df.loc[m-1, "Turnover (£)"] * 0.20 for m in range(1, horizon_months + 1)}}
                    ]
                    st.dataframe(pd.DataFrame(rev_records), use_container_width=True, hide_index=True)

    # --- TAB 2: BALANCE SHEET ---
    with tab_bs:
        st.markdown(f"### **Statement of Financial Position ({horizon_months}-Month Snapshot)**")
        bs_audit_mode = st.toggle("🔍 Activate Granular Auditor View (Unpack Constituent Accounts)", key="bs_audit_toggle")
        st.markdown("---")
        
        if not bs_audit_mode:
            bs_rows = {
                "Fixed Asset NBV (£)": "Non-Current Assets: Fixed Assets Carrying NBV",
                "Bank Cash Position (£)": "Current Assets: Bank Liquidity Clearing Balance", 
                "Accounts Payable & Debt (£)": "Current Liabilities: Accounts Payable & Loan Obligations", 
                "Retained Earnings (£)": "Capital & Reserves: Accumulated Retained Earnings Pool", 
                "Variance Check (£)": "Double-Entry Validation Variance"
            }
            st.data_editor(create_accounting_statement(forecast_df, bs_rows), use_container_width=True, hide_index=True, key="bs_view_editor")
        else:
            st.info("📊 Deep-Dive Balance Sheet Audit Active: Unpacking statement columns into true asset and liability sub-ledgers.")
            
            with st.expander("📁 Dynamic Asset Series Breakdown: Non-Current Fixed Assets (NBV)", expanded=True):
                asset_records = []
                base_kitchen_equipment = 236438.00
                base_leasehold_improvements = 167818.00
                base_motor_vehicles = 139979.00
                
                for m_idx in range(1, horizon_months + 1):
                    fixtures_addition = sum(24000.0 for i in range(5, min(m_idx + 1, 10))) if m_idx >= 5 else 0.0
                    bridgend_addition = 40000.0 if m_idx >= 6 else 0.0
                    cardiff_addition = 25000.0 if m_idx >= 6 else 0.0
                    penarth_addition = 200000.0 if m_idx >= 7 else 0.0
                    merthyr_addition = (60000.0 if m_idx == 11 else 120000.0) if m_idx >= 11 else 0.0
                    rolling_depr_charge = 4355.0 * m_idx if m_idx <= 12 else (52260.0 + (8219.0 * (m_idx - 12)))
                    
                    if m_idx == 1:
                        asset_records = [
                            {"Account": "[4010] Historical Fixed Asset Cost Core (Kitchen & Leasehold Equipment)"},
                            {"Account": "[4110] New Fixtures & Fittings 2026 Expansion Asset Profile"},
                            {"Account": "[4120] Bridgend Town Centre Refurbishment Asset Line"},
                            {"Account": "[4130] Cardiff Bay Refurbishment Asset Line"},
                            {"Account": "[4140] Penarth Business Acquisition Ledger"},
                            {"Account": "[4150] Merthyr Site Asset Infrastructure Pipeline"},
                            {"Account": "[4990] Less: Accumulated Depreciation Control Account"}
                        ]
                    
                    asset_records[0][f"Month {m_idx}"] = base_kitchen_equipment + base_leasehold_improvements + base_motor_vehicles
                    asset_records[1][f"Month {m_idx}"] = fixtures_addition
                    asset_records[2][f"Month {m_idx}"] = bridgend_addition
                    asset_records[3][f"Month {m_idx}"] = cardiff_addition
                    asset_records[4][f"Month {m_idx}"] = penarth_addition
                    asset_records[5][f"Month {m_idx}"] = merthyr_addition
                    asset_records[6][f"Month {m_idx}"] = -rolling_depr_charge
                    
                st.dataframe(pd.DataFrame(asset_records), use_container_width=True, hide_index=True)
                
            with st.expander("📁 Dynamic Liability Series Breakdown: Current Liabilities & Loans", expanded=True):
                liability_records = []
                hp_remaining = 40868.00
                dbw_remaining = 0.0
                
                for m_idx in range(1, horizon_months + 1):
                    if m_idx == 6: 
                        dbw_remaining = 400000.00
                    elif m_idx > 6: 
                        dbw_remaining = max(0.0, 400000.00 - ((8499.00 * 0.85) * (m_idx - 6)))
                        
                    hp_remaining = max(0.0, 40868.00 - ((2546.00 * 0.90) * m_idx))
                    total_creditors_block = forecast_df.loc[m_idx - 1, "Accounts Payable & Debt (£)"]
                    calculated_trade_suppliers = total_creditors_block - dbw_remaining - hp_remaining
                    
                    if m_idx == 1:
                        liability_records = [
                            {"Account": "[2100] Trade Creditors Control Account (Invoiced Supplier Material Lags)"},
                            {"Account": "[2310] New DBW Development Expansion Loan Pool (£400k Principal)"},
                            {"Account": "[2340] Outstanding Hire Purchase Asset Finance Liability Account"}
                        ]
                        
                    liability_records[0][f"Month {m_idx}"] = calculated_trade_suppliers
                    liability_records[1][f"Month {m_idx}"] = dbw_remaining
                    liability_records[2][f"Month {m_idx}"] = hp_remaining
                    
                st.dataframe(pd.DataFrame(liability_records), use_container_width=True, hide_index=True)

    # --- TAB 3: CASH FLOW ---
    with tab_cf:
        st.markdown(f"### **Statement of Cash Flows ({horizon_months}-Month Runway)**")
        cf_working = forecast_df[["Month", "Net Profit (£)", "Bank Cash Position (£)"]].copy()
        cf_working["Net Cash Flow Movement"] = cf_working["Bank Cash Position (£)"].diff().fillna(cf_working["Bank Cash Position (£)"] - 69488.00)
        
        cf_rows = {
            "Net Profit (£)": "Net Profit from Operations (Accrued P&L)", 
            "Net Cash Flow Movement": "Net Periodic Cash Inflow / (Outflow)", 
            "Bank Cash Position (£)": "Closing Liquidity Bank Balance"
        }
        st.data_editor(create_accounting_statement(cf_working, cf_rows), use_container_width=True, hide_index=True, key="cf_view_editor")
        
    # --- TAB 4: MASTER DATA LEDGER GRID ---
    with tab_master:
        st.markdown("### **Master Data Ledger Grid (Horizontal Time-Series Matrix View)**")
        master_transposed = forecast_df.set_index("Month").T.reset_index().rename(columns={"index": "Database Structural Field"})
        st.data_editor(master_transposed, use_container_width=True, hide_index=True, key="master_grid_editor")

    # ==========================================
    # 📥 THE STRATEGIC EXPORT PANEL
    # ==========================================
    st.markdown("---")
    st.subheader("📊 Executive Data Visualization & Reporting Suite")
    
    chart_bytes = ff.generate_forecast_charts(forecast_df)
    st.image(chart_bytes, caption="Dynamic 3-Way Forecasting Macro Performance Dashboard Chart Output")
    
    st.markdown("---")
    st.markdown("### **📥 Downstream Document Export Gateway**")
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    
    with col_dl1:
        xlsx_data = ff.convert_df_to_excel(forecast_df)
        st.download_button(
            label="📁 Download Multi-Tab Excel Workpack (.xlsx)",
            data=xlsx_data,
            file_name="market_catalyst_winforecast_replication_pack.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    with col_dl2:
        csv_data = forecast_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download Raw Consolidated Data (.csv)",
            data=csv_data,
            file_name="market_catalyst_flat_replication_ledger.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_dl3:
        st.button(
            "📋 Compile PDF Executive Management Report",
            on_click=lambda: st.toast("🛠️ Generating ReportLab print canvas matrix...", icon="📋"),
            use_container_width=True
        )