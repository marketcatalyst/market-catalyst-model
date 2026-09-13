🏛️ Document 1: STRATA_Manual_Playbook.md
Markdown
# STRATA SUITE // SYSTEM OPERATIONS & TECHNICAL BLUEPRINT MANIFEST
# SYSTEM SPECIFICATION VERSION: v7.3.0-PRODUCTION // RECOVERY ARCHIVE

---

## 🧭 1. FRAMEWORK ARCHITECTURE & DIRECTORY MAP
The Strata Suite is a multi-page financial intelligence application built on Python and Streamlit. It operates under a strict system-boundary separation model where each file handles exactly one core operational domain.

```text
market-catalyst-model/
│
├── .streamlit/
│   └── config.toml         # System-level server execution parameters
│
├── database/
│   ├── connection.py       # Thread-safe Neon PostgreSQL connection pooling matrix
│   └── schema.py           # Relational DDL definitions & 60-month vertical streaming serialization
│
├── static_data/
│   └── sic_benchmarks.csv  # Statutory UK standard industrial performance criteria
│
├── requirements.txt         # Core environment package dependency vectors
├── packages.txt             # Linux C-libraries required for WeasyPrint rendering
├── home.py                  # Main Entrance Portal, authentication, and cloud transaction I/O
│
└── pages/
    ├── onboarding.py        # Global Industrial SIC presets & custom curve configurations
    ├── app.py               # Aligned 12×5 manual accounting data entry desks
    ├── 1_Data_Ingestion_Gateway.py # Cognitive document scanning sandbox & 5-year parsing array
    └── reports.py           # 60-month transaction ledgers & compiled WeasyPrint PDF generator
🛠️ 2. SYSTEM BOUNDARY INTER-DEPENDENCIES
To eliminate code fragility and editing errors, modifications to the data timeline are fully synchronized across all core sectors simultaneously:

Ingestion Sandbox: pages/1_Data_Ingestion_Gateway.py uses Gemini models to parse unstructured files straight into a 5-year unified array data matrix (y1 through y5).

Data Entry Desks: pages/app.py renders interactive 12×5 matrices, preserving manual overrides and custom seasonal curves across all 60 months.

Ledger Engine: pages/reports.py converts these matrices into atomic transaction tokens, processing rolling quarterly VAT cycles and true double-entry balance sheet verification checks.

Cloud Serialization: database/schema.py loops vertically through active positions to stream rows by index directly into serverless PostgreSQL tables.

📦 3. CORE DEPLOYMENT STEPS
When pushing updates to the live remote track, always stage and commit interdependent files concurrently to prevent runtime container dropouts:

Bash
git add pages/app.py pages/reports.py pages/1_Data_Ingestion_Gateway.py database/schema.py STRATA_Manual_Playbook.md
git commit -m "sys: deploy synchronized 5-year forecast horizons and double-entry validation tracking"
git push origin production