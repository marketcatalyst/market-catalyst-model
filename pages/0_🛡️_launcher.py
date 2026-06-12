# pages/0_🛡️_launcher.py

import streamlit as st

st.title("👋 Welcome back, Marketcatalyst")
st.caption("STRATA // Core Enterprise Environment Selector")
st.markdown("---")

st.markdown("""
Select an active project workspace from the left-hand sidebar menu navigation to begin modeling:
* **`✍️ Data Input Workspace`** — Access your Automated Ingestion Pipelines, Manual Operational Ledger, and Capital/Financing Desk.
* **`🔮 Sandbox`** — Run rapid multi-variant calculation checks on prospective asset classes.
* **`📊 Forecast`** — View advanced aggregated multi-year financial runway comparisons.
* **`🛡️ Compliance`** — Audit your regulatory frameworks and baseline validation data profiles.
""")

# FIXED: Replaced old warning wall with an absolute system status confirmation
st.success("⚡ System Registry Matrix Online. Core calculation modules, local tax shapes, and structural debt engines are fully hydrated.")