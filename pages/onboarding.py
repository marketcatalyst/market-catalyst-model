# pages/onboarding.py
# STRATA SUITE // GLOBAL INDUSTRY PARAMETERS MASTER CONFIG v7.3.6-PRODUCTION

import streamlit as st
import pandas as pd
import os

# Enforce strict native sidebar removal to eliminate duplicates across versions
st.markdown(
    """
    <style>
        div[data-testid="stSidebarNav"], 
        section[data-testid="stSidebarNav"], 
        ul[data-testid="stSidebarNav"], 
        .stSidebarNav {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- SECURITY REDIRECTION INTERCEPT ---
if not st.session_state.get("authenticated"):
    st.title("🏛️ STRATA // Security Intercept")
    st.warning(
        "🔒 This workspace session is currently unauthenticated or has timed out."
    )
    st.markdown(
        "To protect your data matrices, direct access to sub-pages is restricted until access tokens are validated."
    )

    if st.button("🔐 Return to Home Portal & Sign In", use_container_width=True):
        st.switch_page("home.py")
    st.stop()

st.title("🕸️ Global Industry Parameters & Operational Presets")
st.info(
    f"💡 **Active Working Blueprint Instance Context:** `{st.session_state.get('active_project_name', 'Unsaved_Draft_Scenario')}`"
)
st.markdown("---")

# =========================================================================
# 📊 DYNAMIC UK SIC BENCHMARK DATA INGESTION ENGINE
# =========================================================================
st.subheader("🏭 Statutory UK SIC Benchmark Configuration")
st.caption(
    "To expand your corporate selection options, simply append new lines directly to the file static_data/sic_benchmarks.csv."
)

csv_path = "static_data/sic_benchmarks.csv"

if os.path.exists(csv_path):
    try:
        # Read the comprehensive database entries natively
        df_benchmarks = pd.read_csv(csv_path)

        # Clean data types to handle lookup strings safely
        df_benchmarks["sic_code"] = df_benchmarks["sic_code"].astype(str).str.strip()

        # Format a highly professional selection mapping string
        df_benchmarks["display_label"] = (
            df_benchmarks["sic_code"] + " — " + df_benchmarks["industry_description"]
        )

        # Pull choices for dropdown options selection
        sic_options = df_benchmarks["display_label"].tolist()

        # Retain previous memory profile pointers if available
        current_sic = st.session_state.get("sic_profile", {}).get("sic_code", "71121")
        default_index = 0

        matched_row = df_benchmarks[df_benchmarks["sic_code"] == current_sic]
        if not matched_row.empty:
            matched_label = matched_row["display_label"].values[0]
            if matched_label in sic_options:
                default_index = sic_options.index(matched_label)

        selected_label = st.selectbox(
            "Select Target Corporate Classification Rule Base (Dynamic List):",
            options=sic_options,
            index=default_index,
        )

        # Isolate selected record row properties dynamically
        selected_row = df_benchmarks[
            df_benchmarks["display_label"] == selected_label
        ].iloc[0]

        # Map parameters straight into your global volatile memory state variables
        st.session_state["sic_profile"] = {
            "sic_code": selected_row["sic_code"],
            "sector": selected_row["industry_description"],
            "target_gross_margin": float(selected_row["target_gross_margin"]),
            "target_staff_to_rev": float(selected_row["target_staff_to_rev"]),
            "avg_net_margin": float(selected_row["avg_net_margin"]),
            "default_vat_type": "Standard 20%",
            "base_er_nic_rate": 0.138,
        }

        # Display operational metrics feedback dashboards
        st.success(
            f"✔️ Active Framework Parameters locked to Code `{st.session_state['sic_profile']['sic_code']}`"
        )

        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric(
            "Target Gross Margin",
            f"{int(st.session_state['sic_profile']['target_gross_margin'] * 100)}%",
        )
        m_col2.metric(
            "Target Staff-to-Revenue Ratio",
            f"{int(st.session_state['sic_profile']['target_staff_to_rev'] * 100)}%",
        )
        m_col3.metric(
            "Industry Average Net Margin",
            f"{int(st.session_state['sic_profile']['avg_net_margin'] * 100)}%",
        )

    except Exception as err:
        st.error(f"Failed to dynamically map benchmarks lookup table: {str(err)}")
        st.info("Falling back to standard architectural system presets.")
else:
    st.warning(
        "⚠️ Reference file 'static_data/sic_benchmarks.csv' not found. Using baseline memory defaults."
    )

st.markdown("---")

# =========================================================================
# 📈 ADVANCED CUSTOM SEASONALITY DISTRIBUTION SCHEMAS
# =========================================================================
st.subheader("📈 Custom Timeline Operational Seasonality Curves")
st.markdown(
    "Construct multi-dimensional seasonal distribution models here to apply varying monthly business volume scaling trends throughout your calculations."
)

with st.form("custom_curve_form", clear_on_submit=True):
    curve_name = st.text_input(
        "Seasonal Profile Identifier Name:", placeholder="e.g. Q3_High_Velocity_Peak"
    )

    st.markdown(
        "##### Assign Relative Month Weights (Normalized dynamically by system)"
    )
    w_cols = st.columns(12)
    raw_weights = []
    for idx in range(12):
        w_val = w_cols[idx].number_input(
            f"M{str(idx+1).zfill(2)}",
            min_value=0.0,
            max_value=10.0,
            value=1.0,
            step=0.1,
        )
        raw_weights.append(w_val)

    if st.form_submit_button("💾 Compile and Register Seasonality Vector Profile"):
        if curve_name:
            total_sum = sum(raw_weights)
            if total_sum > 0:
                normalized_weights = [w / total_sum for w in raw_weights]
                st.session_state["custom_curves"][curve_name] = normalized_weights
                st.toast(
                    f"Successfully compiled and normalized curve matrix: '{curve_name}'"
                )
                st.rerun()
            else:
                st.error("Cumulative mathematical weight sum must be greater than 0.")

if "custom_curves" in st.session_state and st.session_state["custom_curves"]:
    st.markdown("##### Active Custom Curves Registered in Memory Context:")
    for c_key, c_val in list(st.session_state["custom_curves"].items()):
        cc1, cc2 = st.columns([10, 2])
        cc1.caption(
            f"📈 **{c_key}** // Mapped Distribution Array: `{[round(v, 3) for v in c_val]}`"
        )
        if cc2.button("🗑️ Remove", key=f"rem_cc_{c_key}\r"):
            st.session_state["custom_curves"].pop(c_key)
            st.rerun()

st.markdown("---")

# =========================================================================
# 🧭 FIXED SIDEBAR COMPASS OPTIONS
# =========================================================================
st.sidebar.markdown("### Compass Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link(
    "pages/1_Data_Ingestion_Gateway.py", label="📥 Data Ingestion Gateway"
)
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry Panel")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")
