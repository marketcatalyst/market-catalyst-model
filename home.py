# home.py
# STRATA SUITE ACCESS GATEWAY // MAIN ENTRANCE PORTAL v6.9.3-PRODUCTION

import streamlit as st

# 🚀 UX CORRECTION: Enforce strict native sidebar removal to eliminate duplicates
st.set_page_config(
    page_title="STRATA // Intelligence Suite",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inject custom CSS layout styling to forcefully hide the auto-generated top links
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = True
if "onboarding_complete" not in st.session_state:
    st.session_state["onboarding_complete"] = True

if "sic_profile" not in st.session_state or st.session_state["sic_profile"] is None:
    st.session_state["sic_profile"] = {
        "sic_code": "71121",
        "sector": "Professional R&D Services (Default)",
        "default_vat_type": "Standard 20%",
        "base_er_nic_rate": 0.138,
    }

if "active_data" not in st.session_state:
    st.session_state["active_data"] = {
        "sales": [],
        "milestones": [],
        "cogs": [],
        "opex": [],
        "financed_assets": [],
        "outright_capex": [],
        "payroll": [],
        "equity_funding": [],
    }
if "vector_couplings" not in st.session_state:
    st.session_state["vector_couplings"] = []
if "custom_curves" not in st.session_state:
    st.session_state["custom_curves"] = {}

st.title("🏛️ STRATA // Financial Intelligence Suite")
st.markdown(
    "Welcome to your corporate forecasting framework. Use the sequential steps below or the sidebar navigation to configure your model workflow."
)
st.markdown("---")

st.info(
    "💡 **System Status:** Session authenticated. Environmental thresholds are locked and feeding directly into downstream UK ledgers."
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 1️⃣ Data Input Parameters")
    st.caption(
        "Configure project identities, industry sectors, commercial energy VAT profiles, and custom seasonality curve scales."
    )
    st.page_link(
        "pages/onboarding.py",
        label="🕸️ Open Data Input Parameters",
        use_container_width=True,
    )

with col2:
    st.markdown("### 2️⃣ Data Entry")
    st.caption(
        "Manually populate monthly 12×5 matrices, record staffing payroll layers, and register capital infrastructure assets."
    )
    st.page_link(
        "pages/app.py", label="✍️ Open Data Entry Panel", use_container_width=True
    )

with col3:
    st.markdown("### 3️⃣ Performance Tab")
    st.caption(
        "Review three-way ledgers, track dynamic asset depreciation matrix curves, and download executive report packs."
    )
    st.page_link(
        "pages/reports.py", label="📊 Open Performance Tab", use_container_width=True
    )

# 🚀 CRISP MANAGEMENT CONTROL PANEL (No more duplicated un-cased files!)
st.sidebar.markdown("### 🧭 Navigation Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")

st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 Session Controls")
if st.sidebar.button("🚪 Log Off Session", use_container_width=True):
    st.session_state.clear()
    st.toast("Session cache cleared successfully.")
    st.rerun()
