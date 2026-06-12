# app.py

import os
import streamlit as st
import pandas as pd
from engine.income import IncomeObject
from engine.expenditure import ExpenditureObject
from engine.ledger import MasterLedger
from database.schema import serialize_matrix_to_db

# --- 🔒 SECURITY TIER: CREDENTIAL CONFIGURATION ---
# In production, these should be securely managed via your .env file or host secrets vault.
# For local development verification, we establish rock-solid system baselines.
STRATA_ADMIN_USER = os.environ.get("STRATA_USER", "admin")
STRATA_ADMIN_PASS = os.environ.get("STRATA_PASS", "StrataCore2026!")

# Initialize authentication flag inside individual session memory frames if not present
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def render_login_screen():
    """Renders a locked login form overlay intercepting unauthorized user threads."""
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        st.subheader("🔒 STRATA Corporate Gateway")
        st.caption("Unauthorized Access Prohibited • Session Token Encrypted")
        
        with st.form("strata_login_form"):
            user_input = st.text_input("Username", autocomplete="username")
            pass_input = st.text_input("Security Access Password", type="password", autocomplete="current-password")
            
            # Form submission button utilizing native standard method and correct layout configuration
            submit_btn = st.st.form_submit_button("Authenticate Access Key", width='stretch')
            
            if submit_btn:
                if user_input == STRATA_ADMIN_USER and pass_input == STRATA_ADMIN_PASS:
                    st.session_state.authenticated = True
                    st.success("✔️ Authentication Key Validated. Initializing Engine Ledger...")
                    st.rerun()
                else:
                    st.error("❌ Access Denied: Invalid security credentials or corrupted token.")

# --- 🛰️ ROUTING LAYER GATEKEEPER ---
if not st.session_state.authenticated:
    render_login_screen()
else:
    # --- 📊 FULL APP CORE PRODUCTION ENVIRONMENT (RENDERED ONLY ON PASSWORD PASS) ---
    st.set_page_config(page_title="STRATA // 3-Way Forecasting Engine", layout="wide")

    # Header Row with active User Logged out Trigger Action Button
    header_col1, header_col2 = st.columns([0.85, 0.15])
    with header_col1:
        st.title("📊 STRATA // Integrated 3-Way Financial Matrix Engine")
        st.caption("Systems-Thinking Core Model v1.0 • Running on Neon Cloud PostgreSQL 17")
    with header_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔒 Terminate Session", width='stretch'):
            st.session_state.authenticated = False
            st.rerun()
            
    st.markdown("---")

    # --- 📁 SIDEBAR: OPERATIONAL PROFILE CONTROLLER ---
    st.sidebar.header("⚙️ Scenario Input Vector Controls")

    scenario_name = st.sidebar.text_input("Scenario Name", value="Base Case Forecast Run")
    scenario_desc = st.sidebar.text_area("Scenario Description", value="Standard operational model featuring 40-day VAT delays.")

    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 Revenue Vectors")
    monthly_sales = st.sidebar.number_input("Baseline Monthly Net Revenue (£)", min_value=0.0, value=20000.0, step=1000.0)
    debtor_lag = st.sidebar.slider("Debtor Collection Lag (Months)", min_value=0, max_value=3, value=1)

    # Invoice Finance (ID Facility Options)
    if_enabled = st.sidebar.checkbox("Engage Invoice Finance Facility", value=True)
    if_advance_rate = st.sidebar.slider("Factor Advance Rate (%)", min_value=50, max_value=95, value=85, step=5) / 100.0

    st.sidebar.markdown("---")
    st.sidebar.subheader("📉 Expenditure Vectors")
    monthly_opex = st.sidebar.number_input("Baseline Monthly Net OpEx (£)", min_value=0.0, value=8000.0, step=500.0)
    creditor_lag = st.sidebar.slider("Creditor Payment Lag (Months)", min_value=0, max_value=3, value=0)

    # --- ⚙️ CORE COMPUTATIONAL RE-COMPILATION ENGINE ---
    ledger = MasterLedger(total_timeline_months=12)

    sales_stream = IncomeObject(
        stream_name="Core Revenue", 
        baseline_monthly_net_sales=monthly_sales, 
        vat_rate=0.20, 
        cash_delay_profile={debtor_lag: 1.0}
    )

    opex_stream = ExpenditureObject(
        expense_name="Overhead Costs", 
        baseline_monthly_net_cost=monthly_opex, 
        vat_rate=0.20, 
        creditor_payment_profile={creditor_lag: 1.0}
    )

    ledger.add_income(sales_stream, invoice_finance_eligible=if_enabled, invoice_finance_advance_rate=if_advance_rate)
    ledger.add_expenditure(opex_stream)
    matrix = ledger.compile_forecast_matrix()

    # --- 💾 CLOUD BACKUP TRIGGER BUTTON ---
    if st.sidebar.button("💾 Archive Scenario Run to Neon Cloud", width='stretch'):
        try:
            if not os.environ.get("DATABASE_URL"):
                st.sidebar.error("❌ Local session variable dropped. Please run using the environment pre-load shortcut command.")
            else:
                serialize_matrix_to_db(scenario_name, scenario_desc, matrix)
                st.sidebar.success(f"✔️ Run successfully serialized to Neon!")
        except Exception as e:
            st.sidebar.error(f"❌ Cloud push failure: {str(e)}")

    # --- 📊 PRESENTATION TIER: 3-WAY FINANCIAL STATEMENTS ---
    months_index = [f"Month {i+1}" for i in range(12)]

    df_pl = pd.DataFrame({
        "Gross Revenue (£)": matrix["pl_revenue"],
        "Operating Expenses (£)": matrix["pl_expenses"],
        "Net Operating Profit (£)": [r - e for r, e in zip(matrix["pl_revenue"], matrix["pl_expenses"])]
    }, index=months_index).T

    df_cf = pd.DataFrame({
        "Operational Cash Inflows (£)": matrix["cf_inflows"],
        "Operational Cash Outflows (£)": matrix["cf_outflows"],
        "Net Monthly Cash Delta (£)": [i - o for i, o in zip(matrix["cf_inflows"], matrix["cf_outflows"])]
    }, index=months_index).T

    df_bs = pd.DataFrame({
        "Current Assets: Trade Debtors (£)": matrix["bs_debtors"],
        "Current Liabilities: Trade Creditors (£)": matrix["bs_creditors"],
        "Current Liabilities: HMRC VAT Account (£)": matrix["bs_hmrc_vat_balance"]
    }, index=months_index).T

    tab1, tab2, tab3 = st.tabs(["📉 Profit & Loss Statement", "💸 Cash Flow Statement", "⚖️ Balance Sheet Position"])

    with tab1:
        st.subheader("Profit & Loss Account (Ex VAT)")
        st.dataframe(df_pl.style.format("{:,.2f}"), width='stretch')

    with tab2:
        st.subheader("Cash Flow Timeline (Gross Receipts & Payments)")
        st.dataframe(df_cf.style.format("{:,.2f}"), width='stretch')

    with tab3:
        st.subheader("Statement of Financial Position (Rolling Balances)")
        st.dataframe(df_bs.style.format("{:,.2f}"), width='stretch')
        st.info("💡 Note the HMRC VAT Account profile: it expands through Month 4 and automatically drops back by the exact quarterly block in Month 5 via the 40-day Direct Transit delay mechanic.")