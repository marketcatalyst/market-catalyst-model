# pages/reports.py
# STRATA SUITE PRODUCTION ENGINE // THREE-WAY REPORTING CANVAS v6.9.8-PRODUCTION

import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# Enforce strict native sidebar removal to eliminate duplicates across versions
st.markdown(
    """
    <style>
        div[data-testid="stSidebarNav"], 
        section[data-testid="stSidebarNav"], 
        ul[data-testid="stSidebarNav"], 
        .stSidebarNav {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.get("authenticated"):
    st.title("🏛️ STRATA // Security Intercept")
    st.warning(
        "🔒 This workspace session is currently unauthenticated or has timed out."
    )
    if st.button("🔐 Return to Home Portal & Sign In", use_container_width=True):
        st.switch_page("home.py")
    st.stop()


class JournalToken:
    def __init__(self, month_label, debit_acct, credit_acct, amount):
        self.month_label = month_label
        self.debit_acct = debit_acct
        self.credit_acct = credit_acct
        self.amount = float(amount)


class CommercialTrialBalanceCuboid:
    def __init__(self):
        self.months = [f"M{str(i).zfill(2)}" for i in range(0, 61)]
        self.seasonality_profiles = {
            "Flat_Linear": [1 / 12] * 12,
            "Winter_Peak": [
                0.12,
                0.12,
                0.10,
                0.07,
                0.05,
                0.05,
                0.05,
                0.06,
                0.08,
                0.09,
                0.10,
                0.11,
            ],
            "Summer_Peak": [
                0.05,
                0.05,
                0.07,
                0.10,
                0.12,
                0.12,
                0.12,
                0.11,
                0.09,
                0.07,
                0.05,
                0.05,
            ],
        }
        if "custom_curves" in st.session_state:
            for k, v in st.session_state["custom_curves"].items():
                self.seasonality_profiles[k] = v
        self.token_pool = []

    def inject_token(self, month_idx, debit_acct, credit_acct, amount):
        if amount <= 0.01 or month_idx < 0 or month_idx > 60:
            return
        self.token_pool.append(
            JournalToken(f"M{str(month_idx).zfill(2)}", debit_acct, credit_acct, amount)
        )

    def run_simulation_engine(self, state):
        self.token_pool = []
        sic = st.session_state.get("sic_profile", {"base_er_nic_rate": 0.138})
        nic_rate = float(sic.get("base_er_nic_rate", 0.138))
        couplings = st.session_state.get("vector_couplings", [])

        for eq in state.get("equity_funding", []):
            self.inject_token(
                int(eq.get("month", 0)),
                "BS_Asset_Cash",
                "BS_Equity_Share_Capital",
                float(eq.get("amount", 0.0)),
            )

        for cap in state.get("outright_capex", []):
            self.inject_token(
                int(cap.get("month", 1)),
                "BS_Asset_Fixed_Assets",
                "BS_Asset_Cash",
                float(cap.get("amount", 0.0)),
            )

        for fa in state.get("financed_assets", []):
            m_start = int(fa.get("month", 1))
            total_val = float(fa.get("amount", 0.0))
            deposit_cash = total_val * (float(fa.get("deposit_pct", 10.0)) / 100.0)
            financed_balance = total_val - deposit_cash
            self.inject_token(
                m_start, "BS_Asset_Fixed_Assets", "BS_Asset_Cash", deposit_cash
            )
            if financed_balance > 0:
                self.inject_token(
                    m_start,
                    "BS_Asset_Fixed_Assets",
                    "BS_Liability_Long_Term_Debt",
                    financed_balance,
                )
                term = int(fa.get("term_months", 36))
                apr = float(fa.get("interest_rate", 5.0)) / 100.0
                monthly_p_base = financed_balance / term
                for t in range(1, term + 1):
                    m_curr = m_start + t
                    if m_curr > 60:
                        break
                    interest_charge = (
                        financed_balance - (monthly_p_base * (t - 1))
                    ) * (apr / 12.0)
                    self.inject_token(
                        m_curr,
                        "BS_Liability_Long_Term_Debt",
                        "BS_Asset_Cash",
                        monthly_p_base,
                    )
                    self.inject_token(
                        m_curr, "PL_Expense_Interest", "BS_Asset_Cash", interest_charge
                    )

        for m in range(1, 61):
            sales_computed_map = {}
            for sale in state.get("sales", []):
                val = 0.0
                if sale.get("overrides", {}).get(f"M{str(m).zfill(2)}", 0.0) > 0:
                    val = float(sale["overrides"][f"M{str(m).zfill(2)}"])
                else:
                    y_idx = 1 if m <= 12 else 2 if m <= 24 else 3
                    y_base = float(sale.get(f"y{y_idx}_baseline", 0.0))
                    flex = (
                        1.0 + (float(sale.get("flex_pct", 0.0)) / 100.0)
                        if y_idx > 1
                        else 1.0
                    )
                    weights = self.seasonality_profiles.get(
                        sale.get("seasonality", "Flat_Linear"),
                        self.seasonality_profiles["Flat_Linear"],
                    )
                    val = y_base * flex * weights[(m - 1) % 12]
                sales_computed_map[sale["name"]] = val
                vat_pct = (
                    0.20
                    if "Standard" in sale.get("vat_rate_type", "Standard")
                    else 0.05 if "Reduced" in sale.get("vat_rate_type") else 0.0
                )
                self.inject_token(m, "BS_Asset_Debtors", "PL_Revenue_Gross", val)
                if val * vat_pct > 0:
                    self.inject_token(
                        m, "BS_Asset_Debtors", "BS_Liability_VAT_Payable", val * vat_pct
                    )
                self.inject_token(
                    m + int(int(sale.get("payment_delay", 0)) / 30),
                    "BS_Asset_Cash",
                    "BS_Asset_Debtors",
                    val * (1.0 + vat_pct),
                )

            for c in state.get("cogs", []):
                val = 0.0
                matched_coupling = next(
                    (cp for cp in couplings if cp["cogs_target"] == c["name"]), None
                )
                if (
                    matched_coupling
                    and matched_coupling["sales_driver"] in sales_computed_map
                ):
                    val = (
                        sales_computed_map[matched_coupling["sales_driver"]]
                        * matched_coupling["coefficient"]
                    )
                elif c.get("overrides", {}).get(f"M{str(m).zfill(2)}", 0.0) > 0:
                    val = float(c["overrides"][f"M{str(m).zfill(2)}"])
                else:
                    y_idx = 1 if m <= 12 else 2 if m <= 24 else 3
                    flex = (
                        1.0 + (float(c.get("flex_pct", 0.0)) / 100.0)
                        if y_idx > 1
                        else 1.0
                    )
                    weights = self.seasonality_profiles.get(
                        c.get("seasonality", "Flat_Linear"),
                        self.seasonality_profiles["Flat_Linear"],
                    )
                    val = (
                        float(c.get(f"y{y_idx}_baseline", 0.0))
                        * flex
                        * weights[(m - 1) % 12]
                    )
                vat_pct = (
                    0.05
                    if "Commercial Energy" in c.get("vat_rate_type", "")
                    else (
                        0.20
                        if "Standard" in c.get("vat_rate_type", "Standard")
                        else 0.0
                    )
                )
                self.inject_token(m, "PL_Expense_COGS", "BS_Asset_Cash", val)
                if val * vat_pct > 0:
                    self.inject_token(
                        m, "BS_Liability_VAT_Payable", "BS_Asset_Cash", val * vat_pct
                    )

            for op in state.get("opex", []):
                val = 0.0
                if "matrix_data" in op:
                    y_key = f"Y{((m - 1) // 12) + 1}"
                    val = float(op["matrix_data"].get(y_key, [0.0] * 12)[(m - 1) % 12])
                vat_pct = (
                    0.05
                    if "Commercial Energy" in op.get("vat_rate_type", "")
                    else (
                        0.20
                        if "Standard" in op.get("vat_rate_type", "Standard")
                        else 0.0
                    )
                )
                self.inject_token(m, "PL_Expense_Overheads", "BS_Asset_Cash", val)
                if val * vat_pct > 0:
                    self.inject_token(
                        m, "BS_Liability_VAT_Payable", "BS_Asset_Cash", val * vat_pct
                    )

            for pay in state.get("payroll", []):
                if int(pay.get("start_month", 1)) <= m <= int(pay.get("end_month", 60)):
                    gross_pool = int(pay.get("headcount", 1)) * float(
                        pay.get("monthly_wage", 2000.0)
                    )
                    self.inject_token(
                        m, "PL_Expense_Payroll", "BS_Asset_Cash", gross_pool
                    )
                    self.inject_token(
                        m,
                        "PL_Expense_Payroll",
                        "BS_Liability_PAYE_NIC_Payable",
                        gross_pool * nic_rate,
                    )
                    self.inject_token(
                        m + 1,
                        "BS_Liability_PAYE_NIC_Payable",
                        "BS_Asset_Cash",
                        gross_pool * nic_rate,
                    )

            for outright in state.get("outright_capex", []):
                if int(outright["month"]) <= m:
                    charge = (
                        float(outright["amount"])
                        * float(outright.get("depreciation_rate", 0.20))
                    ) / 12.0
                    self.inject_token(
                        m,
                        "PL_Expense_Depreciation",
                        "BS_Asset_Accumulated_Depreciation",
                        charge,
                    )
            for fin in state.get("financed_assets", []):
                if int(fin["month"]) <= m:
                    charge = (
                        float(fin["amount"]) * float(fin.get("depreciation_rate", 0.15))
                    ) / 12.0
                    self.inject_token(
                        m,
                        "PL_Expense_Depreciation",
                        "BS_Asset_Accumulated_Depreciation",
                        charge,
                    )

            if m in [
                3,
                6,
                9,
                12,
                15,
                18,
                21,
                24,
                27,
                30,
                33,
                36,
                39,
                42,
                45,
                48,
                51,
                54,
                57,
                60,
            ]:
                vat_acc = self.compute_running_balance_to_period(
                    "BS_Liability_VAT_Payable", m
                )
                if vat_acc != 0.0:
                    self.inject_token(
                        m, "BS_Liability_VAT_Payable", "BS_Asset_Cash", vat_acc
                    )

        return self.compile_financial_matrices()

    def compute_running_balance_to_period(self, account, month_limit):
        bal = 0.0
        for t in self.token_pool:
            if int(t.month_label.replace("M", "")) <= month_limit:
                if t.debit_acct == account:
                    bal += t.amount
                if t.credit_acct == account:
                    bal -= t.amount
        return bal

    def compile_financial_matrices(self):
        months_labels = [f"M{str(i).zfill(2)}" for i in range(0, 61)]
        df_pl = pd.DataFrame(
            0.0,
            index=[
                "Total Revenue (£)",
                "Cost of Goods Sold (COGS) (£)",
                "Gross Profit Margin (£)",
                "Operational Overheads (£)",
                "Staff Payroll Overhead (£)",
                "Depreciation Overhead (£)",
                "Financing Interest Cost (£)",
                "Net Operating Profit (EBIT)",
            ],
            columns=months_labels,
        )
        df_cf = pd.DataFrame(
            0.0,
            index=[
                "Trading Cash Collections (£)",
                "Equity Capital Funding Injections (£)",
                "Operational Cash Outflows (£)",
                "Net Trading Cash Movement (£)",
                "Closing Bank Cash Reserves (£)",
            ],
            columns=months_labels,
        )
        df_bs = pd.DataFrame(
            0.0,
            index=[
                "Fixed Infrastructure Assets (£)",
                "Accumulated Depreciation Reserve (£)",
                "Net Book Value Asset Worth (£)",
                "Trade Debtors Balance (£)",
                "HMRC VAT Reserves Owing (£)",
                "HMRC PAYE Obligations Liability (£)",
                "Long Term Facility Debt Liability (£)",
                "Shareholder Invested Equity Reserves (£)",
                "Retained Earnings Accumulation (£)",
                "Ledger Verification Checksum Balance",
            ],
            columns=months_labels,
        )

        for m_idx, m_lbl in enumerate(months_labels):
            for t in self.token_pool:
                if t.month_label == m_lbl:
                    if t.credit_acct == "PL_Revenue_Gross":
                        df_pl.at["Total Revenue (£)", m_lbl] += t.amount
                    if t.debit_acct == "PL_Expense_COGS":
                        df_pl.at["Cost of Goods Sold (COGS) (£)", m_lbl] += t.amount
                    if t.debit_acct == "PL_Expense_Overheads":
                        df_pl.at["Operational Overheads (£)", m_lbl] += t.amount
                    if t.debit_acct == "PL_Expense_Payroll":
                        df_pl.at["Staff Payroll Overhead (£)", m_lbl] += t.amount
                    if t.debit_acct == "PL_Expense_Depreciation":
                        df_pl.at["Depreciation Overhead (£)", m_lbl] += t.amount
                    if t.debit_acct == "PL_Expense_Interest":
                        df_pl.at["Financing Interest Cost (£)", m_lbl] += t.amount
                    if (
                        t.debit_acct == "BS_Asset_Cash"
                        and t.credit_acct == "BS_Asset_Debtors"
                    ):
                        df_cf.at["Trading Cash Collections (£)", m_lbl] += t.amount
                    if (
                        t.debit_acct == "BS_Asset_Cash"
                        and t.credit_acct == "BS_Equity_Share_Capital"
                    ):
                        df_cf.at[
                            "Equity Capital Funding Injections (£)", m_lbl
                        ] += t.amount
                    if t.credit_acct == "BS_Asset_Cash":
                        df_cf.at["Operational Cash Outflows (£)", m_lbl] += t.amount

            df_pl.at["Gross Profit Margin (£)", m_lbl] = (
                df_pl.at["Total Revenue (£)", m_lbl]
                - df_pl.at["Cost of Goods Sold (COGS) (£)", m_lbl]
            )
            df_pl.at["Net Operating Profit (EBIT)", m_lbl] = (
                df_pl.at["Gross Profit Margin (£)", m_lbl]
                - df_pl.at["Operational Overheads (£)", m_lbl]
                - df_pl.at["Staff Payroll Overhead (£)", m_lbl]
                - df_pl.at["Depreciation Overhead (£)", m_lbl]
                - df_pl.at["Financing Interest Cost (£)", m_lbl]
            )
            df_cf.at["Net Trading Cash Movement (£)", m_lbl] = (
                df_cf.at["Trading Cash Collections (£)", m_lbl]
                + df_cf.at["Equity Capital Funding Injections (£)", m_lbl]
                - df_cf.at["Operational Cash Outflows (£)", m_lbl]
            )
            df_cf.at["Closing Bank Cash Reserves (£)", m_lbl] = (
                self.compute_running_balance_to_period("BS_Asset_Cash", m_idx)
            )
            df_bs.at["Fixed Infrastructure Assets (£)", m_lbl] = (
                self.compute_running_balance_to_period("BS_Asset_Fixed_Assets", m_idx)
            )
            df_bs.at["Accumulated Depreciation Reserve (£)", m_lbl] = (
                -self.compute_running_balance_to_period(
                    "BS_Asset_Accumulated_Depreciation", m_idx
                )
            )
            df_bs.at["Net Book Value Asset Worth (£)", m_lbl] = (
                df_bs.at["Fixed Infrastructure Assets (£)", m_lbl]
                - df_bs.at["Accumulated Depreciation Reserve (£)", m_lbl]
            )
            df_bs.at["Trade Debtors Balance (£)", m_lbl] = (
                self.compute_running_balance_to_period("BS_Asset_Debtors", m_idx)
            )
            df_bs.at["HMRC VAT Reserves Owing (£)", m_lbl] = (
                -self.compute_running_balance_to_period(
                    "BS_Liability_VAT_Payable", m_idx
                )
            )
            df_bs.at["HMRC PAYE Obligations Liability (£)", m_lbl] = (
                -self.compute_running_balance_to_period(
                    "BS_Liability_PAYE_NIC_Payable", m_idx
                )
            )
            df_bs.at["Long Term Facility Debt Liability (£)", m_lbl] = (
                -self.compute_running_balance_to_period(
                    "BS_Liability_Long_Term_Debt", m_idx
                )
            )
            df_bs.at["Shareholder Invested Equity Reserves (£)", m_lbl] = (
                -self.compute_running_balance_to_period(
                    "BS_Equity_Share_Capital", m_idx
                )
            )

            h_sum = 0.0
            for pm in months_labels[1 : m_idx + 1]:
                h_sum += df_pl.at["Net Operating Profit (EBIT)", pm]
            df_bs.at["Retained Earnings Accumulation (£)", m_lbl] = h_sum
            assets = (
                df_bs.at["Net Book Value Asset Worth (£)", m_lbl]
                + df_bs.at["Trade Debtors Balance (£)", m_lbl]
                + df_cf.at["Closing Bank Cash Reserves (£)", m_lbl]
            )
            liabs = (
                df_bs.at["HMRC VAT Reserves Owing (£)", m_lbl]
                + df_bs.at["HMRC PAYE Obligations Liability (£)", m_lbl]
                + df_bs.at["Long Term Facility Debt Liability (£)", m_lbl]
                + df_bs.at["Shareholder Invested Equity Reserves (£)", m_lbl]
                + df_bs.at["Retained Earnings Accumulation (£)", m_lbl]
            )
            df_bs.at["Ledger Verification Checksum Balance", m_lbl] = round(
                assets - liabs, 2
            )

        return df_pl, df_cf, df_bs


# =========================================================================
# WORKSPACE DISPLAY RENDERING CANVAS
# =========================================================================
st.title("📊 Performance & Reporting Summary Pack")
st.caption(
    f"Active Scenario context: `{st.session_state.get('active_project_name', 'Unsaved_Draft_Scenario')}`"
)
st.page_link("pages/app.py", label="✍️ Return to Data Entry Panel")
st.markdown("---")

cuboid_engine = CommercialTrialBalanceCuboid()
df_pl, df_cf, df_bs = cuboid_engine.run_simulation_engine(
    st.session_state.get("active_data", {})
)

closing_cash_array = df_cf.loc["Closing Bank Cash Reserves (£)"].astype(float).values
peak_cash = closing_cash_array.max()
lowest_cash = closing_cash_array.min()
y5_worth = df_bs.loc["Retained Earnings Accumulation (£)", "M60"]

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Peak Cash Runway Worth", f"£{peak_cash:,.2f}")
kpi2.metric("Max Venture Risk Valley", f"£{lowest_cash:,.2f}")
kpi3.metric("Year 5 Horizon Value", f"£{y5_worth:,.2f}")

st.markdown("---")

# =========================================================================
# EXPORT CONTROLS HUB
# =========================================================================
st.subheader("📥 Executive Report Pack Export Controls")
exp_col1, exp_col2, exp_col3 = st.columns(3)

with exp_col1:
    csv_pl = df_pl.to_csv().encode("utf-8")
    st.download_button(
        "📥 Download Profit & Loss CSV",
        data=csv_pl,
        file_name="STRATA_Profit_and_Loss.csv",
        mime="text/csv",
        use_container_width=True,
    )

with exp_col2:
    csv_cf = df_cf.to_csv().encode("utf-8")
    st.download_button(
        "📥 Download Cash Flow CSV",
        data=csv_cf,
        file_name="STRATA_Cash_Flow.csv",
        mime="text/csv",
        use_container_width=True,
    )

with exp_col3:
    csv_bs = df_bs.to_csv().encode("utf-8")
    st.download_button(
        "📥 Download Balance Sheet CSV",
        data=csv_bs,
        file_name="STRATA_Balance_Sheet.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.markdown("### 🧠 Gemini AI Executive Management Pack Synthesis")
st.caption(
    "Triggers an automated context scan of your 60-month multi-dimensional arrays to generate a formal corporate analysis report."
)

if st.button("🤖 Generate AI Executive Summary Report", use_container_width=True):
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)

    if not api_key:
        st.error(
            "❌ **Configuration Error:** Gemini API credential vector is missing from server env secrets storage slots."
        )
    else:
        with st.spinner(
            "🤖 Analytical Engine scanning active matrices... Formulating management pack narrative..."
        ):
            try:
                genai.configure(api_key=api_key)
                # 🚀 RESOLVED: Switched retired 1.5-flash endpoints over to standard 2.5-flash framework model identifiers
                model = genai.GenerativeModel("gemini-2.5-flash")

                financial_summary_context = f"""
                Project Name: {st.session_state.get('active_project_name', 'Unsaved Draft Scenario')}
                Peak Cash Runway: £{peak_cash:,.2f}
                Maximum Risk Valley Cash Point: £{lowest_cash:,.2f}
                Year 5 Cumulative Retained Earnings: £{y5_worth:,.2f}
                
                Year 1 Key Revenue Milestones: {df_pl.loc["Total Revenue (£)"].iloc[0:13].to_dict()}
                Year 1 Ending Bank Cash Balances: {df_cf.loc["Closing Bank Cash Reserves (£)"].iloc[0:13].to_dict()}
                """

                prompt = f"""
                You are a senior elite corporate CFO and investment systems strategist. 
                Analyze the following financial projection model context for a high-end sustainable design and industrial innovation project:
                {financial_summary_context}
                
                Provide a structured Executive Management Summary report detailing:
                1. Commercial Runway Strengths & Cash Inflection Points.
                2. Risk Valley Vulnerabilities (identifying when cash drops to its lowest threshold and how to offset it).
                3. Operational Cash Flow Sustainability Analysis across the projection horizons.
                
                Keep the tone sharp, professional, highly analytical, and tailored to C-suite board reviews. Use clean UK English spelling.
                """

                response = model.generate_content(prompt)
                st.markdown("---")
                st.markdown("## 🏛️ Executive Strategy Summary Pack")
                st.write(response.text)
                st.success("✔️ AI Executive Management Pack compiled successfully.")
            except Exception as e:
                st.error(f"Failed to generate report narrative: {str(e)}")

st.markdown("---")

horiz = st.selectbox(
    "Analytical Accounting Window Filter:",
    [
        "Year 1 Horizon View (M00 - M12)",
        "Full 5-Year Comprehensive Asset Track (M00 - M60)",
    ],
)
targets = (
    [f"M{str(i).zfill(2)}" for i in range(0, 13)]
    if "Year 1" in horiz
    else [f"M{str(i).zfill(2)}" for i in range(0, 61)]
)

t1, t2, t3 = st.tabs(
    [
        "📈 Master Three-Way Ledgers",
        "🚜 Fixed Asset Depreciation Ledger",
        "🏦 Loan Amortisation Schedule",
    ]
)

with t1:
    st.markdown("#### Profit & Loss Statement (£)")
    st.dataframe(df_pl[targets].style.format("{:,.2f}"), use_container_width=True)
    st.markdown("#### Cash Flow Statement (£)")
    st.dataframe(df_cf[targets].style.format("{:,.2f}"), use_container_width=True)
    st.markdown("#### Balance Sheet Ledger (£)")
    st.dataframe(df_bs[targets].style.format("{:,.2f}"), use_container_width=True)

with t2:
    st.markdown("### 🚜 Dynamic Fixed Asset Depreciation Ledger")
    fa_rows = []
    active_data = st.session_state.get("active_data", {})
    for outright in active_data.get("outright_capex", []):
        fa_rows.append(
            {
                "Asset Item": outright["name"],
                "Type": "Direct Purchase",
                "Value": outright["amount"],
                "Month": int(outright["month"]),
                "Rate": float(outright.get("depreciation_rate", 0.20)),
            }
        )
    for fin in active_data.get("financed_assets", []):
        fa_rows.append(
            {
                "Asset Item": fin["name"],
                "Type": "Financed HP",
                "Value": fin["amount"],
                "Month": int(fin["month"]),
                "Rate": float(fin.get("depreciation_rate", 0.15)),
            }
        )

    if fa_rows:
        ledger_rows = []
        for item in fa_rows:
            v_rec = {
                "Asset Item": item["Asset Item"],
                "Metric Category": "Net Book Value (£)",
            }
            running_val = 0.0
            for m in range(0, 61):
                m_lbl = f"M{str(m).zfill(2)}"
                if m == item["Month"]:
                    running_val = item["Value"]
                if m >= item["Month"] and running_val > 0:
                    running_val = max(
                        0.0, running_val - ((item["Value"] * item["Rate"]) / 12.0)
                    )
                v_rec[m_lbl] = running_val
            ledger_rows.append(v_rec)
        st.dataframe(
            pd.DataFrame(ledger_rows)
            .set_index(["Asset Item", "Metric Category"])[targets]
            .style.format("{:,.2f}"),
            use_container_width=True,
        )
    else:
        st.info("No fixed assets currently registered.")

with t3:
    st.markdown("### 🏦 Chronological Liability Allocation Ledger")
    if active_data.get("financed_assets"):
        loan_rows = []
        for fin in active_data["financed_assets"]:
            m_start = int(fin["month"])
            fin_bal = float(fin["amount"]) * (
                1.0 - (float(fin.get("deposit_pct", 10.0)) / 100.0)
            )
            term = int(fin["term_months"])
            monthly_principal = fin_bal / term

            bal_rec = {"Facility": fin["name"], "Metric": "Total Outstanding (£)"}
            st_rec = {
                "Facility": fin["name"],
                "Metric": "Current Liabilities (<12m) (£)",
            }
            lt_rec = {"Facility": fin["name"], "Metric": "Non-Current Debt (>1yr) (£)"}

            running_debt = 0.0
            for m in range(0, 61):
                m_lbl = f"M{str(m).zfill(2)}"
                if m == m_start:
                    running_debt = fin_bal
                if m >= m_start and running_debt > 0:
                    st_debt = min(running_debt, monthly_principal * 12)
                    bal_rec[m_lbl] = running_debt
                    st_rec[m_lbl] = st_debt
                    lt_rec[m_lbl] = max(0.0, running_debt - st_debt)
                    running_debt = max(0.0, running_debt - monthly_principal)
                else:
                    bal_rec[m_lbl] = running_debt
                    st_rec[m_lbl] = 0.0
                    lt_rec[m_lbl] = 0.0
            loan_rows.extend([bal_rec, st_rec, lt_rec])
        st.dataframe(
            pd.DataFrame(loan_rows)
            .set_index(["Facility", "Metric"])[targets]
            .style.format("{:,.2f}"),
            use_container_width=True,
        )

# =========================================================================
# 🧭 FIXED SIDEBAR COMPASS OPTIONS
# =========================================================================
st.sidebar.markdown("### Compass Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")
