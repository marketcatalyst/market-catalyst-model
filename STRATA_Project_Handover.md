# STRATA SUITE ARCHITECTURAL HANDOVER SUMMARY
Technical Blueprint & Engineering Transition Documentation

## 1. System Topology & Core Philosophies
STRATA is a Streamlit-based three-way financial forecasting application backed by a double-entry general ledger engine (`AuditedGeneralLedger` in `utils/ledger_engine.py`) and JSON scenario files stored under `saved_scenarios/`.

### Key Modules
* **`home.py`:** Handles session authentication, initializes default session keys, provides one-click blank project creation (`wipe_slate_for_new_client`), and links into the four core workflow pages.
* **`utils/scenario_manager.py`:** Defines `DEFAULT_BLANK_SCENARIO` (`New_Client_Baseline`), canonical entry-mode constants, `normalize_scenario_payload`, disk load/save/delete helpers, and `render_global_scenario_sidebar`.
* **`utils/ledger_engine.py`:** Houses `CHART_OF_ACCOUNTS`, `AuditedGeneralLedger`, `get_exact_period_value`, `audit_ingestion_completeness`, `execute_full_simulation`, and `compile_financial_statements` with no direct `st.session_state` dependency.
* **`pages/1_Data_Ingestion_Gateway.py`, `pages/onboarding.py`, `pages/app.py`, `pages/reports.py`:** Provide document parsing, parameter setup, manual vector entry, dynamic horizon analysis, AI CFO commentary (`gemini-2.5-flash` via `google-genai`), CSV exports, and landscape/portrait PDF generation via `xhtml2pdf`.

## 2. Session State & Scenario Schema
* `st.session_state["authenticated"]`: Boolean gate for workspace access.
* `st.session_state["active_project_name"]`: Active scenario name mapped to `saved_scenarios/<name>.json`.
* `st.session_state["active_data"]`: Dictionary containing `sales`, `cogs`, `opex`, `payroll`, `financed_assets`, `outright_capex`, and `equity_funding`.
* `st.session_state["sic_profile"]`, `st.session_state["onboarding_config"]`, `st.session_state["custom_curves"]`, `st.session_state["vector_couplings"]`, `st.session_state["scratchpad_queue"]`, and `st.session_state["cached_ai_analysis"]`: Supporting configuration and transient workspace state.

## 3. Environment Secrets
* `GEMINI_API_KEY`: Required for document parsing in `pages/1_Data_Ingestion_Gateway.py` and executive commentary generation in `pages/reports.py`.