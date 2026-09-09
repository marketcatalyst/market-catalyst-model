# pages/reports.py
# STRATA SUITE PRODUCTION ENGINE // THREE-WAY REPORTING CANVAS v8.0.0-STATUTORY
# SAGE WINFORECAST DOUBLE-ENTRY VERIFIED ENGINE (UK GAAP COMPLIANT)

import os
import re
import google.generativeai as genai
import pandas as pd
import streamlit as st

try:
    from weasyprint import HTML

    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    HTML = None
    WEASYPRINT_AVAILABLE = False

# Enforce clean full-canvas presentation
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
    if st.button("🔑 Return to Home Portal & Sign In", use_container_width=True):
        st.switch_page("home.py")
    st.stop()


# =========================================================================
# 🏛️ DOUBLE-ENTRY JOURNAL ENGINE
# =========================================================================
class JournalToken:

    def __init__(self, month_label, debit_acct, credit_acct, amount):
        self.month_label = month_label
        self.debit_acct = debit_acct
        self.credit_acct = credit_acct
        self.amount = round(float(amount), 4)


class CommercialTrialBalanceCuboid:

    def __init__(self, horizon_months=36):
        self.horizon_months = horizon_months
        self.months = [f"M{str(i).zfill(2)}" for i in range(0, self.horizon_months + 1)]
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
        if amount <= 0.0001 or month_idx < 0 or month_idx > self.horizon_months:
            return
        self.token_pool.append(
            JournalToken(f"M{str(month_idx).zfill(2)}", debit_acct, credit_acct, amount)
        )

    def run_simulation_engine(self, state):
        self.token_pool = []
        sic = st.session_state.get("sic_profile", {})
        nic_rate = float(sic.get("base_er_nic_rate", 0.138))
        corp_tax_rate = float(sic.get("corp_tax_rate", 0.19))
        supplier_credit_days = int(sic.get("supplier_credit_days", 30))

        couplings = st.session_state.get("vector_couplings", [])

        # 1. Opening Positions: Equity & Outright CapEx
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

        # Financed Assets (Hire Purchase / Leases)
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
                term = max(1, int(fa.get("term_months", 36)))
                apr = float(fa.get("interest_rate", 5.0)) / 100.0
                monthly_p_base = financed_balance / term
                for t in range(1, term + 1):
                    m_curr = m_start + t
                    if m_curr > self.horizon_months:
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
                        m_curr,
                        "PL_Expense_Interest",
                        "BS_Asset_Cash",
                        interest_charge,
                    )

        # 2. Chronological Monthly Execution Loop
        horizon_years = self.horizon_months // 12
        ytd_ebt_tracker = {yr: 0.0 for yr in range(1, horizon_years + 1)}
        ytd_tax_provided = {yr: 0.0 for yr in range(1, horizon_years + 1)}
        annual_taxable_profits = {yr: 0.0 for yr in range(1, horizon_years + 1)}

        # Standard HMRC Stagger 1 Quarterly VAT Months: M05, M08, M11, M14, M17, M20, M23, M26, M29, M32, M35, M38, ...
        vat_settle_months = [
            m
            for m in range(1, self.horizon_months + 1)
            if (m >= 5 and (m - 2) % 3 == 0)
        ]

        for m in range(1, self.horizon_months + 1):
            yr_idx = ((m - 1) // 12) + 1
            sales_computed_map = {}

            # --- REVENUE ---
            for sale in state.get("sales", []):
                val = 0.0
                if sale.get("overrides", {}).get(f"M{str(m).zfill(2)}", 0.0) > 0:
                    val = float(sale["overrides"][f"M{str(m).zfill(2)}"])
                else:
                    y_base = float(
                        sale.get(f"y{yr_idx}_baseline", sale.get("y1_baseline", 0.0))
                    )
                    flex = (
                        (1.0 + (float(sale.get("flex_pct", 0.0)) / 100.0))
                        if yr_idx > 1
                        else 1.0
                    )
                    seasonality_curve = self.seasonality_profiles.get(
                        sale.get("seasonality", "Flat_Linear"),
                        self.seasonality_profiles["Flat_Linear"],
                    )
                    val = y_base * flex * seasonality_curve[(m - 1) % 12]

                sales_computed_map[sale["name"]] = val
                vat_pct = (
                    0.20
                    if "Standard" in sale.get("vat_rate_type", "Standard")
                    else (0.05 if "Reduced" in sale.get("vat_rate_type", "") else 0.0)
                )
                pay_delay = int(int(sale.get("payment_delay", 0)) / 30)

                self.inject_token(m, "BS_Asset_Debtors", "PL_Revenue_Gross", val)
                if val * vat_pct > 0:
                    self.inject_token(
                        m,
                        "BS_Asset_Debtors",
                        "BS_Liability_VAT_Payable",
                        val * vat_pct,
                    )
                self.inject_token(
                    m + pay_delay,
                    "BS_Asset_Cash",
                    "BS_Asset_Debtors",
                    val * (1.0 + vat_pct),
                )

            # --- COGS ---
            for c in state.get("cogs", []):
                val = 0.0
                matched_coupling = next(
                    (cp for cp in couplings if cp["cogs_target"] == c["name"]),
                    None,
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
                    y_base = float(
                        c.get(f"y{yr_idx}_baseline", c.get("y1_baseline", 0.0))
                    )
                    flex = (
                        (1.0 + (float(c.get("flex_pct", 0.0)) / 100.0))
                        if yr_idx > 1
                        else 1.0
                    )
                    seasonality_curve = self.seasonality_profiles.get(
                        c.get("seasonality", "Flat_Linear"),
                        self.seasonality_profiles["Flat_Linear"],
                    )
                    val = y_base * flex * seasonality_curve[(m - 1) % 12]

                vat_pct = (
                    0.05
                    if "Commercial Energy" in c.get("vat_rate_type", "")
                    else (
                        0.20
                        if "Standard" in c.get("vat_rate_type", "Standard")
                        else 0.0
                    )
                )
                is_staff = "staff" in c.get("name", "").lower()
                creditor_lag = (
                    0 if is_staff else (1 if supplier_credit_days >= 30 else 0)
                )

                self.inject_token(
                    m, "PL_Expense_COGS", "BS_Liability_Trade_Creditors", val
                )
                if val * vat_pct > 0:
                    self.inject_token(
                        m,
                        "BS_Liability_VAT_Payable",
                        "BS_Liability_Trade_Creditors",
                        val * vat_pct,
                    )
                self.inject_token(
                    m + creditor_lag,
                    "BS_Liability_Trade_Creditors",
                    "BS_Asset_Cash",
                    val * (1.0 + vat_pct),
                )

            # --- OPEX ---
            for op in state.get("opex", []):
                val = 0.0
                if "matrix_data" in op and f"Y{yr_idx}" in op["matrix_data"]:
                    val = float(op["matrix_data"][f"Y{yr_idx}"][(m - 1) % 12])
                else:
                    val = (
                        float(
                            op.get(
                                f"y{yr_idx}_baseline",
                                op.get("y1_baseline", 0.0),
                            )
                        )
                        / 12.0
                    )

                vat_pct = (
                    0.05
                    if "Commercial Energy" in op.get("vat_rate_type", "")
                    else (
                        0.20
                        if "Standard" in op.get("vat_rate_type", "Standard")
                        else 0.0
                    )
                )
                self.inject_token(
                    m,
                    "PL_Expense_Overheads",
                    "BS_Liability_Trade_Creditors",
                    val,
                )
                if val * vat_pct > 0:
                    self.inject_token(
                        m,
                        "BS_Liability_VAT_Payable",
                        "BS_Liability_Trade_Creditors",
                        val * vat_pct,
                    )
                self.inject_token(
                    m + 1,
                    "BS_Liability_Trade_Creditors",
                    "BS_Asset_Cash",
                    val * (1.0 + vat_pct),
                )

            # --- PAYROLL ---
            for pay in state.get("payroll", []):
                if (
                    int(pay.get("start_month", 1))
                    <= m
                    <= min(int(pay.get("end_month", 60)), self.horizon_months)
                ):
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

            # --- DEPRECIATION ---
            for outright in state.get("outright_capex", []):
                if int(outright.get("month", 1)) <= m:
                    dep_charge = (
                        float(outright.get("amount", 0.0))
                        * float(outright.get("depreciation_rate", 0.20))
                    ) / 12.0
                    self.inject_token(
                        m,
                        "PL_Expense_Depreciation",
                        "BS_Asset_Accumulated_Depreciation",
                        dep_charge,
                    )

            for fin in state.get("financed_assets", []):
                if int(fin.get("month", 1)) <= m:
                    dep_charge = (
                        float(fin.get("amount", 0.0))
                        * float(fin.get("depreciation_rate", 0.15))
                    ) / 12.0
                    self.inject_token(
                        m,
                        "PL_Expense_Depreciation",
                        "BS_Asset_Accumulated_Depreciation",
                        dep_charge,
                    )

            # --- QUARTERLY VAT DISCHARGE ---
            if m in vat_settle_months:
                # Calculate net credit balance in VAT liability account prior to this period's entries
                vat_balance = self.get_net_liability_balance(
                    "BS_Liability_VAT_Payable", m - 1
                )
                if vat_balance > 0.001:
                    self.inject_token(
                        m,
                        "BS_Liability_VAT_Payable",
                        "BS_Asset_Cash",
                        vat_balance,
                    )

            # --- STATUTORY YTD CUMULATIVE TAX ENGINE WITH LOSS RELEASE ---
            m_lbl = f"M{str(m).zfill(2)}"
            m_rev = sum(
                t.amount
                for t in self.token_pool
                if t.month_label == m_lbl and t.credit_acct == "PL_Revenue_Gross"
            )
            m_cogs = sum(
                t.amount
                for t in self.token_pool
                if t.month_label == m_lbl and t.debit_acct == "PL_Expense_COGS"
            )
            m_opex = sum(
                t.amount
                for t in self.token_pool
                if t.month_label == m_lbl and t.debit_acct == "PL_Expense_Overheads"
            )
            m_pay = sum(
                t.amount
                for t in self.token_pool
                if t.month_label == m_lbl and t.debit_acct == "PL_Expense_Payroll"
            )
            m_dep = sum(
                t.amount
                for t in self.token_pool
                if t.month_label == m_lbl and t.debit_acct == "PL_Expense_Depreciation"
            )
            m_int = sum(
                t.amount
                for t in self.token_pool
                if t.month_label == m_lbl and t.debit_acct == "PL_Expense_Interest"
            )

            monthly_ebt = m_rev - m_cogs - m_opex - m_pay - m_dep - m_int
            ytd_ebt_tracker[yr_idx] += monthly_ebt

            required_cumulative_tax = max(0.0, ytd_ebt_tracker[yr_idx] * corp_tax_rate)
            tax_delta = required_cumulative_tax - ytd_tax_provided[yr_idx]

            if tax_delta > 0.0001:
                self.inject_token(
                    m,
                    "PL_Tax_Corporation_Tax",
                    "BS_Liability_Corp_Tax_Provision",
                    tax_delta,
                )
                ytd_tax_provided[yr_idx] += tax_delta
            elif tax_delta < -0.0001:
                release_amt = abs(tax_delta)
                self.inject_token(
                    m,
                    "BS_Liability_Corp_Tax_Provision",
                    "PL_Tax_Corporation_Tax",
                    release_amt,
                )
                ytd_tax_provided[yr_idx] -= release_amt

        # Store annual tax totals for 9-month lag discharge schedule
        for yr in range(1, horizon_years + 1):
            annual_taxable_profits[yr] = ytd_tax_provided[yr]

        # 9-Month Lag Tax Cash Settlements
        tax_settle_map = {1: 21, 2: 33, 3: 45, 4: 57}
        for yr, settle_m in tax_settle_map.items():
            if (
                settle_m <= self.horizon_months
                and annual_taxable_profits.get(yr, 0.0) > 0
            ):
                self.inject_token(
                    settle_m,
                    "BS_Liability_Corp_Tax_Provision",
                    "BS_Asset_Cash",
                    annual_taxable_profits[yr],
                )

        return self.compile_financial_matrices()

    def get_net_liability_balance(self, account, month_limit):
        """Returns the accumulated net liability (credit minus debit) up to month_limit."""
        cr = sum(
            t.amount
            for t in self.token_pool
            if t.credit_acct == account
            and int(t.month_label.replace("M", "")) <= month_limit
        )
        dr = sum(
            t.amount
            for t in self.token_pool
            if t.debit_acct == account
            and int(t.month_label.replace("M", "")) <= month_limit
        )
        return max(0.0, cr - dr)

    def get_net_asset_balance(self, account, month_limit):
        """Returns the accumulated net asset (debit minus credit) up to month_limit."""
        dr = sum(
            t.amount
            for t in self.token_pool
            if t.debit_acct == account
            and int(t.month_label.replace("M", "")) <= month_limit
        )
        cr = sum(
            t.amount
            for t in self.token_pool
            if t.credit_acct == account
            and int(t.month_label.replace("M", "")) <= month_limit
        )
        return max(0.0, dr - cr)

    def compile_financial_matrices(self):
        months_labels = [
            f"M{str(i).zfill(2)}" for i in range(0, self.horizon_months + 1)
        ]

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
                "Corporation Tax Provision (£)",
                "Profit After Tax (PAT) (£)",
            ],
            columns=months_labels,
        )

        df_cf = pd.DataFrame(
            0.0,
            index=[
                "Trading Cash Collections (£)",
                "Equity Capital Funding Injections (£)",
                "Operational Cash Outflows (£)",
                "Corporation Tax Settlement Paid (£)",
                "HMRC VAT Settlement Paid (£)",
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
                "Closing Bank Cash Reserves (£)",
                "Total Assets (£)",
                "Trade Creditors Balance (£)",
                "HMRC VAT Reserves Owing (£)",
                "Provision for Corporation Tax (£)",
                "HMRC PAYE Obligations Liability (£)",
                "Long Term Facility Debt Liability (£)",
                "Total Current & Long-Term Liabilities (£)",
                "Shareholder Invested Equity Reserves (£)",
                "Retained Earnings Accumulation (£)",
                "Total Liabilities & Equity Reserves (£)",
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

                    # Corporation tax charge (Debit) vs tax release (Credit)
                    if t.debit_acct == "PL_Tax_Corporation_Tax":
                        df_pl.at["Corporation Tax Provision (£)", m_lbl] += t.amount
                    if t.credit_acct == "PL_Tax_Corporation_Tax":
                        df_pl.at["Corporation Tax Provision (£)", m_lbl] -= t.amount

                    # Cash Flow Mapping
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
                        if t.debit_acct == "BS_Liability_Corp_Tax_Provision":
                            df_cf.at[
                                "Corporation Tax Settlement Paid (£)", m_lbl
                            ] += t.amount
                        elif t.debit_acct == "BS_Liability_VAT_Payable":
                            df_cf.at["HMRC VAT Settlement Paid (£)", m_lbl] += t.amount
                        else:
                            df_cf.at["Operational Cash Outflows (£)", m_lbl] += t.amount

            # Computed P&L Totals
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
            df_pl.at["Profit After Tax (PAT) (£)", m_lbl] = (
                df_pl.at["Net Operating Profit (EBIT)", m_lbl]
                - df_pl.at["Corporation Tax Provision (£)", m_lbl]
            )

            # Cash Flow Closing Position
            df_cf.at["Net Trading Cash Movement (£)", m_lbl] = (
                df_cf.at["Trading Cash Collections (£)", m_lbl]
                + df_cf.at["Equity Capital Funding Injections (£)", m_lbl]
                - df_cf.at["Operational Cash Outflows (£)", m_lbl]
                - df_cf.at["Corporation Tax Settlement Paid (£)", m_lbl]
                - df_cf.at["HMRC VAT Settlement Paid (£)", m_lbl]
            )

            # Cumulative Cash Balance
            cash_dr = sum(
                t.amount
                for t in self.token_pool
                if t.debit_acct == "BS_Asset_Cash"
                and int(t.month_label.replace("M", "")) <= m_idx
            )
            cash_cr = sum(
                t.amount
                for t in self.token_pool
                if t.credit_acct == "BS_Asset_Cash"
                and int(t.month_label.replace("M", "")) <= m_idx
            )
            closing_cash = round(cash_dr - cash_cr, 2)
            df_cf.at["Closing Bank Cash Reserves (£)", m_lbl] = closing_cash

            # --- BALANCE SHEET MAPPING (STRICT POSITIVE DISPLAY CONVENTION) ---
            fixed_assets = self.get_net_asset_balance("BS_Asset_Fixed_Assets", m_idx)
            accum_dep = self.get_net_liability_balance(
                "BS_Asset_Accumulated_Depreciation", m_idx
            )
            nbv = max(0.0, fixed_assets - accum_dep)
            debtors = self.get_net_asset_balance("BS_Asset_Debtors", m_idx)

            df_bs.at["Fixed Infrastructure Assets (£)", m_lbl] = fixed_assets
            df_bs.at["Accumulated Depreciation Reserve (£)", m_lbl] = accum_dep
            df_bs.at["Net Book Value Asset Worth (£)", m_lbl] = nbv
            df_bs.at["Trade Debtors Balance (£)", m_lbl] = debtors
            df_bs.at["Closing Bank Cash Reserves (£)", m_lbl] = closing_cash

            total_assets = round(nbv + debtors + closing_cash, 2)
            df_bs.at["Total Assets (£)", m_lbl] = total_assets

            trade_creditors = self.get_net_liability_balance(
                "BS_Liability_Trade_Creditors", m_idx
            )
            vat_owing = self.get_net_liability_balance(
                "BS_Liability_VAT_Payable", m_idx
            )
            tax_owing = self.get_net_liability_balance(
                "BS_Liability_Corp_Tax_Provision", m_idx
            )
            paye_owing = self.get_net_liability_balance(
                "BS_Liability_PAYE_NIC_Payable", m_idx
            )
            debt_owing = self.get_net_liability_balance(
                "BS_Liability_Long_Term_Debt", m_idx
            )
            share_capital = self.get_net_liability_balance(
                "BS_Equity_Share_Capital", m_idx
            )

            df_bs.at["Trade Creditors Balance (£)", m_lbl] = trade_creditors
            df_bs.at["HMRC VAT Reserves Owing (£)", m_lbl] = vat_owing
            df_bs.at["Provision for Corporation Tax (£)", m_lbl] = tax_owing
            df_bs.at["HMRC PAYE Obligations Liability (£)", m_lbl] = paye_owing
            df_bs.at["Long Term Facility Debt Liability (£)", m_lbl] = debt_owing

            total_liabs = round(
                trade_creditors + vat_owing + tax_owing + paye_owing + debt_owing,
                2,
            )
            df_bs.at["Total Current & Long-Term Liabilities (£)", m_lbl] = total_liabs

            # Cumulative Retained Earnings from P&L PAT
            cum_pat = sum(
                df_pl.at["Profit After Tax (PAT) (£)", pm]
                for pm in months_labels[1 : m_idx + 1]
            )
            retained_earnings = round(cum_pat, 2)

            df_bs.at["Shareholder Invested Equity Reserves (£)", m_lbl] = share_capital
            df_bs.at["Retained Earnings Accumulation (£)", m_lbl] = retained_earnings

            total_liabs_and_equity = round(
                total_liabs + share_capital + retained_earnings, 2
            )
            df_bs.at["Total Liabilities & Equity Reserves (£)", m_lbl] = (
                total_liabs_and_equity
            )

            # Statutory Verification Checksum: Assets - (Liabilities + Equity) = 0.00
            df_bs.at["Ledger Verification Checksum Balance", m_lbl] = round(
                total_assets - total_liabs_and_equity, 2
            )

        return df_pl, df_cf, df_bs


# =========================================================================
# 🏛️ EXECUTIVE REPORT PACK HTML / PDF COMPILER
# =========================================================================
def compile_premium_html_report(
    project_name,
    peak_cash,
    lowest_cash,
    horizon_worth,
    insight_text,
    df_pl,
    df_cf,
    df_bs,
    active_data,
    horizon_years=3,
):
    clean_insight = (
        insight_text.replace("\n", "<br>")
        .replace("â€™", "'")
        .replace("â€˜", "'")
        .replace("â€œ", '"')
        .replace("â€ ", '"')
    )
    years_labels = [f"Year {i}" for i in range(1, horizon_years + 1)]

    annual_pl, annual_cf, annual_bs = {}, {}, {}
    for idx, yr in enumerate(years_labels):
        m_start = (idx * 12) + 1
        m_end = (idx + 1) * 12
        cols = [f"M{str(i).zfill(2)}" for i in range(m_start, m_end + 1)]
        bs_col = f"M{str(m_end).zfill(2)}"

        annual_pl[yr] = {
            "Revenue": df_pl[cols].loc["Total Revenue (£)"].sum(),
            "COGS": df_pl[cols].loc["Cost of Goods Sold (COGS) (£)"].sum(),
            "Gross": df_pl[cols].loc["Gross Profit Margin (£)"].sum(),
            "Opex": df_pl[cols].loc["Operational Overheads (£)"].sum(),
            "Payroll": df_pl[cols].loc["Staff Payroll Overhead (£)"].sum(),
            "Depreciation": df_pl[cols].loc["Depreciation Overhead (£)"].sum(),
            "Interest": df_pl[cols].loc["Financing Interest Cost (£)"].sum(),
            "EBIT": df_pl[cols].loc["Net Operating Profit (EBIT)"].sum(),
            "Tax": df_pl[cols].loc["Corporation Tax Provision (£)"].sum(),
            "PAT": df_pl[cols].loc["Profit After Tax (PAT) (£)"].sum(),
        }
        annual_cf[yr] = {
            "Inflow": df_cf[cols].loc["Trading Cash Collections (£)"].sum(),
            "Equity": df_cf[cols].loc["Equity Capital Funding Injections (£)"].sum(),
            "Outflow": df_cf[cols].loc["Operational Cash Outflows (£)"].sum(),
            "TaxPaid": df_cf[cols].loc["Corporation Tax Settlement Paid (£)"].sum(),
            "VATPaid": df_cf[cols].loc["HMRC VAT Settlement Paid (£)"].sum(),
            "Closing": df_cf.at["Closing Bank Cash Reserves (£)", bs_col],
        }
        annual_bs[yr] = {
            "Fixed": df_bs.at["Fixed Infrastructure Assets (£)", bs_col],
            "AccumDep": df_bs.at["Accumulated Depreciation Reserve (£)", bs_col],
            "NBV": df_bs.at["Net Book Value Asset Worth (£)", bs_col],
            "Debtors": df_bs.at["Trade Debtors Balance (£)", bs_col],
            "Cash": df_bs.at["Closing Bank Cash Reserves (£)", bs_col],
            "TotalAssets": df_bs.at["Total Assets (£)", bs_col],
            "Creditors": df_bs.at["Trade Creditors Balance (£)", bs_col],
            "VAT": df_bs.at["HMRC VAT Reserves Owing (£)", bs_col],
            "CorpTax": df_bs.at["Provision for Corporation Tax (£)", bs_col],
            "PAYE": df_bs.at["HMRC PAYE Obligations Liability (£)", bs_col],
            "Debt": df_bs.at["Long Term Facility Debt Liability (£)", bs_col],
            "Equity": df_bs.at["Shareholder Invested Equity Reserves (£)", bs_col],
            "Retained": df_bs.at["Retained Earnings Accumulation (£)", bs_col],
            "TotalLiabEquity": df_bs.at[
                "Total Liabilities & Equity Reserves (£)", bs_col
            ],
            "Checksum": df_bs.at["Ledger Verification Checksum Balance", bs_col],
        }

    html_pl = "".join(
        f"<tr style='{'font-weight:bold; background:#f8fafc;' if k in ['Revenue','Gross','EBIT','PAT'] else ''}'>"
        f"<td>{lbl}</td>"
        + "".join(
            f"<td class='text-right'>£{annual_pl[y][k]:,.2f}</td>" for y in years_labels
        )
        + "</tr>"
        for lbl, k in [
            ("Total Revenue", "Revenue"),
            ("Cost of Goods Sold (COGS)", "COGS"),
            ("Gross Profit Margin", "Gross"),
            ("Operational Overheads", "Opex"),
            ("Staff Payroll Overhead", "Payroll"),
            ("Depreciation Overhead", "Depreciation"),
            ("Financing Interest Cost", "Interest"),
            ("Net Operating Profit (EBIT)", "EBIT"),
            ("Corporation Tax Provision", "Tax"),
            ("Profit After Tax (PAT)", "PAT"),
        ]
    )

    html_cf = "".join(
        f"<tr style='{'font-weight:bold; background:#f8fafc;' if k=='Closing' else ''}'>"
        f"<td>{lbl}</td>"
        + "".join(
            f"<td class='text-right'>£{annual_cf[y][k]:,.2f}</td>" for y in years_labels
        )
        + "</tr>"
        for lbl, k in [
            ("Trading Cash Collections", "Inflow"),
            ("Equity Capital Injections", "Equity"),
            ("Operational Cash Outflows", "Outflow"),
            ("Corporation Tax Settlement Paid", "TaxPaid"),
            ("HMRC VAT Settlement Paid", "VATPaid"),
            ("Closing Bank Cash Reserves", "Closing"),
        ]
    )

    html_bs = "".join(
        f"<tr style='{'font-weight:bold; background:#f8fafc;' if k in ['TotalAssets','TotalLiabEquity','Checksum'] else ''}'>"
        f"<td>{lbl}</td>"
        + "".join(
            f"<td class='text-right'>{'£' if k != 'Checksum' else ''}{annual_bs[y][k]:,.2f}</td>"
            for y in years_labels
        )
        + "</tr>"
        for lbl, k in [
            ("Net Book Value Asset Worth", "NBV"),
            ("Trade Debtors Balance", "Debtors"),
            ("Closing Bank Cash Reserves", "Cash"),
            ("Total Assets", "TotalAssets"),
            ("Trade Creditors Balance", "Creditors"),
            ("HMRC VAT Reserves Owing", "VAT"),
            ("Provision for Corporation Tax", "CorpTax"),
            ("HMRC PAYE Obligations Liability", "PAYE"),
            ("Long Term Facility Debt Liability", "Debt"),
            ("Shareholder Invested Equity Reserves", "Equity"),
            ("Retained Earnings Accumulation", "Retained"),
            ("Total Liabilities & Equity Reserves", "TotalLiabEquity"),
            ("Ledger Verification Checksum Balance", "Checksum"),
        ]
    )

    th_headers = "".join(f"<th>{y}</th>" for y in years_labels)
    total_months = horizon_years * 12

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4 portrait; margin: 18mm 15mm;
                @bottom-right {{ content: "Page " counter(page); font-family: sans-serif; font-size: 8pt; color: #94a3b8; }}
                @bottom-left {{ content: "STRATA Suite // Statutory Accounting Engine"; font-family: sans-serif; font-size: 8pt; color: #94a3b8; }}
            }}
            body {{ font-family: Arial, sans-serif; color: #0f172a; line-height: 1.4; font-size: 8.5pt; }}
            .banner {{ background-color: #1e3a8a; color: #ffffff; padding: 18px; border-radius: 4px; margin-bottom: 15px; }}
            .banner h1 {{ margin: 0; font-size: 15pt; font-weight: 700; }}
            .banner p {{ margin: 4px 0 0 0; font-size: 8pt; color: #93c5fd; text-transform: uppercase; letter-spacing: 0.8px; }}
            .ctx {{ margin-bottom: 15px; font-size: 9.5pt; font-weight: bold; color: #334155; }}
            h2 {{ color: #1e3a8a; font-size: 10.5pt; font-weight: 700; margin-top: 18px; border-left: 4px solid #3b82f6; padding-left: 6px; page-break-after: avoid; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 16px; page-break-inside: avoid; }}
            th {{ background-color: #f8fafc; color: #475569; padding: 5px 8px; font-size: 8pt; border-bottom: 2px solid #cbd5e1; text-transform: uppercase; }}
            td {{ padding: 5px 8px; border-bottom: 1px solid #e2e8f0; font-size: 8pt; }}
            .text-right {{ text-align: right; }}
            .page-break {{ page-break-before: always; }}
        </style>
    </head>
    <body>
        <div class="banner">
            <h1>STRATA EXECUTIVE FINANCIAL REPORT PACK</h1>
            <p>Statutory {horizon_years}-Year Integrated Financial Projections (Dual-Entry Audited)</p>
        </div>
        <div class="ctx">Project: {project_name} | Accounting Horizon: {horizon_years} Operating Years ({total_months} Months)</div>
        <table>
            <thead><tr><th>Target Core Metric</th><th class="text-right">Projected Value Position</th></tr></thead>
            <tbody>
                <tr><td>Peak Cumulative Cash Reserves</td><td class="text-right">£{peak_cash:,.2f}</td></tr>
                <tr><td>Maximum Working Capital Trough</td><td class="text-right">£{lowest_cash:,.2f}</td></tr>
                <tr><td>Year {horizon_years} Terminal Retained Equity Worth</td><td class="text-right">£{horizon_worth:,.2f}</td></tr>
            </tbody>
        </table>
        <h2>Executive CFO Narrative Synthesis</h2>
        <div>{clean_insight}</div>
        <div class="page-break">
            <h2>Profit & Loss Forecast Statement (Years 1 to {horizon_years})</h2>
            <table><thead><tr><th>Performance Component</th>{th_headers}</tr></thead><tbody>{html_pl}</tbody></table>
            <h2>Cash Flow Forecast Statement (Years 1 to {horizon_years})</h2>
            <table><thead><tr><th>Liquidity Flow Component</th>{th_headers}</tr></thead><tbody>{html_cf}</tbody></table>
            <h2>Balance Sheet Capital Statement (Years 1 to {horizon_years})</h2>
            <table><thead><tr><th>Ledger Balance Structure</th>{th_headers}</tr></thead><tbody>{html_bs}</tbody></table>
        </div>
    </body>
    </html>
    """

    tmp_html, tmp_pdf = "tmp_report.html", "tmp_report.pdf"
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html_template)
    HTML(tmp_html).write_pdf(tmp_pdf)
    with open(tmp_pdf, "rb") as f:
        pdf_bytes = f.read()
    if os.path.exists(tmp_html):
        os.remove(tmp_html)
    if os.path.exists(tmp_pdf):
        os.remove(tmp_pdf)
    return pdf_bytes


# =========================================================================
# WORKSPACE DISPLAY RENDERING CANVAS
# =========================================================================
st.title("📊 Performance & Reporting Summary Pack")
st.caption(
    f"Active Scenario Context: `{st.session_state.get('active_project_name', 'Unsaved_Draft_Scenario')}`"
)
st.page_link("pages/app.py", label="✍️ Return to Data Entry Panel")
st.markdown("---")

# MASTER REPORTING HORIZON CONFIGURATION
horizon_choice = st.radio(
    "Select Master Forecasting Horizon Window:",
    [
        "3-Year Horizon (M00 - M36) [WinForecast Statutory Benchmark]",
        "5-Year Horizon (M00 - M60) [STRATA Standard Framework]",
    ],
    horizontal=True,
)
horizon_years = 3 if "3-Year" in horizon_choice else 5
horizon_months = horizon_years * 12

cuboid_engine = CommercialTrialBalanceCuboid(horizon_months=horizon_months)
active_data_context = st.session_state.get("active_data", {})
df_pl, df_cf, df_bs = cuboid_engine.run_simulation_engine(active_data_context)

term_month_col = f"M{str(horizon_months).zfill(2)}"
closing_cash_array = df_cf.loc["Closing Bank Cash Reserves (£)"].astype(float).values
peak_cash, lowest_cash = float(closing_cash_array.max()), float(
    closing_cash_array.min()
)
terminal_worth = float(df_bs.loc["Retained Earnings Accumulation (£)", term_month_col])

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Peak Cash Reserves", f"£{peak_cash:,.2f}")
kpi2.metric("Min Cash Trough", f"£{lowest_cash:,.2f}")
kpi3.metric(f"Year {horizon_years} Retained Earnings", f"£{terminal_worth:,.2f}")
st.markdown("---")

if "cached_ai_analysis" not in st.session_state:
    st.session_state["cached_ai_analysis"] = ""

# =========================================================================
# EXPORT CONTROLS HUB
# =========================================================================
st.subheader("📥 Executive Report Pack Export Controls")
exp_col1, exp_col2, exp_col3 = st.columns(3)
with exp_col1:
    st.download_button(
        "📥 Download Profit & Loss CSV",
        data=df_pl.to_csv().encode("utf-8"),
        file_name=f"STRATA_PL_{horizon_years}Yr.csv",
        mime="text/csv",
        use_container_width=True,
    )
with exp_col2:
    st.download_button(
        "📥 Download Cash Flow CSV",
        data=df_cf.to_csv().encode("utf-8"),
        file_name=f"STRATA_CashFlow_{horizon_years}Yr.csv",
        mime="text/csv",
        use_container_width=True,
    )
with exp_col3:
    st.download_button(
        "📥 Download Balance Sheet CSV",
        data=df_bs.to_csv().encode("utf-8"),
        file_name=f"STRATA_BalanceSheet_{horizon_years}Yr.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.markdown("### 🧠 Gemini AI Executive Management Pack Synthesis")
if st.button(
    "🤖 Generate AI Executive Summary Report & Compile PDF Pack",
    use_container_width=True,
):
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        st.error("❌ Configuration Error: Gemini credential vector missing.")
    else:
        with st.spinner("🤖 Analytical Engine scanning active matrices..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                financial_summary_context = (
                    f"Project: {st.session_state.get('active_project_name')}\n"
                    f"Horizon: {horizon_years} Years ({horizon_months} Months)\n"
                    f"Peak Cash: £{peak_cash:,.2f}\n"
                    f"Risk Valley: £{lowest_cash:,.2f}\n"
                    f"Retained Worth: £{terminal_worth:,.2f}"
                )
                prompt = (
                    f"Analyze this financial model as a Chief Financial Officer. "
                    f"Write a comprehensive 3-paragraph executive commentary covering revenue trajectory, "
                    f"tax & working capital drag, and liquidity adequacy. Do not use any markdown asterisks (**):\n"
                    f"{financial_summary_context}"
                )
                response = model.generate_content(prompt)
                st.session_state["cached_ai_analysis"] = str(response.text).replace(
                    "**", ""
                )
                st.success("✔️ AI Executive Management analysis compiled.")
            except Exception as e:
                st.error(f"Failed to generate narrative: {str(e)}")

if st.session_state["cached_ai_analysis"]:
    st.markdown("---")
    st.markdown("## 🏛 Executive Strategy Summary Pack Preview")
    st.write(st.session_state["cached_ai_analysis"])
    if not WEASYPRINT_AVAILABLE:
        st.warning(
            "⚠️ WeasyPrint binary libraries are not detected in the local Windows environment. PDF compilation executes cleanly in Linux cloud deployments."
        )
    else:
        try:
            pdf_binary = compile_premium_html_report(
                project_name=st.session_state.get(
                    "active_project_name", "Unsaved_Draft_Scenario"
                ),
                peak_cash=peak_cash,
                lowest_cash=lowest_cash,
                horizon_worth=terminal_worth,
                insight_text=st.session_state["cached_ai_analysis"],
                df_pl=df_pl,
                df_cf=df_cf,
                df_bs=df_bs,
                active_data=active_data_context,
                horizon_years=horizon_years,
            )
            st.download_button(
                label="📄 Download Official Executive Management Pack PDF",
                data=pdf_binary,
                file_name=f"STRATA_Executive_Summary_{horizon_years}Yr.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as pdf_err:
            st.error(f"PDF binary compiler mismatch: {str(pdf_err)}")

st.markdown("---")

# Presentation Slices
targets = [f"M{str(i).zfill(2)}" for i in range(0, horizon_months + 1)]
active_months_for_sum = [t for t in targets if t != "M00"]

df_pl_view = df_pl[targets].copy()
df_cf_view = df_cf[targets].copy()
df_bs_view = df_bs[targets].copy()

df_pl_view["Horizon Total"] = df_pl[active_months_for_sum].sum(axis=1)
df_pl_view.at["Gross Profit Margin (£)", "Horizon Total"] = (
    df_pl_view.loc["Total Revenue (£)", "Horizon Total"]
    - df_pl_view.loc["Cost of Goods Sold (COGS) (£)", "Horizon Total"]
)
df_pl_view.at["Net Operating Profit (EBIT)", "Horizon Total"] = (
    df_pl_view.loc["Gross Profit Margin (£)", "Horizon Total"]
    - df_pl_view.loc["Operational Overheads (£)", "Horizon Total"]
    - df_pl_view.loc["Staff Payroll Overhead (£)", "Horizon Total"]
    - df_pl_view.loc["Depreciation Overhead (£)", "Horizon Total"]
    - df_pl_view.loc["Financing Interest Cost (£)", "Horizon Total"]
)
df_pl_view.at["Profit After Tax (PAT) (£)", "Horizon Total"] = (
    df_pl_view.loc["Net Operating Profit (EBIT)", "Horizon Total"]
    - df_pl_view.loc["Corporation Tax Provision (£)", "Horizon Total"]
)

df_cf_view["Horizon Total"] = df_cf[active_months_for_sum].sum(axis=1)
df_cf_view.at["Closing Bank Cash Reserves (£)", "Horizon Total"] = df_cf.at[
    "Closing Bank Cash Reserves (£)", targets[-1]
]

df_bs_view["Terminal Position"] = df_bs[targets[-1]]

t1, t2, t3 = st.tabs(
    [
        " Reconciled Financial Statements",
        " Fixed Infrastructure Asset Ledger",
        " External Debt Liabilities Registry",
    ]
)


def highlight_totals(row):
    highlight_rows = [
        "Total Revenue (£)",
        "Gross Profit Margin (£)",
        "Net Operating Profit (EBIT)",
        "Profit After Tax (PAT) (£)",
        "Closing Bank Cash Reserves (£)",
        "Total Assets (£)",
        "Total Current & Long-Term Liabilities (£)",
        "Total Liabilities & Equity Reserves (£)",
        "Ledger Verification Checksum Balance",
    ]
    if row.name in highlight_rows:
        return ["font-weight: bold; background-color: #f1f5f9; color: #1e3a8a;"] * len(
            row
        )
    return [""] * len(row)


with t1:
    st.markdown("#### Profit & Loss Statement (£)")
    st.dataframe(
        df_pl_view.style.format("{:,.2f}").apply(highlight_totals, axis=1),
        use_container_width=True,
    )
    st.markdown("#### Cash Flow Statement (£)")
    st.dataframe(
        df_cf_view.style.format("{:,.2f}").apply(highlight_totals, axis=1),
        use_container_width=True,
    )
    st.markdown("#### Balance Sheet Ledger (£)")
    st.dataframe(
        df_bs_view.style.format("{:,.2f}").apply(highlight_totals, axis=1),
        use_container_width=True,
    )

with t2:
    st.markdown("### 🚜 Dynamic Fixed Asset Depreciation Ledger")
    fa_rows = []
    for outright in active_data_context.get("outright_capex", []):
        fa_rows.append(
            {
                "Asset Item": outright["name"],
                "Type": "Direct Purchase",
                "value": float(outright["amount"]),
                "Month": int(outright["month"]),
                "Rate": float(outright.get("depreciation_rate", 0.20)),
            }
        )
    for fin in active_data_context.get("financed_assets", []):
        fa_rows.append(
            {
                "Asset Item": fin["name"],
                "Type": "Financed HP",
                "value": float(fin["amount"]),
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
            for m in range(0, horizon_months + 1):
                m_lbl = f"M{str(m).zfill(2)}"
                if m == item["Month"]:
                    running_val = item["value"]
                if m >= item["Month"] and running_val > 0:
                    running_val = max(
                        0.0,
                        running_val - ((item["value"] * item["Rate"]) / 12.0),
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
        st.info("No fixed capital assets registered in active scenario.")

with t3:
    st.markdown("### 🏛️ Chronological Liability Allocation Ledger")
    if active_data_context.get("financed_assets"):
        loan_rows = []
        for fin in active_data_context["financed_assets"]:
            m_start = int(fin["month"])
            fin_bal = float(fin["amount"]) * (
                1.0 - (float(fin.get("deposit_pct", 10.0)) / 100.0)
            )
            term = max(1, int(fin.get("term_months", 36)))
            monthly_principal = fin_bal / term
            bal_rec = {
                "Facility": fin["name"],
                "Metric": "Total Outstanding (£)",
            }
            st_rec = {
                "Facility": fin["name"],
                "Metric": "Current Liabilities (<12m) (£)",
            }
            lt_rec = {
                "Facility": fin["name"],
                "Metric": "Non-Current Debt (>1yr) (£)",
            }

            running_debt = 0.0
            for m in range(0, horizon_months + 1):
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
    else:
        st.info("No long-term debt facilities registered in active scenario.")

# =========================================================================
# 🧭 FIXED SIDEBAR COMPASS OPTIONS
# =========================================================================
st.sidebar.markdown("### Compass Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link(
    "pages/1_Data_Ingestion_Gateway.py", label="📥 Data Ingestion Gateway"
)
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry Panel")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")
