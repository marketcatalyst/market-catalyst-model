STRATA SUITE ARCHITECTURAL HANDOVER SUMMARY
Technical Blueprint & Engineering Transition Documentation
1. System Topology & Core Philosophies
STRATA is a production-grade, high-fidelity Three-Way Financial Forecasting Engine served via Streamlit and written in native Python 3.14+. It replaces legacy, error-prone spreadsheet modeling by decoupling calculation inputs from the final outputs.

The core engine uses a transaction-led ledger approach, transforming user inputs into atomic double-entry bookkeeping items (JournalToken) across a 60-month chronological horizon.

Key Architectural Files:
home.py: The system gateway. It initializes top-level settings, verifies secure session states, hosts the enterprise login form, and leverages Streamlit’s native navigation structure (st.navigation) to link components safely.

app.py: The production calculation engine. It runs the database handshake layer, handles unstructured file parsing pipelines, maintains session tables, runs the multi-year transitional token ledger, and structures the dynamic variance dashboard.

2. Low-Level Component Breakdown
A. Core Engine (CommercialTrialBalanceCuboid)
This class forms the back-end ledger system. Rather than storing static financial tables, it computes dynamic 3-way outputs in real-time by processing a pool of double-entry transaction tokens.

Balance Sheet Reconciled Logic: Tracks 16 custom charts of accounts spanning assets (BS_Asset_Cash, BS_Asset_Debtors, BS_Asset_Fixed_Assets), liabilities, equity, and operational P&L trackers.

Tax Integration Cycles: * Models UK-specific standard Output VAT (20%) on sales and recoverable Input VAT on overhead expenses with automated quarterly settlement logic against cash balances.

Simulates corporate payroll deductions (PAYE at 25%, Employer NICs at 13.8%) with automated rolling monthly settlement cycles to HMRC.

Accrues straight-line depreciation at a 10% annual rate based on active net book values of structural infrastructure items.

Warp-Aware Inversion: The .process_simulation() loop accepts real-time macro multipliers (revenue_modifier, opex_modifier, payroll_modifier) allowing the entire 5-year ledger to warp on the fly without mutating base records.

B. Persistence Control Layer (Neon PostgreSQL Pipeline)
The app hooks directly into a serverless Neon database instance via psycopg2. It contains self-healing column migration schemas running automatically at boot time across two system tables:

strata_projects: Stores finalized project scenarios. It packs inputs (sales, opex, payroll, capital) along with active industry classification benchmarks into compressed JSON text objects mapped to a unique project_name index.

strata_staging_inputs: Acts as an unverified, staging ingestion ledger. Scraped entries from unstructured document parsing wait here until a user reviews, overrides, or approves them into production lists.

C. Advanced Multi-Modal Intelligence Desk (Gemini Engine)
Consolidated Parsing (gemini-2.5-flash): Reads raw text, tables, or binary PDF byte buffers via a single-call prompt structure. It concurrently generates a concise structural audit critique and extracts parameters into a formatted JSON vector array to conserve rate scopes.

Strategic Advisory Desk (gemini-1.5-flash): Receives raw 3-way multi-year output dictionaries alongside the active "What-If" slider percentages, synthesizing tailored strategic narrative packs using British English conventions.

3. Session State Registry & Data Models
To ensure strict multi-step data isolation, developers must interact exclusively with these verified session structures:

Python
st.session_state["active_data"] = {
    "sales": [
        {"name": str, "amount": float, "seasonality": str, "debtor_days": int, "vat_applicable": bool}
    ],
    "opex": [
        {"name": str, "amount": float, "seasonality": str, "creditor_days": int, "vat_applicable": bool}
    ],
    "payroll": [
        {"name": str, "amount": float}
    ],
    "capital": [
        {"name": str, "type": str, "value": float, "month": int}
    ],
    "sic_meta": {
        "name": str, "gross_margin": float, "staff_ratio": float, "net_margin": float
    } # Or None
}
st.session_state["active_project_name"] = str         # Active database key
st.session_state["onboarding_complete"] = bool       # Controls benchmark configuration routing
st.session_state["cached_report"] = str              # Retains current Gemini strategic narrative
st.session_state["cached_document_critique"] = str   # Retains AI uploader summary
4. Environment Variables & External Dependencies
The platform requires the following workspace credentials mapped inside your deployment pipeline secrets configuration:

DATABASE_URL: Serverless PostgreSQL connection URI string.

GEMINI_API_KEY: Google AI Studio production credential key.

Comprehensive Environment Requirements (requirements.txt):
streamlit>=1.35.0

pandas>=2.0.0

numpy

matplotlib

openpyxl

google-genai

google-generativeai

pydantic

reportlab

psycopg2-binary

xlsxwriter>=3.1.0

fpdf2

weasyprint==61.2

pydyf==0.10.0

jinja2>=3.1.4

pypdf

tabulate

5. Immediate Technical Roadmap Focus
SIC Benchmark Table Scaling: The data structures load directly from static_data/sic_benchmarks.csv. To expand the app's scope, simply append raw standard corporate listings to this CSV; the application will parse and display them automatically without code changes.

Multi-Scenario Version Control: Upgrade the database payload mapping to support sub-scenario keys (e.g., AD Sports Landlord - Optimistic, AD Sports Landlord - Distress) to house variant financial paths under a unified parent project name.