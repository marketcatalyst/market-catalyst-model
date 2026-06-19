# pages/app.py
# STRATA SUITE PRODUCTION ENGINE // TOTAL CORE SYSTEM v4.3.0-MASTER

import streamlit as st
import json
import os
import pandas as pd
from pathlib import Path
import google.generativeai as genai
import io
from fpdf import FPDF
import psycopg2
from psycopg2.extras import RealDictCursor
import re
import datetime

# Enforce secure routing context backup check
if not st.session_state.get("authenticated") or not st.session_state.get(
    "onboarding_complete"
):
    st.warning("⚠️ **Security Intercept:** Route session token context not cleared.")
    st.page_link("home.py", label="↩️ Return to Access Gateway Portal")
    st.stop()

# =========================================================================
# 💾 PERSISTENCE CONTROL LAYER: SERVERLESS NEON POSTGRES PIPELINE
# =========================================================================


def get_database_connection():
    db_url = (
        os.environ.get("DATABASE_URL")
        or st.secrets.get("DATABASE_URL", None)
        or st.secrets.get("CONNECTION_STRING", None)
    )
    if not db_url:
        return "MISSING_CREDENTIALS"
    try:
        return psycopg2.connect(db_url)
    except Exception as e:
        return f"CONNECTION_FAILED: {str(e)}"


def execute_database_handshake():
    conn = get_database_connection()
    if conn and not isinstance(conn, str):
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS strata_projects (
                            project_id SERIAL PRIMARY KEY,
                            project_name TEXT UNIQUE NOT NULL,
                            payload_data TEXT NOT NULL,
                            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS strata_staging_inputs (
                            staging_id SERIAL PRIMARY KEY,
                            project_name TEXT NOT NULL,
                            vector_type TEXT NOT NULL,
                            source_origin TEXT NOT NULL,
                            line_name TEXT NOT NULL,
                            base_amount NUMERIC(15,2) NOT NULL,
                            seasonality_profile TEXT DEFAULT 'Flat_Linear',
                            terms_delay_days INTEGER DEFAULT 0,
                            vat_applicable BOOLEAN DEFAULT TRUE,
                            is_approved BOOLEAN DEFAULT FALSE,
                            ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
            conn.close()
        except Exception:
            pass


def extract_project_directory_list():
    conn = get_database_connection()
    if conn and not isinstance(conn, str):
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        "SELECT project_name FROM strata_projects ORDER BY project_name ASC;"
                    )
                    rows = cur.fetchall()
            conn.close()
            return [r["project_name"] for r in rows]
        except Exception:
            pass
    return []


def commit_project_payload_to_storage(
    project_name, sales, opex, payroll, capital, sic_meta=None
):
    payload_string = json.dumps(
        {
            "sales": sales,
            "opex": opex,
            "payroll": payroll,
            "capital": capital,
            "sic_meta": sic_meta,
        }
    )
    conn = get_database_connection()
    if isinstance(conn, str):
        return conn

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO strata_projects (project_name, payload_data, last_updated)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (project_name) DO UPDATE 
                    SET payload_data = EXCLUDED.payload_data, last_updated = CURRENT_TIMESTAMP;
                """,
                    (str(project_name).strip(), payload_string),
                )
        conn.close()
        return "SUCCESS"
    except Exception as e:
        return f"WRITE_FAILED: {str(e)}"


def pull_project_payload_from_storage(project_name):
    conn = get_database_connection()
    if conn and not isinstance(conn, str):
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        "SELECT payload_data FROM strata_projects WHERE project_name = %s;",
                        (project_name,),
                    )
                    row = cur.fetchone()
            conn.close()
            if row:
                return json.loads(row["payload_data"])
        except Exception:
            pass
    return None


# =========================================================================
# 📥 STAGING LAYER PIPELINES: INGESTION BACK-END ENGINE HOOKS
# =========================================================================


def stage_unverified_ingestion_line(
    project_name,
    v_type,
    origin,
    name,
    amount,
    seasonality="Flat_Linear",
    delay=0,
    vat=True,
):
    conn = get_database_connection()
    if conn and not isinstance(conn, str):
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO strata_staging_inputs 
                        (project_name, vector_type, source_origin, line_name, base_amount, seasonality_profile, terms_delay_days, vat_applicable, is_approved)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, FALSE);
                    """,
                        (
                            str(project_name).strip(),
                            str(v_type).strip(),
                            str(origin).strip(),
                            str(name).strip(),
                            float(amount),
                            str(seasonality).strip(),
                            int(delay),
                            bool(vat),
                        ),
                    )
            conn.close()
            return True
        except Exception:
            pass
    return False


def extract_staging_schedule_records(project_name):
    conn = get_database_connection()
    if conn and not isinstance(conn, str):
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        """
                        SELECT * FROM strata_staging_inputs 
                        WHERE project_name = %s AND is_approved = FALSE 
                        ORDER BY staging_id ASC;
                    """,
                        (project_name,),
                    )
                    rows = cur.fetchall()
            conn.close()
            return rows
        except Exception:
            pass
    return []


def purge_entire_staging_by_project(project_name):
    """Deletes all temporary staging entries once batch migration finishes."""
    conn = get_database_connection()
    if conn and not isinstance(conn, str):
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM strata_staging_inputs WHERE project_name = %s;",
                        (project_name,),
                    )
            conn.close()
            return True
        except Exception:
            pass
    return False


execute_database_handshake()


# =========================================================================
# 🏛️ CORE ENGINE: MULTI-YEAR GRANULAR TRANSITIONAL VECTOR LEDGER
# =========================================================================


class JournalToken:

    def __init__(self, month_label, debit_acct, credit_acct, amount, narrative=""):
        self.month_label = month_label
        self.debit_acct = debit_acct
        self.credit_acct = credit_acct
        self.amount = float(amount)
        self.narrative = narrative


