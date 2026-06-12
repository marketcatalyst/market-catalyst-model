# app.py

import os
import streamlit as st
import pandas as pd
from engine.income import IncomeObject
from engine.expenditure import ExpenditureObject
from engine.assets import AssetObject
from engine.finance import LoanObject, HirePurchaseObject
from engine.ledger import MasterLedger
from database.schema import serialize_matrix_to_db

# --- 🧠 GLOBAL STATE MEMORY INITIALISATION ---
# Placed at the absolute peak of the file context to guarantee execution parameters exist
if "manual_sales_entries" not in st.session_state:
    st.session_state.manual_sales_entries = []
if "manual_opex_entries" not in st.session_state:
    st.session_state.manual_opex_entries = []
if "manual_capital_entries" not in st.session_state:
    st.session_state.manual_capital_entries = []

# --- 🔒 SECURITY TIER: CREDENTIAL CONFIGURATION ---
STRATA_ADMIN_USER = os.environ.get("STRATA_USER", "admin")
STRATA_ADMIN_PASS = os.environ.get("STRATA_PASS", "StrataCore2026!")

# DEVELOPER SAFE PASS: Forces local session token state to bypass login friction during active builds
if "authenticated" not in st.session_state:
    st.session_state.authenticated = True

def render_login_screen():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.subheader("🔒 STRATA Corporate Gateway")
        st.caption("Unauthorised Access Prohibited • Session Token Encrypted")
        with st.form("strata_login_form"):
            user_input = st.text_input("Username", autocomplete="username")
            pass_input = st.text_input("Security Access Password", type="password", autocomplete="current-password")
            submit_btn = st.form_submit_button("Authenticate Access Key", width='stretch')
            if submit_btn:
                if user_input == STRATA_ADMIN_USER and pass_input == STRATA_ADMIN_PASS:
                    st.session_state.authenticated = True
                    st.success("✔️ Authentication Key Validated. Initializing Engine Ledger...")
                    st.rerun()
                else:
                    st.error("❌ Access Denied: Invalid credentials.")

# --- 🛰️ ROUTING LAYER GATEKEEPER ---
if not st.session_state.authenticated:
    render_login_screen()
