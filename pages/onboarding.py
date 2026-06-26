# pages/onboarding.py
# STRATA SUITE ECOSYSTEM MAPPING ROOM // v6.8.1-PRODUCTION

import streamlit as st
import pandas as pd

if "sic_profile" not in st.session_state:
    st.session_state["sic_profile"] = {
        "sic_code": "71121",
        "sector": "Professional R&D Services (Fallback)",
        "default_vat_type": "Standard 20%",
        "energy_vat_eligible": False,
        "base_er_nic_rate": 0.138,
        "macro_depreciation_baseline": 0.10,
    }

st.title("🕸️ STRATA // Central Ecosystem Mapping Room")
st.markdown("### Ornate Onboarding & Variable Coupling Canvas")
st.page_link("pages/app.py", label="✍️ Proceed to Granular Operational Sandboxes")
st.page_link("pages/reports.py", label="📊 Jump Straight to Report Generation Vault")
st.markdown("---")

t1, t2, t3 = st.tabs(
    [
        "🏭 Macro Industry Scope",
        "📊 Custom Volatility Curves",
        "🔗 Variable Coupling Router",
    ]
)

with t1:
    st.subheader("Global Industry Parameter Boundaries")
    st.markdown(
        "Configure the systemic constraints mapped directly to your targeted economic sector."
    )

    with st.form("sic_scope_form"):
        sic = st.text_input(
            "Target UK Standard Industrial Classification (SIC) Code:",
            value=st.session_state["sic_profile"]["sic_code"],
        )
        sector = st.text_input(
            "Operational Sector Designation Description:",
            value=st.session_state["sic_profile"]["sector"],
        )
        depr = (
            st.number_input(
                "Macro Fixed Asset Linear Depreciation Constraint (% / Year):",
                value=float(
                    st.session_state["sic_profile"]["macro_depreciation_baseline"] * 100
                ),
                step=1.0,
            )
            / 100.0
        )
        nic = (
            st.number_input(
                "Baseline Employer Tax Burden Weight (ER NIC %):",
                value=float(st.session_state["sic_profile"]["base_er_nic_rate"] * 100),
                step=0.1,
            )
            / 100.0
        )
        vat = st.selectbox(
            "Default Environmental Trade VAT Profile:",
            ["Standard 20%", "Reduced 5%", "Exempt / Zero 0%"],
            index=(
                0
                if st.session_state["sic_profile"]["default_vat_type"] == "Standard 20%"
                else 1
            ),
        )

        if st.form_submit_button("🔒 Lock Global Macro Constraints"):
            st.session_state["sic_profile"] = {
                "sic_code": sic,
                "sector": sector,
                "default_vat_type": vat,
                "energy_vat_eligible": False,
                "base_er_nic_rate": nic,
                "macro_depreciation_baseline": depr,
            }
            st.toast("Macro Boundaries Aligned!")
            st.rerun()

with t2:
    st.subheader("Seasonal Profile Registries")
    st.markdown(
        "Review or modify the systemic allocations utilized to sculpt baseline targets across linear monthly streams."
    )

    # Expose the math weights behind the scenes contextually
    profiles_df = pd.DataFrame(
        {
            "Flat_Linear Month Weights": [f"{round((1/12)*100, 2)}%"] * 12,
            "Winter_Peak Month Weights": [
                "12.0%",
                "12.0%",
                "10.0%",
                "7.0%",
                "5.0%",
                "5.0%",
                "5.0%",
                "6.0%",
                "8.0%",
                "9.0%",
                "10.0%",
                "11.0%",
            ],
            "Summer_Peak Month Weights": [
                "5.0%",
                "5.0%",
                "7.0%",
                "10.0%",
                "12.0%",
                "12.0%",
                "12.0%",
                "11.0%",
                "9.0%",
                "7.0%",
                "5.0%",
                "5.0%",
            ],
        },
        index=[f"Month {str(i).zfill(2)}" for i in range(1, 13)],
    )
    st.table(profiles_df)

with t3:
    st.subheader("WinForecast Variable Coupling Configuration")
    st.markdown(
        "Establish direct systemic dependencies between separate parameter descriptors."
    )

    active_data = st.session_state.get("active_data", {})
    sales_lines = [s["name"] for s in active_data.get("sales", [])]
    cogs_lines = [c["name"] for c in active_data.get("cogs", [])]

    if sales_lines and cogs_lines:
        with st.form("coupling_router"):
            chosen_cogs = st.selectbox(
                "Select Target Cost Matrix Descriptor (COGS Line):", cogs_lines
            )
            chosen_sales = st.selectbox(
                "Link directly to Variable Volume Movement Driver (Sales Line):",
                sales_lines,
            )
            coupling_pct = st.slider(
                "Proportional Value Binding Coefficient (Cost as % of Sales Target):",
                0.0,
                100.0,
                35.0,
                step=0.5,
            )

            if st.form_submit_button("🔗 Complete Synaptic Coupling Matrix Route"):
                if "vector_couplings" not in st.session_state:
                    st.session_state["vector_couplings"] = []
                st.session_state["vector_couplings"].append(
                    {
                        "cogs_target": chosen_cogs,
                        "sales_driver": chosen_sales,
                        "coefficient": coupling_pct / 100.0,
                    }
                )
                st.toast("Vectors Coupled Successfully!")
    else:
        st.info(
            "💡 To configure synaptic link routing, please populate at least one active Sales Driver vector line and one Direct Production Cost row item inside your sandbox entry decks."
        )
