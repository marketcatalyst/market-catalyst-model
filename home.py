# home.py
# STRATA SUITE ENTERPRISE // SAAS PORTAL ENTRY GATEWAY v4.0.0

import streamlit as st
import pandas as pd
from pathlib import Path

# Enforce uniform platform layout tracking parameters
st.set_page_colls = True  # Streamlit baseline configuration hook placeholder

# 1. Initialize global system state structures across page contexts
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "onboarding_complete" not in st.session_state:
    st.session_state["onboarding_complete"] = False

if "active_project_name" not in st.session_state:
    st.session_state["active_project_name"] = "Unsaved_Draft_Scenario"

if "active_data" not in st.session_state:
    st.session_state["active_data"] = {
        "sales": [],
        "opex": [],
        "payroll": [],
        "capital": [],
        "sic_meta": None,
    }


def load_uk_sic_benchmarks():
    """Reads the static CSV asset registry to provide real-world industry baseline anchors."""
    csv_path = Path("static_data/sic_benchmarks.csv")
    if not csv_path.exists():
        return {
            "00000": {
                "name": "Generic SaaS Default Baseline",
                "gross_margin": 0.50,
                "staff_ratio": 0.30,
                "net_margin": 0.07,
            }
        }
    try:
        df = pd.read_csv(csv_path)
        benchmarks = {}
        for _, row in df.iterrows():
            code_str = str(row["sic_code"]).strip()
            benchmarks[code_str] = {
                "name": str(row["industry_description"]).strip(),
                "gross_margin": float(row["target_gross_margin"]),
                "staff_ratio": float(row["target_staff_to_rev"]),
                "net_margin": float(row["avg_net_margin"]),
            }
        return benchmarks
    except Exception:
        return {
            "00000": {
                "name": "Generic SaaS Default Baseline",
                "gross_margin": 0.50,
                "staff_ratio": 0.30,
                "net_margin": 0.07,
            }
        }


# =========================================================================
# 🔐 PASSCODE SECURITY INTERCEPT FILTER
# =========================================================================
if not st.session_state["authenticated"]:
    st.title("🛡️ STRATA SUITE // Secure Access Gateway")
    st.caption("Forecasting Digital Twin Platform SaaS Isolation Layer")
    st.markdown("---")

    st.markdown(
        "##### Authenticate with your secure environmental passphrase key to unlock project workspaces:"
    )

    with st.form("auth_gate_form"):
        entered_passphrase = st.text_input(
            "Environmental Passphrase Key Target:", type="password"
        )
        submit_auth = st.form_submit_button("🔑 Unlock System Desks")

        if submit_auth:
            if entered_passphrase.strip() == "strata-catalyst-2026":
                st.session_state["authenticated"] = True
                st.toast("🔑 Authentication Verified. System un-isolated.")
                st.rerun()
            else:
                st.error(
                    "❌ **Access Denied:** Invalid environmental passphrase credentials."
                )
    st.stop()


# =========================================================================
# 🧙‍♂️ INTERSTITIAL ONBOARDING CONFIGURATION WIZARD
# =========================================================================
if not st.session_state["onboarding_complete"] or not st.session_state[
    "active_data"
].get("sic_meta"):
    st.title("🧙‍♂️ STRATA // Canvas Configuration Wizard")
    st.caption("Onboarding Blueprint Registry & Target Guardrail Initialization")
    st.markdown("---")

    st.markdown(
        "##### Welcome back. To tailor your predictive dashboard boundaries, prime your target market classification sector:"
    )

    sic_library = load_uk_sic_benchmarks()
    industry_options = [
        f"{code} - {meta['name']}" for code, meta in sic_library.items()
    ]
    selected_wizard_sector = st.selectbox(
        "Target UK Industry Sector (SIC Library Registry):",
        options=["-- Click to Expand Official UK Sector Registries --"]
        + industry_options,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("ℹ️ What parameters does this configure?", expanded=True):
        st.info(
            "Selecting a sector calibrates the baseline financial performance targets. Your simulation outputs will be "
            "actively cross-referenced against standard UK margins and human capital ratios, providing a defensive validation layer."
        )

    if st.button(
        "🚀 Prime Operational Forecast Canvas", type="primary", use_container_width=True
    ):
        if (
            selected_wizard_sector
            != "-- Click to Expand Official UK Sector Registries --"
        ):
            chosen_code = selected_wizard_sector.split(" - ")[0]
            st.session_state["active_data"]["sic_meta"] = sic_library[chosen_code]
            st.session_state["onboarding_complete"] = True
            st.toast(f"🎯 Primed Sector Target: {sic_library[chosen_code]['name']}")
            st.rerun()
        else:
            st.warning(
                "⚠️ Select a reference sector baseline to establish your operational parameters canvas."
            )
    st.stop()


# =========================================================================
# 🏛️ SAAS DASHBOARD CENTRAL ROUTER LINK HUB
# =========================================================================
st.title("🏛️ STRATA // Corporate Command Center")
st.caption(
    f"Active Tenant Context Model Session: `{st.session_state['active_project_name']}`"
)
st.markdown("---")

st.info(
    "📊 **System Status:** Session authenticated and tracking thresholds successfully mapped to industry parameters."
)

col_n1, col_n2 = st.columns(2)
with col_n1:
    st.markdown("### ✍️ Operational Planning Canvas")
    st.write(
        "Ingest raw documents via document scanning, append structural ledger profiles manually, or load existing database project schemas."
    )
    # Native relative linking routing layout
    st.page_link(
        "app.py",
        label="🚀 Launch Parameter Workspaces Desk",
        use_container_width=True,
    )

with col_n2:
    st.markdown("### 🚪 Workspace Session Control")
    st.write(
        "Disconnect active ledger matrix memory instances, lock storage configurations, or exit active session windows securely."
    )
    if st.button("🚪 Terminate Session & Log Out", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["onboarding_complete"] = False
        st.session_state["active_data"] = {
            "sales": [],
            "opex": [],
            "payroll": [],
            "capital": [],
            "sic_meta": None,
        }
        st.rerun()
