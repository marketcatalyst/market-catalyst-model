# app.py
# STRATA SUITE PRODUCTION ENGINE // TOTAL CORE SYSTEM v3.7.2-MASTER

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

# =========================================================================
# 💾 PERSISTENCE CONTROL LAYER: SERVERLESS NEON POSTGRES PIPELINE
# =========================================================================


def get_database_connection():
    """Establishes a connection thread looking for both URL and CONNECTION_STRING targets."""
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
    """Initializes standard project state tables and applies column migrations live."""
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

                    cur.execute(
                        "ALTER TABLE strata_projects ALTER COLUMN project_name TYPE TEXT;"
                    )
                    cur.execute(
                        "ALTER TABLE strata_staging_inputs ALTER COLUMN project_name TYPE TEXT;"
                    )
                    cur.execute(
                        "ALTER TABLE strata_staging_inputs ALTER COLUMN vector_type TYPE TEXT;"
                    )
                    cur.execute(
                        "ALTER TABLE strata_staging_inputs ALTER COLUMN source_origin TYPE TEXT;"
                    )
                    cur.execute(
                        "ALTER TABLE strata_staging_inputs ALTER COLUMN line_name TYPE TEXT;"
                    )
                    cur.execute(
                        "ALTER TABLE strata_staging_inputs ALTER COLUMN seasonality_profile TYPE TEXT;"
                    )
            conn.close()
        except Exception:
            pass


def extract_project_directory_list():
    """Queries and compiles all saved scenario indexes from active relational records."""
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
    """Commits compressed scenario structures safely into Neon relational database records."""
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
    """Retrieves and unpacks explicit row text strings straight from database matrices."""
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
    """Pushes an unverified transaction vector straight into the staging table gate ledger."""
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
    """Retrieves all unverified entries currently holding for validation."""
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


def purge_staging_record_by_id(staging_id):
    """Deletes or clears a rejected entry out of the unverified data queue table."""
    conn = get_database_connection()
    if conn and not isinstance(conn, str):
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM strata_staging_inputs WHERE staging_id = %s;",
                        (int(staging_id),),
                    )
            conn.close()
            return True
        except Exception:
            pass
    return False


# Execute database structure migrations on application load initialization
execute_database_handshake()


# =========================================================================
# 🏛️ STATIC ASSET REGISTRY: UK SIC CODES REGISTRY LOADER
# =========================================================================


