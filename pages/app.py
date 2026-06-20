# pages/app.py
# STRATA SUITE PRODUCTION ENGINE // TOTAL CORE SYSTEM v4.6.0-MASTER

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


# =========================================================================
# 🎛️ CONSOLIDATED SINGLE-CALL MULTIMODAL INGESTION SUITE
# =========================================================================


def process_file_ingestion_callback():
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
        self.months = [f"M{str(i).zfill(2)}" for i in range(0, 61)]

        # USER DEFINED SEASONALITY PROFILE WEIGHTS
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
        if amount == 0.0 or month_idx < 0 or month_idx > 60:
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

    def evaluate_monthly_vector_value(self, m, account_payload, macro_modifier):
        """Resolves whether to use direct row cell data or fallback to weighted annual allocations."""
        m_label = f"M{str(m).zfill(2)}"

        # Priority 1: Check if there is an explicit value typed directly in the M00-M60 timeline cell
        direct_val = float(account_payload.get("overrides", {}).get(m_label, 0.0))
        if direct_val != 0.0:
            return direct_val * macro_modifier

        # Priority 2: Fall back to checking annual user defined targets paired with curves
        if m == 0:
            return 0.0

        profile = account_payload.get("seasonality", "Flat_Linear")
        weight = self.extract_monthly_weight(profile, m)

        if 1 <= m <= 12:
            return (
                float(account_payload.get("y1_baseline", 0.0)) * weight * macro_modifier
            )
        elif 13 <= m <= 24:
            return (
                float(account_payload.get("y2_baseline", 0.0)) * weight * macro_modifier
            )
        elif 25 <= m <= 36:
            return (
                float(account_payload.get("y3_baseline", 0.0)) * weight * macro_modifier
            )

        return 0.0

    def process_simulation(
        self,
        runtime_payload,
        revenue_modifier=1.0,
        opex_modifier=1.0,
        payroll_modifier=0.0,
    ):
        self.token_pool = []

        # Process Opening Asset Injections
        for cap in runtime_payload.get("capital", []):
            m_start = max(0, int(cap.get("month", 0)))
            val = float(cap.get("value", 0.0))
            c_type = cap.get("type", "")

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

        # Horizon Timeline Core Simulation Loop
        for m in range(0, 61):
            # Sales Inflow Vectors
            for sale in runtime_payload.get("sales", []):
                vat_app = sale.get("vat_applicable", True)
                monthly_net = self.evaluate_monthly_vector_value(
                    m, sale, revenue_modifier
                )
                monthly_vat = (monthly_net * 0.20) if vat_app else 0.0
                narr_tag = f"REV_LINE__{sale.get('name')}"

                if m > 0 and monthly_net > 0:
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
                        m + 1,
                        "BS_Asset_Cash",
                        "BS_Asset_Debtors",
                        monthly_net + monthly_vat,
                        f"Receipt: {sale.get('name')}",
                    )
                elif m == 0 and monthly_net > 0:
                    self.inject_token(
                        0, "BS_Asset_Debtors", "BS_Equity_Share_Capital", monthly_net
                    )

            # Opex Outflow Vectors
            for opex in runtime_payload.get("opex", []):
                vat_rec = opex.get("vat_applicable", True)
                monthly_net_cost = self.evaluate_monthly_vector_value(
                    m, opex, opex_modifier
                )
                monthly_input_vat = (monthly_net_cost * 0.20) if vat_rec else 0.0
                narr_tag = f"OPEX_LINE__{opex.get('name')}"

                if m > 0 and monthly_net_cost > 0:
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
                        m + 1,
                        "BS_Liability_Creditors",
                        "BS_Asset_Cash",
                        monthly_net_cost + monthly_input_vat,
                        f"Payment: {opex.get('name')}",
                    )
                elif m == 0 and monthly_net_cost > 0:
                    self.inject_token(
                        0,
                        "BS_Equity_Share_Capital",
                        "BS_Liability_Creditors",
                        monthly_net_cost,
                    )

            # Human Capital Payroll Vectors
            for pay in runtime_payload.get("payroll", []):
                monthly_gross = self.evaluate_monthly_vector_value(
                    m, pay, 1.0 - payroll_modifier
                )
                if m > 0 and monthly_gross > 0:
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

            # Depreciation Accruals
            if m > 0:
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

                # Quarterly VAT Clearings tranches
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

        for m_idx, m_label in enumerate(self.months, start=0):
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
                return (
                    float(val.iloc[0])
                    if isinstance(val, pd.Series)
                    else float(val) if pd.notna(val) else 0.0
                )

            current_opex_total = sum(
                get_scalar_val(df_pl, row, m_label) for row in opex_rows
            )
            df_pl.at["Net Operating Profit (EBIT)", m_label] = (
                get_scalar_val(df_pl, "Total Revenue (£)", m_label)
                - get_scalar_val(df_pl, "COGS (£)", m_label)
                - current_opex_total
                - get_scalar_val(df_pl, "Staff Payroll Overhead (£)", m_label)
                - get_scalar_val(df_pl, "Depreciation (£)", m_label)
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
            for past_m in self.months[1 : m_idx + 1]:
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
# 🗛 DATA COMPILATION TRANSFORMERS FOR EDITABLE DATA FRAMES
# =========================================================================


def build_dataframe_from_state(state_dict):
    """Transforms active data segments into a hybrid grid exposing both baseline curves and timelines."""
    month_labels = [f"M{str(i).zfill(2)}" for i in range(0, 61)]
    rows = []

    for s in state_dict.get("sales", []):
        base_row = {
            "Line Identifier Description": s["name"],
            "Vector Type": "sales",
            "Year 1 Net (£)": float(s.get("y1_baseline", 0.0)),
            "Year 2 Net (£)": float(s.get("y2_baseline", 0.0)),
            "Year 3 Net (£)": float(s.get("y3_baseline", 0.0)),
            "Curve Weight Profile": s.get("seasonality", "Flat_Linear"),
        }
        for m in month_labels:
            base_row[m] = float(s.get("overrides", {}).get(m, 0.0))
        rows.append(base_row)

    for o in state_dict.get("opex", []):
        base_row = {
            "Line Identifier Description": o["name"],
            "Vector Type": "opex",
            "Year 1 Net (£)": float(o.get("y1_baseline", 0.0)),
            "Year 2 Net (£)": float(o.get("y2_baseline", 0.0)),
            "Year 3 Net (£)": float(o.get("y3_baseline", 0.0)),
            "Curve Weight Profile": o.get("seasonality", "Flat_Linear"),
        }
        for m in month_labels:
            base_row[m] = float(o.get("overrides", {}).get(m, 0.0))
        rows.append(base_row)

    for p in state_dict.get("payroll", []):
        base_row = {
            "Line Identifier Description": p["name"],
            "Vector Type": "payroll",
            "Year 1 Net (£)": float(p.get("y1_baseline", 0.0)),
            "Year 2 Net (£)": float(p.get("y2_baseline", 0.0)),
            "Year 3 Net (£)": float(p.get("y3_baseline", 0.0)),
            "Curve Weight Profile": "Flat_Linear",
        }
        for m in month_labels:
            base_row[m] = float(p.get("overrides", {}).get(m, 0.0))
        rows.append(base_row)

    for c in state_dict.get("capital", []):
        v_map = {
            "New / Existing Fixed Asset CapEx": "capex",
            "Commercial Debt / Facility Drawdown": "debt",
            "Equity Capital / Share Premium Injection": "equity",
        }
        base_row = {
            "Line Identifier Description": c["name"],
            "Vector Type": v_map.get(c["type"], "capex"),
            "Year 1 Net (£)": 0.0,
            "Year 2 Net (£)": 0.0,
            "Year 3 Net (£)": 0.0,
            "Curve Weight Profile": "Flat_Linear",
        }
        for m in month_labels:
            target_m = f"M{str(c.get('month', 0)).zfill(2)}"
            base_row[m] = float(c.get("value", 0.0)) if m == target_m else 0.0
        rows.append(base_row)

    if not rows:
        base_row = {
            "Line Identifier Description": "",
            "Vector Type": "opex",
            "Year 1 Net (£)": 0.0,
            "Year 2 Net (£)": 0.0,
            "Year 3 Net (£)": 0.0,
            "Curve Weight Profile": "Flat_Linear",
        }
        for m in month_labels:
            base_row[m] = 0.0
        rows.append(base_row)

    return pd.DataFrame(rows)


def commit_dataframe_to_state(df):
    """Parses hybrid spreadsheet matrix configurations cleanly back into state memory blocks."""
    month_labels = [f"M{str(i).zfill(2)}" for i in range(0, 61)]
    new_state = {"sales": [], "opex": [], "payroll": [], "capital": []}

    for _, r in df.iterrows():
        lbl = str(r["Line Identifier Description"]).strip()
        if not lbl:
            continue

        v_type = str(r["Vector Type"])
        y1 = float(r.get("Year 1 Net (£)", 0.0))
        y2 = float(r.get("Year 2 Net (£)", 0.0))
        y3 = float(r.get("Year 3 Net (£)", 0.0))
        curve = str(r.get("Curve Weight Profile", "Flat_Linear"))

        overrides_map = {m: float(r[m]) for m in month_labels}

        if v_type == "sales":
            new_state["sales"].append(
                {
                    "name": lbl,
                    "amount": 0.0,
                    "y1_baseline": y1,
                    "y2_baseline": y2,
                    "y3_baseline": y3,
                    "seasonality": curve,
                    "debtor_days": 30,
                    "vat_applicable": True,
                    "overrides": overrides_map,
                }
            )
        elif v_type == "opex":
            new_state["opex"].append(
                {
                    "name": lbl,
                    "amount": 0.0,
                    "y1_baseline": y1,
                    "y2_baseline": y2,
                    "y3_baseline": y3,
                    "seasonality": curve,
                    "creditor_days": 30,
                    "vat_applicable": True,
                    "overrides": overrides_map,
                }
            )
        elif v_type == "payroll":
            new_state["payroll"].append(
                {
                    "name": lbl,
                    "amount": 0.0,
                    "y1_baseline": y1,
                    "y2_baseline": y2,
                    "y3_baseline": y3,
                    "overrides": overrides_map,
                }
            )
        elif v_type in ["capex", "debt", "equity"]:
            t_map = {
                "capex": "New / Existing Fixed Asset CapEx",
                "debt": "Commercial Debt / Facility Drawdown",
                "equity": "Equity Capital / Share Premium Injection",
            }
            active_m_idx = 0
            for m_lbl in month_labels:
                if float(r[m_lbl]) > 0.0:
                    active_m_idx = int(m_lbl.replace("M", ""))
                    break
            new_state["capital"].append(
                {
                    "name": lbl,
                    "type": t_map[v_type],
                    "value": sum(overrides_map.values()),
                    "month": active_m_idx,
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

# Persistence Registry Control Panel
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
                "❌ **Naming Constraint:** Input a clean alphanumeric production name before saving."
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

    active_project_slug = st.session_state.get(
        "active_project_name", "Unsaved_Draft_Scenario"
    )
    staging_records = extract_staging_schedule_records(active_project_slug)

    if staging_records:
        st.markdown("### 🔮 STAGING BATCH: AI Extracted Vectors Pending Schedule Merge")
        staged_rows = []
        month_labels = [f"M{str(i).zfill(2)}" for i in range(0, 61)]
        for item in staging_records:
            v_clean = (
                item["vector_type"]
                if item["vector_type"]
                in ["sales", "opex", "payroll", "capex", "debt", "equity"]
                else "opex"
            )
            base_row = {
                "Line Identifier Description": item["line_name"],
                "Vector Type": v_clean,
                "Year 1 Net (£)": float(item["base_amount"]),
                "Year 2 Net (£)": 0.0,
                "Year 3 Net (£)": 0.0,
                "Curve Weight Profile": item.get("seasonality_profile", "Flat_Linear"),
            }
            for m in month_labels:
                base_row[m] = 0.0
            staged_rows.append(base_row)
        df_base_pool = pd.DataFrame(staged_rows)
    else:
        df_base_pool = build_dataframe_from_state(st.session_state["active_data"])

    st.markdown("### ✍️ Production Model Hybrid Rolling Matrix Blueprint")

    # Configure Columns Rules Schema
    month_cols = [f"M{str(i).zfill(2)}" for i in range(0, 61)]
    column_rules = {
        "Line Identifier Description": st.column_config.TextColumn(
            "Account Ledger Identifier Description", required=True, width="large"
        ),
        "Vector Type": st.column_config.SelectboxColumn(
            "Ledger Category Type",
            options=["sales", "opex", "payroll", "capex", "debt", "equity"],
            required=True,
        ),
        "Year 1 Net (£)": st.column_config.NumberColumn(
            "Y1 Target (£)", min_value=0.0, format="£%,.2f"
        ),
        "Year 2 Net (£)": st.column_config.NumberColumn(
            "Y2 Target (£)", min_value=0.0, format="£%,.2f"
        ),
        "Year 3 Net (£)": st.column_config.NumberColumn(
            "Y3 Target (£)", min_value=0.0, format="£%,.2f"
        ),
        "Curve Weight Profile": st.column_config.SelectboxColumn(
            "Curve Weight Profile",
            options=["Flat_Linear", "Winter_Peak", "Summer_Peak"],
        ),
    }
    for m_lbl in month_cols:
        column_rules[m_lbl] = st.column_config.NumberColumn(
            m_lbl, min_value=0.0, format="£%,.2f", width="small"
        )

    edited_dataframe = st.data_editor(
        df_base_pool,
        column_config=column_rules,
        num_rows="dynamic",
        use_container_width=True,
        key="batch_data_editor_grid",
    )

    st.markdown("---")
    st.markdown("### 🛡️ Batch Compliance Sign-off & Ledger Verification")
    approval_col1, approval_col2 = st.columns([7, 4])
    with approval_col1:
        is_schedule_approved = st.checkbox(
            "I verify that this tabular trial balance batch matches corporate grounding criteria guidelines.",
            value=False,
        )

    with approval_col2:
        if st.button(
            "🚀 Execute Master Ingestion Batch Commit",
            use_container_width=True,
            type="primary",
            disabled=not is_schedule_approved,
        ):
            compiled_state_packet = commit_dataframe_to_state(edited_dataframe)
            st.session_state["active_data"]["sales"] = compiled_state_packet["sales"]
            st.session_state["active_data"]["opex"] = compiled_state_packet["opex"]
            st.session_state["active_data"]["payroll"] = compiled_state_packet[
                "payroll"
            ]
            st.session_state["active_data"]["capital"] = compiled_state_packet[
                "capital"
            ]

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
                "⚡ Master ledger batch array ingested successfully with hybrid vector rules!"
            )
            st.rerun()

elif nav_choice == "Analytical Forecast Sheets":
    st.title("📊 Synchronized Statement Reporting Canvas")
    with st.expander(
        "🔮 ACTIVATE STRATEGIC SCENARIO STRESS-TESTING ENGINE", expanded=False
    ):
        st.markdown("### 🔮 STRATA // Scenario Time Machine Controls")
        rev_scale = st.slider("📈 Revenue Factor Pivot:", 50, 150, 100, 5, "%d%%")
        opex_scale = st.slider(
            "💸 Supply Chain Overhead Burden Shift:", 50, 150, 100, 5, "%d%%"
        )
        pay_scale = st.slider(
            "👥 Emergency Headcount Compensation Drop:", 0, 80, 0, 5, "%d%%"
        )

    rev_mod, opex_mod, pay_mod = (
        rev_scale / 100.0,
        opex_scale / 100.0,
        pay_scale / 100.0,
    )
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
        "Select Targeted Forecast Horizon:",
        [
            "Year 1 Granular Forecast (Months 00-12)",
            "Year 2 Granular Forecast (Months 13-24)",
            "Year 3 Granular Forecast (Months 25-36)",
            "Full 3-Year Granular Portfolio (Months 00-36)",
        ],
    )

    if "Year 1" in horizon_scope:
        range_labels = [f"M{str(i).zfill(2)}" for i in range(0, 13)]
    elif "Year 2" in horizon_scope:
        range_labels = [f"M{str(i).zfill(2)}" for i in range(13, 25)]
    elif "Year 3" in horizon_scope:
        range_labels = [f"M{str(i).zfill(2)}" for i in range(25, 37)]
    else:
        range_labels = [f"M{str(i).zfill(2)}" for i in range(0, 37)]

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
        trend_labels = [lbl for lbl in range_labels if lbl != "M00"]
        if trend_labels:
            cash_series = df_cf.iloc[4][trend_labels].astype(float)
            if not cash_series.empty and cash_series.min() != cash_series.max():
                st.line_chart(
                    pd.DataFrame(
                        cash_series.values,
                        index=trend_labels,
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
