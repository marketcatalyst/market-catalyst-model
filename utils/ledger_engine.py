# utils/ledger_engine.py
# STRATA SUITE PRODUCTION ENGINE // DOUBLE-ENTRY GENERAL LEDGER & SIMULATION CORE
# DECOUPLED SSOT ACCOUNTING ENGINE (ZERO UI DEPENDENCY)

import re
import pandas as pd

from utils.depreciation import calculate_monthly_depreciation
from utils.scenario_manager import (
    ENTRY_MODE_CURVE,
    ENTRY_MODE_FLAT,
    ENTRY_MODE_OVERRIDE,
)

CHART_OF_ACCOUNTS = {
    "1200": {"name": "Bank Current Account", "type": "Asset", "sign": 1},
    "1100": {"name": "Trade Debtors Control", "type": "Asset", "sign": 1},
    "0020": {"name": "Fixed Infrastructure Assets", "type": "Asset", "sign": 1},
    "0021": {
        "name": "Accumulated Depreciation Reserve",
        "type": "Contra-Asset",
        "sign": -1,
    },
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
    "3000": {"name": "Shareholder Invested Equity", "type": "Equity", "sign": -1},
    "3200": {"name": "Retained Earnings Accumulation", "type": "Equity", "sign": -1},
    "4000": {"name": "Gross Turnover Revenue", "type": "Income", "sign": -1},
    "5000": {"name": "Cost of Goods Sold (COGS)", "type": "Expense", "sign": 1},
    "6000": {"name": "Operational Overheads", "type": "Expense", "sign": 1},
    "7000": {"name": "Staff Payroll Overhead", "type": "Expense", "sign": 1},
    "8000": {"name": "Depreciation Expense", "type": "Expense", "sign": 1},
    "8100": {"name": "Financing Interest Cost", "type": "Expense", "sign": 1},
    "9000": {"name": "Corporation Tax Provision", "type": "TaxExpense", "sign": 1},
}