else:
    # --- 📊 FULL APP CORE ENVIRONMENT ---
    # Top Header Layout Row with active User Logged-out Trigger
    header_col1, header_col2 = st.columns([0.85, 0.15])
    with header_col1:
        st.title("📊 STRATA // Integrated 3-Way Financial Matrix Engine")
        st.caption("Systems-Thinking Core Model v1.0 • Connected to Neon Cloud PostgreSQL 17")
    with header_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔒 Terminate Session", width='stretch'):
            st.session_state.authenticated = False
            st.rerun()
            
    st.markdown("---")

    # --- 📁 SIDEBAR: GLOBAL RUN PARAMS ---
    st.sidebar.header("📁 Active Scenario Runway")
    scenario_name = st.sidebar.text_input("Scenario Reference Name", value="Base Case Forecast Run")
    scenario_desc = st.sidebar.text_area("Scenario Notes / Description", value="Standard operational model with structural adjustments.")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🛡️ Factoring / Invoice Finance")
    if_enabled = st.sidebar.checkbox("Engage Invoice Finance (ID Facility)", value=True)
    if_advance_rate = st.sidebar.slider("Factor Advance Rate (%)", min_value=50, max_value=95, value=85, step=5) / 100.0

    # --- 🏗️ CENTRAL OPERATIONS WORKSPACE PANEL GRID ---
    panel_col1, panel_col2 = st.columns([0.55, 0.45])

    with panel_col1:
        st.subheader("📥 Step 1: Ingestion & Transaction Desks")
        
        ingest_tab1, ingest_tab2, ingest_tab3 = st.tabs([
            "📂 Automated Payload Ingestion", 
            "✍️ Manual Operational Entries",
            "🏦 Capital & Financing Desk"
        ])
        
        with ingest_tab1:
            uploaded_files = st.file_uploader(
                "Drop Corporate Document Payload", accept_multiple_files=True, label_visibility="collapsed"
            )
            status_col1, status_col2 = st.columns(2)
            status_col1.metric("Ingested Items", value=len(uploaded_files) if uploaded_files else 0)
            status_col2.metric("Pipeline Engine", value="Idle" if not uploaded_files else "Ready to Parse")
            
        with ingest_tab2:
            st.caption("Inject customised operational income/expenditure lines into current run memory:")
            op_book = st.selectbox("Operational Target Book", ["📈 Sales Revenue Invoices", "📉 Operational OpEx Bill / Cost"])
            
            with st.form("manual_op_form", clear_on_submit=True):
                col_a, col_b = st.columns(2)
                op_name = col_a.text_input("Item Description", placeholder="e.g. Project Phase A Delivery")
                op_amount = col_b.number_input("Monthly Net Amount (£)", min_value=0.0, value=1000.0, step=500.0)
                
                col_c, col_d = st.columns(2)
                op_lag = col_c.slider("Credit Timing Delay (Months)", min_value=0, max_value=3, value=0)
                op_vat = col_d.selectbox("VAT Setting", ["Standard Rate (20%)", "Zero Rated (0%)"])
                
                if st.form_submit_button("➕ Commit Operational Line to Memory", width='stretch'):
                    vat_computed = 0.20 if "20%" in op_vat else 0.00
                    new_op = {"name": op_name if op_name else "Manual Op Line", "amount": op_amount, "lag": op_lag, "vat": vat_computed}
                    if "Sales" in op_book:
                        st.session_state.manual_sales_entries.append(new_op)
                    else:
                        st.session_state.manual_opex_entries.append(new_op)
                    st.toast("Operational entry logged.")
            
        with ingest_tab3:
            st.caption("Key in high-impact capitalisation events, funding injections, or long-term debt additions:")
            cap_type = st.selectbox("Capital Transaction Class", ["Fixed Asset Purchase", "Hire Purchase (HP) Agreement", "New Bank Loan Injection", "Director / Equity Inflow"])
            
            with st.form("manual_capital_form", clear_on_submit=True):
                col_x, col_y = st.columns(2)
                cap_name = col_x.text_input("Facility / Asset Name", placeholder="e.g. CNC Mill Machine, Lloyds Bank Tranche")
                cap_value = col_y.number_input("Principal / Purchase Value (£)", min_value=0.0, value=10000.0, step=1000.0)
                
                col_w, col_z = st.columns(2)
                cap_month = col_w.number_input("Execution Event Month (1-12)", min_value=1, max_value=12, value=1)
                cap_param = col_z.number_input("Term (Months) / Depreciation Rate (%)", min_value=0.0, value=12.0, step=1.0)
                
                if st.form_submit_button("🏛️ Inject Structural Event to Ledger", width='stretch'):
                    new_cap = {"type": cap_type, "name": cap_name if cap_name else f"Manual {cap_type}", "value": cap_value, "month": int(cap_month), "parameter": cap_param}
                    st.session_state.manual_capital_entries.append(new_cap)
                    st.toast("Capital adjustments captured successfully.")
            
            if st.button("🗑️ Reset All Local Custom Memory Entries", width='content'):
                st.session_state.manual_sales_entries = []
                st.session_state.manual_opex_entries = []
                st.session_state.manual_capital_entries = []
                st.rerun()

    with panel_col2:
        st.subheader("⚙️ Step 2: Global Adjustments & Queue Balance")
        with st.container(border=True):
            monthly_wages = st.number_input("Monthly Gross Staff Wages (£)", min_value=0.0, value=0.0, step=500.0)
            auto_enrol_opt_out = st.checkbox("Statutory Auto-Enrolment Opt-Out", value=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("📋 Active Pipeline Queue Diagnostic Inventory:")
        st.text(f"• Sales Invoices in Queue: {len(st.session_state.manual_sales_entries)}")
        st.text(f"• OpEx Expenditures in Queue: {len(st.session_state.manual_opex_entries)}")
        st.text(f"• Financing & Asset Structures in Queue: {len(st.session_state.manual_capital_entries)}")

    st.markdown("---")

    # --- ⚙️ MASTER MODEL CALCULATION MATRIX COMPILER ---
    ledger = MasterLedger(total_timeline_months=12)

    # 1. Processing Sales Invoices
    if not st.session_state.manual_sales_entries:
        ledger.add_income(IncomeObject("Baseline Revenue Stream", 20000.0, vat_rate=0.20, cash_delay_profile={1: 1.0}), invoice_finance_eligible=if_enabled, invoice_finance_advance_rate=if_advance_rate)
    else:
        for item in st.session_state.manual_sales_entries:
            ledger.add_income(IncomeObject(item["name"], item["amount"], vat_rate=item["vat"], cash_delay_profile={item["lag"]: 1.0}), invoice_finance_eligible=if_enabled, invoice_finance_advance_rate=if_advance_rate)

    # 2. Processing OpEx Lines
    if not st.session_state.manual_opex_entries:
        ledger.add_expenditure(ExpenditureObject("Baseline OpEx Overheads", 8000.0, vat_rate=0.20, creditor_payment_profile={0: 1.0}))
    else:
        for item in st.session_state.manual_opex_entries:
            ledger.add_expenditure(ExpenditureObject(item["name"], item["amount"], vat_rate=item["vat"], creditor_payment_profile={item["lag"]: 1.0}))

    # 3. Processing Structural Capital Adjustments Matrix
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

    # --- 📊 PRESENTATION TIER: 3-WAY FINANCIAL STATEMENTS CONTAINER ---
    st.subheader("📊 Compiled 3-Way Integrated Financial Runway")
    months_index = [f"Month {i+1}" for i in range(12)]

    df_pl = pd.DataFrame({
        "Gross Revenue (£)": matrix["pl_revenue"],
        "Operating Expenses (£)": matrix["pl_expenses"],
        "Finance Interests (£)": matrix["pl_interest"],
        "Asset Depreciations (£)": matrix["pl_depreciation"],
        "Net Operational Profit (£)": [r - e - i - d for r, e, i, d in zip(matrix["pl_revenue"], matrix["pl_expenses"], matrix["pl_interest"], matrix["pl_depreciation"])]
    }, index=months_index).T

    df_cf = pd.DataFrame({
        "Total Cash Receipts / Inflows (£)": matrix["cf_inflows"],
        "Total Cash Disbursals / Outflows (£)": matrix["cf_outflows"],
        "Net Monthly Cash Delta (£)": [i - o for i, o in zip(matrix["cf_inflows"], matrix["cf_outflows"])]
    }, index=months_index).T

    df_bs = pd.DataFrame({
        "Current Assets: Trade Debtors (£)": matrix["bs_debtors"],
        "Current Liabilities: Trade Creditors (£)": matrix["bs_creditors"],
        "Current Liabilities: HMRC VAT Account (£)": matrix["bs_hmrc_vat_balance"],
        "Term Liabilities: Loan Amortization (£)": matrix["bs_loan_liability"],
        "Term Liabilities: HP Obligations (£)": matrix["bs_hp_liability"],
        "Fixed Assets: Net Book Value Asset NBV (£)": matrix["bs_asset_nbv"]
    }, index=months_index).T

    tab1, tab2, tab3 = st.tabs(["📉 Profit & Loss Statement", "💸 Cash Flow Statement", "⚖️ Balance Sheet Position"])
    with tab1: st.dataframe(df_pl.style.format("{:,.2f}"), width='stretch')
    with tab2: st.dataframe(df_cf.style.format("{:,.2f}"), width='stretch')
    with tab3: st.dataframe(df_bs.style.format("{:,.2f}"), width='stretch')

    # Secure Cloud Serialization Trigger Row
    st.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button("💾 Archive Scenario Run to Neon Cloud", width='stretch'):
        try:
            if not os.environ.get("DATABASE_URL"):
                st.sidebar.error("❌ Database session context lost.")
            else:
                serialize_matrix_to_db(scenario_name, scenario_desc, matrix)
                st.sidebar.success(f"✔️ Run successfully serialized to Neon!")
        except Exception as e:
            st.sidebar.error(f"❌ Cloud push failure: {str(e)}")