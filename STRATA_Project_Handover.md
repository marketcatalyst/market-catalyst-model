# STRATA Project Handover Baseline & Engineering Blueprint
**System Status:** Core Engine & Cloud Persistence Layer Verified
**Target Platform:** Python 3.11+ | Streamlit | Neon PostgreSQL (v17)
**Current Date:** June 12, 2026

---

## 🧭 Executive Architecture & System Intent
STRATA is a pure Python, object-oriented financial forecasting and 3-way integration engine designed to completely mirror the legacy relational rulesets of WinForecast. It bypasses flat, monolithic cell logic by utilizing isolated, decoupled domain objects that generate strict 60-month array vectors. These vectors are aggregated into a single centralized accounting ledger to build mathematically balanced Profit & Loss, Cash Flow, and Balance Sheet matrices.

---

## 📈 Completed Engineering Milestones

### 1. Core Computational Layer (`engine/`)
* **`assets.py` (Fixed Asset Engine):** Handles capitalized acquisition items, monitoring depreciation curves and Net Book Value (NBV) balances.
* **`finance.py` (Debt Suite Modules):**
    * `HirePurchaseObject`: A dual-engine hybrid that pairs background asset capitalisation/depreciation arrays with reducing-balance debt loops.
    * `LoanObject`: Manages standard long-term corporate tranches, handling upfront gross liquidity injections and principal/interest reduction paths.
* **`income.py` (Revenue Matrix Module):** Maps flat net revenue paths into multi-tier structures. Features dynamic client cash-realization delay profiles (Trade Debtors aging matrices) and native output VAT allocations.
* **`expenditure.py` (Operational OpEx Module):** Maps overhead costs against custom creditor supplier payment terms (Trade Creditors aging matrices) and independent input VAT metrics.
* **`ledger.py` (Centralised Accounting Controller):** The unified master integration brain. Integrates all sub-stream vectors, handles line-by-line Invoice Discounting (Factoring) cash acceleration triggers, and executes continuous rolling UK VAT netting loops with an ironclad 40-day statutory HMRC Direct Debit delay channel.

### 2. Persistence & Serialization Layer (`database/`)
* **`connection.py` (Cloud Infrastructural Gateway):** Manages secure SSL communication handshakes directly with the Neon Cloud database cluster. Implements a thread-safe `ThreadedConnectionPool` (configured for min 1, max 10 concurrent active pipelines) to ensure high-velocity database access without connection degradation or thread locking.
* **`schema.py` (Relational Vector Storage):** Provisions an optimized parent-child database architecture. Top-level configurations are captured in `forecast_scenarios`, while raw 60-month output arrays are streamed vertically into `forecast_monthly_ledger` using high-performance `UPSERT` loops (`ON CONFLICT DO UPDATE`) to maintain absolute data integrity.

### 3. Automated Validation Framework (`tests/`)
A dedicated unit testing folder structure has been established at the root level to run validation checks directly against core financial calculations, shielding the system from logical corruption during downstream upgrades:
* `tests/test_finance.py` — Validates synchronized HP tracking and bank loan amortization.
* `tests/test_income.py` — Verifies multi-month debtor payment profiles and cash recovery.
* `tests/test_expenditure.py` — Verifies creditor supplier delays and cash outflow timing.
* `tests/test_ledger.py` — Audits the 40-day VAT timeline, verifying that the Balance Sheet accurately reflects 4 months of accumulated tax in Month 4, followed by a crisp quarterly settlement clearance in Month 5.
* `tests/test_database.py` — Verifies secure remote connection handshakes with Neon PostgreSQL 17.
* `tests/test_schema.py` — Validates dynamic DDL deployment and verifies zero-loss vector serialization down to the cloud tables.

---

## 🏁 Live Compilation Audit Records (Pass State)

```text
--- ⚖️ HMRC 40-DAY VAT DIRECT DEBIT TIMING VERIFICATION ---
✔️ Month 2 Cumulative VAT Liability:       £4,800.00
✔️ Month 3 Quarter Ends (Liability Held):  £7,200.00
✔️ Month 4 Preparing Return (Cash Intact): £9,600.00
✔️ Month 5 Direct Debit Clears (Settled):  £4,800.00

--- ☁️ NEON POSTGRESQL CONNECTION HANDSHAKE VERIFICATION ---
INFO:STRATA_DATABASE:Neon PostgreSQL connection pool active and provisioned.
🚀 Live Handshake Successful! Connected to: PostgreSQL 17.10

--- ⚖️ STRATA CLOUD SCHEMA SERIALIZATION VERIFICATION ---
INFO:STRATA_SCHEMA:Deploying STRATA relational database tables to Neon Cloud...
INFO:STRATA_SCHEMA:DDL Schema deployment completed successfully.
INFO:STRATA_SCHEMA:Streaming 12-month financial matrix run to cloud table...
INFO:STRATA_SCHEMA:Database sync complete for scenario ID: 1
🚀 SUCCESS! Financial matrix has been dynamically pushed and relational database constraints verified.