# STRATA SUITE // SYSTEM OPERATIONS & TECHNICAL BLUEPRINT MANIFEST
# SYSTEM SPECIFICATION VERSION: v12.0-SSOT-PRODUCTION

---

## 1. FRAMEWORK ARCHITECTURE & DIRECTORY MAP
STRATA is a multi-page financial intelligence application built on Python and Streamlit. It decouples double-entry general ledger accounting and scenario state management from UI rendering and report exports.

    market-catalyst-model/
    ├── home.py                            # Main portal, session auth, and project hub
    ├── requirements.txt                   # Python package dependencies
    ├── packages.txt                       # System packages for deployment environments
    ├── saved_scenarios/                   # JSON scenario files persisted on disk
    ├── pages/
    │   ├── 1_Data_Ingestion_Gateway.py    # Document/image scanning sandbox (google-genai)
    │   ├── onboarding.py                  # Baseline parameters and setup wizard
    │   ├── app.py                         # Vector configuration and data entry desk
    │   └── reports.py                     # 3-way statements, schedules, AI commentary & PDF/CSV exports
    └── utils/
        ├── scenario_manager.py            # Scenario CRUD, schema normalization & sidebar desk
        ├── ledger_engine.py               # Double-entry GL, simulation & statement compiler
        ├── depreciation.py                # Monthly asset depreciation calculations
        ├── invoice_finance.py             # Invoice finance advance/fee helper
        └── consolidation.py               # Multi-entity balance sheet consolidation

## 2. SYSTEM BOUNDARY INTER-DEPENDENCIES
* **Project Hub (`home.py` & `utils/scenario_manager.py`):** Manages `DEFAULT_BLANK_SCENARIO` (`New_Client_Baseline`), switching saved scenarios, starting a new blank project (`create_blank_scenario`), saving/cloning scenarios, and deleting active scenarios without auto-seeding legacy demo files on empty folders.
* **Data Ingestion Gateway (`pages/1_Data_Ingestion_Gateway.py`):** Uses `google-genai` (`genai.Client`) to extract structured items into a temporary `scratchpad_queue` before authorizing and committing them into `st.session_state["active_data"]`.
* **Parameters & Data Entry (`pages/onboarding.py` & `pages/app.py`):** Captures setup parameters (`onboarding_config`) and vector items across `sales`, `cogs`, `opex`, `payroll`, `outright_capex`, `financed_assets`, and `equity_funding`, supporting `Annual Baseline + Monthly Distribution Curve`, `Manual Monthly Override`, and `Flat Linear Baseline`.
* **Ledger Engine & Reporting (`utils/ledger_engine.py` & `pages/reports.py`):** `execute_full_simulation` posts double-entry journals into `AuditedGeneralLedger` and compiles Profit & Loss, Cash Flow, and Balance Sheet statements across configurable operating horizons, feeding UI tables, CSV downloads, and `xhtml2pdf` report packs.

## 3. DEPLOYMENT WORKFLOW
1. Verify syntax across modified modules (`python -m py_compile ...`).
2. Remove any unwanted test/demo `.json` files in `saved_scenarios/` prior to beta release.
3. Stage, commit, and push changes to `origin/main` to trigger Streamlit Cloud redeployment.