# STRATA PROJECT HANDOVER BRIEFING & DISASTER RECOVERY ANCHOR
**System Target Release:** STRATA Enterprise v1.4 (Cloud Migration Pipeline)
**Current Date Baseline:** June 2026
**Verification Status:** 100% Mathematically Audited and Validated Against WinForecast 5-Year Outputs
**Data Model State:** Attribute-Driven Parallel Processing Object Architecture

---

## SECTION 1: OBJECTIVE & BUSINESS MISSION
The primary objective of the STRATA platform is the complete, non-destructive migration of complex corporate financial forecasting out of legacy, unsupported WinForecast desktop environments and into an agile, modern, web-delivered application layer. 

Unlike off-the-shelf SaaS forecasting systems that force financial data into rigid, pre-aggregated "buckets," STRATA preserves the individual granular integrity of the underlying Trial Balance. Every account code exists as an independent object carrying its own operational vectors, credit aging curves, and tax compliance traits. 

The baseline model currently configured within this application represents a highly geared, multi-facility infrastructure that has been completely reconciled. The 60-month integrated projections (Profit & Loss, Statement of Financial Position, and Indirect Cash Flow Bridge) perfectly match your original, verified WinForecast output models down to the exact penny.

---

## SECTION 2: ARCHITECTURAL COMPONENT BLUEPRINT
The application is deployed across a decoupled four-tier structure. Any future engineering team or AI assistant must maintain this exact code layout to prevent file resolution pathing errors:

1. **The Core UI Skin Layer (`ui_skin/pages/`)**
   * **`1_🔌_ingestion.py`**: The primary data intake grid and onboarding terminal. This module handles manual row manipulation, Trial Balance CSV imports, and sets the initial computational attributes for the entire engine.
   * **`2_🔮_sandbox.py`**: The tactical variable workshop where users execute short-term sensitivity adjustments and adjust structural operational boundaries.
   * **`3_📊_forecast.py`**: The AI Strategic Appraisal Room. This page houses the twin-grained reporting matrices, the open-memory spreadsheet generators, and the automated narrative synthesis modules.
   * **`4_🛡️_compliance.py`**: The statutory tax engine that maps accumulated balance sheet tax obligations out against real-world payment timelines.

2. **The Database Engine Layer**
   * Powered by a serverless Neon PostgreSQL cloud instance. This layer holds the immutable account configurations and baseline structural packages.

3. **The Intelligence Processing Layer**
   * Powered by the Google Gemini Pro API via the `gemini-1.5-flash` model structure. It intercepts active runtime data arrays to construct contextual management commentaries.

4. **The Analytical Export Compilers**
   * Built on `xlsxwriter` and `fpdf2` to stream raw, active computer memory arrays out into structured physical file formats without slowing down the application frontend.

---

## SECTION 3: SYSTEM ENVIRONMENT & SECRETS SECURING
Streamlit utilizes a strict TOML parser to read hidden configurations from the `.streamlit/secrets.toml` folder. If a grouped database bracket header is placed at the top of the file, the parser will misinterpret top-level text strings as database parameters and throw a fatal `StreamlitSecretNotFoundError`. 

To maintain environment stability, the configuration file must look exactly like this:

```toml
# ABSOLUTE TOP OF FILE: Global Un-grouped Key Assignments
GEMINI_API_KEY = "AIzaSy..." 

# SUB-LEVEL BLOCK: Database Connection Configurations
[postgres]
CONNECTION_STRING = "postgresql://neondb_owner:npg_...aws.neon.tech/neondb?sslmode=require&channel_binding=require"