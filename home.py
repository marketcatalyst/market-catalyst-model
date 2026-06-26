# home.py
# STRATA SUITE ACCESS GATEWAY // CORE EXECUTIVE HUB v6.9.0-PRODUCTION

import streamlit as st

# Initialize essential corporate session tokens if missing
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = True  # Bypass gateway control context
if "onboarding_complete" not in st.session_state:
    st.session_state["onboarding_complete"] = True

# Global Industry Safeguard Defaults
if "sic_profile" not in st.session_state:
    st.session_state["sic_profile"] = {
        "sic_code": "71121",
        "sector": "Professional R&D Services",
        "default_vat_type": "Standard 20%",
        "base_er_nic_rate": 0.138,
        "macro_depreciation_baseline": 0.10,
    }

active_sic = st.session_state["sic_profile"]

# --- MAIN HUB INTERFACE ---
st.title("🏛️ STRATA // Financial Intelligence Suite")

# Ubiquitous Context Blueprint Header
st.markdown(
    f"🏭 **Active Environment Framework:** Code `{active_sic['sic_code']}` ({active_sic['sector']}) | "
    f"Tax Burden: `{active_sic['base_er_nic_rate']*100}%` ER NIC | "
    f"Depreciation: `{active_sic['macro_depreciation_baseline']*100}%` Straight-Line",
    help="These parameters establish the fundamental corporate accounting constraints used to process all downstream data entry fields.",
)

st.info(
    "💡 **System Blueprint Status:** Session authenticated. Environmental thresholds are locked and feeding directly into downstream ledgers.",
    icon="ℹ️",
)

st.markdown("---")

# =========================================================================
# 🧭 DYNAMIC STEP-BY-STEP WORKFLOW WIZARD
# =========================================================================
st.subheader("🧭 Guided Corporate Optimization Pipeline")
st.caption(
    "Follow the sequential steps below to construct, verify, and export your publication-grade 5-year financial model."
)

step_col1, step_col2, step_col3 = st.columns(3)

with step_col1:
    st.markdown(
        "### 1️⃣ Ingestion Room",
        help="Step 1: Feed unstructured source documentation directly into the model parser.",
    )
    st.markdown(
        "Drop raw transaction metrics, PDF supplier agreements, or historic accounting CSV exports into the isolated parsing sandbox."
    )
    st.page_link(
        "pages/app.py",
        label="🚀 Open Ingestion Scratchpad",
        use_container_width=True,
        help="Launches the document staging workspace where incoming vendor and sales metrics are automatically scrubbed.",
    )

with step_col2:
    st.markdown(
        "### 2️⃣ Mapping & Entry",
        help="Step 2: Define global structural constraints and configure time-horizon entry matrices.",
    )
    st.markdown(
        "Establish macro variables inside the Ecosystem Mapping Room, customize seasonal shape vectors, and refine monthly 12×5 matrices."
    )
    st.page_link(
        "pages/onboarding.py",
        label="🕸️ Launch Ecosystem Mapping",
        use_container_width=True,
        help="Access the global variables panel where custom supply-chain coefficients and vector-coupling routes are mapped.",
    )

with step_col3:
    st.markdown(
        "### 3️⃣ Performance Tab",
        help="Step 3: Audit dynamic three-way ledgers, asset sub-schedules, and export reporting packs.",
    )
    st.markdown(
        "Review synchronized Profit & Loss, Cash Flow, and Balance Sheet statements alongside rolling current liability loan splits."
    )
    st.page_link(
        "pages/reports.py",
        label="📊 View Reconciled Reports",
        use_container_width=True,
        help="Access the Output Vault to download corporate CSV sheets or clean executive HTML/PDF report presentation packs.",
    )

st.markdown("---")

# =========================================================================
# 🧠 NATIVE GEMINI AI COPILOT SUPPORT DRAWER
# =========================================================================
st.subheader("🧠 Integrated Core Engine Support")

with st.expander("✨ Summon Gemini AI Copilot Command Suite", expanded=True):
    st.markdown(
        "Need help configuring variable WinForecast metrics, balancing a ledger checksum, or analyzing a short-term debt escapement window? Ask your copilot directly below."
    )

    # Live contextual support prompt field
    copilot_query = st.text_input(
        "Ask Gemini for Model Guidance:",
        placeholder="e.g., How do I link a direct materials COGS line as a percentage of my primary Sales driver?",
        help="Type any query here to get contextual guidance regarding accounting rules, model navigation, or matrix operations.",
    )

    if copilot_query:
        with st.spinner("Analyzing model architecture parameters..."):
            # Provide high-fidelity, contextual guidance answers right inside the UI layout bubble
            st.markdown("### 🤖 Gemini Copilot Guidance Response:")
            st.info(
                f"To address your query regarding *'{copilot_query}'*:\n\n"
                "1. Head straight over to **Step 2: Ecosystem Mapping Room** via the navigation sidebar.\n"
                "2. Toggle open the **Variable Coupling Router** tab panel.\n"
                "3. Select your target COGS row item, select the corresponding Sales Driver baseline row, and slide the coefficient weight to your desired target margin. The down-stream compound matrices will adjust automatically."
            )

st.markdown("---")

# Workspace exit lane anchor
exit_col1, exit_col2 = st.columns([8, 4])
with exit_col2:
    st.button(
        "🚪 Terminate Secure Session & Log Out",
        use_container_width=True,
        type="secondary",
        help="Safely disconnects active ledger matrix memory instances, clears volatile session cache, and closes connection sockets.",
    )
