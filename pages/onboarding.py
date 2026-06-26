# pages/onboarding.py
# STRATA SUITE // GLOBAL INDUSTRY PARAMETERS MASTER CONFIG v7.0.0-PRODUCTION

import streamlit as st

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

# Initialize custom curve memory structures if missing
if "custom_curves" not in st.session_state:
    st.session_state["custom_curves"] = {}

# =========================================================================
# SYSTEM CONFIGURATION DESK 1: INDUSTRIAL SIC PROFILE COMPASS
# =========================================================================
st.subheader("🏭 Section 1: Standard Industrial Classification (SIC) Alignment")
st.markdown(
    "Select your primary operational framework vector to automatically set baseline employer overhead conditions."
)

sic_options = {
    "71121": {
        "sector": "Professional R&D Services (Default)",
        "vat": "Standard 20%",
        "nic": 0.138,
    },
    "26110": {
        "sector": "Electronic Component Manufacturing",
        "vat": "Standard 20%",
        "nic": 0.138,
    },
    "35110": {
        "sector": "Electricity Generation (Renewables / AVAWT Hub)",
        "vat": "Reduced 5% (Commercial Energy Eligible)",
        "nic": 0.138,
    },
    "41202": {
        "sector": "Residential Housing Development Construction",
        "vat": "Standard 20%",
        "nic": 0.138,
    },
}

current_sic = st.session_state.get("sic_profile", {"sic_code": "71121"})["sic_code"]
selected_sic_code = st.selectbox(
    "Select Active Macro Industrial Class Code Vector:",
    list(sic_options.keys()),
    index=list(sic_options.keys()).index(current_sic),
)

mapped_meta = sic_options[selected_sic_code]
st.markdown(
    f"**Mapped Sector:** `{mapped_meta['sector']}` | **Default Tax Status:** `{mapped_meta['vat']}` | **Baseline ER NIC Rate:** `{mapped_meta['nic']*100}%`"
)

if st.button("💾 Apply & Update Industrial Profile Presets", use_container_width=True):
    st.session_state["sic_profile"] = {
        "sic_code": selected_sic_code,
        "sector": mapped_meta["sector"],
        "default_vat_type": mapped_meta["vat"],
        "base_er_nic_rate": mapped_meta["nic"],
    }
    st.toast(
        "Industrial Profile Presets successfully synchronized across global state memory arrays!"
    )

st.markdown("---")

# =========================================================================
# SYSTEM CONFIGURATION DESK 2: CUSTOM TIMELINE CURVES ARCHITECT
# =========================================================================
st.subheader("📊 Section 2: Custom Parameter Seasonal Shapes Distribution")
st.markdown(
    "Construct custom 12-month proportional weight distributions to handle unique operational trends cleanly."
)

with st.form("custom_curve_creator", clear_on_submit=True):
    curve_name = (
        st.text_input(
            "Unique Curve Identifier Name:", placeholder="e.g. Phase_1_Build_Spike"
        )
        .strip()
        .replace(" ", "_")
    )
    st.markdown("##### Assign Relative Weightings for Each Operating Month Interval:")

    col1, col2, col3, col4 = st.columns(4)
    m1 = col1.number_input("Month 01 Weight:", min_value=0.0, value=1.0, step=0.1)
    m2 = col2.number_input("Month 02 Weight:", min_value=0.0, value=1.0, step=0.1)
    m3 = col3.number_input("Month 03 Weight:", min_value=0.0, value=1.0, step=0.1)
    m4 = col4.number_input("Month 04 Weight:", min_value=0.0, value=1.0, step=0.1)

    m5 = col1.number_input("Month 05 Weight:", min_value=0.0, value=1.0, step=0.1)
    m6 = col2.number_input("Month 06 Weight:", min_value=0.0, value=1.0, step=0.1)
    m7 = col3.number_input("Month 07 Weight:", min_value=0.0, value=1.0, step=0.1)
    m8 = col4.number_input("Month 08 Weight:", min_value=0.0, value=1.0, step=0.1)

    m9 = col1.number_input("Month 09 Weight:", min_value=0.0, value=1.0, step=0.1)
    m10 = col2.number_input("Month 10 Weight:", min_value=0.0, value=1.0, step=0.1)
    m11 = col3.number_input("Month 11 Weight:", min_value=0.0, value=1.0, step=0.1)
    m12 = col4.number_input("Month 12 Weight:", min_value=0.0, value=1.0, step=0.1)

    if st.form_submit_button("➕ Register Custom Seasonality Matrix Curve Profile"):
        if curve_name:
            raw_weights = [m1, m2, m3, m4, m5, m6, m7, m8, m9, m10, m11, m12]
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

if st.session_state["custom_curves"]:
    st.markdown("##### Active Custom Curves Registered in Memory Context:")
    for c_key, c_val in list(st.session_state["custom_curves"].items()):
        cc1, cc2 = st.columns([10, 2])
        cc1.caption(
            f"📈 **{c_key}** // Mapped Distribution Array: `{[round(v, 3) for v in c_val]}`"
        )
        if cc2.button("🗑️ Remove", key=f"rem_cc_{c_key}"):
            st.session_state["custom_curves"].pop(c_key)
            st.rerun()

st.markdown("---")

# =========================================================================
# 🧭 FIXED SIDEBAR COMPASS OPTIONS
# =========================================================================
st.sidebar.markdown("### Compass Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")
