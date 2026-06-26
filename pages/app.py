# pages/app.py
# STRATA SUITE // DATA ENTRY & UPLOAD MATRIX DESK v6.9.2-PRODUCTION

import streamlit as st
import pandas as pd

if not st.session_state.get("authenticated"):
    st.warning("⚠️ Access Intercepted.")
    st.stop()

active_sic = st.session_state["sic_profile"]
st.title("📥 Unstructured Data Upload Gateway")
st.markdown(
    f"🏭 **Active Industry Configuration:** Mapped to Code `{active_sic['sic_code']}` ({active_sic['sector']}) | Default Tax Rule: `{active_sic.get('default_vat_type', 'Standard 20%')}`"
)
st.caption(
    "🔒 Secure Sandbox Workspace // Data processed here is isolated inside volatile browser memory caches."
)
st.markdown("---")

# =========================================================================
# 🚀 RESOLVED PURGE: "Ingestion Playbook" is now "Data Upload Playbook"
# 🚀 RESOLVED PURGE: US "Analyzes" is now UK "Analyses"
# =========================================================================
col_left, col_right = st.columns([7, 5])

with col_left:
    st.markdown("### 💡 Data Upload Playbook & System Capabilities")
    st.markdown(
        "* **Intelligent Scanning:** Drop raw transaction metrics, text-based PDF invoices, or supplier agreements to isolate financial strings instantly.\n"
        "* **Automated Mapping:** Formulates standalone baseline target profiles for Years 1, 2, and 3, matching your active industrial framework parameters behind the scenes.\n"
        "* **Predictive Curve Shaping:** Analyses description text syntax to match trading volumes with corresponding business curves (e.g., `Winter_Peak` or `Summer_Peak`)."
    )

with col_right:
    st.markdown("### 🔒 Data Sovereignty & Sandbox Safety")
    st.info(
        "**Isolated Memory Safeguard:** This page acts strictly as a temporary scratchpad. "
        "No uploaded files or AI interpretations are written to your permanent database project files. "
        "You have total control to review, edit, or delete items before officially pushing them into the workspace.",
        icon="🧠",
    )

st.markdown("---")
st.subheader("✍️ Granular Core Input Matrix Vectors")

# Build curve map dictionary combining standard definitions with custom user profiles
seasonality_profiles = {
    "Flat_Linear": [1 / 12] * 12,
    "Winter_Peak": [
        0.12,
        0.12,
        0.10,
        0.07,
        0.05,
        0.05,
        0.05,
        0.06,
        0.08,
        0.09,
        0.10,
        0.11,
    ],
    "Summer_Peak": [
        0.05,
        0.05,
        0.07,
        0.10,
        0.12,
        0.12,
        0.12,
        0.11,
        0.09,
        0.07,
        0.05,
        0.05,
    ],
}
if "custom_curves" in st.session_state:
    for c_name, c_weights in st.session_state["custom_curves"].items():
        seasonality_profiles[c_name] = c_weights

with st.expander("📈 1. THE SALES DRIVER DESK", expanded=True):
    with st.form("sales_form", clear_on_submit=True):
        n = st.text_input(
            "Sales Line Name / Identifier:",
            placeholder="e.g. Counter Trading Retail Sales",
        )
        y1 = st.number_input(
            "Year 1 Expected Net Base Target (£):", min_value=0.0, step=1000.0
        )
        y2 = st.number_input(
            "Year 2 Expected Net Base Target (£):", min_value=0.0, step=1000.0
        )
        y3 = st.number_input(
            "Year 3 Expected Net Base Target (£):", min_value=0.0, step=1000.0
        )
        curve = st.selectbox(
            "Timeline Seasonal Shape Curve:", list(seasonality_profiles.keys())
        )
        delay = st.selectbox(
            "Commercial Credit Terms Delay:",
            [0, 30, 60],
            format_func=lambda x: (
                f"Paid Instantly" if x == 0 else f"{x} Days Credit Delay"
            ),
        )
        flex = st.slider(
            "Annual Pricing Indexation Escalator Shift (Sales Flex %):", -10, 30, 0
        )
        v_rate = st.selectbox(
            "UK VAT Classification Rate:",
            [
                "Standard 20%",
                "Reduced 5%",
                "Reduced 5% (Commercial Energy Eligible)",
                "Exempt / Zero 0%",
            ],
        )
        if st.form_submit_button("➕ Append Trading Sales Revenue Vector"):
            if n:
                st.session_state["active_data"]["sales"].append(
                    {
                        "name": n,
                        "y1_baseline": y1,
                        "y2_baseline": y2,
                        "y3_baseline": y3,
                        "seasonality": curve,
                        "payment_delay": delay,
                        "flex_pct": flex,
                        "vat_rate_type": v_rate,
                        "overrides": {},
                    }
                )
                st.rerun()

with st.expander("🚜 5. THE FINANCED ASSET WIZARD"):
    with st.form("financed_form", clear_on_submit=True):
        n = st.text_input(
            "Financed Asset Identifier Name:",
            placeholder="e.g. Commercial Fleet Vehicle",
        )
        amt = st.number_input(
            "Asset Procurement Invoice Value (£):", min_value=0.0, step=5000.0
        )
        m_start = st.number_input(
            "Acquisition Target Deployment Month:", min_value=1, max_value=60, value=1
        )
        dp = st.slider("Upfront Deposit Commitment Percentage (%):", 0, 100, 10)
        term = st.number_input(
            "Amortisation Term Horizon (Months):", min_value=3, max_value=60, value=36
        )
        rate = st.number_input(
            "Financing Matrix Interest Rate (APR %):",
            min_value=0.0,
            value=5.0,
            step=0.5,
        )
        asset_depr_rate = (
            st.number_input(
                "Asset-Specific Annual Depreciation Rate (% Straight-Line):",
                min_value=0.0,
                max_value=100.0,
                value=15.0,
                step=1.0,
            )
            / 100.0
        )

        if st.form_submit_button("🚀 Trigger Auto-Balancing Financed Asset Vector"):
            if n:
                st.session_state["active_data"]["financed_assets"].append(
                    {
                        "name": n,
                        "amount": amt,
                        "month": m_start,
                        "deposit_pct": dp,
                        "term_months": term,
                        "interest_rate": rate,
                        "depreciation_rate": asset_depr_rate,
                    }
                )
                st.rerun()

# Sidebar consistent layout loop
st.sidebar.markdown("### 🧭 Navigation Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")
