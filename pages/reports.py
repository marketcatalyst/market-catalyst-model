# pages/reports.py
# STRATA SUITE PRODUCTION ENGINE // THREE-WAY REPORTING CANVAS v9.8.0-STATUTORY
# WINFORECAST GROUND TRUTH // MODERN GOOGLE-GENAI SDK // UNIFIED SCENARIO CONTROL DESK

import os
import sys
import re
from io import BytesIO
import pandas as pd
import streamlit as st

# Inject project root into Python system path for pages/ directory imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Centralized Scenario Persistence Engine
from utils.scenario_manager import render_global_scenario_sidebar

# Modern Google GenAI SDK
try:
    from google import genai

    GENAI_AVAILABLE = True
except ImportError:
    genai = None
    GENAI_AVAILABLE = False

try:
    from xhtml2pdf import pisa

    PDF_ENGINE_AVAILABLE = True
except ImportError:
    pisa = None
    PDF_ENGINE_AVAILABLE = False

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
    if st.button("🔑 Return to Home Portal & Sign In", width="stretch"):
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
        sign = CHART_OF_ACCOUNTS[nominal_code]["sign"]
        return (dr - cr) * sign

    def get_cumulative_balance(self, nominal_code: str, month_limit: int) -> float:
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


def get_exact_period_value(
    item_dict: dict, month_idx: int, yr_idx: int, seasonality_profiles: dict
) -> float:
    m_lbl = f"M{str(month_idx).zfill(2)}"

    if "overrides" in item_dict and isinstance(item_dict["overrides"], dict):
        if m_lbl in item_dict["overrides"]:
            val = item_dict["overrides"][m_lbl]
            try:
                f_val = float(val)
                if f_val > 0.0:
                    return f_val
            except (ValueError, TypeError):
                pass

    if "matrix_data" in item_dict and isinstance(item_dict["matrix_data"], dict):
        y_key = f"Y{yr_idx}"
        if y_key in item_dict["matrix_data"]:
            month_offset = (month_idx - 1) % 12
            arr = item_dict["matrix_data"][y_key]
            if isinstance(arr, list) and len(arr) > month_offset:
                try:
                    f_val = float(arr[month_offset])
                    if f_val > 0.0:
                        return f_val
                except (ValueError, TypeError):
                    pass

    y_base = float(
        item_dict.get(f"y{yr_idx}_baseline", item_dict.get("y1_baseline", 0.0))
    )
    flex = (
        (1.0 + (float(item_dict.get("flex_pct", 0.0)) / 100.0)) if yr_idx > 1 else 1.0
    )
    season_name = item_dict.get("seasonality", "Flat_Linear")
    crv = seasonality_profiles.get(
        season_name, seasonality_profiles.get("Flat_Linear", [1 / 12] * 12)
    )
    return y_base * flex * crv[(month_idx - 1) % 12]


