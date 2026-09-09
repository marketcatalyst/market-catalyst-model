# pages/reports.py
# STRATA SUITE PRODUCTION ENGINE // THREE-WAY REPORTING CANVAS v9.0.0-STATUTORY
# STRICT DOUBLE-ENTRY GENERAL LEDGER ARCHITECTURE (SAGE WINFORECAST RECONCILED)

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
# 🏛️ AUDITED GENERAL LEDGER DOUBLE-ENTRY ENGINE
# =========================================================================

CHART_OF_ACCOUNTS = {
    # Assets (Normal balance: DEBIT)
    "1200": {"name": "Bank Current Account", "type": "Asset", "sign": 1},
    "1100": {"name": "Trade Debtors Control", "type": "Asset", "sign": 1},
    "0020": {"name": "Fixed Infrastructure Assets", "type": "Asset", "sign": 1},
    "0021": {
        "name": "Accumulated Depreciation Reserve",
        "type": "Contra-Asset",
        "sign": -1,
    },
    # Liabilities (Normal balance: CREDIT)
    "2100": {"name": "Trade Creditors Control", "type": "Liability", "sign": -1},
    "2200": {"name": "HMRC VAT Control Account", "type": "Liability", "sign": -1},
    "2210": {"name": "HMRC PAYE/NIC Obligations", "type": "Liability", "sign": -1},
    "2220": {
        "name": "Corporation Tax Liability Provision",
        "type": "Liability",
        "sign": -1,
    },
    "2300": {
        "name": "Long-Term Facility Debt Liability",
        "type": "Liability",
        "sign": -1,
    },
    # Capital & Reserves (Normal balance: CREDIT)
    "3000": {"name": "Shareholder Invested Equity", "type": "Equity", "sign": -1},
    "3200": {"name": "Retained Earnings Accumulation", "type": "Equity", "sign": -1},
    # P&L Income (Normal balance: CREDIT)
    "4000": {"name": "Gross Turnover Revenue", "type": "Income", "sign": -1},
    # P&L Expenses (Normal balance: DEBIT)
    "5000": {"name": "Cost of Goods Sold (COGS)", "type": "Expense", "sign": 1},
    "6000": {"name": "Operational Overheads", "type": "Expense", "sign": 1},
    "7000": {"name": "Staff Payroll Overhead", "type": "Expense", "sign": 1},
    "8000": {"name": "Depreciation Expense", "type": "Expense", "sign": 1},
    "8100": {"name": "Financing Interest Cost", "type": "Expense", "sign": 1},
    "9000": {"name": "Corporation Tax Provision", "type": "TaxExpense", "sign": 1},
}


class AuditedGeneralLedger:
    def __init__(self, horizon_months=36):
        self.horizon_months = horizon_months
        self.journal_entries = []

    def post_journal(
        self,
        month: int,
        debit_code: str,
        credit_code: str,
        amount: float,
        memo: str = "",
    ):
        amt = round(float(amount), 2)
        if amt <= 0.00:
            return
        if month < 0 or month > self.horizon_months:
            return
        # Strict Double-Entry: Each journal entry records equal and opposite debits and credits
        self.journal_entries.append(
            {
                "month": month,
                "debit_code": str(debit_code),
                "credit_code": str(credit_code),
                "amount": amt,
                "memo": memo,
            }
        )

    def get_period_movement(self, nominal_code: str, month: int) -> float:
        """Returns the net movement of an account in a single period."""
        dr = sum(
            j["amount"]
            for j in self.journal_entries
            if j["month"] == month and j["debit_code"] == nominal_code
        )
        cr = sum(
            j["amount"]
            for j in self.journal_entries
            if j["month"] == month and j["credit_code"] == nominal_code
        )
        # Normal debit accounts: Dr - Cr. Normal credit accounts: Cr - Dr
        sign = CHART_OF_ACCOUNTS[nominal_code]["sign"]
        return (dr - cr) * sign

    def get_cumulative_balance(self, nominal_code: str, month_limit: int) -> float:
        """Returns the cumulative ledger balance up to month_limit."""
        dr = sum(
            j["amount"]
            for j in self.journal_entries
            if j["month"] <= month_limit and j["debit_code"] == nominal_code
        )
        cr = sum(
            j["amount"]
            for j in self.journal_entries
            if j["month"] <= month_limit and j["credit_code"] == nominal_code
        )
        sign = CHART_OF_ACCOUNTS[nominal_code]["sign"]
        return (dr - cr) * sign


