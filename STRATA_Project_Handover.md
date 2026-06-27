### 🏛️ Document 2: `STRATA_Project_Handover.md`

```markdown
# STRATA SUITE ARCHITECTURAL HANDOVER SUMMARY
Technical Blueprint & Engineering Transition Documentation

## 1. System Topology & Core Philosophies
STRATA is a production-grade, high-fidelity Three-Way Financial Forecasting Engine served via Streamlit and written in native Python 3.11+. It replaces legacy spreadsheet modeling by decoupling calculation inputs from final financial reports.

The core engine uses a transaction-led ledger approach, transforming user inputs into atomic double-entry bookkeeping items (`JournalToken`) across a 60-month chronological horizon.

### Key Architectural Files:
* **`home.py`**: The system gateway. It initializes top-level settings, verifies secure session states, hosts the enterprise sign-in form, and handles saving/loading full scenario payloads to storage.
* **`pages/app.py`**: The production data gateway. It exposes granular input forms for all 8 core account categories extended out to 5 full years (`y1` through `y5`).
* **`pages/reports.py`**: The core simulation and reporting engine. It processes the multi-year token ledgers, runs visual data tab views, and compiles boardroom-ready HTML report print layers into PDFs via WeasyPrint.

## 2. Low-Level Component Breakdown

### A. Core Engine (`CommercialTrialBalanceCuboid`)
This class forms the back-end ledger system. Rather than storing static financial tables, it computes dynamic 3-way outputs in real-time by processing a pool of double-entry transaction tokens.
* **Balance Sheet Checksum Reconciled Logic**: Tracks custom charts of accounts spanning assets (`BS_Asset_Cash`, `BS_Asset_Debtors`, `BS_Asset_Fixed_Assets`), liabilities, equity, and operational P&L trackers. The verification checksum accounts for inverse sign coefficients cleanly via `assets + liabs`, preventing structural verification distortions.
* **Tax Integration Cycles**: Models UK-specific standard Output VAT (20%) on sales and recoverable Input VAT on expenses with automated quarterly settlement logic against cash balances. Simulates corporate payroll deductions (PAYE, Employer NICs at 13.8%) with automated rolling monthly settlement cycles to HMRC.
* **Horizon Curve Scaling**: Loops sequentially from Month 1 to Month 60. Sales and COGS generation lines parse distinct properties for `y1_baseline` through `y5_baseline` fields, running a growth-retention fallback to Year 3 parameters if long-range horizons are left unpopulated by external files.

### B. Persistence Control Layer (Neon PostgreSQL Pipeline)
The app hooks directly into a serverless Neon database instance via `psycopg2` and a centralized connection pool manager.
* **`forecast_scenarios`**: Houses parent metadata configurations indexed to a unique named handle.
* **`forecast_monthly_ledger`**: Automatically streams calculated data arrays vertically by `month_index` (from Month 1 to Month 60). Because it records metrics on a monthly rolling basis rather than hardcoding year columns horizontally, the schema natively scales to support full 5-year datasets without requiring structural DDL migrations.

### C. Advanced Multi-Modal Intelligence Desk (Gemini Engine)
* **Consolidated Parsing (`gemini-pro`)**: Used in `pages/1_Data_Ingestion_Gateway.py` to extract 5-year structured parameters (`y1` through `y5`) and curve profiles out of unstructured documents directly into a sandbox data editor grid.
* **Strategic Advisory Desk (`gemini-2.5-flash`)**: Processes compiled 3-way output dictionaries, delivering deep systems-thinking evaluations and sharp corporate narratives tailored to C-suite board reviews using clean UK English conventions.

## 3. Session State Registry & Data Models
To ensure multi-step data isolation, developers must interact exclusively with these verified session structures:

```python
st.session_state["active_data"] = {
    "sales": [
        {
            "name": str, "y1_baseline": float, "y2_baseline": float, "y3_baseline": float, 
            "y4_baseline": float, "y5_baseline": float, "seasonality": str, 
            "payment_delay": int, "flex_pct": int, "vat_rate_type": str, "overrides": dict
        }
    ],
    "cogs": [
        {
            "name": str, "y1_baseline": float, "y2_baseline": float, "y3_baseline": float, 
            "y4_baseline": float, "y5_baseline": float, "seasonality": str, 
            "flex_pct": int, "vat_rate_type": str, "overrides": dict
        }
    ],
    "opex": [
        {
            "name": str, "vat_rate_type": str, "flex_rates": dict, "matrix_data": dict
        }
    ],
    "payroll": [
        {
            "name": str, "headcount": int, "monthly_wage": float, "start_month": int, 
            "end_month": int, "flex_pct": int
        }
    ],
    "financed_assets": [
        {
            "name": str, "amount": float, "month": int, "deposit_pct": int, 
            "term_months": int, "interest_rate": float, "depreciation_rate": float
        }
    ],
    "outright_capex": [
        {
            "name": str, "amount": float, "month": int, "depreciation_rate": float
        }
    ],
    "equity_funding": [
        {"name": str, "amount": float, "month": int}
    ]
}
st.session_state["active_project_name"] = str         # Active database scenario lookup key
st.session_state["authenticated"] = bool             # Controls gateway access token verification
st.session_state["scratchpad_queue"] = list          # Temporary volatile uploader sandbox storage
4. Environment Variables & External Dependencies
The platform requires the following workspace credentials mapped inside your deployment pipeline secrets configuration:

DATABASE_URL: Serverless PostgreSQL connection URI string.

GEMINI_API_KEY: Google AI Studio production credential key.


---

### 📦 Push Documentation Assets to Production

To commit both complete markdown logs directly into your local directory and sync them with your remote repository, execute this terminal block:

```bash
cd C:\Users\marke\market-catalyst-model

# Stage both verified documentation assets
git add STRATA_Manual_Playbook.md STRATA_Project_Handover.md

# Lock them into your local branch history
git commit -m "docs: write absolute single source of truth for playbook and handover documents"

# Push directly to GitHub
git push origin production