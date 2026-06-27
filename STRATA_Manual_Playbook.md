# STRATA SUITE // SYSTEM OPERATIONS & TECHNICAL BLUEPRINT MANIFEST
# SYSTEM SPECIFICATION VERSION: v7.1.0-PRODUCTION // RECOVERY ARCHIVE

---

## 🧭 1. FRAMEWORK ARCHITECTURE & DIRECTORY MAP
The Strata Suite is a multi-page financial intelligence application built on Python and Streamlit. It operates under a strict system-boundary separation model where each file handles exactly one core operational domain.

```text
market-catalyst-model/
│
├── .streamlit/
│   └── config.toml         # System-level server execution parameters
│
├── requirements.txt         # Core environment package dependency vectors
│
├── home.py                  # Main Entrance Portal, authentication, and database I/O
│
└── pages/
    ├── onboarding.py        # Global Industrial SIC presets & custom curve configurations
    ├── app.py               # Granular 12x5 accounting data entry desks
    └── reports.py           # 3-Way trial balance simulation engine & WeasyPrint PDF compiler