def execute_full_simulation(state, horizon_months=36):
    gl = AuditedGeneralLedger(horizon_months=horizon_months)
    horizon_years = horizon_months // 12
    sic = st.session_state.get("sic_profile", {})
    nic_rate = float(sic.get("base_er_nic_rate", 0.138))
    corp_tax_rate = float(sic.get("corp_tax_rate", 0.19))
    supplier_credit_days = int(sic.get("supplier_credit_days", 30))

    seasonality = {
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
            seasonality[k] = v

    # 1. Month 00 Setup: Share Capital & CapEx
    for eq in state.get("equity_funding", []):
        gl.post_journal(
            int(eq.get("month", 0)),
            "1200",
            "3000",
            float(eq.get("amount", 0.0)),
            "Initial Share Capital",
        )

    for cap in state.get("outright_capex", []):
        gl.post_journal(
            int(cap.get("month", 1)),
            "0020",
            "1200",
            float(cap.get("amount", 0.0)),
            "Direct CapEx Purchase",
        )

    for fa in state.get("financed_assets", []):
        m_start = int(fa.get("month", 1))
        t_val = float(fa.get("amount", 0.0))
        dp_pct = float(fa.get("deposit_pct", 10.0)) / 100.0
        dp_cash = t_val * dp_pct
        financed = t_val - dp_cash

        gl.post_journal(m_start, "0020", "1200", dp_cash, f"HP Deposit: {fa['name']}")
        if financed > 0:
            gl.post_journal(
                m_start,
                "0020",
                "2300",
                financed,
                f"HP Facility Principal: {fa['name']}",
            )
            term = max(1, int(fa.get("term_months", 36)))
            m_principal = financed / term
            apr = float(fa.get("interest_rate", 5.0)) / 100.0
            for t in range(1, term + 1):
                m_target = m_start + t
                if m_target > horizon_months:
                    break
                interest = (financed - (m_principal * (t - 1))) * (apr / 12.0)
                gl.post_journal(
                    m_target,
                    "2300",
                    "1200",
                    m_principal,
                    f"HP Principal Pay: {fa['name']}",
                )
                gl.post_journal(
                    m_target, "8100", "1200", interest, f"HP Interest: {fa['name']}"
                )

    # 2. Monthly Ledger Operations
    ytd_ebt = {yr: 0.0 for yr in range(1, horizon_years + 1)}
    ytd_tax = {yr: 0.0 for yr in range(1, horizon_years + 1)}
    annual_final_tax = {yr: 0.0 for yr in range(1, horizon_years + 1)}

    vat_settle_months = [
        m for m in range(1, horizon_months + 1) if (m >= 5 and (m - 2) % 3 == 0)
    ]

    for m in range(1, horizon_months + 1):
        yr = ((m - 1) // 12) + 1

        # Revenue & Debtors
        for sale in state.get("sales", []):
            if sale.get("overrides", {}).get(f"M{str(m).zfill(2)}", 0.0) > 0:
                net_rev = float(sale["overrides"][f"M{str(m).zfill(2)}"])
            else:
                y_base = float(
                    sale.get(f"y{yr}_baseline", sale.get("y1_baseline", 0.0))
                )
                flex = (
                    (1.0 + (float(sale.get("flex_pct", 0.0)) / 100.0))
                    if yr > 1
                    else 1.0
                )
                crv = seasonality.get(
                    sale.get("seasonality", "Flat_Linear"), seasonality["Flat_Linear"]
                )
                net_rev = y_base * flex * crv[(m - 1) % 12]

            vat_rate = (
                0.20
                if "Standard" in sale.get("vat_rate_type", "Standard")
                else 0.05 if "Reduced" in sale.get("vat_rate_type", "") else 0.0
            )
            vat_val = net_rev * vat_rate
            gross_rev = net_rev + vat_val

            # Dr Debtors, Cr Sales, Cr VAT
            gl.post_journal(m, "1100", "4000", net_rev, "Trading Revenue Invoiced")
            if vat_val > 0:
                gl.post_journal(
                    m, "1100", "2200", vat_val, "Output VAT on Invoiced Sales"
                )

            delay_m = int(int(sale.get("payment_delay", 0)) / 30)
            # Cash collection clears debtors: Dr Bank, Cr Debtors
            gl.post_journal(
                m + delay_m, "1200", "1100", gross_rev, "Debtor Receipt Clearing"
            )

        # COGS & Direct Creditors
        for c in state.get("cogs", []):
            if c.get("overrides", {}).get(f"M{str(m).zfill(2)}", 0.0) > 0:
                net_cost = float(c["overrides"][f"M{str(m).zfill(2)}"])
            else:
                y_base = float(c.get(f"y{yr}_baseline", c.get("y1_baseline", 0.0)))
                flex = (
                    (1.0 + (float(c.get("flex_pct", 0.0)) / 100.0)) if yr > 1 else 1.0
                )
                crv = seasonality.get(
                    c.get("seasonality", "Flat_Linear"), seasonality["Flat_Linear"]
                )
                net_cost = y_base * flex * crv[(m - 1) % 12]

            vat_rate = (
                0.05
                if "Commercial Energy" in c.get("vat_rate_type", "")
                else (0.20 if "Standard" in c.get("vat_rate_type", "Standard") else 0.0)
            )
            vat_val = net_cost * vat_rate
            gross_cost = net_cost + vat_val

            is_staff = "staff" in c.get("name", "").lower()
            lag = 0 if is_staff else (1 if supplier_credit_days >= 30 else 0)

            # Dr COGS, Dr VAT (Input VAT relieves liability), Cr Trade Creditors
            gl.post_journal(m, "5000", "2100", net_cost, "COGS Incurred")
            if vat_val > 0:
                gl.post_journal(m, "2200", "2100", vat_val, "Input VAT on COGS")
            # Payment: Dr Trade Creditors, Cr Bank
            gl.post_journal(
                m + lag, "2100", "1200", gross_cost, "Trade Creditor Settlement"
            )

        # OPEX Overheads
        for op in state.get("opex", []):
            if "matrix_data" in op and f"Y{yr}" in op["matrix_data"]:
                net_op = float(op["matrix_data"][f"Y{yr}"][(m - 1) % 12])
            else:
                net_op = (
                    float(op.get(f"y{yr}_baseline", op.get("y1_baseline", 0.0))) / 12.0
                )

            vat_rate = (
                0.05
                if "Commercial Energy" in op.get("vat_rate_type", "")
                else (
                    0.20 if "Standard" in op.get("vat_rate_type", "Standard") else 0.0
                )
            )
            vat_val = net_op * vat_rate
            gross_op = net_op + vat_val

            gl.post_journal(
                m, "6000", "2100", net_op, f"Overhead Incurred: {op.get('name')}"
            )
            if vat_val > 0:
                gl.post_journal(
                    m,
                    "2200",
                    "2100",
                    vat_val,
                    f"Input VAT on Overhead: {op.get('name')}",
                )
            gl.post_journal(
                m + 1, "2100", "1200", gross_op, f"Overhead Paid: {op.get('name')}"
            )

        # Payroll & PAYE
        for pay in state.get("payroll", []):
            if (
                int(pay.get("start_month", 1))
                <= m
                <= min(int(pay.get("end_month", 60)), horizon_months)
            ):
                gross_sal = int(pay.get("headcount", 1)) * float(
                    pay.get("monthly_wage", 2000.0)
                )
                nic = gross_sal * nic_rate
                # Dr Staff Payroll (P&L), Cr Bank (Net pay)
                gl.post_journal(m, "7000", "1200", gross_sal, "Staff Net Wages Paid")
                # Dr Staff Payroll (P&L), Cr PAYE/NIC Liability
                gl.post_journal(m, "7000", "2210", nic, "Employer NIC Accrual")
                # Payment: Dr PAYE/NIC Liability, Cr Bank in following month
                gl.post_journal(m + 1, "2210", "1200", nic, "HMRC PAYE/NIC Payment")

        # Depreciation
        for outright in state.get("outright_capex", []):
            if int(outright.get("month", 1)) <= m:
                dep = (
                    float(outright.get("amount", 0.0))
                    * float(outright.get("depreciation_rate", 0.20))
                ) / 12.0
                gl.post_journal(
                    m, "8000", "0021", dep, f"Depr Direct CapEx: {outright['name']}"
                )

        for fin in state.get("financed_assets", []):
            if int(fin.get("month", 1)) <= m:
                dep = (
                    float(fin.get("amount", 0.0))
                    * float(fin.get("depreciation_rate", 0.15))
                ) / 12.0
                gl.post_journal(
                    m, "8000", "0021", dep, f"Depr Lease Asset: {fin['name']}"
                )

        # VAT Quarterly Settlement
        if m in vat_settle_months:
            vat_liability = gl.get_cumulative_balance("2200", m - 1)
            if vat_liability > 0.01:
                gl.post_journal(
                    m,
                    "2200",
                    "1200",
                    vat_liability,
                    "Quarterly VAT Return Payment to HMRC",
                )

        # Cumulative Annual Corporation Tax with Loss Release
        m_rev = gl.get_period_movement("4000", m)
        m_cogs = gl.get_period_movement("5000", m)
        m_opex = gl.get_period_movement("6000", m)
        m_pay = gl.get_period_movement("7000", m)
        m_dep = gl.get_period_movement("8000", m)
        m_int = gl.get_period_movement("8100", m)

        period_ebt = m_rev - (m_cogs + m_opex + m_pay + m_dep + m_int)
        ytd_ebt[yr] += period_ebt

        # Required cumulative provision (floored at 0)
        req_cum_tax = max(0.0, ytd_ebt[yr] * corp_tax_rate)
        tax_delta = round(req_cum_tax - ytd_tax[yr], 2)

        if tax_delta > 0.01:
            # Charge: Dr 9000 Tax Expense, Cr 2220 Tax Liability
            gl.post_journal(
                m, "9000", "2220", tax_delta, "Monthly Corp Tax Provision Accrual"
            )
            ytd_tax[yr] += tax_delta
        elif tax_delta < -0.01:
            # Loss month release: Dr 2220 Tax Liability, Cr 9000 Tax Expense
            release = abs(tax_delta)
            gl.post_journal(
                m, "2220", "9000", release, "Loss Month Tax Provision Release Credit"
            )
            ytd_tax[yr] -= release

    # Store finalized annual corporation tax for statutory 9-month lag discharge
    for yr in range(1, horizon_years + 1):
        annual_final_tax[yr] = ytd_tax[yr]

    corp_tax_pay_calendar = {1: 21, 2: 33, 3: 45, 4: 57}
    for yr, settle_m in corp_tax_pay_calendar.items():
        if settle_m <= horizon_months and annual_final_tax.get(yr, 0.0) > 0.01:
            gl.post_journal(
                settle_m,
                "2220",
                "1200",
                annual_final_tax[yr],
                f"Year {yr} Corporation Tax Discharge to HMRC",
            )

    return compile_financial_statements(gl, horizon_months)


# =========================================================================
# 🏛️ FINANCIAL STATEMENTS COMPILED DIRECTLY FROM TRIAL BALANCE
# =========================================================================


def compile_financial_statements(gl: AuditedGeneralLedger, horizon_months: int):
    months_labels = [f"M{str(i).zfill(2)}" for i in range(0, horizon_months + 1)]

    # 1. Profit & Loss Matrix
    pl_rows = [
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
    ]
    df_pl = pd.DataFrame(0.0, index=pl_rows, columns=months_labels)

    # 2. Cash Flow Matrix
    cf_rows = [
        "Trading Cash Collections (£)",
        "Equity Capital Funding Injections (£)",
        "Operational Cash Outflows (£)",
        "Corporation Tax Settlement Paid (£)",
        "HMRC VAT Settlement Paid (£)",
        "Net Trading Cash Movement (£)",
        "Closing Bank Cash Reserves (£)",
    ]
    df_cf = pd.DataFrame(0.0, index=cf_rows, columns=months_labels)

    # 3. Balance Sheet Matrix
    bs_rows = [
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
        "Trial Balance Checksum Balance",
    ]
    df_bs = pd.DataFrame(0.0, index=bs_rows, columns=months_labels)

    for m in range(0, horizon_months + 1):
        lbl = f"M{str(m).zfill(2)}"

        # P&L derived from period account movements
        rev = gl.get_period_movement("4000", m)
        cogs = gl.get_period_movement("5000", m)
        opex = gl.get_period_movement("6000", m)
        pay = gl.get_period_movement("7000", m)
        dep = gl.get_period_movement("8000", m)
        int_cost = gl.get_period_movement("8100", m)
        tax = gl.get_period_movement("9000", m)

        df_pl.at["Total Revenue (£)", lbl] = rev
        df_pl.at["Cost of Goods Sold (COGS) (£)", lbl] = cogs
        df_pl.at["Gross Profit Margin (£)", lbl] = rev - cogs
        df_pl.at["Operational Overheads (£)", lbl] = opex
        df_pl.at["Staff Payroll Overhead (£)", lbl] = pay
        df_pl.at["Depreciation Overhead (£)", lbl] = dep
        df_pl.at["Financing Interest Cost (£)", lbl] = int_cost
        ebit = rev - cogs - opex - pay - dep - int_cost
        df_pl.at["Net Operating Profit (EBIT)", lbl] = ebit
        df_pl.at["Corporation Tax Provision (£)", lbl] = tax
        df_pl.at["Profit After Tax (PAT) (£)", lbl] = ebit - tax

        # Cash Flow derived strictly from Bank account (1200) journal counterparts
        inflows_trading = sum(
            j["amount"]
            for j in gl.journal_entries
            if j["month"] == m
            and j["debit_code"] == "1200"
            and j["credit_code"] == "1100"
        )
        inflows_equity = sum(
            j["amount"]
            for j in gl.journal_entries
            if j["month"] == m
            and j["debit_code"] == "1200"
            and j["credit_code"] == "3000"
        )
        outflows_vat = sum(
            j["amount"]
            for j in gl.journal_entries
            if j["month"] == m
            and j["credit_code"] == "1200"
            and j["debit_code"] == "2200"
        )
        outflows_tax = sum(
            j["amount"]
            for j in gl.journal_entries
            if j["month"] == m
            and j["credit_code"] == "1200"
            and j["debit_code"] == "2220"
        )
        outflows_other = sum(
            j["amount"]
            for j in gl.journal_entries
            if j["month"] == m
            and j["credit_code"] == "1200"
            and j["debit_code"] not in ["2200", "2220"]
        )

        df_cf.at["Trading Cash Collections (£)", lbl] = inflows_trading
        df_cf.at["Equity Capital Funding Injections (£)", lbl] = inflows_equity
        df_cf.at["Operational Cash Outflows (£)", lbl] = outflows_other
        df_cf.at["Corporation Tax Settlement Paid (£)", lbl] = outflows_tax
        df_cf.at["HMRC VAT Settlement Paid (£)", lbl] = outflows_vat
        df_cf.at["Net Trading Cash Movement (£)", lbl] = (
            inflows_trading + inflows_equity
        ) - (outflows_other + outflows_tax + outflows_vat)
        closing_bank = gl.get_cumulative_balance("1200", m)
        df_cf.at["Closing Bank Cash Reserves (£)", lbl] = closing_bank

        # Balance Sheet derived from cumulative general ledger balances
        fa_orig = gl.get_cumulative_balance("0020", m)
        accum_dep = gl.get_cumulative_balance("0021", m)
        nbv = fa_orig - accum_dep
        debtors = gl.get_cumulative_balance("1100", m)
        total_assets = nbv + debtors + closing_bank

        df_bs.at["Fixed Infrastructure Assets (£)", lbl] = fa_orig
        df_bs.at["Accumulated Depreciation Reserve (£)", lbl] = accum_dep
        df_bs.at["Net Book Value Asset Worth (£)", lbl] = nbv
        df_bs.at["Trade Debtors Balance (£)", lbl] = debtors
        df_bs.at["Closing Bank Cash Reserves (£)", lbl] = closing_bank
        df_bs.at["Total Assets (£)", lbl] = total_assets

        creditors = gl.get_cumulative_balance("2100", m)
        vat_owing = gl.get_cumulative_balance("2200", m)
        tax_owing = gl.get_cumulative_balance("2220", m)
        paye_owing = gl.get_cumulative_balance("2210", m)
        debt_owing = gl.get_cumulative_balance("2300", m)
        total_liabs = creditors + vat_owing + tax_owing + paye_owing + debt_owing

        df_bs.at["Trade Creditors Balance (£)", lbl] = creditors
        df_bs.at["HMRC VAT Reserves Owing (£)", lbl] = vat_owing
        df_bs.at["Provision for Corporation Tax (£)", lbl] = tax_owing
        df_bs.at["HMRC PAYE Obligations Liability (£)", lbl] = paye_owing
        df_bs.at["Long Term Facility Debt Liability (£)", lbl] = debt_owing
        df_bs.at["Total Current & Long-Term Liabilities (£)", lbl] = total_liabs

        equity = gl.get_cumulative_balance("3000", m)
        cum_retained = sum(
            df_pl.at["Profit After Tax (PAT) (£)", f"M{str(i).zfill(2)}"]
            for i in range(1, m + 1)
        )

        df_bs.at["Shareholder Invested Equity Reserves (£)", lbl] = equity
        df_bs.at["Retained Earnings Accumulation (£)", lbl] = cum_retained

        total_liabs_and_equity = total_liabs + equity + cum_retained
        df_bs.at["Total Liabilities & Equity Reserves (£)", lbl] = (
            total_liabs_and_equity
        )

        # Formal Double-Entry Proof: Total Assets - (Total Liabilities + Equity) MUST EQUAL 0.00
        tb_checksum = round(total_assets - total_liabs_and_equity, 2)
        df_bs.at["Trial Balance Checksum Balance", lbl] = tb_checksum

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
        m_start, m_end = (idx * 12) + 1, (idx + 1) * 12
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
            "Checksum": df_bs.at["Trial Balance Checksum Balance", bs_col],
        }

    html_pl = "".join(
        f"<tr style='{'font-weight:bold; background:#f8fafc;' if k in ['Revenue','Gross','EBIT','PAT'] else ''}'><td>{lbl}</td>"
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
        f"<tr style='{'font-weight:bold; background:#f8fafc;' if k=='Closing' else ''}'><td>{lbl}</td>"
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
        f"<tr style='{'font-weight:bold; background:#f8fafc;' if k in ['TotalAssets','TotalLiabEquity','Checksum'] else ''}'><td>{lbl}</td>"
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
            ("Trial Balance Checksum Balance", "Checksum"),
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
                @bottom-left {{ content: "STRATA Suite // Statutory General Ledger Engine"; font-family: sans-serif; font-size: 8pt; color: #94a3b8; }}
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
            <p>Statutory {horizon_years}-Year Integrated Financial Projections (Trial Balance Audited)</p>
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
# 🎛️ WORKSPACE DISPLAY RENDERING CANVAS
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

active_data_context = st.session_state.get("active_data", {})
df_pl, df_cf, df_bs = execute_full_simulation(
    active_data_context, horizon_months=horizon_months
)

term_month_col = f"M{str(horizon_months).zfill(2)}"
closing_cash_array = df_cf.loc["Closing Bank Cash Reserves (£)"].astype(float).values
peak_cash = float(closing_cash_array.max())
lowest_cash = float(closing_cash_array.min())
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
        "Trial Balance Checksum Balance",
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
                        0.0, running_val - ((item["value"] * item["Rate"]) / 12.0)
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
            bal_rec = {"Facility": fin["name"], "Metric": "Total Outstanding (£)"}
            st_rec = {
                "Facility": fin["name"],
                "Metric": "Current Liabilities (<12m) (£)",
            }
            lt_rec = {"Facility": fin["name"], "Metric": "Non-Current Debt (>1yr) (£)"}

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