def audit_ingestion_completeness(state: dict, horizon_years: int = 3):
    warnings = []
    aggregation_notes = {"Sales": [], "COGS": [], "OPEX": [], "Payroll": []}

    sales = state.get("sales", [])
    if not sales:
        warnings.append(
            "⚠️ CRITICAL: No Sales Revenue vectors found in active scenario."
        )
    for s in sales:
        name = s.get("name", "Unnamed Sales Vector")
        y1 = float(s.get("y1_baseline", 0.0))
        y2 = float(s.get("y2_baseline", 0.0))
        y3 = float(s.get("y3_baseline", 0.0))
        has_ov = any(
            float(v) > 0 for v in s.get("overrides", {}).values() if str(v).strip()
        )
        if y1 == 0 and y2 == 0 and y3 == 0 and not has_ov:
            warnings.append(
                f"⚠️ Vector '{name}' in Sales has zero revenue across all years and overrides."
            )
        aggregation_notes["Sales"].append(
            {
                "Line Item": name,
                "VAT Profile": s.get("vat_rate_type", "Standard 20%"),
                "Payment Terms": f"{s.get('payment_delay', 0)} Days Lag",
                "Year 1": y1,
                "Year 2": y2,
                "Year 3": y3,
            }
        )

    cogs = state.get("cogs", [])
    for c in cogs:
        name = c.get("name", "Unnamed COGS Vector")
        y1 = float(c.get("y1_baseline", 0.0))
        y2 = float(c.get("y2_baseline", 0.0))
        y3 = float(c.get("y3_baseline", 0.0))
        aggregation_notes["COGS"].append(
            {
                "Line Item": name,
                "VAT Profile": c.get("vat_rate_type", "Standard 20%"),
                "Cost Nature": (
                    "Direct Personnel"
                    if "staff" in name.lower()
                    else "Direct Operating Cost"
                ),
                "Year 1": y1,
                "Year 2": y2,
                "Year 3": y3,
            }
        )

    opex = state.get("opex", [])
    for op in opex:
        name = op.get("name", "Unnamed Overhead")
        y1 = float(op.get("y1_baseline", 0.0))
        y2 = float(op.get("y2_baseline", 0.0))
        y3 = float(op.get("y3_baseline", 0.0))
        aggregation_notes["OPEX"].append(
            {
                "Line Item": name,
                "VAT Profile": op.get("vat_rate_type", "Standard 20%"),
                "Year 1": y1,
                "Year 2": y2,
                "Year 3": y3,
            }
        )

    payroll = state.get("payroll", [])
    for p in payroll:
        name = p.get("name", "Unnamed Role")
        hc = int(p.get("headcount", 1))
        mw = float(p.get("monthly_wage", 0.0))
        ann = hc * mw * 12
        aggregation_notes["Payroll"].append(
            {
                "Line Item": f"{name} (x{hc})",
                "Monthly Wage": f"£{mw:,.2f}",
                "Annual Cost": ann,
            }
        )

    return warnings, aggregation_notes


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

    couplings = st.session_state.get("vector_couplings", [])

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

        gl.post_journal(
            m_start, "0020", "1200", dp_cash, f"HP Deposit: {fa.get('name')}"
        )
        if financed > 0:
            gl.post_journal(
                m_start,
                "0020",
                "2300",
                financed,
                f"HP Facility Principal: {fa.get('name')}",
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
                    f"HP Principal Pay: {fa.get('name')}",
                )
                gl.post_journal(
                    m_target, "8100", "1200", interest, f"HP Interest: {fa.get('name')}"
                )

    ytd_ebt = {yr: 0.0 for yr in range(1, horizon_years + 1)}
    ytd_tax = {yr: 0.0 for yr in range(1, horizon_years + 1)}
    annual_final_tax = {yr: 0.0 for yr in range(1, horizon_years + 1)}

    vat_settle_months = [
        m for m in range(1, horizon_months + 1) if (m >= 5 and (m - 2) % 3 == 0)
    ]

    for m in range(1, horizon_months + 1):
        yr = ((m - 1) // 12) + 1
        sales_computed_map = {}

        for sale in state.get("sales", []):
            net_rev = get_exact_period_value(sale, m, yr, seasonality)
            sales_computed_map[sale.get("name", "")] = net_rev

            vat_rate = (
                0.20
                if "Standard" in sale.get("vat_rate_type", "Standard")
                else (0.05 if "Reduced" in sale.get("vat_rate_type", "") else 0.0)
            )
            vat_val = net_rev * vat_rate
            gross_rev = net_rev + vat_val

            gl.post_journal(m, "1100", "4000", net_rev, "Trading Revenue Invoiced")
            if vat_val > 0:
                gl.post_journal(
                    m, "1100", "2200", vat_val, "Output VAT on Invoiced Sales"
                )

            delay_m = int(int(sale.get("payment_delay", 0)) / 30)
            gl.post_journal(
                m + delay_m, "1200", "1100", gross_rev, "Debtor Receipt Clearing"
            )

        for c in state.get("cogs", []):
            matched_coupling = next(
                (cp for cp in couplings if cp.get("cogs_target") == c.get("name")), None
            )
            if (
                matched_coupling
                and matched_coupling.get("sales_driver") in sales_computed_map
            ):
                net_cost = sales_computed_map[
                    matched_coupling["sales_driver"]
                ] * matched_coupling.get("coefficient", 0.0)
            else:
                net_cost = get_exact_period_value(c, m, yr, seasonality)

            vat_rate = (
                0.05
                if "Commercial Energy" in c.get("vat_rate_type", "")
                else (0.20 if "Standard" in c.get("vat_rate_type", "Standard") else 0.0)
            )
            vat_val = net_cost * vat_rate
            gross_cost = net_cost + vat_val

            is_staff = "staff" in c.get("name", "").lower()
            lag = 0 if is_staff else (1 if supplier_credit_days >= 30 else 0)

            gl.post_journal(m, "5000", "2100", net_cost, "COGS Incurred")
            if vat_val > 0:
                gl.post_journal(m, "2200", "2100", vat_val, "Input VAT on COGS")
            gl.post_journal(
                m + lag, "2100", "1200", gross_cost, "Trade Creditor Settlement"
            )

        for op in state.get("opex", []):
            net_op = get_exact_period_value(op, m, yr, seasonality)
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
                gl.post_journal(m, "7000", "1200", gross_sal, "Staff Net Wages Paid")
                gl.post_journal(m, "7000", "2210", nic, "Employer NIC Accrual")
                gl.post_journal(m + 1, "2210", "1200", nic, "HMRC PAYE/NIC Payment")

        for outright in state.get("outright_capex", []):
            if int(outright.get("month", 1)) <= m:
                dep = (
                    float(outright.get("amount", 0.0))
                    * float(outright.get("depreciation_rate", 0.20))
                ) / 12.0
                gl.post_journal(
                    m, "8000", "0021", dep, f"Depr Direct CapEx: {outright.get('name')}"
                )

        for fin in state.get("financed_assets", []):
            if int(fin.get("month", 1)) <= m:
                dep = (
                    float(fin.get("amount", 0.0))
                    * float(fin.get("depreciation_rate", 0.15))
                ) / 12.0
                gl.post_journal(
                    m, "8000", "0021", dep, f"Depr Lease Asset: {fin.get('name')}"
                )

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

        m_rev = gl.get_period_movement("4000", m)
        m_cogs = gl.get_period_movement("5000", m)
        m_opex = gl.get_period_movement("6000", m)
        m_pay = gl.get_period_movement("7000", m)
        m_dep = gl.get_period_movement("8000", m)
        m_int = gl.get_period_movement("8100", m)

        period_ebt = m_rev - (m_cogs + m_opex + m_pay + m_dep + m_int)
        ytd_ebt[yr] += period_ebt

        req_cum_tax = max(0.0, ytd_ebt[yr] * corp_tax_rate)
        tax_delta = round(req_cum_tax - ytd_tax[yr], 2)

        if tax_delta > 0.01:
            gl.post_journal(
                m, "9000", "2220", tax_delta, "Monthly Corp Tax Provision Accrual"
            )
            ytd_tax[yr] += tax_delta
        elif tax_delta < -0.01:
            release = abs(tax_delta)
            gl.post_journal(
                m, "2220", "9000", release, "Loss Month Tax Provision Release Credit"
            )
            ytd_tax[yr] -= release

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


def compile_financial_statements(gl: AuditedGeneralLedger, horizon_months: int):
    months_labels = [f"M{str(i).zfill(2)}" for i in range(0, horizon_months + 1)]

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
        df_bs.at["Trial Balance Checksum Balance", lbl] = round(
            total_assets - total_liabs_and_equity, 2
        )

    return df_pl, df_cf, df_bs


def format_df_for_csv(
    df: pd.DataFrame, index_title: str = "Financial Line Item (£)"
) -> bytes:
    df_clean = df.copy()
    for col in df_clean.columns:
        df_clean[col] = df_clean[col].apply(
            lambda x: (
                f"{float(x):.2f}" if pd.notnull(x) and str(x).strip() != "" else "0.00"
            )
        )
    df_clean.index.name = index_title
    return df_clean.to_csv(index=True).encode("utf-8-sig")


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
) -> bytes:
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
        f"<tr style='{'font-weight:bold; background-color:#f1f5f9;' if k in ['Revenue','Gross','EBIT','PAT'] else ''}'><td>{lbl}</td>"
        + "".join(
            f"<td align='right'>£{annual_pl[y][k]:,.2f}</td>" for y in years_labels
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
        f"<tr style='{'font-weight:bold; background-color:#f1f5f9;' if k=='Closing' else ''}'><td>{lbl}</td>"
        + "".join(
            f"<td align='right'>£{annual_cf[y][k]:,.2f}</td>" for y in years_labels
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
        f"<tr style='{'font-weight:bold; background-color:#f1f5f9;' if k in ['TotalAssets','TotalLiabEquity','Checksum'] else ''}'><td>{lbl}</td>"
        + "".join(
            f"<td align='right'>{'£' if k != 'Checksum' else ''}{annual_bs[y][k]:,.2f}</td>"
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
                size: a4 portrait;
                margin: 1.5cm;
                @frame footer {{
                    -pdf-frame-content: footerContent;
                    bottom: 0.5cm;
                    margin-left: 1.5cm;
                    margin-right: 1.5cm;
                    height: 1cm;
                }}
            }}
            body {{ font-family: Helvetica, Arial, sans-serif; color: #0f172a; font-size: 8pt; }}
            .banner {{ background-color: #1e3a8a; color: #ffffff; padding: 12px; margin-bottom: 12px; }}
            .banner h1 {{ margin: 0; font-size: 14pt; }}
            .banner p {{ margin: 3px 0 0 0; font-size: 7.5pt; color: #93c5fd; }}
            .ctx {{ margin-bottom: 12px; font-size: 8.5pt; font-weight: bold; color: #334155; }}
            h2 {{ color: #1e3a8a; font-size: 10pt; margin-top: 14px; margin-bottom: 6px; border-bottom: 1px solid #3b82f6; padding-bottom: 2px; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 12px; }}
            th {{ background-color: #f8fafc; color: #475569; padding: 4px 6px; font-size: 7.5pt; border-bottom: 1px solid #cbd5e1; text-align: left; }}
            td {{ padding: 4px 6px; border-bottom: 1px solid #e2e8f0; font-size: 7.5pt; }}
        </style>
    </head>
    <body>
        <div id="footerContent" align="right" style="font-size: 7pt; color: #94a3b8;">
            STRATA Suite // Statutory General Ledger Engine &nbsp;|&nbsp; Page <pdf:pagenumber> of <pdf:pagecount>
        </div>

        <div class="banner">
            <h1>STRATA EXECUTIVE FINANCIAL REPORT PACK</h1>
            <p>Statutory {horizon_years}-Year Integrated Financial Projections (Trial Balance Audited)</p>
        </div>
        <div class="ctx">Project: {project_name} | Accounting Horizon: {horizon_years} Operating Years ({total_months} Months)</div>
        
        <table>
            <thead><tr><th>Target Core Metric</th><th align="right">Projected Value Position</th></tr></thead>
            <tbody>
                <tr><td>Peak Cumulative Cash Reserves</td><td align="right">£{peak_cash:,.2f}</td></tr>
                <tr><td>Maximum Working Capital Trough</td><td align="right">£{lowest_cash:,.2f}</td></tr>
                <tr><td>Year {horizon_years} Terminal Retained Equity Worth</td><td align="right">£{horizon_worth:,.2f}</td></tr>
            </tbody>
        </table>

        <h2>Executive CFO Narrative Synthesis</h2>
        <div style="margin-bottom: 15px;">{clean_insight}</div>

        <pdf:nextpage />

        <h2>Profit & Loss Forecast Statement (Years 1 to {horizon_years})</h2>
        <table><thead><tr><th>Performance Component</th>{th_headers}</tr></thead><tbody>{html_pl}</tbody></table>

        <h2>Cash Flow Forecast Statement (Years 1 to {horizon_years})</h2>
        <table><thead><tr><th>Liquidity Flow Component</th>{th_headers}</tr></thead><tbody>{html_cf}</tbody></table>

        <h2>Balance Sheet Capital Statement (Years 1 to {horizon_years})</h2>
        <table><thead><tr><th>Ledger Balance Structure</th>{th_headers}</tr></thead><tbody>{html_bs}</tbody></table>
    </body>
    </html>
    """

    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_template, dest=pdf_buffer)
    if pisa_status.err:
        raise Exception(f"xhtml2pdf encountered an error code: {pisa_status.err}")
    return pdf_buffer.getvalue()


# =========================================================================
# 🎛️ WORKSPACE DISPLAY RENDERING CANVAS
# =========================================================================

st.title("📊 Performance & Reporting Summary Pack")
st.caption(
    f"Active Scenario Context: `{st.session_state.get('active_project_name', 'Unsaved_Draft_Scenario')}`"
)
st.page_link("pages/app.py", label="✍️ Return to Data Entry Panel")
st.markdown("---")

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

warnings_list, agg_breakdowns = audit_ingestion_completeness(
    active_data_context, horizon_years
)
if warnings_list:
    for w in warnings_list:
        st.warning(w)

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

# =========================================================================
# 📥 PRODUCTION EXPORT CONTROLS (WIDTH='STRETCH' COMPLIANT)
# =========================================================================
st.subheader("📥 Executive Report Pack Export Controls")
exp_col1, exp_col2, exp_col3 = st.columns(3)

with exp_col1:
    clean_pl_bytes = format_df_for_csv(
        df_pl_view, index_title="Profit & Loss Account (£)"
    )
    st.download_button(
        "📥 Download Profit & Loss CSV",
        data=clean_pl_bytes,
        file_name=f"STRATA_PL_{horizon_years}Yr_Sensitised.csv",
        mime="text/csv",
        width="stretch",
    )

with exp_col2:
    clean_cf_bytes = format_df_for_csv(df_cf_view, index_title="Cash Flow Account (£)")
    st.download_button(
        "📥 Download Cash Flow CSV",
        data=clean_cf_bytes,
        file_name=f"STRATA_CashFlow_{horizon_years}Yr_Sensitised.csv",
        mime="text/csv",
        width="stretch",
    )

with exp_col3:
    clean_bs_bytes = format_df_for_csv(
        df_bs_view, index_title="Balance Sheet Account (£)"
    )
    st.download_button(
        "📥 Download Balance Sheet CSV",
        data=clean_bs_bytes,
        file_name=f"STRATA_BalanceSheet_{horizon_years}Yr_Sensitised.csv",
        mime="text/csv",
        width="stretch",
    )

with st.expander(
    "📋 Statutory Notes & Analysis of Aggregated Performance Lines", expanded=True
):
    st.caption(
        "Detailed line-item disclosures showing exact vector compositions of aggregated P&L rows."
    )

    an_col1, an_col2 = st.columns(2)
    with an_col1:
        st.markdown("##### 1. Total Turnover Revenue Vectors Composition")
        if agg_breakdowns["Sales"]:
            df_sales_notes = pd.DataFrame(agg_breakdowns["Sales"]).set_index(
                "Line Item"
            )
            st.dataframe(
                df_sales_notes.style.format(
                    {"Year 1": "£{:,.2f}", "Year 2": "£{:,.2f}", "Year 3": "£{:,.2f}"}
                ),
                width="stretch",
            )
        else:
            st.info("No active sales vectors ingested.")

    with an_col2:
        st.markdown("##### 2. Direct Cost of Goods Sold (COGS) Breakdown")
        if agg_breakdowns["COGS"]:
            df_cogs_notes = pd.DataFrame(agg_breakdowns["COGS"]).set_index("Line Item")
            st.dataframe(
                df_cogs_notes.style.format(
                    {"Year 1": "£{:,.2f}", "Year 2": "£{:,.2f}", "Year 3": "£{:,.2f}"}
                ),
                width="stretch",
            )
        else:
            st.info("No active direct COGS vectors ingested.")

    an_col3, an_col4 = st.columns(2)
    with an_col3:
        st.markdown("##### 3. Operational Overheads (OPEX) Composition")
        if agg_breakdowns["OPEX"]:
            df_opex_notes = pd.DataFrame(agg_breakdowns["OPEX"]).set_index("Line Item")
            st.dataframe(
                df_opex_notes.style.format(
                    {"Year 1": "£{:,.2f}", "Year 2": "£{:,.2f}", "Year 3": "£{:,.2f}"}
                ),
                width="stretch",
            )
        else:
            st.info("No overhead expense lines registered.")

    with an_col4:
        st.markdown("##### 4. Salaried Personnel & Payroll Obligations")
        if agg_breakdowns["Payroll"]:
            df_pay_notes = pd.DataFrame(agg_breakdowns["Payroll"]).set_index(
                "Line Item"
            )
            st.dataframe(
                df_pay_notes.style.format({"Annual Cost": "£{:,.2f}"}), width="stretch"
            )
        else:
            st.info(
                "No administrative payroll items registered (direct court/canteen staff are allocated to COGS)."
            )

st.markdown("---")

# =========================================================================
# 🧠 MODERN GEMINI AI SYNTHESIS (google-genai SDK)
# =========================================================================
st.markdown("### 🧠 Gemini AI Executive Management Pack Synthesis")
if "cached_ai_analysis" not in st.session_state:
    st.session_state["cached_ai_analysis"] = ""

if st.button(
    "🤖 Generate AI Executive Summary Report & Compile PDF Pack", width="stretch"
):
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        st.error("❌ Configuration Error: GEMINI_API_KEY credential missing.")
    elif not GENAI_AVAILABLE:
        st.error("❌ google-genai library missing. Run `pip install google-genai`.")
    else:
        with st.spinner("🤖 Analytical Engine scanning active matrices..."):
            try:
                client = genai.Client(api_key=api_key)
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
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
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

    if not PDF_ENGINE_AVAILABLE:
        st.warning(
            "⚠️ PDF generation engine not installed. Run `pip install xhtml2pdf`."
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
                width="stretch",
            )
        except Exception as pdf_err:
            st.error(f"PDF binary compiler mismatch: {str(pdf_err)}")

st.markdown("---")

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
        width="stretch",
    )
    st.markdown("#### Cash Flow Statement (£)")
    st.dataframe(
        df_cf_view.style.format("{:,.2f}").apply(highlight_totals, axis=1),
        width="stretch",
    )
    st.markdown("#### Balance Sheet Ledger (£)")
    st.dataframe(
        df_bs_view.style.format("{:,.2f}").apply(highlight_totals, axis=1),
        width="stretch",
    )

with t2:
    st.markdown("### 🚜 Dynamic Fixed Asset Depreciation Ledger")
    fa_rows = []
    for outright in active_data_context.get("outright_capex", []):
        fa_rows.append(
            {
                "Asset Item": outright.get("name"),
                "Type": "Direct Purchase",
                "value": float(outright.get("amount", 0.0)),
                "Month": int(outright.get("month", 1)),
                "Rate": float(outright.get("depreciation_rate", 0.20)),
            }
        )
    for fin in active_data_context.get("financed_assets", []):
        fa_rows.append(
            {
                "Asset Item": fin.get("name"),
                "Type": "Financed HP",
                "value": float(fin.get("amount", 0.0)),
                "Month": int(fin.get("month", 1)),
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
            width="stretch",
        )
    else:
        st.info("No fixed capital assets registered in active scenario.")

with t3:
    st.markdown("### 🏛️ Chronological Liability Allocation Ledger")
    if active_data_context.get("financed_assets"):
        loan_rows = []
        for fin in active_data_context["financed_assets"]:
            m_start = int(fin.get("month", 1))
            fin_bal = float(fin.get("amount", 0.0)) * (
                1.0 - (float(fin.get("deposit_pct", 10.0)) / 100.0)
            )
            term = max(1, int(fin.get("term_months", 36)))
            monthly_principal = fin_bal / term
            bal_rec = {"Facility": fin.get("name"), "Metric": "Total Outstanding (£)"}
            st_rec = {
                "Facility": fin.get("name"),
                "Metric": "Current Liabilities (<12m) (£)",
            }
            lt_rec = {
                "Facility": fin.get("name"),
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
            width="stretch",
        )
    else:
        st.info("No long-term debt facilities registered in active scenario.")

# =========================================================================
# 🧭 FIXED SIDEBAR COMPASS & UNIFIED SCENARIO CONTROLS
# =========================================================================
st.sidebar.markdown("### Compass Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link(
    "pages/1_Data_Ingestion_Gateway.py", label="📥 Data Ingestion Gateway"
)
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry Panel")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")

# Unified Global Scenario Manager
render_global_scenario_sidebar()