DEFAULT_SEASONALITY_CURVES = {
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


class AuditedGeneralLedger:
    def __init__(self, horizon_months: int = 36):
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
        return round((dr - cr) * sign, 2)

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
        val = (dr - cr) * sign
        return 0.0 if abs(val) < 0.005 else round(val, 2)

    def journal_sum(self, debit_code: str, credit_code: str, month: int) -> float:
        return sum(
            j["amount"]
            for j in self.journal_entries
            if j["month"] == month
            and j["debit_code"] == debit_code
            and j["credit_code"] == credit_code
        )


def sanitize_label(name: str) -> str:
    cleaned = re.sub(r"\[.*?\]|\(.*?\)", "", str(name))
    cleaned = re.sub(
        r"^(AI Scan|OCR|Ingested)\s*[:-]?\s*", "", cleaned, flags=re.IGNORECASE
    )
    cleaned = " ".join(cleaned.split())
    return cleaned if cleaned else str(name)


def collect_registered_assets(active_data: dict) -> list:
    """Single SSOT helper compiling both outright CapEx and financed HP assets."""
    assets = []
    for cap in active_data.get("outright_capex", []):
        assets.append(
            {
                "Name": sanitize_label(cap.get("name")),
                "Type": "Direct Purchase",
                "Cost": float(cap.get("amount", 0.0)),
                "Month": int(cap.get("month", 1)),
                "Rate": float(cap.get("depreciation_rate", 0.20)),
            }
        )
    for fin in active_data.get("financed_assets", []):
        assets.append(
            {
                "Name": sanitize_label(fin.get("name")),
                "Type": "Financed HP",
                "Cost": float(fin.get("amount", 0.0)),
                "Month": int(fin.get("month", 1)),
                "Rate": float(fin.get("depreciation_rate", 0.15)),
            }
        )
    return assets


def build_seasonality_profiles(custom_curves: dict = None) -> dict:
    seasonality = {k: list(v) for k, v in DEFAULT_SEASONALITY_CURVES.items()}
    if isinstance(custom_curves, dict):
        for k, v in custom_curves.items():
            seasonality[k] = v
    return seasonality


def get_exact_period_value(
    item_dict: dict, month_idx: int, yr_idx: int, seasonality_profiles: dict
) -> float:
    """
    Explicit Mode SSOT Period Resolver:
    1. 'Manual Monthly Override': Reads strictly from monthly overrides / matrix grids.
    2. 'Flat Linear Baseline': Evenly divides the annual baseline across 12 months.
    3. 'Annual Baseline + Monthly Distribution Curve': Applies the selected curve distribution weights.
    """
    entry_mode = item_dict.get("entry_mode", ENTRY_MODE_CURVE)
    if entry_mode == "Annual Baseline + Seasonality Curve":
        entry_mode = ENTRY_MODE_CURVE

    m_offset = (month_idx - 1) % 12
    m_lbl = f"M{str(month_idx).zfill(2)}"

    if entry_mode == ENTRY_MODE_OVERRIDE:
        overrides = item_dict.get("overrides", {})
        if m_lbl in overrides and str(overrides[m_lbl]).strip() != "":
            try:
                return float(overrides[m_lbl])
            except (ValueError, TypeError):
                pass
        matrix = item_dict.get("matrix_data", {})
        y_key = f"Y{yr_idx}"
        if isinstance(matrix, dict) and y_key in matrix:
            arr = matrix[y_key]
            if isinstance(arr, list) and len(arr) > m_offset:
                try:
                    val = arr[m_offset]
                    if val is not None and str(val).strip() != "":
                        return float(val)
                except (ValueError, TypeError):
                    pass
        return 0.0

    elif entry_mode == ENTRY_MODE_FLAT:
        y_base = float(
            item_dict.get(f"y{yr_idx}_baseline", item_dict.get("y1_baseline", 0.0))
        )
        flex = (
            (1.0 + (float(item_dict.get("flex_pct", 0.0)) / 100.0))
            if yr_idx > 1
            else 1.0
        )
        return (y_base * flex) / 12.0

    else:
        y_base = float(
            item_dict.get(f"y{yr_idx}_baseline", item_dict.get("y1_baseline", 0.0))
        )
        flex = (
            (1.0 + (float(item_dict.get("flex_pct", 0.0)) / 100.0))
            if yr_idx > 1
            else 1.0
        )
        season_name = item_dict.get("seasonality", "Flat_Linear")
        crv = seasonality_profiles.get(season_name, [1 / 12] * 12)
        return y_base * flex * crv[m_offset]


def audit_ingestion_completeness(state: dict, horizon_years: int = 3):
    warnings = []
    aggregation_notes = {"Sales": [], "COGS": [], "OPEX": [], "Payroll": []}

    sales = state.get("sales", [])
    if not sales:
        warnings.append(
            "⚠️ CRITICAL: No Sales Revenue vectors found in active scenario."
        )
    for s in sales:
        name = sanitize_label(s.get("name", "Unnamed Sales Vector"))
        y1 = float(s.get("y1_baseline", 0.0))
        y2 = float(s.get("y2_baseline", 0.0))
        y3 = float(s.get("y3_baseline", 0.0))
        aggregation_notes["Sales"].append(
            {
                "Line Item": name,
                "Entry Mode": s.get("entry_mode", ENTRY_MODE_CURVE),
                "VAT Profile": s.get("vat_rate_type", "Standard 20%"),
                "Year 1": y1,
                "Year 2": y2,
                "Year 3": y3,
            }
        )

    cogs = state.get("cogs", [])
    for c in cogs:
        name = sanitize_label(c.get("name", "Unnamed COGS Vector"))
        y1 = float(c.get("y1_baseline", 0.0))
        y2 = float(c.get("y2_baseline", 0.0))
        y3 = float(c.get("y3_baseline", 0.0))
        aggregation_notes["COGS"].append(
            {
                "Line Item": name,
                "Entry Mode": c.get("entry_mode", ENTRY_MODE_CURVE),
                "VAT Profile": c.get("vat_rate_type", "Standard 20%"),
                "Year 1": y1,
                "Year 2": y2,
                "Year 3": y3,
            }
        )

    opex = state.get("opex", [])
    for op in opex:
        name = sanitize_label(op.get("name", "Unnamed Overhead"))
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
        name = sanitize_label(p.get("name", "Unnamed Role"))
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


def execute_full_simulation(
    state: dict,
    horizon_months: int = 36,
    sic_profile: dict = None,
    custom_curves: dict = None,
    vector_couplings: list = None,
):
    gl = AuditedGeneralLedger(horizon_months=horizon_months)
    horizon_years = horizon_months // 12
    sic = sic_profile or {}
    nic_rate = float(sic.get("base_er_nic_rate", 0.138))
    corp_tax_rate = float(sic.get("corp_tax_rate", 0.19))
    supplier_credit_days = int(sic.get("supplier_credit_days", 30))

    seasonality = build_seasonality_profiles(custom_curves)
    couplings = vector_couplings or []

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
                <= min(int(pay.get("end_month", 120)), horizon_months)
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
                dep = calculate_monthly_depreciation(outright, m)
                gl.post_journal(
                    m,
                    "8000",
                    "0021",
                    dep,
                    f"Depreciation Direct CapEx: {outright.get('name')}",
                )

        for fin in state.get("financed_assets", []):
            if int(fin.get("month", 1)) <= m:
                dep = calculate_monthly_depreciation(fin, m)
                gl.post_journal(
                    m,
                    "8000",
                    "0021",
                    dep,
                    f"Depreciation Lease Asset: {fin.get('name')}",
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

    for yr in range(1, horizon_years + 1):
        settle_m = (yr * 12) + 9
        if settle_m <= horizon_months and annual_final_tax.get(yr, 0.0) > 0.01:
            gl.post_journal(
                settle_m,
                "2220",
                "1200",
                annual_final_tax[yr],
                f"Year {yr} Corporation Tax Discharge to HMRC",
            )

    df_pl, df_cf, df_bs = compile_financial_statements(
        gl, horizon_months, state=state, seasonality_profiles=seasonality
    )
    return df_pl, df_cf, df_bs, gl


def compile_financial_statements(
    gl: AuditedGeneralLedger,
    horizon_months: int,
    state: dict = None,
    seasonality_profiles: dict = None,
):
    months_labels = [f"M{str(i).zfill(2)}" for i in range(0, horizon_months + 1)]
    seasonality = seasonality_profiles or build_seasonality_profiles()

    sales_vectors = state.get("sales", []) if state else []
    sales_row_names = [
        sanitize_label(s.get("name", "Sales Vector")) for s in sales_vectors
    ]
    if not sales_row_names:
        sales_row_names = ["Total Revenue (£)"]

    pl_rows = sales_row_names + [
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
        yr = ((m - 1) // 12) + 1 if m > 0 else 1

        total_rev_m = 0.0
        if sales_vectors and m > 0:
            for s in sales_vectors:
                s_name = sanitize_label(s.get("name", "Sales Vector"))
                s_val = get_exact_period_value(s, m, yr, seasonality)
                df_pl.at[s_name, lbl] = s_val
                total_rev_m += s_val
        elif m == 0:
            total_rev_m = 0.0
        else:
            total_rev_m = gl.get_period_movement("4000", m)

        df_pl.at["Total Revenue (£)", lbl] = total_rev_m
        rev = total_rev_m

        cogs = gl.get_period_movement("5000", m)
        opex = gl.get_period_movement("6000", m)
        pay = gl.get_period_movement("7000", m)
        dep = gl.get_period_movement("8000", m)
        int_cost = gl.get_period_movement("8100", m)
        tax = gl.get_period_movement("9000", m)

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

        inflows_trading = gl.journal_sum("1200", "1100", m)
        inflows_equity = gl.journal_sum("1200", "3000", m)
        outflows_vat = gl.journal_sum("1200", "2200", m)
        outflows_tax = gl.journal_sum("1200", "2220", m)
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

    for col in df_bs.columns:
        for idx in df_bs.index:
            if abs(df_bs.at[idx, col]) < 0.50:
                df_bs.at[idx, col] = 0.00

    return df_pl, df_cf, df_bs
