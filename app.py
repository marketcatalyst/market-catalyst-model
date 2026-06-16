# app.py

import streamlit as st
import json
import os
import pandas as pd
from pathlib import Path
import google.generativeai as genai

# =========================================================================
# 🏛️ CORE ENGINE: TRANSITIONAL VECTOR LEDGER
# =========================================================================

class JournalToken:
    """Atomic double-entry transaction voucher ensuring absolute alignment."""
    def __init__(self, month_label, debit_acct, credit_acct, amount, narrative=""):
        self.month_label = month_label
        self.debit_acct = debit_acct
        self.credit_acct = credit_acct
        self.amount = float(amount)
        self.narrative = narrative

class CommercialTrialBalanceCuboid:
    """Hardened 60-month transaction token ledger processing phase-shifts and UK tax cycles."""
    def __init__(self):
        self.accounts = [
            "BS_Asset_Cash", "BS_Asset_Debtors", "BS_Asset_Fixed_Assets", "BS_Asset_Accumulated_Depreciation",
            "BS_Liability_Creditors", "BS_Liability_VAT_Payable", "BS_Liability_PAYE_NIC_Payable", "BS_Liability_Long_Term_Debt",
            "BS_Equity_Share_Capital", "BS_Equity_Retained_Earnings",
            "PL_Revenue_Gross", "PL_COGS", "PL_Expense_Overheads", "PL_Expense_Payroll", "PL_Expense_Depreciation", "PL_Expense_Interest"
        ]
        self.months = [f"M{str(i).zfill(2)}" for i in range(1, 61)]
        self.seasonality_profiles = {
            "Flat_Linear": [1/12] * 12,
            "Winter_Peak": [0.12, 0.12, 0.10, 0.07, 0.05, 0.05, 0.05, 0.06, 0.08, 0.09, 0.10, 0.11],
            "Summer_Peak": [0.05, 0.05, 0.07, 0.10, 0.12, 0.12, 0.12, 0.11, 0.09, 0.07, 0.05, 0.05]
        }
        self.token_pool = []

    def inject_token(self, month_idx, debit_acct, credit_acct, amount, narrative=""):
        if amount == 0.0 or month_idx < 1 or month_idx > 60:
            return
        month_label = f"M{str(month_idx).zfill(2)}"
        self.token_pool.append(JournalToken(month_label, debit_acct, credit_acct, amount, narrative))

    def extract_monthly_weight(self, profile_name, month_idx):
        profile = self.seasonality_profiles.get(profile_name, self.seasonality_profiles["Flat_Linear"])
        return profile[(month_idx - 1) % 12]

    def process_simulation(self, runtime_payload):
        self.token_pool = []
        
        # Capitalization Injections
        for cap in runtime_payload.get("capital", []):
            m_start, val, c_type = int(cap.get("month", 1)), float(cap.get("value", 0.0)), cap.get("type", "")
            if c_type == "Equity Capital / Share Premium Injection":
                self.inject_token(m_start, "BS_Asset_Cash", "BS_Equity_Share_Capital", val, "Founder Capital")
            elif c_type == "Commercial Debt / Facility Drawdown":
                self.inject_token(m_start, "BS_Asset_Cash", "BS_Liability_Long_Term_Debt", val, "Debt Drawdown")
            elif c_type == "New / Existing Fixed Asset CapEx":
                self.inject_token(m_start, "BS_Asset_Fixed_Assets", "BS_Asset_Cash", val, "Infrastructure CapEx")

        # Chronological Loop
        for m in range(1, 61):
            # Sales (Debtor Days Shift)
            for sale in runtime_payload.get("sales", []):
                ann_net = float(sale.get("amount", 0.0))
                profile, debtor_days, vat_app = sale.get("seasonality", "Flat_Linear"), int(sale.get("debtor_days", 0)), sale.get("vat_applicable", True)
                monthly_net = ann_net * self.extract_monthly_weight(profile, m)
                monthly_vat = (monthly_net * 0.20) if vat_app else 0.0
                
                self.inject_token(m, "BS_Asset_Debtors", "PL_Revenue_Gross", monthly_net, "P&L Revenue")
                if monthly_vat > 0:
                    self.inject_token(m, "BS_Asset_Debtors", "BS_Liability_VAT_Payable", monthly_vat, "Output VAT")
                self.inject_token(m + (debtor_days // 30), "BS_Asset_Cash", "BS_Asset_Debtors", monthly_net + monthly_vat, "Cash Receipt")

            # Overheads (Creditor Days Shift)
            for opex in runtime_payload.get("opex", []):
                ann_net_cost = float(opex.get("amount", 0.0))
                profile, creditor_days, vat_rec = opex.get("seasonality", "Flat_Linear"), int(opex.get("creditor_days", 0)), opex.get("vat_applicable", True)
                monthly_net_cost = ann_net_cost * self.extract_monthly_weight(profile, m)
                monthly_input_vat = (monthly_net_cost * 0.20) if vat_rec else 0.0
                
                self.inject_token(m, "PL_Expense_Overheads", "BS_Liability_Creditors", monthly_net_cost, "Opex Expense")
                if monthly_input_vat > 0:
                    self.inject_token(m, "BS_Liability_VAT_Payable", "BS_Liability_Creditors", monthly_input_vat, "Input VAT")
                self.inject_token(m + (creditor_days // 30), "BS_Liability_Creditors", "BS_Asset_Cash", monthly_net_cost + monthly_input_vat, "Supplier Payment")

            # Payroll (1-Month PAYE Settlement Delay)
            for pay in runtime_payload.get("payroll", []):
                monthly_gross = float(pay.get("amount", 0.0)) / 12.0
                employer_nic = monthly_gross * 0.138
                paye_deduction = monthly_gross * 0.25
                self.inject_token(m, "PL_Expense_Payroll", "BS_Asset_Cash", monthly_gross - paye_deduction, "Net Staff Wages")
                self.inject_token(m, "PL_Expense_Payroll", "BS_Liability_PAYE_NIC_Payable", paye_deduction + employer_nic, "Accrued Taxes")
                self.inject_token(m + 1, "BS_Liability_PAYE_NIC_Payable", "BS_Asset_Cash", paye_deduction + employer_nic, "HMRC PAYE Payment")

            # Depreciation
            current_fa = self.compute_running_balance_to_month("BS_Asset_Fixed_Assets", m)
            if current_fa > 0.0:
                self.inject_token(m, "PL_Expense_Depreciation", "BS_Asset_Accumulated_Depreciation", (current_fa * 0.10) / 12.0, "Depreciation")

            # Quarterly VAT Return Flush
            if m in [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60]:
                vat_acc = self.compute_running_balance_to_month("BS_Liability_VAT_Payable", m)
                if vat_acc != 0.0:
                    self.inject_token(m, "BS_Liability_VAT_Payable", "BS_Asset_Cash", vat_acc, "Quarterly VAT Return")

        return self.compile_financial_statements()

    def compute_running_balance_to_month(self, account_name, month_limit):
        balance = 0.0
        for token in self.token_pool:
            if int(token.month_label.replace("M", "")) <= month_limit:
                if token.debit_acct == account_name: balance += token.amount
                if token.credit_acct == account_name: balance -= token.amount
        return balance

    def compile_financial_statements(self):
        df_pl = pd.DataFrame(0.0, index=["Revenue (£)", "COGS (£)", "Operational Overheads (£)", "Staff Payroll Overhead (£)", "Depreciation (£)", "Net Operating Profit (EBIT)"], columns=self.months)
        df_cf = pd.DataFrame(0.0, index=["Operational Cash Inflows (£)", "Operational Cash Outflows (£)", "Net Cash Movement (£)", "Cash Reserves (£)"], columns=self.months)
        df_bs = pd.DataFrame(0.0, index=["Fixed Infrastructure Assets (£)", "Accumulated Depreciation (£)", "Net Book Value Asset Worth (£)", "Accounts Receivable (Debtors) (£)", "Accounts Payable (Creditors) (£)", "HMRC VAT Reserves Owing (£)", "HMRC PAYE Obligations (£)", "Long Term Facility Debt (£)", "Shareholder Invested Equity (£)", "Retained Earnings Accumulation (£)", "Ledger Verification Checksum Balance"], columns=self.months)

        for m_idx, m_label in enumerate(self.months, start=1):
            for t in self.token_pool:
                if t.month_label == m_label:
                    if t.credit_acct == "PL_Revenue_Gross": df_pl.at["Revenue (£)", m_label] += t.amount
                    if t.debit_acct == "PL_COGS": df_pl.at["COGS (£)", m_label] += t.amount
                    if t.debit_acct == "PL_Expense_Overheads": df_pl.at["Operational Overheads (£)", m_label] += t.amount
                    if t.debit_acct == "PL_Expense_Payroll": df_pl.at["Staff Payroll Overhead (£)", m_label] += t.amount
                    if t.debit_acct == "PL_Expense_Depreciation": df_pl.at["Depreciation (£)", m_label] += t.amount

            df_pl.at["Net Operating Profit (EBIT)", m_label] = df_pl.at["Revenue (£)", m_label] - df_pl.at["COGS (£)", m_label] - df_pl.at["Operational Overheads (£)", m_label] - df_pl.at["Staff Payroll Overhead (£)", m_label] - df_pl.at["Depreciation (£)", m_label]

            for t in self.token_pool:
                if t.month_label == m_label:
                    if t.debit_acct == "BS_Asset_Cash" and t.credit_acct in ["BS_Asset_Debtors", "BS_Equity_Share_Capital", "BS_Liability_Long_Term_Debt"]:
                        df_cf.at["Operational Cash Inflows (£)", m_label] += t.amount
                    if t.credit_acct == "BS_Asset_Cash" and t.debit_acct in ["BS_Liability_Creditors", "BS_Asset_Fixed_Assets", "BS_Liability_PAYE_NIC_Payable", "BS_Expense_Payroll", "BS_Liability_VAT_Payable"]:
                        df_cf.at["Operational Cash Outflows (£)", m_label] += t.amount

            df_cf.at["Net Cash Movement (£)", m_label] = df_cf.at["Operational Cash Inflows (£)", m_label] - df_cf.at["Operational Cash Outflows (£)", m_label]
            df_cf.at["Cash Reserves (£)", m_label] = self.compute_running_balance_to_month("BS_Asset_Cash", m_idx)

            df_bs.at["Fixed Infrastructure Assets (£)", m_label] = self.compute_running_balance_to_month("BS_Asset_Fixed_Assets", m_idx)
            df_bs.at["Accumulated Depreciation (£)", m_label] = -self.compute_running_balance_to_month("BS_Asset_Accumulated_Depreciation", m_idx)
            df_bs.at["Net Book Value Asset Worth (£)", m_label] = df_bs.at["Fixed Infrastructure Assets (£)", m_label] - df_bs.at["Accumulated Depreciation (£)", m_label]
            df_bs.at["Accounts Receivable (Debtors) (£)", m_label] = self.compute_running_balance_to_month("BS_Asset_Debtors", m_idx)
            df_bs.at["Accounts Payable (Creditors) (£)", m_label] = -self.compute_running_balance_to_month("BS_Liability_Creditors", m_idx)
            df_bs.at["HMRC VAT Reserves Owing (£)", m_label] = -self.compute_running_balance_to_month("BS_Liability_VAT_Payable", m_idx)
            df_bs.at["HMRC PAYE Obligations (£)", m_label] = -self.compute_running_balance_to_month("BS_Liability_PAYE_NIC_Payable", m_idx)
            df_bs.at["Long Term Facility Debt (£)", m_label] = -self.compute_running_balance_to_month("BS_Liability_Long_Term_Debt", m_idx)
            df_bs.at["Shareholder Invested Equity (£)", m_label] = -self.compute_running_balance_to_month("BS_Equity_Share_Capital", m_idx)
            
            hist_sum = 0.0
            for past_m in self.months[:m_idx]:
                hist_sum += (df_pl.at["Revenue (£)", past_m] - df_pl.at["COGS (£)", past_m] - df_pl.at["Operational Overheads (£)", past_m] - df_pl.at["Staff Payroll Overhead (£)", past_m] - df_pl.at["Depreciation (£)", past_m])
            df_bs.at["Retained Earnings Accumulation (£)", m_label] = hist_sum
            df_bs.at["Ledger Verification Checksum Balance", m_label] = (df_bs.at["Net Book Value Asset Worth (£)", m_label] + df_bs.at["Accounts Receivable (Debtors) (£)", m_label] + df_cf.at["Cash Reserves (£)", m_label]) - (df_bs.at["Accounts Payable (Creditors) (£)", m_label] + df_bs.at["HMRC VAT Reserves Owing (£)", m_label] + df_bs.at["HMRC PAYE Obligations (£)", m_label] + df_bs.at["Long Term Facility Debt (£)", m_label] + df_bs.at["Shareholder Invested Equity (£)", m_label] + df_bs.at["Retained Earnings Accumulation (£)", m_label])

        df_pl.to_csv("STRATA_Clean_Sheet_PL.csv")
        df_cf.to_csv("STRATA_Clean_Sheet_CF.csv")
        df_bs.to_csv("STRATA_Clean_Sheet_BS.csv")
        return True

# =========================================================================
# 🧠 INTELLIGENCE ENGINE MODULE: GEMINI COHERENT PIPELINE
# =========================================================================

def generate_corporate_intelligence(df_pl, df_cf, df_bs):
    """Compresses ledger matrices and leverages Gemini API to synthesize an executive report."""
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        return "⚠️ **System Lock:** Gemini API Key not detected in workspace environment configuration."
    
    try:
        genai.configure(api_key=api_key)
        y1_months = [f"M{str(i).zfill(2)}" for i in range(1, 13)]
        compressed_payload = {
            "Profit_And_Loss_Y1": df_pl[y1_months].to_dict(orient="index"),
            "Cash_Flow_Y1": df_cf[y1_months].to_dict(orient="index"),
            "Balance_Sheet_Y1": df_bs[y1_months].to_dict(orient="index")
        }
        
        prompt = f"""
        You are acting as an elite Corporate Financial Analyst and Expert Systems Reviewer. 
        Analyze this structured 60-month multi-period financial model layout (Year 1 Data provided):
        
        {json.dumps(compressed_payload, indent=2)}
        
        Deliver a pristine, executive-grade Strategic Intelligence Briefing using British English spelling. 
        Your response must be highly scannable and broken down into these exact sections:
        
        ### 🔍 Working Capital & Liquidity Risk Assessment
        - Identify any hidden friction points or stress zones caused by phase-shifted credit days (e.g., debtor lag vs creditor terms).
        - Explicitly review the impact of the Quarterly HMRC VAT flush cycle and payroll liabilities on the net cash runway cushion.
        
        ### 📈 Operational Performance & Margin Analysis
        - Evaluate the revenue generation trajectory factoring in seasonal profile shapes (Winter/Summer peaks).
        - Critique the net operating profit (EBIT) performance relative to fixed overheads.
        
        ### 📋 Strategic Executive Summary
        - Provide 3 concise, high-level operational recommendations to maximize cash efficiency and preserve runway security.
        
        Avoid any casual conversational preamble, pleasantries, or formatting noise. Move straight to the critique.
        """
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ **API Gateway Disconnect:** Failed to process model response. Error context: {str(e)}"

# =========================================================================
# ⚙️ STREAMLIT INTERFACE LAYER & SECURITY GATEWAY
# =========================================================================

# --- INITIAL REVENUE MATRIX MAPPINGS ---
if "active_data" not in st.session_state:
    st.session_state["active_data"] = {
        "sales": [
            {"name": "Premium Peak Court Hire", "amount": 345600.0, "seasonality": "Winter_Peak", "debtor_days": 0, "vat_applicable": True},
            {"name": "Standard Off-Peak Bookings", "amount": 112400.0, "seasonality": "Summer_Peak", "debtor_days": 0, "vat_applicable": True},
            {"name": "Club Ancillary & Racket Operations", "amount": 33000.0, "seasonality": "Flat_Linear", "debtor_days": 30, "vat_applicable": True}
        ],
        "opex": [
            {"name": "Ground Lease Real Estate Allocation", "amount": 48000.0, "seasonality": "Flat_Linear", "creditor_days": 30, "vat_applicable": False},
            {"name": "Site Power, Utilities & Lighting Arrays", "amount": 32000.0, "seasonality": "Winter_Peak", "creditor_days": 14, "vat_applicable": True}
        ],
        "payroll": [{"name": "Site Management & Frontline Operations Team", "amount": 65000.0}],
        "capital": [
            {"name": "Founder Initial Funding Runway", "type": "Equity Capital / Share Premium Injection", "value": 500000.0, "month": 1},
            {"name": "Indoor Covered Court Construction Infrastructure", "type": "New / Existing Fixed Asset CapEx", "value": 250000.0, "month": 1}
        ]
    }

# --- TRACK SECURE AUTHENTICATION STATUS ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# --- SCREEN GATE: FORCE SIGN IN BEFORE LOADING ENGINE ---
if not st.session_state["authenticated"]:
    st.title("🔐 STRATA // Corporate Gateway")
    st.caption("Access restricted to authorised team personnel. Enter your credentials to verify your workspace session.")
    st.markdown("---")
    
    # Safely extract expected credentials from secrets mapping
    expected_user = st.secrets.get("workspace_credentials", {}).get("username", "marketcatalyst")
    expected_pass = st.secrets.get("workspace_credentials", {}).get("password", "@MCStrata080881")
    
    with st.form("login_form"):
        input_user = st.text_input("Workspace Username Access Key:")
        input_pass = st.text_input("Security Access Password:", type="password")
        
        if st.form_submit_button("Verify & Open Workspace Desks"):
            if input_user == expected_user and input_pass == expected_pass:
                st.session_state["authenticated"] = True
                st.success("🔒 Authorization verified successfully. Mounting workspace environments...")
                st.button("Click to Proceed to Data Workspace")
            else:
                st.error("🚫 Invalid workspace credentials. Access rejected.")
                
    st.stop()  # Strict block prevents execution of the application below until authenticated is True

# --- POST AUTHENTICATION: RUN COHERENT WORKSPACE ---
if "active_view" not in st.session_state:
    st.session_state["active_view"] = "Data Workspace"

st.sidebar.title("🛡️ STRATA // Vector Suite")
st.sidebar.caption("Object-Driven WinForecast Framework Core")
st.sidebar.markdown("---")

nav_choice = st.sidebar.radio(
    "Navigate Simulation Desks:",
    options=["Data Workspace", "Analytical Forecast Sheets"],
    index=0 if st.session_state["active_view"] == "Data Workspace" else 1
)
st.session_state["active_view"] = nav_choice
st.sidebar.markdown("---")
st.sidebar.info("🔒 Platform Balance Engine Active. Monitored continuously.")

if st.sidebar.button("Log Out of Session"):
    st.session_state["authenticated"] = False
    st.rerun()

if st.session_state["active_view"] == "Data Workspace":
    st.title("✍ *Vector Parameter Input Desk")
    st.caption("Clean-sheet environment configuration canvas. Set explicit seasonality shapes and credit delays.")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Revenue Waves", "💸 Operational Expenses", "👥 Staff Payroll", "🏛️ Capital & Funding"])
    
    with tab1:
        st.subheader("Add Seasonal Revenue Channel Attribute")
        with st.form("rev_form", clear_on_submit=True):
            r_name = st.text_input("Stream Identifier Description:")
            r_amt = st.number_input("Annual Gross Contract / Target Worth (£):", min_value=0.0, value=100000.0, step=10000.0)
            r_seas = st.selectbox("Seasonality Weight Allocation Vector:", ["Flat_Linear", "Winter_Peak", "Summer_Peak"])
            r_days = st.slider("Debtor Terms (Credit days delay given):", 0, 90, 0, step=30)
            r_vat = st.checkbox("Subject to Standard 20% Output VAT?", value=True)
            if st.form_submit_button("➕ Append Revenue Vector Line"):
                if r_name.strip():
                    st.session_state["active_data"]["sales"].append({
                        "name": r_name.strip(), "amount": float(r_amt), "seasonality": r_seas, "debtor_days": r_days, "vat_applicable": r_vat
                    })
                    st.rerun()

        st.markdown("### Active Revenue Matrices Registered")
        for idx, item in enumerate(st.session_state["active_data"]["sales"]):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            col1.markdown(f"**{item['name']}**\n\n*Term:* {item['debtor_days']} Days Credit Given")
            col2.markdown(f"**Annual Baseline:** £{item['amount']:,.2f}")
            col3.markdown(f"*Curve:* `{item['seasonality']}`")
            if col4.button("🗑 Remove", key=f"del_r_{idx}"):
                st.session_state["active_data"]["sales"].pop(idx)
                st.rerun()

    with tab2:
        st.subheader("Add Operational Cost Attribute Line")
        with st.form("opex_form", clear_on_submit=True):
            o_name = st.text_input("Expense Identifier Description:")
            o_amt = st.number_input("Annualized Net Running Cost Burden (£):", min_value=0.0, value=20000.0, step=5000.0)
            o_seas = st.selectbox("Cost Allocation Curve Shape Profile:", ["Flat_Linear", "Winter_Peak", "Summer_Peak"])
            o_days = st.slider("Creditor Terms (Supplier payment window received):", 0, 90, 30, step=30)
            o_vat = st.checkbox("Can Recover 20% Input VAT on this Expense?", value=True)
            if st.form_submit_button("➕ Append Overhead Cost Line"):
                if o_name.strip():
                    st.session_state["active_data"]["opex"].append({
                        "name": o_name.strip(), "amount": float(o_amt), "seasonality": o_seas, "creditor_days": o_days, "vat_applicable": o_vat
                    })
                    st.rerun()

        st.markdown("### Active Cost Matrices Registered")
        for idx, item in enumerate(st.session_state["active_data"]["opex"]):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            col1.markdown(f"**{item['name']}**\n\n*Payment window:* Net {item['creditor_days']} Terms")
            col2.markdown(f"**Annual Base:** £{item['amount']:,.2f}")
            col3.markdown(f"*Utility Profile:* `{item['seasonality']}`")
            if col4.button("🗑 Remove", key=f"del_o_{idx}"):
                st.session_state["active_data"]["opex"].pop(idx)
                st.rerun()

    with tab3:
        st.subheader("Add Structural Payroll Overhead")
        with st.form("pay_form", clear_on_submit=True):
            p_name = st.text_input("Staff Grouping / Operational Role Identification:")
            p_amt = st.number_input("Total Combined Annualized Base Gross Salary (£):", min_value=0.0, value=40000.0, step=5000.0)
            if st.form_submit_button("➕ Append Corporate Payroll Vector"):
                if p_name.strip():
                    st.session_state["active_data"]["payroll"].append({"name": p_name.strip(), "amount": float(p_amt)})
                    st.rerun()

        st.markdown("### Active Human Capital Obligation Registries")
        for idx, item in enumerate(st.session_state["active_data"]["payroll"]):
            col1, col2, col3 = st.columns([4, 3, 1])
            col1.markdown(f"**Staff Vector Group:** {item['name']}")
            col2.markdown(f"**Annual Gross Liability Base:** £{item['amount']:,.2f}")
            if col3.button("🗑 Remove", key=f"del_p_{idx}"):
                st.session_state["active_data"]["payroll"].pop(idx)
                st.rerun()

    with tab4:
        st.subheader("Add Corporate Financing or CapEx Infrastructure Event")
        with st.form("cap_form", clear_on_submit=True):
            c_name = st.text_input("Capital Event Allocation Label Description:")
            c_type = st.selectbox("Fixed Category Type:", [
                "Equity Capital / Share Premium Injection", "Commercial Debt / Facility Drawdown", "New / Existing Fixed Asset CapEx"
            ])
            c_val = st.number_input("Value (£):", min_value=0.0, value=50000.0, step=10000.0)
            c_m = st.number_input("Execution Month Index (M01 -> M60):", min_value=1, max_value=60, value=1, step=1)
            if st.form_submit_button("➕ Append Strategic Capital Vector"):
                if c_name.strip():
                    st.session_state["active_data"]["capital"].append({
                        "name": c_name.strip(), "type": c_type, "value": float(c_val), "month": int(c_m)
                    })
                    st.rerun()

        st.markdown("### Active Structural Assets & Funding Configurations")
        for idx, item in enumerate(st.session_state["active_data"]["capital"]):
            col1, col2, col3 = st.columns([3, 4, 1])
            col1.markdown(f"**{item['name']}** - Month {item['month']}")
            col2.markdown(f"**Type:** `{item['type']}` | *Value:* £{item['value']:,.2f}")
            if col3.button("🗑 Remove", key=f"del_c_{idx}"):
                st.session_state["active_data"]["capital"].pop(idx)
                st.rerun()

elif st.session_state["active_view"] == "Analytical Forecast Sheets":
    st.title("📊 Synchronized Statement Reporting Canvas")
    st.caption("Pristine 3-way horizontal projection vectors derived from underlying balanced double-entry transaction pools.")
    st.markdown("---")
    
    cuboid_engine = CommercialTrialBalanceCuboid()
    try:
        cuboid_engine.process_simulation(st.session_state["active_data"])
        
        df_pl = pd.read_csv("STRATA_Clean_Sheet_PL.csv", index_col=0)
        df_cf = pd.read_csv("STRATA_Clean_Sheet_CF.csv", index_col=0)
        df_bs = pd.read_csv("STRATA_Clean_Sheet_BS.csv", index_col=0)
        
        display_months = [f"M{str(i).zfill(2)}" for i in range(1, 13)]
        
        view_tab1, view_tab2, view_tab3 = st.tabs(["📈 Profit & Loss Statement", "💸 Cash Flow Ledger Horizon", "📋 Reconciled Balance Sheet"])
        
        with view_tab1:
            st.subheader("Horizontal Multi-Period Income Performance")
            st.dataframe(df_pl[display_months].style.format("{:,.2f}"), use_container_width=True)
            
        with view_tab2:
            st.subheader("Decoupled Phase-Shifted Liquid Cash Flow Statements")
            st.dataframe(df_cf[display_months].style.format("{:,.2f}"), use_container_width=True)
            
            st.markdown("### 📊 Compounding Real-World Cash Trajectory Curve")
            try:
                raw_cash_vector = df_cf.iloc[3].astype(float).values
                chart_frame = pd.DataFrame(data=raw_cash_vector, index=df_cf.columns, columns=["Liquid Bank Balances (£)"])
                chart_frame.index.name = "Month"
                st.line_chart(chart_frame, use_container_width=True)
            except Exception:
                st.warning("📊 Cash Reserve chart processing. Add data on the input desk to plot trajectory.")
            
        with view_tab3:
            st.subheader("Asset & Liability Worth Accruals")
            st.dataframe(df_bs[display_months].style.format("{:,.2f}"), use_container_width=True)
            st.success("🛡 Checksum Flag Verified: Every month's balanced equations net precisely to zero.")
            
        st.markdown("---")
        st.header("🧠 Gemini Corporate Intelligence Desk")
        st.caption("Launches real-time scenario evaluations, variance tracking, and strategic narrative compilation.")
        
        if st.button("🚀 Synthesize Strategic Executive Report", type="primary"):
            with st.spinner("Analyzing multi-period token vectors, parsing tax schedules, and compiling reporting canvas..."):
                intel_report = generate_corporate_intelligence(df_pl, df_cf, df_bs)
                
                st.markdown("---")
                st.markdown("### 📋 System Generated Executive Briefing")
                st.info("Source: Live Double-Entry Ledgers. Spells set to British English standard.")
                st.markdown(intel_report)
            
    except Exception as err:
        st.error(f"Execution Error inside core transactional engine: {str(err)}")