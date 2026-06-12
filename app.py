# app.py

import os
import streamlit as st

# Configure global multi-page entry shell parameters
st.set_page_config(page_title="STRATA // Corporate Portal", layout="wide")

st.title("🛡️ STRATA // Financial Intelligence Portal")
st.caption("Enterprise Workspace Security Engine & Scenario Access Control Gateway")
st.markdown("---")

st.subheader("👋 Welcome back, Marketcatalyst")
st.markdown("""
Select an active project workspace from the left-hand sidebar menu navigation to begin modeling:
* **`✍️ Data Input Workspace`** — Access your Automated Ingestion Pipelines, Manual Operational Ledger, and Capital/Financing Desk.
* **`⚗️ Sandbox`** — Run rapid multi-variant calculation checks on prospective asset classes.
* **`📈 Forecast Matrix`** — View advanced aggregated multi-year financial runway comparisons.
""")

st.success("⚡ System Registry Matrix Online. Core calculation modules, local tax shapes, and structural debt engines are fully hydrated.")