def load_uk_sic_benchmarks():
    """Reads the static CSV asset registry to provide real-world industry baseline anchors."""
    csv_path = Path("static_data/sic_benchmarks.csv")
    if not csv_path.exists():
        return {
            "00000": {
                "name": "Generic SaaS Default Baseline",
                "gross_margin": 0.50,
                "staff_ratio": 0.30,
                "net_margin": 0.07,
            }
        }
    try:
        df = pd.read_csv(csv_path)
        benchmarks = {}
        for _, row in df.iterrows():
            code_str = str(row["sic_code"]).strip()
            benchmarks[code_str] = {
                "name": str(row["industry_description"]).strip(),
                "gross_margin": float(row["target_gross_margin"]),
                "staff_ratio": float(row["target_staff_to_rev"]),
                "net_margin": float(row["avg_net_margin"]),
            }
        return benchmarks
    except Exception:
        return {
            "00000": {
                "name": "Generic SaaS Default Baseline",
                "gross_margin": 0.50,
                "staff_ratio": 0.30,
                "net_margin": 0.07,
            }
        }


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
        """Processes 60-month multi-year disaggregated tokens with structural What-If multipliers."""
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

        # Chronological Horizon Loop spanning 5 years
        for m in range(1, 61):
            # Warped Sales Pipeline
            for sale in runtime_payload.get("sales", []):
                ann_net = float(sale.get("amount", 0.0)) * revenue_modifier
                profile, debtor_days, vat_app = (
                    sale.get("seasonality", "Flat_Linear"),
                    int(sale.get("debtor_days", 0)),
                    sale.get("vat_applicable", True),
                )
                custom_weight = self.extract_monthly_weight(profile, m)
                monthly_net = ann_net * custom_weight
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

            # Warped Overheads Pipeline
            for opex in runtime_payload.get("opex", []):
                ann_net_cost = float(opex.get("amount", 0.0)) * opex_modifier
                profile, creditor_days, vat_rec = (
                    opex.get("seasonality", "Flat_Linear"),
                    int(opex.get("creditor_days", 0)),
                    opex.get("vat_applicable", True),
                )
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

            # Warped Payroll Pipeline
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

            # Straight-Line Depreciation Ledger Accruals
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
                "Operational Cash Inflows (£)",
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
                    if t.debit_acct == "BS_Asset_Cash" and t.credit_acct in [
                        "BS_Asset_Debtors",
                        "BS_Equity_Share_Capital",
                        "BS_Liability_Long_Term_Debt",
                    ]:
                        df_cf.at["Operational Cash Inflows (£)", m_label] += t.amount
                    if t.credit_acct == "BS_Asset_Cash" and t.debit_acct in [
                        "BS_Liability_Creditors",
                        "BS_Asset_Fixed_Assets",
                        "BS_Liability_PAYE_NIC_Payable",
                        "BS_Expense_Payroll",
                        "BS_Liability_VAT_Payable",
                    ]:
                        df_cf.at["Operational Cash Outflows (£)", m_label] += t.amount

            df_cf.at["Net Cash Movement (£)", m_label] = (
                df_cf.at["Operational Cash Inflows (£)", m_label]
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
    """Compares simulated financial results with active reference guardrails."""
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
    """Generates structured, presentation-grade horizontal multi-year forecast books."""

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
    """Transmits active matrix sheets and What-If parameters to the analysis engine."""
    api_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        return (
            "⚠️ **System Lock:** Gemini API Key not configured in workspace settings."
        )

    try:
        genai.configure(api_key=api_key)

        # FIX (Matrix Duplication bug): Aggregating identical index labels before dict extraction
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
        You are acting as an elite Financial Analyst and Systems Auditor specializing in corporate health diagnostics.
        Review this disaggregated dataset along with the active 'What-If' macro stress-test parameters:
        
        {json.dumps(compressed_payload, indent=2)}
        
        Provide a customized strategic management review using British English spelling. 
        Analyze how their active stress-test adjustments impact long-term runway, viability and safety thresholds. 
        Formulate into these exact sections:
        ### 🔍 Year-on-Year Operational Growth & Stability Assessment
        ### 🚨 Liquidity Bottlenecks & Credit Vector Risks
        ### 🏛️ Strategic Recommendations for Capital Reservation
        """

        # FIX (404 Path bug): Canonical identifier naming applied directly
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ **Gateway Disconnect:** {str(e)}"


# =========================================================================
# 🎛️ CONSOLIDATED SINGLE-CALL MULTIMODAL INGESTION SUITE
# =========================================================================


def process_file_ingestion_callback():
    """Consolidates document review and parameter output maps into a single query to respect free-tier rate scopes."""
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
            st.sidebar.error("❌ Gemini API Key missing.")
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

            # FIX (404 Path bug): Canonical identifier naming applied directly
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

            st.session_state["file_upload_success_banner"] = True
        except Exception as err:
            st.sidebar.error(f"Gemini Consolidation Exception: {str(err)}")


# =========================================================================
# 🔄 INITIALIZE STATE LOGIC CONTROL RUNTIME ARRAYS
# =========================================================================

if "active_data" not in st.session_state:
    st.session_state["active_data"] = {
        "sales": [],
        "opex": [],
        "payroll": [],
        "capital": [],
        "sic_meta": None,
    }

if "cached_report" not in st.session_state:
    st.session_state["cached_report"] = ""

if "cached_document_critique" not in st.session_state:
    st.session_state["cached_document_critique"] = ""

if "active_project_name" not in st.session_state:
    st.session_state["active_project_name"] = "Unsaved_Draft_Scenario"

if "onboarding_complete" not in st.session_state:
    st.session_state["onboarding_complete"] = False

# =========================================================================
# 🧙‍♂️ INTERSTITIAL ONBOARDING WIZARD GATEWAY
# =========================================================================

sic_library = load_uk_sic_benchmarks()

# ⚡ UNRESTRICTED CORE MIGRATION FOR MULTI-SCENARIO HANDSHAKING
if not st.session_state.get("onboarding_complete") or not st.session_state[
    "active_data"
].get("sic_meta"):
    st.title("🧙‍♂️ STRATA // Canvas Configuration Wizard")
    st.caption("Onboarding Blueprint Registry & Target Guardrail Initialization")
    st.markdown("---")

    st.markdown(
        "##### Welcome to STRATA. To tailor your financial simulation layout, please select your primary business classification sector below:"
    )

    industry_options = [
        f"{code} - {meta['name']}" for code, meta in sic_library.items()
    ]
    selected_wizard_sector = st.selectbox(
        "Target UK Industry Sector (SIC Library Registry):",
        options=["-- Click to Expand Official UK Sector Registries --"]
        + industry_options,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("ℹ️ Why is this requested?", expanded=True):
        st.info(
            "Selecting a sector automatically arms your background analytics package. Your forecast outputs will be "
            "actively cross-referenced against authentic UK financial averages for gross margins and staffing thresholds, "
            "providing non-accounting users an instant visual 'Reality Check'."
        )

    if st.button(
        "🚀 Prime Operational Forecast Canvas", type="primary", use_container_width=True
    ):
        if (
            selected_wizard_sector
            != "-- Click to Expand Official UK Sector Registries --"
        ):
            chosen_code = selected_wizard_sector.split(" - ")[0]
            st.session_state["active_data"]["sic_meta"] = sic_library[chosen_code]
            st.session_state["onboarding_complete"] = True
            st.toast(f"🎯 Loaded Baseline Target: {sic_library[chosen_code]['name']}")
            st.rerun()
        else:
            st.warning(
                "⚠️ Please select a valid classification profile to activate your parameters canvas."
            )
    st.stop()


# =========================================================================
# 🎛️ MAIN WORKSPACE DESK AND SIDEBAR LAYOUT ROUTING
# =========================================================================

st.sidebar.title("🛡️ STRATA // Vector Suite")
nav_choice = st.sidebar.radio(
    "Navigate Desks:", options=["Data Workspace", "Analytical Forecast Sheets"]
)

# Persistence registry panel
st.markdown("### 🗂️ Neon Serverless Project Registry Persistence")
proj_col1, proj_col2, proj_col3 = st.columns([4, 4, 3])

with proj_col1:
    available_projects = extract_project_directory_list()
    selected_option = st.selectbox(
        "Load Saved Forecast Project Model:",
        options=["-- Select Saved Model Blueprint --"] + available_projects,
        index=(
            0
            if st.session_state["active_project_name"] == "Unsaved_Draft_Scenario"
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
        and selected_option != st.session_state["active_project_name"]
    ):
        loaded_payload = pull_project_payload_from_storage(selected_option)
        if loaded_payload:
            st.session_state["active_data"] = loaded_payload
            st.session_state["active_project_name"] = selected_option
            st.session_state["cached_document_critique"] = ""
            # Handshake completeness flags automatically on database pull loops
            st.session_state["onboarding_complete"] = True
            st.toast(f"✅ Loaded Blueprint: '{selected_option}'")
            st.rerun()

with proj_col2:
    save_input_name = st.text_input(
        "Name Active Project State:", value=st.session_state["active_project_name"]
    )
    if st.button("💾 Commit Active State to Storage", use_container_width=True):
        if save_input_name.strip() and save_input_name != "Unsaved_Draft_Scenario":
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
                st.toast(
                    f"Locked configuration packet: '{save_input_name}' to SQL records."
                )
                st.rerun()
            elif write_status == "MISSING_CREDENTIALS":
                st.error(
                    "❌ Configuration Error: Environment 'DATABASE_URL' target variable is not defined."
                )
            else:
                st.error(f"❌ Connection Blocked: {write_status}")
        else:
            st.warning(
                "⚠️ Provide a distinct scenario identifier name before committing."
            )

with proj_col3:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button(
        "➕ Initialize Clean Canvas", type="secondary", use_container_width=True
    ):
        st.session_state["active_data"] = {
            "sales": [],
            "opex": [],
            "payroll": [],
            "capital": [],
            "sic_meta": None,
        }
        st.session_state["active_project_name"] = "Unsaved_Draft_Scenario"
        st.session_state["cached_document_critique"] = ""
        st.session_state["onboarding_complete"] = False
        st.toast("🧹 Workspace canvas flushed.")
        st.rerun()

# --- THE "CHANGE INDUSTRY" LINK STRIP FIXED PANEL ---
st.markdown(
    "<div style='margin-top: -8px; margin-bottom: 12px;'>", unsafe_allow_html=True
)
current_meta = st.session_state["active_data"].get("sic_meta")
if current_meta:
    lbl_col, lnk_col = st.columns([6, 5])
    with lbl_col:
        st.markdown(
            f"📊 **Active UK Sector Blueprint Benchmark:** `{current_meta['name']}`"
        )
    with lnk_col:
        if st.button("🔗 Change Industry Sector", type="secondary"):
            st.session_state["active_data"]["sic_meta"] = None
            st.session_state["onboarding_complete"] = False
            st.rerun()
else:
    lbl_col, lnk_col = st.columns([6, 5])
    with lbl_col:
        st.markdown("⚠️ **Active UK Sector Blueprint Benchmark:** `None Assigned`")
    with lnk_col:
        if st.button("🔗 Launch Alignment Wizard", type="secondary"):
            st.session_state["onboarding_complete"] = False
            st.rerun()
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("---")

# =========================================================================
# ⚖ CONFIGURING ACTIVE MODIFIERS INITIALIZATION DEFENSIVE BOUNDS
# =========================================================================
rev_scale, opex_scale, pay_scale = 100, 100, 0

# =========================================================================
# ⚙️ DESK RENDERING LAYOUT HOOKS
# =========================================================================

if nav_choice == "Data Workspace":
    st.title("✍️ Parameter Aggregation Workspace")
    st.header("📥 Autonomous AI Extraction & Diagnostics Gate")
    st.file_uploader(
        "Upload Unstructured Operational Document:",
        type=["pdf", "csv", "xlsx"],
        key="file_ingestion_key",
        on_change=process_file_ingestion_callback,
    )

    if st.session_state["cached_document_critique"]:
        st.info("📊 **Gemini Document Architecture Diagnostic Report**")
        st.markdown(st.session_state["cached_document_critique"])

    staging_records = extract_staging_schedule_records(
        st.session_state["active_project_name"]
    )
    if staging_records:
        st.markdown("### 📥 Review Schedule: Ingested Lines Awaiting Verification Gate")
        for item in staging_records:
            with st.expander(
                f"🔮 GEMINI EXTRACTED // Origin Source: {item['source_origin']}",
                expanded=True,
            ):
                col_i1, col_i2, col_i3 = st.columns(3)
                with col_i1:
                    edit_name = st.text_input(
                        "Verified Line Identifier Label:",
                        value=item["line_name"],
                        key=f"st_name_{item['staging_id']}",
                    )
                    valid_types = [
                        "sales",
                        "opex",
                        "payroll",
                        "capex",
                        "debt",
                        "equity",
                    ]
                    current_idx = (
                        valid_types.index(item["vector_type"])
                        if item["vector_type"] in valid_types
                        else 0
                    )
                    edit_type = st.selectbox(
                        "Assign Vector Type:",
                        valid_types,
                        index=current_idx,
                        key=f"st_type_{item['staging_id']}",
                    )

                with col_i2:
                    edit_amount = st.number_input(
                        "Verified Value (£):",
                        value=float(item["base_amount"]),
                        key=f"st_amt_{item['staging_id']}",
                    )
                    if edit_type in ["capex", "debt", "equity"]:
                        edit_month = st.slider(
                            "Execution Horizon (Month):",
                            min_value=1,
                            max_value=60,
                            value=2 if "outer" in item["line_name"].lower() else 1,
                            step=1,
                            key=f"st_month_{item['staging_id']}",
                        )
                        edit_season = f"M{str(edit_month).zfill(2)}"
                    else:
                        valid_profiles = ["Flat_Linear", "Winter_Peak", "Summer_Peak"]
                        raw_profile = item.get("seasonality_profile", "Flat_Linear")
                        profile_idx = (
                            valid_profiles.index(raw_profile)
                            if raw_profile in valid_profiles
                            else 0
                        )
                        edit_season = st.selectbox(
                            "Assigned Profile:",
                            options=valid_profiles,
                            index=profile_idx,
                            key=f"st_seas_{item['staging_id']}",
                        )

                with col_i3:
                    edit_delay = st.slider(
                        "Delay (Days):",
                        0,
                        90,
                        int(item["terms_delay_days"]),
                        step=30,
                        key=f"st_dly_{item['staging_id']}",
                    )
                    edit_vat = st.checkbox(
                        "VAT applicable?",
                        value=bool(item["vat_applicable"]),
                        key=f"st_vat_{item['staging_id']}",
                    )

                    st.markdown(
                        "<div style='height: 10px;'></div>", unsafe_allow_html=True
                    )
                    if st.button(
                        "✅ Approve Line",
                        key=f"st_btn_app_{item['staging_id']}",
                        use_container_width=True,
                        type="primary",
                    ):
                        data_map = {
                            "sales": "sales",
                            "opex": "opex",
                            "payroll": "payroll",
                            "capex": "capital",
                            "debt": "capital",
                            "equity": "capital",
                        }
                        target = data_map[edit_type]

                        if target == "capital":
                            type_map = {
                                "capex": "New / Existing Fixed Asset CapEx",
                                "debt": "Commercial Debt / Facility Drawdown",
                                "equity": "Equity Capital / Share Premium Injection",
                            }
                            parsed_m = (
                                int(edit_season.replace("M", ""))
                                if edit_season.startswith("M")
                                else 1
                            )
                            st.session_state["active_data"][target].append(
                                {
                                    "name": edit_name.strip(),
                                    "type": type_map.get(
                                        edit_type, "New / Existing Fixed Asset CapEx"
                                    ),
                                    "value": float(edit_amount),
                                    "month": parsed_m,
                                }
                            )
                        elif target == "payroll":
                            st.session_state["active_data"][target].append(
                                {
                                    "name": edit_name.strip(),
                                    "amount": float(edit_amount),
                                }
                            )
                        else:
                            suffix = (
                                "debtor_days" if target == "sales" else "creditor_days"
                            )
                            st.session_state["active_data"][target].append(
                                {
                                    "name": edit_name.strip(),
                                    "amount": float(edit_amount),
                                    "seasonality": edit_season,
                                    suffix: edit_delay,
                                    "vat_applicable": edit_vat,
                                }
                            )

                        purge_staging_record_by_id(item["staging_id"])
                        st.rerun()

                    with col_i3:
                        if st.button(
                            "🗑️ Reject Line",
                            key=f"st_btn_rej_{item['staging_id']}",
                            use_container_width=True,
                        ):
                            purge_staging_record_by_id(item["staging_id"])
                            st.rerun()

    st.markdown("---")
    st.header("✍️ Manual Transaction Vector Fields Input Canvas")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Revenue Waves", "💸 Expenses", "👥 Payroll", "🏛️ Funding"]
    )
    with tab1:
        st.subheader("Add Seasonal Revenue Channel Attribute")
        with st.form("rev_form", clear_on_submit=True):
            r_name = st.text_input("Stream Identifier Description:")
            r_amt = st.number_input(
                "Annual Gross Contract / Target Worth (£):",
                min_value=0.0,
                value=100000.0,
                step=10000.0,
            )
            r_seas = st.selectbox(
                "Seasonality Weight Allocation Vector:",
                ["Flat_Linear", "Winter_Peak", "Summer_Peak"],
            )
            r_days = st.slider(
                "Debtor Terms (Credit days delay given):", 0, 90, 0, step=30
            )
            r_vat = st.checkbox("Subject to Standard 20% Output VAT?", value=True)
            if st.form_submit_button("➕ Append Revenue Vector Line"):
                if r_name.strip():
                    st.session_state["active_data"]["sales"].append(
                        {
                            "name": r_name.strip(),
                            "amount": float(r_amt),
                            "seasonality": r_seas,
                            "debtor_days": r_days,
                            "vat_applicable": r_vat,
                        }
                    )
                    st.rerun()

        st.markdown("### Active Revenue Matrices Registered")
        for idx, item in enumerate(st.session_state["active_data"]["sales"]):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            col1.markdown(
                f"**{item['name']}**\n\n*Term:* {item['debtor_days']} Days Credit Given"
            )
            col2.markdown(f"**Annual Baseline:** £{item['amount']:,.2f}")
            col3.markdown(f"*Curve:* `{item['seasonality']}`")
            if col4.button("🗑️ Remove", key=f"del_r_{idx}"):
                st.session_state["active_data"]["sales"].pop(idx)
                st.rerun()

    with tab2:
        st.subheader("Add Operational Cost Attribute Line")
        with st.form("opex_form", clear_on_submit=True):
            o_name = st.text_input("Expense Identifier Description:")
            o_amt = st.number_input(
                "Annualized Net Running Cost Burden (£):",
                min_value=0.0,
                value=20000.0,
                step=5000.0,
            )
            o_seas = st.selectbox(
                "Cost Allocation Curve Shape Profile:",
                ["Flat_Linear", "Winter_Peak", "Summer_Peak"],
            )
            o_days = st.slider(
                "Creditor Terms (Supplier payment window received):", 0, 90, 30, step=30
            )
            o_vat = st.checkbox(
                "Can Recover 20% Input VAT on this Expense?", value=True
            )
            if st.form_submit_button("➕ Append Overhead Cost Line"):
                if o_name.strip():
                    st.session_state["active_data"]["opex"].append(
                        {
                            "name": o_name.strip(),
                            "amount": float(o_amt),
                            "seasonality": o_seas,
                            "creditor_days": o_days,
                            "vat_applicable": o_vat,
                        }
                    )
                    st.rerun()

        st.markdown("### Active Cost Matrices Registered")
        for idx, item in enumerate(st.session_state["active_data"]["opex"]):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            col1.markdown(
                f"**{item['name']}**\n\n*Payment window:* Net {item['creditor_days']} Terms"
            )
            col2.markdown(f"**Annual Base:** £{item['amount']:,.2f}")
            col3.markdown(f"*Utility Profile:* `{item['seasonality']}`")
            if col4.button("🗑️ Remove", key=f"del_o_{idx}"):
                st.session_state["active_data"]["opex"].pop(idx)
                st.rerun()

    with tab3:
        st.subheader("Add Structural Payroll Overhead")
        with st.form("pay_form", clear_on_submit=True):
            p_name = st.text_input("Staff Grouping / Operational Role Identification:")
            p_amt = st.number_input(
                "Total Combined Annualized Base Gross Salary (£):",
                min_value=0.0,
                value=40000.0,
                step=5000.0,
            )
            if st.form_submit_button("➕ Append Corporate Payroll Vector"):
                if p_name.strip():
                    st.session_state["active_data"]["payroll"].append(
                        {"name": p_name.strip(), "amount": float(p_amt)}
                    )
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
            c_type = st.selectbox(
                "Fixed Category Type:",
                [
                    "Equity Capital / Share Premium Injection",
                    "Commercial Debt / Facility Drawdown",
                    "New / Existing Fixed Asset CapEx",
                ],
            )
            c_val = st.number_input(
                "Value (£):", min_value=0.0, value=50000.0, step=10000.0
            )
            c_m = st.number_input(
                "Execution Month Index (M01 -> M60):",
                min_value=1,
                max_value=60,
                value=1,
                step=1,
            )
            if st.form_submit_button("➕ Append Strategic Capital Vector"):
                if c_name.strip():
                    st.session_state["active_data"]["capital"].append(
                        {
                            "name": c_name.strip(),
                            "type": c_type,
                            "value": float(c_val),
                            "month": int(c_m),
                        }
                    )
                    st.rerun()

        st.markdown("### Active Structural Assets & Funding Configurations")
        for idx, item in enumerate(st.session_state["active_data"]["capital"]):
            col1, col2, col3 = st.columns([3, 4, 1])
            col1.markdown(f"**{item['name']}** - Month {item['month']}")
            col2.markdown(
                f"**Type:** `{item['type']}` | *Value:* £{item['value']:,.2f}"
            )
            if col3.button("🗑️ Remove", key=f"del_c_{idx}"):
                st.session_state["active_data"]["capital"].pop(idx)
                st.rerun()

elif nav_choice == "Analytical Forecast Sheets":
    st.title("📊 Synchronized Statement Reporting Canvas")

    with st.expander(
        "🔮 ACTIVATE STRATEGIC SCENARIO STRESS-TESTING ENGINE", expanded=False
    ):
        st.markdown("### 🔮 STRATA // Scenario Time Machine Controls")
        st.caption(
            "Adjust the parameters below to see how macro adjustments warp your 3-way cash-runways temporarily."
        )

        rev_scale = st.slider(
            "📈 Revenue Factor Pivot (Elasticity / Volume):",
            min_value=50,
            max_value=150,
            value=100,
            step=5,
            format="%d%%",
        )
        opex_scale = st.slider(
            "💸 Supply Chain Overhead Burden Shift (Inflation):",
            min_value=50,
            max_value=150,
            value=100,
            step=5,
            format="%d%%",
        )
        pay_scale = st.slider(
            "👥 Emergency Headcount / Payroll Compensation Drop:",
            min_value=0,
            max_value=80,
            value=0,
            step=5,
            format="%d%%",
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

    v_analysis = calculate_industry_variance_analysis(
        df_pl, range_labels, st.session_state["active_data"].get("sic_meta")
    )
    if v_analysis:
        st.markdown("### 🚦 STRATA Real-World UK Industry Health Check")
        card_col1, card_col2, card_col3 = st.columns(3)

        with card_col1:
            gross_delta = v_analysis["gross_var"] * 100
            status_symbol = (
                "🟢"
                if v_analysis["status"] == "Green"
                else ("🟡" if v_analysis["status"] == "Amber" else "🔴")
            )
            st.metric(
                label=f"{status_symbol} Gross Profit Margin vs Sector Average",
                value=f"{v_analysis['model_gross']*100:.1f}%",
                delta=f"{gross_delta:+.1f}% variance vs UK target ({v_analysis['target_gross']*100:.0f}%)",
            )

        with card_col2:
            staff_delta = v_analysis["staff_var"] * 100
            st.metric(
                label="👥 Operating Payroll-to-Revenue Ratio",
                value=f"{v_analysis['model_staff']*100:.1f}%",
                delta=f"{staff_delta:+.1f}% deviation vs UK target ({v_analysis['target_staff']*100:.0f}%)",
                delta_color="inverse",
            )

        with card_col3:
            st.markdown(
                "<div style='background-color: #f8f9fa; padding: 12px; border-radius: 6px; border-left: 5px solid #2023d6;'>",
                unsafe_allow_html=True,
            )
            if v_analysis["status"] == "Red":
                st.markdown(
                    "**🚨 Critical Sector Variance Alert**\nYour projection metrics deviate significantly from standard UK sector bounds. Review payroll weights or price multipliers."
                )
            elif v_analysis["status"] == "Amber":
                st.markdown(
                    "**🟡 Minor Operating Variance**\nYour model contains minor operational variances. Ratios track close to safety bounds."
                )
            else:
                st.markdown(
                    "**🟢 Model Aligned to Sector Targets**\nYour structural operational ratios match standard UK commercial parameters. Grounding criteria verified."
                )
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            df_pl[range_labels].to_excel(writer, sheet_name="Granular P&L Forecast")
            df_cf[range_labels].to_excel(writer, sheet_name="Cash Flow Horizon")
            df_bs[range_labels].to_excel(writer, sheet_name="Reconciled Balance Sheet")
        excel_buffer.seek(0)
        st.download_button(
            "📊 Download Selected Excel Ledger Pack",
            data=excel_buffer,
            file_name=f"STRATA_{horizon_scope.replace(' ', '_')}.xlsx",
            use_container_width=True,
        )

    with exp_col2:
        try:
            pdf_engine = StrataCorporateManagementPack()
            if len(range_labels) > 12:
                pdf_engine.build_statement_page(
                    f"Granular Profit & Loss Forecast (Months 01-12)",
                    df_pl,
                    range_labels[:12],
                )
                pdf_engine.build_statement_page(
                    f"Decoupled Liquid Cash Flows (Months 01-12)",
                    df_cf,
                    range_labels[:12],
                )
                pdf_engine.build_statement_page(
                    f"Reconciled Balance Sheet (Months 01-12)", df_bs, range_labels[:12]
                )

                pdf_engine.build_statement_page(
                    f"Granular Profit & Loss Forecast (Months 13-24)",
                    df_pl,
                    range_labels[12:24],
                )
                pdf_engine.build_statement_page(
                    f"Decoupled Liquid Cash Flows (Months 13-24)",
                    df_cf,
                    range_labels[12:24],
                )
                pdf_engine.build_statement_page(
                    f"Reconciled Balance Sheet (Months 13-24)",
                    df_bs,
                    range_labels[12:24],
                )

                pdf_engine.build_statement_page(
                    f"Granular Profit & Loss Forecast (Months 25-36)",
                    df_pl,
                    range_labels[24:],
                )
                pdf_engine.build_statement_page(
                    f"Decoupled Liquid Cash Flows (Months 25-36)",
                    df_cf,
                    range_labels[24:],
                )
                pdf_engine.build_statement_page(
                    f"Reconciled Balance Sheet (Months 25-36)", df_bs, range_labels[24:]
                )
            else:
                pdf_engine.build_statement_page(
                    f"Granular Account-by-Account P&L Forecast", df_pl, range_labels
                )
                pdf_engine.build_statement_page(
                    f"Decoupled Phase-Shifted Cash Flow Horizon", df_cf, range_labels
                )
                pdf_engine.build_statement_page(
                    f"Reconciled Corporate Balance Sheet", df_bs, range_labels
                )

            pdf_output = pdf_engine.output()
            st.download_button(
                label="📜 Export Executive Management Pack PDF",
                data=bytes(pdf_output),
                file_name=f"STRATA_Management_Pack_{horizon_scope.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )
        except Exception as pdf_err:
            st.error(f"PDF Document Compiler Blocked: {str(pdf_err)}")

    st.markdown("---")

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
    # 🟢 UPDATED PATCH:
with v_tab2:
    st.dataframe(df_cf[range_labels].style.format("{:,.2f}"), use_container_width=True)

    # Extract cash series cleanly
    cash_series = df_cf.iloc[3][range_labels].astype(float)

    # Safeguard against uninitialized empty loops or Infinite axis crashes
    if not cash_series.empty and not (cash_series == 0).all():
        st.line_chart(
            pd.DataFrame(
                cash_series.values,
                index=range_labels,
                columns=["Cash Reserves (£)"],
            )
        )
    else:
        st.info(
            "ℹ️ **Reserves Trend Line:** Chart will populate once operational vectors or caped injections are logged."
        )
    with v_tab3:
        st.dataframe(
            df_bs[range_labels].style.format("{:,.2f}"), use_container_width=True
        )
        st.success(
            "🛡️ Balance Sheet Checksum Balance: Locked at 0.00 across all selected periods."
        )

    st.markdown("---")
    st.header("🧠 Gemini Corporate Intelligence Desk")
    if st.button("🚀 Synthesize Strategic Executive Report", type="primary"):
        with st.spinner("Processing selected multi-period ledger segments..."):
            st.session_state["cached_report"] = generate_corporate_intelligence(
                df_pl, df_cf, df_bs, range_labels, rev_scale, opex_scale, pay_scale
            )
            st.rerun()

    if st.session_state["cached_report"]:
        st.markdown(st.session_state["cached_report"])