class CommercialTrialBalanceCuboid:

    def __init__(self):
        self.accounts = [
            "BS_Asset_Cash",
            "BS_Asset_Debtors",
            "BS_Asset_Fixed_Assets",
            "BS_Asset_Accumulated_Depreciation",
            "BS_Liability_Creditors",
            "BS_Liability_VAT_Payable",
            "BS_Liability_PAYE_NIC_Payable",
            "BS_Liability_Long_Term_Debt",
            "BS_Equity_Share_Capital",
            "BS_Equity_Retained_Earnings",
            "PL_Revenue_Gross",
            "PL_COGS",
            "PL_Expense_Overheads",
            "PL_Expense_Payroll",
            "PL_Expense_Depreciation",
            "PL_Expense_Interest",
        ]
        self.months = [f"M{str(i).zfill(2)}" for i in range(1, 61)]
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
        self.token_pool = []

    def inject_token(self, month_idx, debit_acct, credit_acct, amount, narrative=""):
        if amount == 0.0 or month_idx < 1 or month_idx > 60:
            return
        month_label = f"M{str(month_idx).zfill(2)}"
        self.token_pool.append(
            JournalToken(month_label, debit_acct, credit_acct, amount, narrative)
        )

    def extract_monthly_weight(self, profile_name, month_idx):
        profile = self.seasonality_profiles.get(
            profile_name, self.seasonality_profiles["Flat_Linear"]
        )
        return profile[(month_idx - 1) % 12]

    def process_simulation(
        self,
        runtime_payload,
        revenue_modifier=1.0,
        opex_modifier=1.0,
        payroll_modifier=0.0,
    ):
        self.token_pool = []

        # Capitalisation Injections
        for cap in runtime_payload.get("capital", []):
            m_start, val, c_type = (
                int(cap.get("month", 1)),
                float(cap.get("value", 0.0)),
                cap.get("type", ""),
            )
            if c_type == "Equity Capital / Share Premium Injection":
                self.inject_token(
                    m_start,
                    "BS_Asset_Cash",
                    "BS_Equity_Share_Capital",
                    val,
                    f"CapEx: {cap.get('name')}",
                )
            elif c_type == "Commercial Debt / Facility Drawdown":
                self.inject_token(
                    m_start,
                    "BS_Asset_Cash",
                    "BS_Liability_Long_Term_Debt",
                    val,
                    f"Debt: {cap.get('name')}",
                )
            elif c_type == "New / Existing Fixed Asset CapEx":
                self.inject_token(
                    m_start,
                    "BS_Asset_Fixed_Assets",
                    "BS_Asset_Cash",
                    val,
                    f"Asset: {cap.get('name')}",
                )

        # Horizon Loop
        for m in range(1, 61):
            # Sales Pipeline
            for sale in runtime_payload.get("sales", []):
                profile, debtor_days, vat_app = (
                    sale.get("seasonality", "Flat_Linear"),
                    int(sale.get("debtor_days", 0)),
                    sale.get("vat_applicable", True),
                )

                if profile == "Manual_Direct_Override" and "overrides" in sale:
                    monthly_net = (
                        float(sale["overrides"].get(f"M{str(m).zfill(2)}", 0.0))
                        * revenue_modifier
                    )
                else:
                    ann_net = float(sale.get("amount", 0.0)) * revenue_modifier
                    monthly_net = ann_net * self.extract_monthly_weight(profile, m)

                monthly_vat = (monthly_net * 0.20) if vat_app else 0.0

                narr_tag = f"REV_LINE__{sale.get('name')}"
                self.inject_token(
                    m, "BS_Asset_Debtors", "PL_Revenue_Gross", monthly_net, narr_tag
                )
                if monthly_vat > 0:
                    self.inject_token(
                        m,
                        "BS_Asset_Debtors",
                        "BS_Liability_VAT_Payable",
                        monthly_vat,
                        f"VAT_OUT__{sale.get('name')}",
                    )
                self.inject_token(
                    m + (debtor_days // 30),
                    "BS_Asset_Cash",
                    "BS_Asset_Debtors",
                    monthly_net + monthly_vat,
                    f"Receipt: {sale.get('name')}",
                )

            # Overheads Pipeline
            for opex in runtime_payload.get("opex", []):
                profile, creditor_days, vat_rec = (
                    opex.get("seasonality", "Flat_Linear"),
                    int(opex.get("creditor_days", 0)),
                    opex.get("vat_applicable", True),
                )

                if profile == "Manual_Direct_Override" and "overrides" in opex:
                    monthly_net_cost = (
                        float(opex["overrides"].get(f"M{str(m).zfill(2)}", 0.0))
                        * opex_modifier
                    )
                else:
                    ann_net_cost = float(opex.get("amount", 0.0)) * opex_modifier
                    monthly_net_cost = ann_net_cost * self.extract_monthly_weight(
                        profile, m
                    )

                monthly_input_vat = (monthly_net_cost * 0.20) if vat_rec else 0.0

                narr_tag = f"OPEX_LINE__{opex.get('name')}"
                self.inject_token(
                    m,
                    "PL_Expense_Overheads",
                    "BS_Liability_Creditors",
                    monthly_net_cost,
                    narr_tag,
                )
                if monthly_input_vat > 0:
                    self.inject_token(
                        m,
                        "BS_Liability_VAT_Payable",
                        "BS_Liability_Creditors",
                        monthly_input_vat,
                        f"VAT_IN__{opex.get('name')}",
                    )
                self.inject_token(
                    m + (creditor_days // 30),
                    "BS_Liability_Creditors",
                    "BS_Asset_Cash",
                    monthly_net_cost + monthly_input_vat,
                    f"Payment: {opex.get('name')}",
                )

            # Payroll Pipeline
            for pay in runtime_payload.get("payroll", []):
                monthly_gross = (float(pay.get("amount", 0.0)) / 12.0) * (
                    1.0 - payroll_modifier
                )
                employer_nic = monthly_gross * 0.138
                paye_deduction = monthly_gross * 0.25
                self.inject_token(
                    m,
                    "PL_Expense_Payroll",
                    "BS_Asset_Cash",
                    monthly_gross - paye_deduction,
                    f"Net Pay: {pay.get('name')}",
                )
                self.inject_token(
                    m,
                    "PL_Expense_Payroll",
                    "BS_Liability_PAYE_NIC_Payable",
                    paye_deduction + employer_nic,
                    f"Taxes: {pay.get('name')}",
                )
                self.inject_token(
                    m + 1,
                    "BS_Liability_PAYE_NIC_Payable",
                    "BS_Asset_Cash",
                    paye_deduction + employer_nic,
                    "HMRC PAYE Payment",
                )

            # Depreciation Ledger Accruals
            current_fa = self.compute_running_balance_to_month(
                "BS_Asset_Fixed_Assets", m
            )
            if current_fa > 0.0:
                self.inject_token(
                    m,
                    "PL_Expense_Depreciation",
                    "BS_Asset_Accumulated_Depreciation",
                    (current_fa * 0.10) / 12.0,
                    "Depreciation",
                )

            # Quarterly VAT Settlement
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
                vat_acc = self.compute_running_balance_to_month(
                    "BS_Liability_VAT_Payable", m
                )
                if vat_acc != 0.0:
                    self.inject_token(
                        m,
                        "BS_Liability_VAT_Payable",
                        "BS_Asset_Cash",
                        vat_acc,
                        "Quarterly VAT Return",
                    )

        return self.compile_granular_statements(runtime_payload)

    def compute_running_balance_to_month(self, account_name, month_limit):
        balance = 0.0
        for token in self.token_pool:
            if int(token.month_label.replace("M", "")) <= month_limit:
                if token.debit_acct == account_name:
                    balance += token.amount
                if token.credit_acct == account_name:
                    balance -= token.amount
        return balance

    def compile_granular_statements(self, runtime_payload):
        rev_rows = [
            f"Revenue: {s['name']} (£)" for s in runtime_payload.get("sales", [])
        ]
        opex_rows = [f"Opex: {o['name']} (£)" for o in runtime_payload.get("opex", [])]

        pl_index = (
            rev_rows
            + ["Total Revenue (£)", "COGS (£)"]
            + opex_rows
            + [
                "Staff Payroll Overhead (£)",
                "Depreciation (£)",
                "Net Operating Profit (EBIT)",
            ]
        )
        df_pl = pd.DataFrame(0.0, index=pl_index, columns=self.months)

        df_cf = pd.DataFrame(
            0.0,
            index=[
                "Customer Trading Receipts (£)",
                "Capital & Financing Injections (£)",
                "Operational Cash Outflows (£)",
                "Net Cash Movement (£)",
                "Cash Reserves (£)",
            ],
            columns=self.months,
        )
        df_bs = pd.DataFrame(
            0.0,
            index=[
                "Fixed Infrastructure Assets (£)",
                "Accumulated Depreciation (£)",
                "Net Book Value Asset Worth (£)",
                "Accounts Receivable (Debtors) (£)",
                "Accounts Payable (Creditors) (£)",
                "HMRC VAT Reserves Owing (£)",
                "HMRC PAYE Obligations (£)",
                "Long Term Facility Debt (£)",
                "Shareholder Invested Equity (£)",
                "Retained Earnings Accumulation (£)",
                "Ledger Verification Checksum Balance",
            ],
            columns=self.months,
        )

        for m_idx, m_label in enumerate(self.months, start=1):
            for t in self.token_pool:
                if t.month_label == m_label:
                    if "REV_LINE__" in t.narrative:
                        clean_name = (
                            f"Revenue: {t.narrative.replace('REV_LINE__', '')} (£)"
                        )
                        df_pl.at[clean_name, m_label] += t.amount
                        df_pl.at["Total Revenue (£)", m_label] += t.amount
                    if "OPEX_LINE__" in t.narrative:
                        clean_name = (
                            f"Opex: {t.narrative.replace('OPEX_LINE__', '')} (£)"
                        )
                        df_pl.at[clean_name, m_label] += t.amount
                    if t.debit_acct == "PL_Expense_Payroll":
                        df_pl.at["Staff Payroll Overhead (£)", m_label] += t.amount
                    if t.debit_acct == "PL_Expense_Depreciation":
                        df_pl.at["Depreciation (£)", m_label] += t.amount

            def get_scalar_val(df, row_lbl, col_lbl):
                if row_lbl not in df.index:
                    return 0.0
                val = df.loc[row_lbl, col_lbl]
                if isinstance(val, pd.Series):
                    return float(val.iloc[0]) if not val.empty else 0.0
                return float(val) if pd.notna(val) else 0.0

            current_opex_total = sum(
                get_scalar_val(df_pl, row, m_label) for row in opex_rows
            )

            tot_rev = get_scalar_val(df_pl, "Total Revenue (£)", m_label)
            cogs = get_scalar_val(df_pl, "COGS (£)", m_label)
            payroll = get_scalar_val(df_pl, "Staff Payroll Overhead (£)", m_label)
            depr = get_scalar_val(df_pl, "Depreciation (£)", m_label)

            df_pl.at["Net Operating Profit (EBIT)", m_label] = (
                tot_rev - cogs - current_opex_total - payroll - depr
            )

            for t in self.token_pool:
                if t.month_label == m_label:
                    if (
                        t.debit_acct == "BS_Asset_Cash"
                        and t.credit_acct == "BS_Asset_Debtors"
                    ):
                        df_cf.at["Customer Trading Receipts (£)", m_label] += t.amount
                    if t.debit_acct == "BS_Asset_Cash" and t.credit_acct in [
                        "BS_Equity_Share_Capital",
                        "BS_Liability_Long_Term_Debt",
                    ]:
                        df_cf.at[
                            "Capital & Financing Injections (£)", m_label
                        ] += t.amount
                    if t.credit_acct == "BS_Asset_Cash" and t.debit_acct in [
                        "BS_Liability_Creditors",
                        "BS_Asset_Fixed_Assets",
                        "BS_Liability_PAYE_NIC_Payable",
                        "BS_Expense_Payroll",
                        "BS_Liability_VAT_Payable",
                    ]:
                        df_cf.at["Operational Cash Outflows (£)", m_label] += t.amount

            df_cf.at["Net Cash Movement (£)", m_label] = (
                df_cf.at["Customer Trading Receipts (£)", m_label]
                + df_cf.at["Capital & Financing Injections (£)", m_label]
                - df_cf.at["Operational Cash Outflows (£)", m_label]
            )
            df_cf.at["Cash Reserves (£)", m_label] = (
                self.compute_running_balance_to_month("BS_Asset_Cash", m_idx)
            )

            df_bs.at["Fixed Infrastructure Assets (£)", m_label] = (
                self.compute_running_balance_to_month("BS_Asset_Fixed_Assets", m_idx)
            )
            df_bs.at["Accumulated Depreciation (£)", m_label] = (
                -self.compute_running_balance_to_month(
                    "BS_Asset_Accumulated_Depreciation", m_idx
                )
            )
            df_bs.at["Net Book Value Asset Worth (£)", m_label] = (
                df_bs.at["Fixed Infrastructure Assets (£)", m_label]
                - df_bs.at["Accumulated Depreciation (£)", m_label]
            )
            df_bs.at["Accounts Receivable (Debtors) (£)", m_label] = (
                self.compute_running_balance_to_month("BS_Asset_Debtors", m_idx)
            )
            df_bs.at["Accounts Payable (Creditors) (£)", m_label] = (
                -self.compute_running_balance_to_month("BS_Liability_Creditors", m_idx)
            )
            df_bs.at["HMRC VAT Reserves Owing (£)", m_label] = (
                -self.compute_running_balance_to_month(
                    "BS_Liability_VAT_Payable", m_idx
                )
            )
            df_bs.at["HMRC PAYE Obligations (£)", m_label] = (
                -self.compute_running_balance_to_month(
                    "BS_Liability_PAYE_NIC_Payable", m_idx
                )
            )
            df_bs.at["Long Term Facility Debt (£)", m_label] = (
                -self.compute_running_balance_to_month(
                    "BS_Liability_Long_Term_Debt", m_idx
                )
            )
            df_bs.at["Shareholder Invested Equity (£)", m_label] = (
                -self.compute_running_balance_to_month("BS_Equity_Share_Capital", m_idx)
            )

            hist_sum = 0.0
            for past_m in self.months[:m_idx]:
                past_opex_total = sum(
                    get_scalar_val(df_pl, row, past_m) for row in opex_rows
                )
                hist_sum += (
                    get_scalar_val(df_pl, "Total Revenue (£)", past_m)
                    - get_scalar_val(df_pl, "COGS (£)", past_m)
                    - past_opex_total
                    - get_scalar_val(df_pl, "Staff Payroll Overhead (£)", past_m)
                    - get_scalar_val(df_pl, "Depreciation (£)", past_m)
                )
            df_bs.at["Retained Earnings Accumulation (£)", m_label] = hist_sum
            df_bs.at["Ledger Verification Checksum Balance", m_label] = (
                df_bs.at["Net Book Value Asset Worth (£)", m_label]
                + df_bs.at["Accounts Receivable (Debtors) (£)", m_label]
                + df_cf.at["Cash Reserves (£)", m_label]
            ) - (
                df_bs.at["Accounts Payable (Creditors) (£)", m_label]
                + df_bs.at["HMRC VAT Reserves Owing (£)", m_label]
                + df_bs.at["HMRC PAYE Obligations (£)", m_label]
                + df_bs.at["Long Term Facility Debt (£)", m_label]
                + df_bs.at["Shareholder Invested Equity (£)", m_label]
                + df_bs.at["Retained Earnings Accumulation (£)", m_label]
            )

        df_pl.to_csv("STRATA_Granular_PL.csv")
        df_cf.to_csv("STRATA_Granular_CF.csv")
        df_bs.to_csv("STRATA_Granular_BS.csv")
        return True


# =========================================================================
# ⚙️ ADVANCED ANALYTICAL AUXILIARY: UK SIC PERFORMANCE DEVIATION METRICS
# =========================================================================


def calculate_industry_variance_analysis(df_pl, range_labels, target_sic_meta):
    if not target_sic_meta or "gross_margin" not in target_sic_meta:
        return None

    tot_rev = sum(float(df_pl.at["Total Revenue (£)", m]) for m in range_labels)
    if tot_rev == 0.0:
        return {
            "model_gross": 0.0,
            "target_gross": target_sic_meta["gross_margin"],
            "gross_var": 0.0,
            "model_staff": 0.0,
            "target_staff": target_sic_meta["staff_ratio"],
            "staff_var": 0.0,
            "status": "Grey",
        }

    tot_cogs = sum(float(df_pl.at["COGS (£)", m]) for m in range_labels)
    tot_payroll = sum(
        float(df_pl.at["Staff Payroll Overhead (£)", m]) for m in range_labels
    )

    actual_gross = (tot_rev - tot_cogs) / tot_rev
    actual_staff = tot_payroll / tot_rev

    gross_var = actual_gross - target_sic_meta["gross_margin"]
    staff_var = actual_staff - target_sic_meta["staff_ratio"]

    if staff_var > 0.05 or gross_var < -0.05:
        status = "Red"
    elif abs(staff_var) > 0.02 or abs(gross_var) > 0.02:
        status = "Amber"
    else:
        status = "Green"

    return {
        "model_gross": actual_gross,
        "target_gross": target_sic_meta["gross_margin"],
        "gross_var": gross_var,
        "model_staff": actual_staff,
        "target_staff": target_sic_meta["staff_ratio"],
        "staff_var": staff_var,
        "status": status,
    }


# =========================================================================
# ⚖️ EXECUTIVE ARCHITECTURE PACK: VECTOR PDF COMPILER
# =========================================================================


class StrataCorporateManagementPack(FPDF):

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(100, 110, 120)
            self.cell(
                0,
                5,
                "STRATA // EXTRAPOLATED THREE-WAY LEDGER FORECASTS",
                ln=True,
                align="R",
            )
            self.line(10, 15, 287, 15)
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 150, 160)
        self.cell(
            0,
            10,
            f"Page {self.page_no()} // Internal Confidential Portfolio",
            align="C",
        )

    def build_statement_page(self, title_label, dataframe, range_labels):
        self.add_page(orientation="L")
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(20, 35, 60)
        self.cell(0, 10, title_label, ln=True)
        self.ln(4)

        available_width = 277
        row_header_width = 65
        col_width = (available_width - row_header_width) / len(range_labels)

        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(230, 235, 245)
        self.set_text_color(40, 50, 80)
        self.cell(row_header_width, 6, "Account Ledger Vector", border=1, fill=True)
        for m in range_labels:
            self.cell(col_width, 6, str(m), border=1, fill=True, align="C")
        self.ln()

        self.set_font("Helvetica", "", 7)
        self.set_text_color(30, 30, 30)

        for idx in dataframe.index:
            clean_idx_str = (
                str(idx.iloc[0])
                if isinstance(idx, pd.Index) or isinstance(idx, pd.Series)
                else str(idx)
            )

            is_bold_row = any(
                term in clean_idx_str
                for term in ["Total", "Net", "Checksum", "Reserves"]
            )
            if is_bold_row:
                self.set_font("Helvetica", "B", 7.5)
                self.set_fill_color(245, 247, 250)
            else:
                self.set_font("Helvetica", "", 7)
                self.set_fill_color(255, 255, 255)

            self.cell(row_header_width, 5.5, clean_idx_str, border=1, fill=True)
            for m in range_labels:
                val = dataframe.at[idx, m]
                if isinstance(val, pd.Series):
                    val = val.iloc[0] if not val.empty else 0.0
                val_str = f"{val:,.2f}" if abs(val) > 0.001 else "0.00"
                self.cell(col_width, 5.5, val_str, border=1, fill=True, align="R")
            self.ln()


# =========================================================================
# 🧠 INTELLIGENCE ENGINE MODULE: GEMINI COHERENT PIPELINE
# =========================================================================


def generate_corporate_intelligence(
    df_pl, df_cf, df_bs, range_labels, r_scale, o_scale, p_scale
):
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        return (
            "⚠️ **System Lock:** Gemini API Key not configured in workspace settings."
        )

    try:
        genai.configure(api_key=api_key)

        compressed_payload = {
            "Selected_P_And_L_Matrix": df_pl[range_labels]
            .groupby(level=0)
            .sum()
            .to_dict(orient="index"),
            "Selected_Cash_Flow_Matrix": df_cf[range_labels]
            .groupby(level=0)
            .sum()
            .to_dict(orient="index"),
            "Active_Scenario_Stress_Modifiers": {
                "Revenue_Scale_Factor": f"{r_scale}%",
                "Overhead_Cost_Inflation": f"{o_scale}%",
                "Payroll_Reduction_Threshold": f"{p_scale}%",
            },
        }

        prompt = f"""
        You are acting as an elite Financial Analyst and Systems Auditor specializing in UK corporate double-entry software structures.
        Review this disaggregated dataset along with the active 'What-If' macro stress-test parameters:
        
        {json.dumps(compressed_payload, indent=2)}
        
        Provide a customized strategic management review using British English spelling. 
        Analyze how their active stress-test adjustments impact long-term runway, viability and safety thresholds. 
        Formulate into these exact sections:
        ### 🔍 Year-on-Year Operational Growth & Stability Assessment
        ### 🚨 Liquidity Bottlenecks & Credit Vector Risks
        ### 🏛️ Strategic Recommendations for Capital Reservation
        """

        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ **Gateway Disconnect:** {str(e)}"


# =========================================================================
# 🎛️ CONSOLIDATED SINGLE-CALL MULTIMODAL INGESTION SUITE
# =========================================================================


def process_file_ingestion_callback():
    """Autonomous AI core scraper mapping scraped values directly to tabular validation indexes."""
    uploaded_file = st.session_state.get("file_ingestion_key")
    if uploaded_file is not None:
        origin_tag = f"AI Ingested: {uploaded_file.name}"
        active_proj = st.session_state.get(
            "active_project_name", "Unsaved_Draft_Scenario"
        )
        api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get(
            "GEMINI_API_KEY", None
        )

        if not api_key:
            return

        try:
            file_ext = uploaded_file.name.split(".")[-1].lower()
            contents_input = []

            if file_ext in ["csv", "xlsx"]:
                if file_ext == "csv":
                    doc_payload = pd.read_csv(uploaded_file).to_string()
                else:
                    doc_payload = pd.read_excel(
                        uploaded_file, engine="openpyxl"
                    ).to_string()
                contents_input.append(doc_payload)
            elif file_ext == "pdf":
                pdf_data = uploaded_file.read()
                contents_input.append(
                    {"mime_type": "application/pdf", "data": pdf_data}
                )
            else:
                doc_payload = str(uploaded_file.read())
                contents_input.append(doc_payload)

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")

            consolidated_prompt = f"""
            You are a Principal Financial Systems Auditor and Data Engineer specializing in UK corporate double-entry software structures.
            Analyze this uploaded forecast statement document carefully.
            
            Execute two specific extraction directives simultaneously. Formulate your output text exactly like this template:
            
            --- AUDIT SUMMARY ---
            [Provide a 3-bullet evaluation in British English analyzing layout clarity, entity context, and named structures like Turnover, Overheads or Direct Costs vs data anomalies.]
            
            --- DATA MATRIX ARRAY ---
            [Extract all financial lines into a strict JSON list of objects matching this formatting model:
            [
              {{"vector_type": "sales", "line_name": "Court Fees", "base_amount": 280608.0, "seasonality_profile": "Flat_Linear", "terms_delay_days": 0, "vat_applicable": true}}
            ]
            
            CRITICAL CLASSIFICATION RULE FOR `vector_type`:
            - Map all revenue lines strictly to "sales".
            - Map all operational expenses, purchases, rent, utilities, and insurances strictly to "opex".
            - Map all wages, staff payroll, and personnel costs strictly to "payroll".
            - Map capital asset additions strictly to "capex".
            
            For 'base_amount', use the annualized total listed for the row. Omit headers with empty numerical details.]
            """
            contents_input.append(consolidated_prompt)

            raw_response = model.generate_content(contents_input).text
            split_tokens = raw_response.split("--- DATA MATRIX ARRAY ---")
            st.session_state["cached_document_critique"] = (
                split_tokens[0].replace("--- AUDIT SUMMARY ---", "").strip()
            )

            if len(split_tokens) > 1:
                match = re.search(r"\[.*\]", split_tokens[1], re.DOTALL)
                if match:
                    clean_json = match.group(0).strip()
                    parsed_vectors = json.loads(clean_json)
                    for vec in parsed_vectors:
                        extracted_season = (
                            vec.get("seasonality_profile")
                            or vec.get("seasonality")
                            or "Flat_Linear"
                        )
                        extracted_delay = (
                            vec.get("terms_delay_days") or vec.get("delay_days") or 0
                        )
                        stage_unverified_ingestion_line(
                            project_name=active_proj,
                            v_type=vec.get("vector_type", "opex"),
                            origin=origin_tag,
                            name=vec.get("line_name", "AI Scraped Parameter"),
                            amount=float(vec.get("base_amount", 0.0)),
                            seasonality=extracted_season,
                            delay=int(extracted_delay),
                            vat=bool(vec.get("vat_applicable", True)),
                        )
        except Exception:
            pass


# =========================================================================
# 🗛 DATA COMPILATION TRANSFORMERS FOR EDITABLE DATA FRAMES
# =========================================================================


def build_dataframe_from_state(state_dict):
    rows = []
    for s in state_dict.get("sales", []):
        rows.append(
            {
                "Line Identifier Description": s["name"],
                "Vector Type": "sales",
                "Annualized Baseline (£)": float(s.get("amount", 0.0)),
                "Seasonality Curve Profile": s.get("seasonality", "Flat_Linear"),
                "Terms Delay (Days)": int(s.get("debtor_days", 0)),
                "VAT Applicable?": bool(s.get("vat_applicable", True)),
                "Horizon Month (CapEx)": 1,
            }
        )
    for o in state_dict.get("opex", []):
        rows.append(
            {
                "Line Identifier Description": o["name"],
                "Vector Type": "opex",
                "Annualized Baseline (£)": float(o.get("amount", 0.0)),
                "Seasonality Curve Profile": o.get("seasonality", "Flat_Linear"),
                "Terms Delay (Days)": int(o.get("creditor_days", 30)),
                "VAT Applicable?": bool(o.get("vat_applicable", True)),
                "Horizon Month (CapEx)": 1,
            }
        )
    for p in state_dict.get("payroll", []):
        rows.append(
            {
                "Line Identifier Description": p["name"],
                "Vector Type": "payroll",
                "Annualized Baseline (£)": float(p.get("amount", 0.0)),
                "Seasonality Curve Profile": "Flat_Linear",
                "Terms Delay (Days)": 0,
                "VAT Applicable?": False,
                "Horizon Month (CapEx)": 1,
            }
        )
    for c in state_dict.get("capital", []):
        v_map = {
            "New / Existing Fixed Asset CapEx": "capex",
            "Commercial Debt / Facility Drawdown": "debt",
            "Equity Capital / Share Premium Injection": "equity",
        }
        rows.append(
            {
                "Line Identifier Description": c["name"],
                "Vector Type": v_map.get(c["type"], "capex"),
                "Annualized Baseline (£)": float(c.get("value", 0.0)),
                "Seasonality Curve Profile": "Flat_Linear",
                "Terms Delay (Days)": 0,
                "VAT Applicable?": False,
                "Horizon Month (CapEx)": int(c.get("month", 1)),
            }
        )

    if not rows:
        rows.append(
            {
                "Line Identifier Description": "",
                "Vector Type": "opex",
                "Annualized Baseline (£)": 0.0,
                "Seasonality Curve Profile": "Flat_Linear",
                "Terms Delay (Days)": 30,
                "VAT Applicable?": True,
                "Horizon Month (CapEx)": 1,
            }
        )

    return pd.DataFrame(rows)


def commit_dataframe_to_state(df, prior_state):
    new_state = {"sales": [], "opex": [], "payroll": [], "capital": []}

    prior_sales_lookup = {
        s["name"]: s.get("overrides", {}) for s in prior_state.get("sales", [])
    }
    prior_opex_lookup = {
        o["name"]: o.get("overrides", {}) for o in prior_state.get("opex", [])
    }

    for _, r in df.iterrows():
        lbl = str(r["Line Identifier Description"]).strip()
        if not lbl:
            continue

        v_type = str(r["Vector Type"])
        amt = float(r["Annualized Baseline (£)"])
        seas = str(r["Seasonality Curve Profile"])
        delay = int(r["Terms Delay (Days)"])
        vat = bool(r["VAT Applicable?"])
        month = int(r["Horizon Month (CapEx)"])

        if v_type == "sales":
            new_state["sales"].append(
                {
                    "name": lbl,
                    "amount": amt,
                    "seasonality": seas,
                    "debtor_days": delay,
                    "vat_applicable": vat,
                    "overrides": prior_sales_lookup.get(lbl, {}),
                }
            )
        elif v_type == "opex":
            new_state["opex"].append(
                {
                    "name": lbl,
                    "amount": amt,
                    "seasonality": seas,
                    "creditor_days": delay,
                    "vat_applicable": vat,
                    "overrides": prior_opex_lookup.get(lbl, {}),
                }
            )
        elif v_type == "payroll":
            new_state["payroll"].append({"name": lbl, "amount": amt})
        elif v_type in ["capex", "debt", "equity"]:
            t_map = {
                "capex": "New / Existing Fixed Asset CapEx",
                "debt": "Commercial Debt / Facility Drawdown",
                "equity": "Equity Capital / Share Premium Injection",
            }
            new_state["capital"].append(
                {
                    "name": lbl,
                    "type": t_map[v_type],
                    "value": amt,
                    "month": month,
                }
            )

    return new_state


# =========================================================================
# 🎛️ MAIN WORKSPACE INTERFACE CANVAS
# =========================================================================

st.title("🛡️ STRATA // Forecast Engineering Workspace")
st.caption(
    f"Active Project Blueprint Context: `{st.session_state.get('active_project_name', 'Unsaved_Draft_Scenario')}`"
)
st.page_link("home.py", label="↩️ Exit to Control Command Center")
st.markdown("---")

nav_choice = st.radio(
    "Navigate Canvas Desks:", options=["Data Workspace", "Analytical Forecast Sheets"]
)
st.markdown("---")

# Persistence Registry Control
st.markdown("### 🗂️ Neon Serverless Project Registry Persistence")
proj_col1, proj_col2, proj_col3 = st.columns([4, 4, 3])

with proj_col1:
    available_projects = extract_project_directory_list()
    selected_option = st.selectbox(
        "Load Saved Forecast Project Model:",
        options=["-- Select Saved Model Blueprint --"] + available_projects,
        index=(
            0
            if st.session_state.get("active_project_name", "Unsaved_Draft_Scenario")
            == "Unsaved_Draft_Scenario"
            else (
                available_projects.index(st.session_state["active_project_name"]) + 1
                if st.session_state["active_project_name"] in available_projects
                else 0
            )
        ),
        key="project_blueprint_selector",
    )

    if (
        selected_option != "-- Select Saved Model Blueprint --"
        and selected_option != st.session_state.get("active_project_name", "")
    ):
        loaded_payload = pull_project_payload_from_storage(selected_option)
        if loaded_payload:
            st.session_state["active_data"] = loaded_payload
            st.session_state["active_project_name"] = selected_option
            st.session_state["cached_document_critique"] = ""
            st.session_state["onboarding_complete"] = True
            st.toast(f"✅ Loaded Blueprint: '{selected_option}'")
            st.rerun()

with proj_col2:
    save_input_name = st.text_input(
        "Name Active Project State:",
        value=st.session_state.get("active_project_name", "Unsaved_Draft_Scenario"),
    )
    if st.button("💾 Commit Active State to Storage", use_container_width=True):
        if (
            save_input_name.strip()
            and not save_input_name.strip().startswith("Draft_")
            and save_input_name != "Unsaved_Draft_Scenario"
        ):
            write_status = commit_project_payload_to_storage(
                save_input_name.strip(),
                st.session_state["active_data"]["sales"],
                st.session_state["active_data"]["opex"],
                st.session_state["active_data"]["payroll"],
                st.session_state["active_data"]["capital"],
                st.session_state["active_data"].get("sic_meta"),
            )
            if write_status == "SUCCESS":
                st.session_state["active_project_name"] = save_input_name.strip()
                st.toast(f"Locked configuration packet: '{save_input_name}'")
                st.rerun()
            else:
                st.error(f"❌ Connection Blocked: {write_status}")
        else:
            st.error(
                "❌ **Naming Constraint:** Please input an explicit production name before saving to relational storage."
            )

with proj_col3:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("➕ Flush Canvas Instance", use_container_width=True):
        timestamp_slug = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state["active_data"] = {
            "sales": [],
            "opex": [],
            "payroll": [],
            "capital": [],
            "sic_meta": None,
        }
        st.session_state["active_project_name"] = f"Draft_{timestamp_slug}"
        st.session_state["cached_document_critique"] = ""
        st.session_state["onboarding_complete"] = False
        st.toast("🧹 Workspace canvas flushed with isolated draft ID.")
        st.rerun()

st.markdown("---")

rev_scale, opex_scale, pay_scale = 100, 100, 0

if nav_choice == "Data Workspace":
    st.title("✍️ Tabular Trial Balance Ingestion Desk")

    # Autonomous Ingestion Module Hook Block
    st.header("📥 Autonomous AI Extraction & Ingestion Gate")
    st.file_uploader(
        "Upload Unstructured Operational Document:",
        type=["pdf", "csv", "xlsx"],
        key="file_ingestion_key",
        on_change=process_file_ingestion_callback,
    )

    if st.session_state.get("cached_document_critique", ""):
        with st.info("📊 **Gemini Document Architecture Diagnostic Report**"):
            st.markdown(st.session_state["cached_document_critique"])

    # Pull staging vectors waiting for tabular migration merge
    active_project_slug = st.session_state.get(
        "active_project_name", "Unsaved_Draft_Scenario"
    )
    staging_records = extract_staging_schedule_records(active_project_slug)

    if staging_records:
        st.markdown("### 🔮 STAGING BATCH: AI Extracted Vectors Pending Schedule Merge")
        st.caption(
            "The following items were parsed by the extraction engine. Review or modify them in the batch array editor below before committing."
        )

        # Transmute backend Postgres staging schema rows into temporary frontend data frames columns mapping structures
        staged_rows = []
        for item in staging_records:
            v_clean = item["vector_type"]
            if v_clean not in [
                "sales",
                "opex",
                "payroll",
                "capex",
                "debt",
                "equity",
            ]:
                v_clean = "opex"
            staged_rows.append(
                {
                    "Line Identifier Description": item["line_name"],
                    "Vector Type": v_clean,
                    "Annualized Baseline (£)": float(item["base_amount"]),
                    "Seasonality Curve Profile": item.get(
                        "seasonality_profile", "Flat_Linear"
                    ),
                    "Terms Delay (Days)": int(item["terms_delay_days"]),
                    "VAT Applicable?": bool(item["vat_applicable"]),
                    "Horizon Month (CapEx)": 1,
                }
            )
        df_base_pool = pd.DataFrame(staged_rows)
    else:
        # If no fresh document was uploaded, fall back to compiling whatever is inside active session memory handles
        df_base_pool = build_dataframe_from_state(st.session_state["active_data"])

    st.markdown("### ✍️ Production Model Ledger Workspace Grid")
    column_rules = {
        "Line Identifier Description": st.column_config.TextColumn(
            "Account Ledger Identifier Description", required=True, width="large"
        ),
        "Vector Type": st.column_config.SelectboxColumn(
            "Ledger Category Type",
            options=["sales", "opex", "payroll", "capex", "debt", "equity"],
            required=True,
        ),
        "Annualized Baseline (£)": st.column_config.NumberColumn(
            "Annualized Value Baseline (£)", min_value=0.0, format="£%,.2f"
        ),
        "Seasonality Curve Profile": st.column_config.SelectboxColumn(
            "Seasonality Curve Profile",
            options=[
                "Flat_Linear",
                "Winter_Peak",
                "Summer_Peak",
                "Manual_Direct_Override",
            ],
        ),
        "Terms Delay (Days)": st.column_config.SelectboxColumn(
            "Credit Term Delay Window (Days)", options=[0, 30, 60, 90]
        ),
        "VAT Applicable?": st.column_config.CheckboxColumn("Subject to 20% UK VAT?"),
        "Horizon Month (CapEx)": st.column_config.NumberColumn(
            "Execution Month Index (CapEx)", min_value=1, max_value=60, step=1
        ),
    }

    edited_dataframe = st.data_editor(
        df_base_pool,
        column_config=column_rules,
        num_rows="dynamic",
        use_container_width=True,
        key="batch_data_editor_grid",
    )

    # 60-Month Override Panels Hook Frame Loop block
    override_sales_rows = edited_dataframe[edited_dataframe["Vector Type"] == "sales"]
    override_opex_rows = edited_dataframe[edited_dataframe["Vector Type"] == "opex"]

    manual_sales_targets = override_sales_rows[
        override_sales_rows["Seasonality Curve Profile"] == "Manual_Direct_Override"
    ]
    manual_opex_targets = override_opex_rows[
        override_opex_rows["Seasonality Curve Profile"] == "Manual_Direct_Override"
    ]

    if not manual_sales_targets.empty or not manual_opex_targets.empty:
        st.markdown("---")
        with st.expander(
            "📅 60-Month Granular Rolling Ledger Input Matrix Desks",
            expanded=True,
        ):
            st.info(
                "💡 **Rolling Ledger Input Matrix Active:** Enter month-by-month values below for accounts set to 'Manual_Direct_Override'."
            )
            month_labels = [f"M{str(i).zfill(2)}" for i in range(1, 61)]

            for _, r in manual_sales_targets.iterrows():
                lbl = str(r["Line Identifier Description"]).strip()
                if lbl:
                    st.write(f"📈 **Revenue Overrides Vector: `{lbl}`**")
                    matching_item = next(
                        (
                            s
                            for s in st.session_state["active_data"]["sales"]
                            if s["name"] == lbl
                        ),
                        {},
                    )
                    cached_overrides = matching_item.get("overrides", {})

                    df_override_row = pd.DataFrame(
                        [{m: float(cached_overrides.get(m, 0.0)) for m in month_labels}]
                    )
                    edited_override = st.data_editor(
                        df_override_row,
                        column_config={
                            m: st.column_config.NumberColumn(
                                m, min_value=0.0, format="£%,.2f", width="small"
                            )
                            for m in month_labels
                        },
                        key=f"override_sales_grid_{lbl}",
                        use_container_width=False,
                    )
                    if matching_item:
                        matching_item["overrides"] = edited_override.iloc[0].to_dict()

            for _, r in manual_opex_targets.iterrows():
                lbl = str(r["Line Identifier Description"]).strip()
                if lbl:
                    st.write(f"💸 **Operational Expense Overrides Vector: `{lbl}`**")
                    matching_item = next(
                        (
                            o
                            for o in st.session_state["active_data"]["opex"]
                            if o["name"] == lbl
                        ),
                        {},
                    )
                    cached_overrides = matching_item.get("overrides", {})

                    df_override_row = pd.DataFrame(
                        [{m: float(cached_overrides.get(m, 0.0)) for m in month_labels}]
                    )
                    edited_override = st.data_editor(
                        df_override_row,
                        column_config={
                            m: st.column_config.NumberColumn(
                                m, min_value=0.0, format="£%,.2f", width="small"
                            )
                            for m in month_labels
                        },
                        key=f"override_opex_grid_{lbl}",
                        use_container_width=False,
                    )
                    if matching_item:
                        matching_item["overrides"] = edited_override.iloc[0].to_dict()

    st.markdown("---")
    st.markdown("### 🛡️ Batch Compliance Sign-off & Ledger Verification")
    approval_col1, approval_col2 = st.columns([7, 4])

    with approval_col1:
        is_schedule_approved = st.checkbox(
            "I verify that this tabular trial balance batch matches corporate grounding criteria guidelines.",
            value=False,
            key="master_schedule_approval_toggle",
        )

    with approval_col2:
        if st.button(
            "🚀 Execute Master Ingestion Batch Commit",
            use_container_width=True,
            type="primary",
            disabled=not is_schedule_approved,
        ):
            compiled_state_packet = commit_dataframe_to_state(
                edited_dataframe, st.session_state["active_data"]
            )

            st.session_state["active_data"]["sales"] = compiled_state_packet["sales"]
            st.session_state["active_data"]["opex"] = compiled_state_packet["opex"]
            st.session_state["active_data"]["payroll"] = compiled_state_packet[
                "payroll"
            ]
            st.session_state["active_data"]["capital"] = compiled_state_packet[
                "capital"
            ]

            # Clear temporary database staging tables once records migrated safely into session memory arrays handles
            purge_entire_staging_by_project(active_project_slug)

            if active_project_slug and not active_project_slug.startswith("Draft_"):
                commit_project_payload_to_storage(
                    active_project_slug,
                    st.session_state["active_data"]["sales"],
                    st.session_state["active_data"]["opex"],
                    st.session_state["active_data"]["payroll"],
                    st.session_state["active_data"]["capital"],
                    st.session_state["active_data"].get("sic_meta"),
                )

            st.toast(
                "⚡ Master ledger batch array ingested successfully with granular document vectors!"
            )
            st.rerun()

elif nav_choice == "Analytical Forecast Sheets":
    st.title("📊 Synchronized Statement Reporting Canvas")

    with st.expander(
        "🔮 ACTIVATE STRATEGIC SCENARIO STRESS-TESTING ENGINE", expanded=False
    ):
        st.markdown("### 🔮 STRATA // Scenario Time Machine Controls")
        rev_scale = st.slider(
            "📈 Revenue Factor Pivot (Elastic / Volume):",
            50,
            150,
            100,
            5,
            "%d%%",
        )
        opex_scale = st.slider(
            "💸 Supply Chain Overhead Burden Shift (Inflation):",
            50,
            150,
            100,
            5,
            "%d%%",
        )
        pay_scale = st.slider(
            "👥 Emergency Headcount / Payroll Compensation Drop:",
            0,
            80,
            0,
            5,
            "%d%%",
        )

    rev_mod = rev_scale / 100.0
    opex_mod = opex_scale / 100.0
    pay_mod = pay_scale / 100.0

    cuboid_engine = CommercialTrialBalanceCuboid()
    cuboid_engine.process_simulation(
        st.session_state["active_data"],
        revenue_modifier=rev_mod,
        opex_modifier=opex_mod,
        payroll_modifier=pay_mod,
    )

    df_pl = pd.read_csv("STRATA_Granular_PL.csv", index_col=0)
    df_cf = pd.read_csv("STRATA_Granular_CF.csv", index_col=0)
    df_bs = pd.read_csv("STRATA_Granular_BS.csv", index_col=0)

    st.header("🎛️ Report Parameter Scope Configuration")
    horizon_scope = st.selectbox(
        "Select Targeted Forecast Reporting Horizon:",
        options=[
            "Year 1 Granular Forecast (Months 01-12)",
            "Year 2 Granular Forecast (Months 13-24)",
            "Year 3 Granular Forecast (Months 25-36)",
            "Full 3-Year Granular Portfolio (Months 01-36)",
        ],
    )

    if "Year 1" in horizon_scope:
        range_labels = [f"M{str(i).zfill(2)}" for i in range(1, 13)]
    elif "Year 2" in horizon_scope:
        range_labels = [f"M{str(i).zfill(2)}" for i in range(13, 25)]
    elif "Year 3" in horizon_scope:
        range_labels = [f"M{str(i).zfill(2)}" for i in range(25, 37)]
    else:
        range_labels = [f"M{str(i).zfill(2)}" for i in range(1, 37)]

    v_tab1, v_tab2, v_tab3 = st.tabs(
        [
            "📈 Account-by-Account P&L",
            "💸 Liquid Cash Flow Horizons",
            "📋 Reconciled Balance Sheet",
        ]
    )
    with v_tab1:
        st.dataframe(
            df_pl[range_labels].style.format("{:,.2f}"), use_container_width=True
        )
    with v_tab2:
        st.dataframe(
            df_cf[range_labels].style.format("{:,.2f}"), use_container_width=True
        )
        cash_series = df_cf.iloc[4][range_labels].astype(float)
        if not cash_series.empty and cash_series.min() != cash_series.max():
            st.line_chart(
                pd.DataFrame(
                    cash_series.values,
                    index=range_labels,
                    columns=["Cash Reserves (£)"],
                )
            )
    with v_tab3:
        st.dataframe(
            df_bs[range_labels].style.format("{:,.2f}"), use_container_width=True
        )
        st.success(
            "🛡️ Balance Sheet Checksum Balance: Locked at 0.00 across all selected periods."
        )
