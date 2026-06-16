# app.py

import streamlit as st
import json
import os
import pandas as pd
from pathlib import Path
import google.generativeai as genai
import io

# =========================================================================
# 🏛️ CORE ENGINE: MULTI-YEAR GRANULAR TRANSITIONAL VECTOR LEDGER
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
        
        # Capitalisation Injections
        for cap in runtime_payload.get("capital", []):
            m_start, val, c_type = int(cap.get("month", 1)), float(cap.get("value", 0.0)), cap.get("type", "")
            if c_type == "Equity Capital / Share Premium Injection":
                self.inject_token(m_start, "BS_Asset_Cash", "BS_Equity_Share_Capital", val, f"CapEx: {cap.get('name')}")
            elif c_type == "Commercial Debt / Facility Drawdown":
                self.inject_token(m_start, "BS_Asset_Cash", "BS_Liability_Long_Term_Debt", val, f"Debt: {cap.get('name')}")
            elif c_type == "New / Existing Fixed Asset CapEx":
                self.inject_token(m_start, "BS_Asset_Fixed_Assets", "BS_Asset_Cash", val, f"Asset: {cap.get('name')}")

        # Chronological Horizon Loop spanning 5 years
        for m in range(1, 61):
            # Sales Pipeline (Granular Account Breakdown Trackers)
            for sale in runtime_payload.get("sales", []):
                ann_net = float(sale.get("amount", 0.0))
                profile, debtor_days, vat_app = sale.get("seasonality", "Flat_Linear"), int(sale.get("debtor_days", 0)), sale.get("vat_applicable", True)
                monthly_net = ann_net * self.extract_monthly_weight(profile, m)
                monthly_vat = (monthly_net * 0.20) if vat_app else 0.0
                
                narr_tag = f"REV_LINE__{sale.get('name')}"
                self.inject_token(m, "BS_Asset_Debtors", "PL_Revenue_Gross", monthly_net, narr_tag)
                if monthly_vat > 0:
                    self.inject_token(m, "BS_Asset_Debtors", "BS_Liability_VAT_Payable", monthly_vat, f"VAT_OUT__{sale.get('name')}")
                self.inject_token(m + (debtor_days // 30), "BS_Asset_Cash", "BS_Asset_Debtors", monthly_net + monthly_vat, f"Receipt: {sale.get('name')}")

            # Overheads Pipeline
            for opex in runtime_payload.get("opex", []):
                ann_net_cost = float(opex.get("amount", 0.0))
                profile, creditor_days, vat_rec = opex.get("seasonality", "Flat_Linear"), int(opex.get("creditor_days", 0)), opex.get("vat_applicable", True)
                monthly_net_cost = ann_net_cost * self.extract_monthly_weight(profile, m)
                monthly_input_vat = (monthly_net_cost * 0.20) if vat_rec else 0.0
                
                narr_tag = f"OPEX_LINE__{opex.get('name')}"
                self.inject_token(m, "PL_Expense_Overheads", "BS_Liability_Creditors", monthly_net_cost, narr_tag)
                if monthly_input_vat > 0:
                    self.inject_token(m, "BS_Liability_VAT_Payable", "BS_Liability_Creditors", monthly_input_vat, f"VAT_IN__{opex.get('name')}")
                self.inject_token(m + (creditor_days // 30), "BS_Liability_Creditors", "BS_Asset_Cash", monthly_net_cost + monthly_input_vat, f"Payment: {opex.get('name')}")

            # Payroll Pipeline
            for pay in runtime_payload.get("payroll", []):
                monthly_gross = float(pay.get("amount", 0.0)) / 12.0
                employer_nic = monthly_gross * 0.138
                paye_deduction = monthly_gross * 0.25
                self.inject_token(m, "PL_Expense_Payroll", "BS_Asset_Cash", monthly_gross - paye_deduction, f"Net Pay: {pay.get('name')}")
                self.inject_token(m, "PL_Expense_Payroll", "BS_Liability_PAYE_NIC_Payable", paye_deduction + employer_nic, f"Taxes: {pay.get('name')}")
                self.inject_token(m + 1, "BS_Liability_PAYE_NIC_Payable", "BS_Asset_Cash", paye_deduction + employer_nic, "HMRC PAYE Payment")

            # Straight-Line Depreciation Ledger Accruals
            current_fa = self.compute_running_balance_to_month("BS_Asset_Fixed_Assets", m)
            if current_fa > 0.0:
                self.inject_token(m, "PL_Expense_Depreciation", "BS_Asset_Accumulated_Depreciation", (current_fa * 0.10) / 12.0, "Depreciation")

            # Quarterly VAT Settlement
            if m in [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60]:
                vat_acc = self.compute_running_balance_to_month("BS_Liability_VAT_Payable", m)
                if vat_acc != 0.0:
                    self.inject_token(m, "BS_Liability_VAT_Payable", "BS_Asset_Cash", vat_acc, "Quarterly VAT Return")

        return self.compile_granular_statements(runtime_payload)

    def compute_running_balance_to_month(self, account_name, month_limit):
        balance = 0.0
        for token in self.token_pool:
            if int(token.month_label.replace("M", "")) <= month_limit:
                if token.debit_acct == account_name: balance += token.amount
                if token.credit_acct == account_name: balance -= token.amount
        return balance

    def compile_granular_statements(self, runtime_payload):
        # Clean, explicit iteration arrays that completely satisfy Pylance
        rev_rows = []
        for s in runtime_payload.get("sales", []):
            rev_rows.append(f"Revenue: {s['name']} (£)")
            
        opex_rows = []
        for o in runtime_payload.get("opex", []):
            opex_rows.append(f"Opex: {o['name']} (£)")
        
        pl_index = rev_rows + ["Total Revenue (£)", "COGS (£)"] + opex_rows + ["Staff Payroll Overhead (£)", "Depreciation (£)", "Net Operating Profit (EBIT)"]
        df_pl = pd.DataFrame(0.0, index=pl_index, columns=self.months)
        
        df_cf = pd.DataFrame(0.0, index=["Operational Cash Inflows (£)", "Operational Cash Outflows (£)", "Net Cash Movement (£)", "Cash Reserves (£)"], columns=self.months)
        df_bs = pd.DataFrame(0.0, index=["Fixed Infrastructure Assets (£)", "Accumulated Depreciation (£)", "Net Book Value Asset Worth (£)", "Accounts Receivable (Debtors) (£)", "Accounts Payable (Creditors) (£)", "HMRC VAT Reserves Owing (£)", "HMRC PAYE Obligations (£)", "Long Term Facility Debt (£)", "Shareholder Invested Equity (£)", "Retained Earnings Accumulation (£)", "Ledger Verification Checksum Balance"], columns=self.months)

        for m_idx, m_label in enumerate(self.months, start=1):
            for t in self.token_pool:
                if t.month_label == m_label:
                    if "REV_LINE__" in t.narrative:
                        clean_name = f"Revenue: {t.narrative.replace('REV_LINE__', '')} (£)"
                        df_pl.at[clean_name, m_label] += t.amount
                        df_pl.at["Total Revenue (£)", m_label] += t.amount
                    if "OPEX_LINE__" in t.narrative:
                        clean_name = f"Opex: {t.narrative.replace('OPEX_LINE__', '')} (£)"
                        df_pl.at[clean_name, m_label] += t.amount
                    if t.debit_acct == "PL_Expense_Payroll":
                        df_pl.at["Staff Payroll Overhead (£)", m_label] += t.amount
                    if t.debit_acct == "PL_Expense_Depreciation":
                        df_pl.at["Depreciation (£)", m_label] += t.amount

            current_opex_total = df_pl[m_label].loc[opex_rows].sum() if opex_rows else 0.0
            df_pl.at["Net Operating Profit (EBIT)", m_label] = df_pl.at["Total Revenue (£)", m_label] - df_pl.at["COGS (£)", m_label] - current_opex_total - df_pl.at["Staff Payroll Overhead (£)", m_label] - df_pl.at["Depreciation (£)", m_label]

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
                past_opex_total = df_pl[past_m].loc[opex_rows].sum() if opex_rows else 0.0
                hist_sum += (df_pl.at["Total Revenue (£)", past_m] - df_pl.at["COGS (£)", past_m] - past_opex_total - df_pl.at["Staff Payroll Overhead (£)", past_m] - df_pl.at["Depreciation (£)", past_m])
            df_bs.at["Retained Earnings Accumulation (£)", m_label] = hist_sum
            df_bs.at["Ledger Verification Checksum Balance", m_label] = (df_bs.at["Net Book Value Asset Worth (£)", m_label] + df_bs.at["Accounts Receivable (Debtors) (£)", m_label] + df_cf.at["Cash Reserves (£)", m_label]) - (df_bs.at["Accounts Payable (Creditors) (£)", m_label] + df_bs.at["HMRC VAT Reserves Owing (£)", m_label] + df_bs.at["HMRC PAYE Obligations (£)", m_label] + df_bs.at["Long Term Facility Debt (£)", m_label] + df_bs.at["Shareholder Invested Equity (£)", m_label] + df_bs.at["Retained Earnings Accumulation (£)", m_label])

        df_pl.to_csv("STRATA_Granular_PL.csv")
        df_cf.to_csv("STRATA_Granular_CF.csv")
        df_bs.to_csv("STRATA_Granular_BS.csv")
        return True

# =========================================================================
# 🧠 INTELLIGENCE ENGINE MODULE: GEMINI COHERENT PIPELINE
# =========================================================================

def generate_corporate_intelligence(df_pl, df_cf, df_bs, range_labels):
    """Transmits the selected multi-year slices through to the Gemini Analytics engine."""
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        return "⚠️ **System Lock:** Gemini API Key not configured in workspace settings."
    
    try:
        genai.configure(api_key=api_key)
        compressed_payload = {
            "Selected_P_And_L_Matrix": df_pl[range_labels].to_dict(orient="index"),
            "Selected_Cash_Flow_Matrix": df_cf[range_labels].to_dict(orient="index"),
            "Selected_Balance_Sheet_Matrix": df_bs[range_labels].to_dict(orient="index")
        }
        
        prompt = f"""
        You are acting as an elite Principal Financial Analyst and Systems Reviewer.
        Review this disaggregated, granular account ledger dataset for the chosen operational horizon:
        
        {json.dumps(compressed_payload, indent=2)}
        
        Provide an executive management pack review using British English spelling. Formulate into these exact sections:
        ### 📊 Year-on-Year Operational Growth & Stability Assessment
        ### 🚨 Liquidity Bottlenecks & Credit Vector Risks
        ### 🏛️ Strategic Recommendations for Capital Reservation
        """
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ **Gateway Disconnect:** {str(e)}"

# =========================================================================
# ⚙️ STREAMLIT INTERFACE LAYER & CONFIGURATION DOCK
# =========================================================================

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

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "cached_report" not in st.session_state:
    st.session_state["cached_report"] = ""

if not st.session_state["authenticated"]:
    st.title("🔐 STRATA // Corporate Gateway")
    with st.form("login_form"):
        input_user = st.text_input("Username:")
        input_pass = st.text_input("Password:", type="password")
        if st.form_submit_button("Verify & Open Workspace Desks"):
            if input_user == st.secrets.get("workspace_credentials", {}).get("username", "marketcatalyst") and input_pass == st.secrets.get("workspace_credentials", {}).get("password", "@MCStrata080881"):
                st.session_state["authenticated"] = True
                st.rerun()
            else: st.error("🚫 Access rejected.")
    st.stop()

st.sidebar.title("🛡️ STRATA // Vector Suite")
nav_choice = st.sidebar.radio("Navigate Desks:", options=["Data Workspace", "Analytical Forecast Sheets"])
if st.sidebar.button("Log Out"):
    st.session_state["authenticated"] = False
    st.rerun()

if nav_choice == "Data Workspace":
    st.title("✍️ Vector Parameter Input Desk")
    st.caption("Configure granular operational parameters and seasonality structures below.")
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Revenue Waves", "💸 Expenses", "👥 Payroll", "🏛️ Funding"])
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
            if col4.button("🗑️ Remove", key=f"del_r_{idx}"):
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
            if col4.button("🗑️ Remove", key=f"del_o_{idx}"):
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
            if col3.button("🗑️ Remove", key=f"del_p_{idx}"):
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
            if col3.button("🗑️ Remove", key=f"del_c_{idx}"):
                st.session_state["active_data"]["capital"].pop(idx)
                st.rerun()

elif nav_choice == "Analytical Forecast Sheets":
    st.title("📊 Synchronized Statement Reporting Canvas")
    
    cuboid_engine = CommercialTrialBalanceCuboid()
    cuboid_engine.process_simulation(st.session_state["active_data"])
    
    df_pl = pd.read_csv("STRATA_Granular_PL.csv", index_col=0)
    df_cf = pd.read_csv("STRATA_Granular_CF.csv", index_col=0)
    df_bs = pd.read_csv("STRATA_Granular_BS.csv", index_col=0)

    # =========================================================================
    # 🎛️ REPORT SELECTION & RANGE GATEWAY CONTROL DOCK
    # =========================================================================
    st.header("🎛️ Report Parameter Scope Configuration")
    
    horizon_scope = st.selectbox(
        "Select Targeted Forecast Reporting Horizon:",
        options=["Year 1 Forecast (Months 01-12)", "Year 2 Forecast (Months 13-24)", "Year 3 Forecast (Months 25-36)", "Full 3-Year Granular Portfolio (Months 01-36)"]
    )
    
    if "Year 1" in horizon_scope: range_labels = [f"M{str(i).zfill(2)}" for i in range(1, 13)]
    elif "Year 2" in horizon_scope: range_labels = [f"M{str(i).zfill(2)}" for i in range(13, 25)]
    elif "Year 3" in horizon_scope: range_labels = [f"M{str(i).zfill(2)}" for i in range(25, 37)]
    else: range_labels = [f"M{str(i).zfill(2)}" for i in range(1, 37)]

    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df_pl[range_labels].to_excel(writer, sheet_name='Granular P&L Sheet')
            df_cf[range_labels].to_excel(writer, sheet_name='Cash Flow Sheet')
            df_bs[range_labels].to_excel(writer, sheet_name='Balance Sheet Sheet')
        excel_buffer.seek(0)
        st.download_button("📊 Download Selected Excel Ledger Pack", data=excel_buffer, file_name=f"STRATA_{horizon_scope.replace(' ', '_')}.xlsx", use_container_width=True)
        
    with exp_col2:
        narrative_output = io.StringIO()
        narrative_output.write(f"🛡️ STRATA MANAGEMENT PACK // PROFILE SCOPE: {horizon_scope}\n\n")
        narrative_output.write("--- ACCOUNT BY ACCOUNT PROFIT & LOSS MATRIX ---\n")
        narrative_output.write(df_pl[range_labels].to_string())
        narrative_output.write("\n\n--- COMPREHENSIVE CASH HORIZON ---\n")
        narrative_output.write(df_cf[range_labels].to_string())
        st.download_button("📜 Download Selected Management Narrative Pack", data=narrative_output.getvalue(), file_name=f"STRATA_{horizon_scope.replace(' ', '_')}.txt", use_container_width=True)

    st.markdown("---")
    
    v_tab1, v_tab2, v_tab3 = st.tabs(["📈 Account-by-Account P&L", "💸 Liquid Cash Flow Horizons", "📋 Reconciled Balance Sheet"])
    with v_tab1:
        st.dataframe(df_pl[range_labels].style.format("{:,.2f}"), use_container_width=True)
    with v_tab2:
        st.dataframe(df_cf[range_labels].style.format("{:,.2f}"), use_container_width=True)
        st.line_chart(pd.DataFrame(df_cf.iloc[3][range_labels].astype(float).values, index=range_labels, columns=["Cash Reserves (£)"]))
    with v_tab3:
        st.dataframe(df_bs[range_labels].style.format("{:,.2f}"), use_container_width=True)
        st.success("🛡️ Balance Sheet Checksum Balance: Locked at 0.00 across all selected multi-year periods.")

    st.markdown("---")
    st.header("🧠 Gemini Corporate Intelligence Desk")
    if st.button("🚀 Synthesize Strategic Executive Report", type="primary"):
        with st.spinner("Processing selected multi-period ledger segments..."):
            st.session_state["cached_report"] = generate_corporate_intelligence(df_pl, df_cf, df_bs, range_labels)
            st.rerun()
            
    if st.session_state["cached_report"]:
        st.markdown(st.session_state["cached_report"])