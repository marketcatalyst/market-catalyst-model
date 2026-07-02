# pages/reports.py
# STRATA SUITE PRODUCTION ENGINE // THREE-WAY REPORTING CANVAS v7.3.5-PRODUCTION

import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
from weasyprint import HTML  # 🚀 SYSTEMS RE-ENGINEERED: Upgraded to WeasyPrint

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
    if st.button("🔑 Return to Home Portal & Sign In", use_container_width=True):
        st.switch_page("home.py")
    st.stop()


# =========================================================================
# 🏛️ SYSTEM COMPILER FUNCTION: WEASYPRINT INDUSTRIAL EXPORTER
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
):
    """Generates an executive board-ready HTML template and compiles it to PDF via WeasyPrint."""

    # Clean down special character hooks safely
    clean_insight = (
        insight_text.replace("\n", "<br>")
        .replace("â€™", "'")
        .replace("â€˜", "'")
        .replace("â€œ", '"')
        .replace("â€ ", '"')
    )

    # 1. GENERATE THE 5-YEAR ANNUAL PRIMARY STATEMENTS HTML
    years_labels = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    annual_pl_data = {}
    annual_cf_data = {}
    annual_bs_data = {}

    for idx, yr in enumerate(years_labels):
        m_start = (idx * 12) + 1
        m_end = (idx + 1) * 12
        cols = [f"M{str(i).zfill(2)}" for i in range(m_start, m_end + 1)]
        bs_col = f"M{str(m_end).zfill(2)}"

        # Profit & Loss Aggregation
        annual_pl_data[yr] = {
            "Revenue": df_pl[cols].loc["Total Revenue (£)"].sum(),
            "COGS": df_pl[cols].loc["Cost of Goods Sold (COGS) (£)"].sum(),
            "Opex": df_pl[cols].loc["Operational Overheads (£)"].sum(),
            "Payroll": df_pl[cols].loc["Staff Payroll Overhead (£)"].sum(),
            "Depreciation": df_pl[cols].loc["Depreciation Overhead (£)"].sum(),
            "Interest": df_pl[cols].loc["Financing Interest Cost (£)"].sum(),
            "EBIT": df_pl[cols].loc["Net Operating Profit (EBIT)"].sum(),
        }

        # Cash Flow Aggregation
        annual_cf_data[yr] = {
            "Inflow": df_cf[cols].loc["Trading Cash Collections (£)"].sum(),
            "Equity": df_cf[cols].loc["Equity Capital Funding Injections (£)"].sum(),
            "Outflow": df_cf[cols].loc["Operational Cash Outflows (£)"].sum(),
            "Closing": df_cf.at["Closing Bank Cash Reserves (£)", bs_col],
        }

        # Balance Sheet Point-in-Time Positions
        annual_bs_data[yr] = {
            "Fixed": df_bs.at["Fixed Infrastructure Assets (£)", bs_col],
            "AccumDep": df_bs.at["Accumulated Depreciation Reserve (£)", bs_col],
            "NBV": df_bs.at["Net Book Value Asset Worth (£)", bs_col],
            "Debtors": df_bs.at["Trade Debtors Balance (£)", bs_col],
            "VAT": df_bs.at["HMRC VAT Reserves Owing (£)", bs_col],
            "PAYE": df_bs.at["HMRC PAYE Obligations Liability (£)", bs_col],
            "Debt": df_bs.at["Long Term Facility Debt Liability (£)", bs_col],
            "Equity": df_bs.at["Shareholder Invested Equity Reserves (£)", bs_col],
            "Retained": df_bs.at["Retained Earnings Accumulation (£)", bs_col],
        }

    # Build Primary Financial HTML Tables
    html_pl_rows = ""
    for row_lbl, key in [
        ("Total Revenue", "Revenue"),
        ("Cost of Goods Sold (COGS)", "COGS"),
        ("Operational Overheads", "Opex"),
        ("Staff Payroll Overhead", "Payroll"),
        ("Depreciation Overhead", "Depreciation"),
        ("Financing Interest Cost", "Interest"),
        ("Net Operating Profit (EBIT)", "EBIT"),
    ]:
        weight = (
            "font-weight: bold; background-color: #f8fafc;"
            if key in ["Revenue", "EBIT"]
            else ""
        )
        html_pl_rows += (
            f"<tr style='{weight}'><td>{row_lbl}</td>"
            + "".join(
                [
                    f"<td class='text-right'>£{annual_pl_data[y][key]:,.2f}</td>"
                    for y in years_labels
                ]
            )
            + "</tr>"
        )

    html_cf_rows = ""
    for row_lbl, key in [
        ("Trading Cash Collections", "Inflow"),
        ("Equity Capital Funding Injections", "Equity"),
        ("Operational Cash Outflows", "Outflow"),
        ("Closing Bank Cash Reserves", "Closing"),
    ]:
        weight = (
            "font-weight: bold; background-color: #f8fafc;" if key == "Closing" else ""
        )
        html_cf_rows += (
            f"<tr style='{weight}'><td>{row_lbl}</td>"
            + "".join(
                [
                    f"<td class='text-right'>£{annual_cf_data[y][key]:,.2f}</td>"
                    for y in years_labels
                ]
            )
            + "</tr>"
        )

    html_bs_rows = ""
    for row_lbl, key in [
        ("Fixed Infrastructure Assets", "Fixed"),
        ("Accumulated Depreciation Reserve", "AccumDep"),
        ("Net Book Value Asset Worth", "NBV"),
        ("Trade Debtors Balance", "Debtors"),
        ("HMRC VAT Reserves Owing", "VAT"),
        ("HMRC PAYE Obligations Liability", "PAYE"),
        ("Long Term Facility Debt Liability", "Debt"),
        ("Shareholder Invested Equity Reserves", "Equity"),
        ("Retained Earnings Accumulation", "Retained"),
    ]:
        weight = (
            "font-weight: bold; background-color: #f8fafc;"
            if key in ["NBV", "Retained"]
            else ""
        )
        html_bs_rows += (
            f"<tr style='{weight}'><td>{row_lbl}</td>"
            + "".join(
                [
                    f"<td class='text-right'>£{annual_bs_data[y][key]:,.2f}</td>"
                    for y in years_labels
                ]
            )
            + "</tr>"
        )

    # 2. GENERATE FIXED ASSET REGISTERS SCHEDULE HTML
    fa_rows = []
    for outright in active_data.get("outright_capex", []):
        fa_rows.append(
            {
                "name": outright["name"],
                "type": "Direct Purchase",
                "value": float(outright["amount"]),
                "m": int(outright["month"]),
                "r": float(outright.get("depreciation_rate", 0.20)),
                "method": "Straight Line",
            }
        )
    for fin in active_data.get("financed_assets", []):
        fa_rows.append(
            {
                "name": fin["name"],
                "type": "Financed HP",
                "value": float(fin["amount"]),
                "m": int(fin["month"]),
                "r": float(fin.get("depreciation_rate", 0.15)),
                "method": "Straight Line",
            }
        )

    html_fa_schedule = ""
    if fa_rows:
        for item in fa_rows:
            r_val = item["value"]
            for m in range(0, 61):
                if m >= item["m"] and r_val > 0:
                    r_val = max(0.0, r_val - ((item["value"] * item["r"]) / 12.0))
            cum_dep = item["value"] - r_val
            html_fa_schedule += f"""
            <tr>
                <td><strong>{item['name']}</strong> ({item['type']})</td>
                <td class='text-right'>{int(item['r']*100)}%</td>
                <td>{item['method']}</td>
                <td class='text-right'>£{item['value']:,.2f}</td>
                <td class='text-right'>£{cum_dep:,.2f}</td>
                <td class='text-right'>£{r_val:,.2f}</td>
            </tr>
            """
    else:
        html_fa_schedule = "<tr><td colspan='6'>No fixed assets registered.</td></tr>"

    # 3. GENERATE DYNAMIC LOAN BALANCES SCHEDULE HTML
    html_loan_schedule = ""
    if active_data.get("financed_assets"):
        for fin in active_data["financed_assets"]:
            m_start = int(fin["month"])
            fin_bal = float(fin["amount"]) * (
                1.0 - (float(fin.get("deposit_pct", 10.0)) / 100.0)
            )
            term = int(fin["term_months"])
            monthly_principal = fin_bal / term

            html_loan_schedule += f"<tr><th colspan='7' style='background-color:#e2e8f0; color:#1e3a8a;'>Facility: {fin['name']}</th></tr>"

            running_debt = fin_bal
            for yr in range(1, 6):
                m_yr_start = (yr - 1) * 12 + 1
                m_yr_end = yr * 12

                yr_opening = 0.0
                for m in range(0, m_yr_start):
                    if m == m_start:
                        yr_opening = fin_bal
                    if m >= m_start and m < m_yr_start:
                        yr_opening = max(0.0, yr_opening - monthly_principal)

                yr_closing = yr_opening
                st_debt = 0.0
                lt_debt = 0.0
                for m in range(m_yr_start, m_yr_end + 1):
                    if m >= m_start:
                        st_debt = min(yr_closing, monthly_principal * 12)
                        lt_debt = max(0.0, yr_closing - st_debt)
                        if m <= m_start + term:
                            yr_closing = max(0.0, yr_closing - monthly_principal)

                interest_est = yr_opening * (
                    float(fin.get("interest_rate", 5.0)) / 100.0
                )
                repay_est = (monthly_principal * 12) if yr_opening > 0 else 0.0

                html_loan_schedule += f"""
                <tr>
                    <td><strong>Year {yr}</strong> (M{str(m_yr_start).zfill(2)}-M{str(m_yr_end).zfill(2)})</td>
                    <td class='text-right'>£{yr_opening:,.2f}</td>
                    <td class='text-right'>£{interest_est:,.2f}</td>
                    <td class='text-right'>£{repay_est:,.2f}</td>
                    <td class='text-right'>£{yr_closing:,.2f}</td>
                    <td class='text-right'>£{st_debt:,.2f}</td>
                    <td class='text-right'>£{lt_debt:,.2f}</td>
                </tr>
                """
    else:
        html_loan_schedule = (
            "<tr><td colspan='7'>No debt facilities registered.</td></tr>"
        )

    # COMPLETE GLOBAL SPECIFICATION HTML MARKUP TEMPLATE
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4 portrait; margin: 20mm 15mm;
                @bottom-right {{ content: "Page " counter(page); font-family: sans-serif; font-size: 8pt; color: #94a3b8; }}
                @bottom-left {{ content: "STRATA // Strictly Private & Confidential"; font-family: sans-serif; font-size: 8pt; color: #94a3b8; }}
            }}
            body {{ font-family: Arial, sans-serif; color: #0f172a; line-height: 1.5; font-size: 9.5pt; }}
            .header-banner {{ background-color: #1e3a8a; color: #ffffff; padding: 25px 20px; margin-bottom: 25px; border-radius: 4px; }}
            .header-banner h1 {{ margin: 0; font-size: 18pt; font-weight: 700; }}
            .header-banner p {{ margin: 5px 0 0 0; font-size: 8.5pt; color: #93c5fd; text-transform: uppercase; letter-spacing: 1px; }}
            .context-section {{ margin-bottom: 20px; font-size: 10.5pt; font-weight: bold; color: #334155; }}
            h2 {{ color: #1e3a8a; font-size: 12pt; font-weight: 700; margin-top: 30px; border-left: 4px solid #3b82f6; padding-left: 8px; page-break-after: avoid; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 25px; page-break-inside: avoid; }}
            th {{ background-color: #f8fafc; color: #475569; padding: 8px 10px; font-size: 8.5pt; border-bottom: 2px solid #cbd5e1; text-transform: uppercase; }}
            td {{ padding: 8px 10px; border-bottom: 1px solid #e2e8f0; font-size: 9pt; }}
            .text-right {{ text-align: right; }}
            .page-break {{ page-break-before: always; }}
        </style>
    </head>
    <body>
        <div class="header-banner">
            <h1>STRATA EXECUTIVE FINANCIAL REPORT PACK</h1>
            <p>Integrated 5-Year Financial Summary & Engineering Projections</p>
        </div>
        <div class="context-section">Project Context: {project_name}</div>
        <table>
            <thead><tr><th>Target Metric</th><th class="text-right">Value Position</th></tr></thead>
            <tbody>
                <tr><td>Peak Cash Runway</td><td class="text-right">£{peak_cash:,.2f}</td></tr>
                <tr><td>Max Venture Risk Valley</td><td class="text-right">£{lowest_cash:,.2f}</td></tr>
                <tr><td>Year 5 Horizon Retained Valuation</td><td class="text-right">£{horizon_worth:,.2f}</td></tr>
            </tbody>
        </table>
        <h2>Gemini AI Strategic Insight Narrative Analysis</h2>
        <div>{clean_insight}</div>
        <div class="page-break">
            <h2>Profit & Loss Forecast Statement (Years 1 to 5)</h2>
            <table><thead><tr><th>Performance Component</th><th>Year 1</th><th>Year 2</th><th>Year 3</th><th>Year 4</th><th>Year 5</th></tr></thead>
            <tbody>{html_pl_rows}</tbody></table>
            <h2>Cash Flow Forecast Statement (Years 1 to 5)</h2>
            <table><thead><tr><th>Liquidity Flow Component</th><th>Year 1</th><th>Year 2</th><th>Year 3</th><th>Year 4</th><th>Year 5</th></tr></thead>
            <tbody>{html_cf_rows}</tbody></table>
            <h2>Balance Sheet Capital Statement (Years 1 to 5)</h2>
            <table><thead><tr><th>Ledger Allocation Structure</th><th>Year 1</th><th>Year 2</th><th>Year 3</th><th>Year 4</th><th>Year 5</th></tr></thead>
            <tbody>{html_bs_rows}</tbody></table>
        </div>
        <div class="page-break">
            <h2>⚙️ Schedule 1: Fixed Asset Ledger & Capital Depreciation</h2>
            <table><thead><tr><th>Asset Category Class</th><th>Rate</th><th>Method</th><th>Original Cost</th><th>Cumulative Depr.</th><th>Net Book Value (NBV)</th></tr></thead>
            <tbody>{html_fa_schedule}</tbody></table>
            <h2>💳 Schedule 2: Debt Servicing & Liability Amortisation</h2>
            <table><thead><tr><th>Amortisation Period</th><th>Opening (b/f)</th><th>Interest</th><th>Repayments</th><th>Closing (c/f)</th><th>Current Liab (<12M)</th><th>Non-Current Debt (>1Y)</th></tr></thead>
            <tbody>{html_loan_schedule}</tbody></table>
        </div>
    </body>
    </html>
    """

    tmp_html, tmp_pdf = "tmp_report.html", "tmp_report.pdf"
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    HTML(tmp_html).write_pdf(tmp_pdf)
    with open(tmp_pdf, "rb") as f:
        pdf_bytes = f.read()
    if os.path.exists(tmp_html):
        os.remove(tmp_html)
    if os.path.exists(tmp_pdf):
        os.remove(tmp_pdf)
    return pdf_bytes


class JournalToken:
    def __init__(self, month_label, debit_acct, credit_acct, amount):
        self.month_label, self.debit_acct, self.credit_acct, self.amount = (
            month_label,
            debit_acct,
            credit_acct,
            float(amount),
        )


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
        nic_rate = float(
            st.session_state.get("sic_profile", {"base_er_nic_rate": 0.138}).get(
                "base_er_nic_rate", 0.138
            )
        )
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
                    y_idx = (
                        1
                        if m <= 12
                        else 2 if m <= 24 else 3 if m <= 36 else 4 if m <= 48 else 5
                    )
                    y_base = float(
                        sale.get(f"y{y_idx}_baseline", sale.get("y3_baseline", 0.0))
                    )
                    flex = (
                        (1.0 + (float(sale.get("flex_pct", 0.0)) / 100.0))
                        if y_idx > 1
                        else 1.0
                    )
                    val = (
                        y_base
                        * flex
                        * self.seasonality_profiles.get(
                            sale.get("seasonality", "Flat_Linear"),
                            self.seasonality_profiles["Flat_Linear"],
                        )[(m - 1) % 12]
                    )
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
                    y_idx = (
                        1
                        if m <= 12
                        else 2 if m <= 24 else 3 if m <= 36 else 4 if m <= 48 else 5
                    )
                    val = (
                        float(c.get(f"y{y_idx}_baseline", c.get("y3_baseline", 0.0)))
                        * (
                            (1.0 + (float(c.get("flex_pct", 0.0)) / 100.0))
                            if y_idx > 1
                            else 1.0
                        )
                        * self.seasonality_profiles.get(
                            c.get("seasonality", "Flat_Linear"),
                            self.seasonality_profiles["Flat_Linear"],
                        )[(m - 1) % 12]
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
                            m,
                            "BS_Liability_VAT_Payable",
                            "BS_Asset_Cash",
                            val * vat_pct,
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
                    self.inject_token(
                        m,
                        "PL_Expense_Depreciation",
                        "BS_Asset_Accumulated_Depreciation",
                        (
                            float(outright["amount"])
                            * float(outright.get("depreciation_rate", 0.20))
                        )
                        / 12.0,
                    )
            for fin in state.get("financed_assets", []):
                if int(fin["month"]) <= m:
                    self.inject_token(
                        m,
                        "PL_Expense_Depreciation",
                        "BS_Asset_Accumulated_Depreciation",
                        (
                            float(fin["amount"])
                            * float(fin.get("depreciation_rate", 0.15))
                        )
                        / 12.0,
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
                assets + liabs, 2
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
active_data_context = st.session_state.get("active_data", {})
df_pl, df_cf, df_bs = cuboid_engine.run_simulation_engine(active_data_context)

closing_cash_array = df_cf.loc["Closing Bank Cash Reserves (£)"].astype(float).values
peak_cash, lowest_cash = closing_cash_array.max(), closing_cash_array.min()
y5_worth = df_bs.loc["Retained Earnings Accumulation (£)", "M60"]

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Peak Cash Runway Worth", f"£{peak_cash:,.2f}")
kpi2.metric("Max Venture Risk Valley", f"£{lowest_cash:,.2f}")
kpi3.metric("Year 5 Horizon Value", f"£{y5_worth:,.2f}")
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
        file_name="STRATA_Profit_and_Loss.csv",
        mime="text/csv",
        use_container_width=True,
    )
with exp_col2:
    st.download_button(
        "📥 Download Cash Flow CSV",
        data=df_cf.to_csv().encode("utf-8"),
        file_name="STRATA_Cash_Flow.csv",
        mime="text/csv",
        use_container_width=True,
    )
with exp_col3:
    st.download_button(
        "📥 Download Balance Sheet CSV",
        data=df_bs.to_csv().encode("utf-8"),
        file_name="STRATA_Balance_Sheet.csv",
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
                financial_summary_context = f"Project: {st.session_state.get('active_project_name')}\nPeak Cash: £{peak_cash:,.2f}\nRisk Valley: £{lowest_cash:,.2f}\nRetained: £{y5_worth:,.2f}"
                prompt = f"Analyze this financial context as a CFO and output a professional executive summary with zero markdown asterisks:\n{financial_summary_context}"
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
    try:
        pdf_binary = compile_premium_html_report(
            project_name=st.session_state.get(
                "active_project_name", "Unsaved_Draft_Scenario"
            ),
            peak_cash=peak_cash,
            lowest_cash=lowest_cash,
            horizon_worth=y5_worth,
            insight_text=st.session_state["cached_ai_analysis"],
            df_pl=df_pl,
            df_cf=df_cf,
            df_bs=df_bs,
            active_data=active_data_context,
        )
        st.download_button(
            label="📄 Download Official Executive Management Pack PDF",
            data=pdf_binary,
            file_name=f"STRATA_Executive_Summary.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as pdf_err:
        st.error(f"PDF binary compiler mismatch: {str(pdf_err)}")

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
active_months_for_sum = [t for t in targets if t != "M00"]

df_pl_view, df_cf_view, df_bs_view = (
    df_pl[targets].copy(),
    df_cf[targets].copy(),
    df_bs[targets].copy(),
)
df_pl_view["Year Total"] = df_pl[active_months_for_sum].sum(axis=1)
df_pl_view.at["Gross Profit Margin (£)", "Year Total"] = (
    df_pl_view.loc["Total Revenue (£)", "Year Total"]
    - df_pl_view.loc["Cost of Goods Sold (COGS) (£)", "Year Total"]
)
df_pl_view.at["Net Operating Profit (EBIT)", "Year Total"] = (
    df_pl_view.loc["Gross Profit Margin (£)", "Year Total"]
    - df_pl_view.loc["Operational Overheads (£)", "Year Total"]
    - df_pl_view.loc["Staff Payroll Overhead (£)", "Year Total"]
    - df_pl_view.loc["Depreciation Overhead (£)", "Year Total"]
    - df_pl_view.loc["Financing Interest Cost (£)", "Year Total"]
)

df_cf_view["Year Total"] = df_cf[active_months_for_sum].sum(axis=1)
df_cf_view.at["Closing Bank Cash Reserves (£)", "Year Total"] = (
    df_cf[targets[-1]].iloc[0]
    if isinstance(df_cf[targets[-1]], pd.Series)
    else df_cf.at["Closing Bank Cash Reserves (£)", targets[-1]]
)
df_bs_view["Closing Position"] = df_bs[targets[-1]]

t1, t2, t3 = st.tabs(
    [
        " Reconciled Financial Statements",
        " Fixed Infrastructure Asset Ledger",
        " External Debt Liabilities Registry",
    ]
)


def style_financials(val):
    return "font-weight: bold; background-color: #f1f5f9; color: #1e3a8a;"


with t1:
    st.markdown("#### Profit & Loss Statement (£)")
    st.dataframe(
        df_pl_view.style.format("{:,.2f}").apply(
            lambda x: [
                (
                    style_financials(v)
                    if x.name
                    in [
                        "Total Revenue (£)",
                        "Gross Profit Margin (£)",
                        "Net Operating Profit (EBIT)",
                    ]
                    else ""
                )
                for v in x
            ],
            axis=1,
        ),
        use_container_width=True,
    )
    st.markdown("#### Cash Flow Statement (£)")
    st.dataframe(
        df_cf_view.style.format("{:,.2f}").apply(
            lambda x: [
                (
                    style_financials(v)
                    if x.name == "Closing Bank Cash Reserves (£)"
                    else ""
                )
                for v in x
            ],
            axis=1,
        ),
        use_container_width=True,
    )
    st.markdown("#### Balance Sheet Ledger (£)")
    st.dataframe(
        df_bs_view.style.format("{:,.2f}").apply(
            lambda x: [
                (
                    style_financials(v)
                    if x.name
                    in [
                        "Net Book Value Asset Worth (£)",
                        "Retained Earnings Accumulation (£)",
                        "Ledger Verification Checksum Balance",
                    ]
                    else ""
                )
                for v in x
            ],
            axis=1,
        ),
        use_container_width=True,
    )

with t2:
    st.markdown("### 🚜 Dynamic Fixed Asset Depreciation Ledger")
    fa_rows_view = []
    for outright in active_data_context.get("outright_capex", []):
        fa_rows_view.append(
            {
                "Asset Item": outright["name"],
                "Type": "Direct Purchase",
                "value": outright["amount"],
                "Month": int(outright["month"]),
                "Rate": float(outright.get("depreciation_rate", 0.20)),
            }
        )
    for fin in active_data_context.get("financed_assets", []):
        fa_rows_view.append(
            {
                "Asset Item": fin["name"],
                "Type": "Financed HP",
                "value": fin["amount"],
                "Month": int(fin["month"]),
                "Rate": float(fin.get("depreciation_rate", 0.15)),
            }
        )
    if fa_rows_view:
        ledger_rows = []
        for item in fa_rows_view:
            v_rec = {
                "Asset Item": item["Asset Item"],
                "Metric Category": "Net Book Value (£)",
            }
            running_val = 0.0
            for m in range(0, 61):
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
        st.info("No assets registered.")

with t3:
    st.markdown("### 🏛️ Chronological Liability Allocation Ledger")
    if active_data_context.get("financed_assets"):
        loan_rows = []
        for fin in active_data_context["financed_assets"]:
            m_start = int(fin["month"])
            fin_bal = float(fin["amount"]) * (
                1.0 - (float(fin.get("deposit_pct", 10.0)) / 100.0)
            )
            term = int(fin["term_months"])
            monthly_principal = fin_bal / term
            bal_rec, st_rec, lt_rec = (
                {"Facility": fin["name"], "Metric": "Total Outstanding (£)"},
                {"Facility": fin["name"], "Metric": "Current Liabilities (<12m) (£)"},
                {"Facility": fin["name"], "Metric": "Non-Current Debt (>1yr) (£)"},
            )
            running_debt = 0.0
            for m in range(0, 61):
                m_lbl = f"M{str(m).zfill(2)}"
                if m == m_start:
                    running_debt = fin_bal
                if m >= m_start and running_debt > 0:
                    st_debt = min(running_debt, monthly_principal * 12)
                    bal_rec[m_lbl], st_rec[m_lbl], lt_rec[m_lbl] = (
                        running_debt,
                        st_debt,
                        max(0.0, running_debt - st_debt),
                    )
                    running_debt = max(0.0, running_debt - monthly_principal)
                else:
                    bal_rec[m_lbl], st_rec[m_lbl], lt_rec[m_lbl] = (
                        running_debt,
                        0.0,
                        0.0,
                    )
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
st.sidebar.page_link(
    "pages/1_Data_Ingestion_Gateway.py", label="📥 Data Ingestion Gateway"
)
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry Panel")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")
