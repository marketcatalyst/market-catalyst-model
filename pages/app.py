# pages/app.py
# STRATA SUITE // DATA ENTRY & UPLOAD MASTER CANVAS v6.9.4-PRODUCTION

import streamlit as st
import pandas as pd

# Enforce strict native sidebar removal to eliminate duplicates
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

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
st.subheader("✍️ Granular Core Input Account Categories")

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

# =========================================================================
# ALL 8 ACCOUNT CATEGORY ENTRY DESKS (FULLY RESTORED)
# =========================================================================

with st.expander("📈 1. THE SALES DRIVER DESK", expanded=False):
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
            "Timeline Seasonal Shape Curve:",
            list(seasonality_profiles.keys()),
            key="sb_s",
        )
        delay = st.selectbox(
            "Commercial Credit Terms Delay:",
            [0, 30, 60],
            format_func=lambda x: (
                f"Paid Instantly" if x == 0 else f"{x} Days Credit Delay"
            ),
        )
        flex = st.slider(
            "Annual Pricing Indexation Escalator Shift (Sales Flex %):",
            -10,
            30,
            0,
            key="sl_s",
        )
        v_rate = st.selectbox(
            "UK VAT Classification Rate:",
            [
                "Standard 20%",
                "Reduced 5%",
                "Reduced 5% (Commercial Energy Eligible)",
                "Exempt / Zero 0%",
            ],
            key="vt_s",
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

with st.expander("💼 2. THE MILESTONE CONTRACT DESK", expanded=False):
    with st.form("milestone_form", clear_on_submit=True):
        n = st.text_input(
            "Contract Entity Account Name:",
            placeholder="e.g. Enterprise Implementation Alpha",
        )
        tcv = st.number_input(
            "Total Contract Value (TCV £):", min_value=0.0, step=5000.0
        )
        dur = st.number_input(
            "Operational Delivery Duration (Months):",
            min_value=1,
            max_value=60,
            value=6,
        )
        start = st.number_input(
            "Execution Start Month Index (M01-M60):", min_value=1, max_value=60, value=1
        )
        dp = st.slider("Upfront Retainer Inflow (%):", 0, 100, 20)
        v_rate = st.selectbox(
            "UK VAT Classification Rate (Contracts):",
            ["Standard 20%", "Reduced 5%", "Exempt / Zero 0%"],
            key="ms_vat",
        )
        if st.form_submit_button("➕ Secure Milestone Contract Parameter Block"):
            if n:
                st.session_state["active_data"]["milestones"].append(
                    {
                        "name": n,
                        "tcv": tcv,
                        "duration": dur,
                        "start_month": start,
                        "deposit_pct": dp,
                        "vat_rate_type": v_rate,
                    }
                )
                st.rerun()

with st.expander("📦 3. THE PRODUCTION COGS DESK", expanded=False):
    with st.form("cogs_form", clear_on_submit=True):
        n = st.text_input(
            "Direct Production Cost Title:", placeholder="e.g. Raw Material Allocation"
        )
        y1 = st.number_input(
            "Year 1 Expected Net Base Target (£):", min_value=0.0, step=500.0
        )
        y2 = st.number_input(
            "Year 2 Expected Net Base Target (£):", min_value=0.0, step=500.0
        )
        y3 = st.number_input(
            "Year 3 Expected Net Base Target (£):", min_value=0.0, step=500.0
        )
        curve = st.selectbox(
            "Cost Seasonal Volatility Shape Profile:",
            list(seasonality_profiles.keys()),
            key="c_curve",
        )
        flex = st.slider(
            "Annual Macro Supply Chain Inflation Indexation Shift (COGS Flex %):",
            -10,
            30,
            0,
            key="sl_c",
        )
        v_rate = st.selectbox(
            "Supply Chain VAT Rate Profile:",
            ["Standard 20%", "Reduced 5%", "Exempt / Zero 0%"],
            key="c_vat",
        )
        if st.form_submit_button("➕ Append Direct Production COGS Vector"):
            if n:
                st.session_state["active_data"]["cogs"].append(
                    {
                        "name": n,
                        "y1_baseline": y1,
                        "y2_baseline": y2,
                        "y3_baseline": y3,
                        "seasonality": curve,
                        "flex_pct": flex,
                        "vat_rate_type": v_rate,
                        "overrides": {},
                    }
                )
                st.rerun()

with st.expander("💸 4. THE GENERAL OVERHEAD CARD", expanded=False):
    with st.form("matrix_opex_creator", clear_on_submit=True):
        n = st.text_input(
            "Operational Overhead Category Title:",
            placeholder="e.g. Commercial Utility Electricity",
        )
        v_rate = st.selectbox(
            "UK VAT Category Profile:",
            [
                "Standard 20%",
                "Reduced 5%",
                "Reduced 5% (Commercial Energy Eligible)",
                "Exempt / Zero 0%",
            ],
            key="op_mat_vat",
        )
        if st.form_submit_button("➕ Initialise Empty 12 × 5 Corporate Matrix Row"):
            if n:
                blank_matrix = {
                    "name": n,
                    "vat_rate_type": v_rate,
                    "flex_rates": {"Y2": 0.0, "Y3": 0.0, "Y4": 0.0, "Y5": 0.0},
                    "matrix_data": {
                        "Y1": [0.0] * 12,
                        "Y2": [0.0] * 12,
                        "Y3": [0.0] * 12,
                        "Y4": [0.0] * 12,
                        "Y5": [0.0] * 12,
                        "overwrites": {},
                    },
                }
                st.session_state["active_data"]["opex"].append(blank_matrix)
                st.rerun()

    if st.session_state["active_data"].get("opex"):
        for idx, op in enumerate(st.session_state["active_data"]["opex"]):
            st.markdown(
                f"#### 📦 Account Row: **{op['name']}** ({op['vat_rate_type']})"
            )
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            y2_f = f_col1.number_input(
                f"Y2 Flex % ({op['name']})",
                value=float(op.get("flex_rates", {}).get("Y2", 0.0)),
                step=0.5,
                key=f"f2_{idx}",
            )
            y3_f = f_col2.number_input(
                f"Y3 Flex % ({op['name']})",
                value=float(op.get("flex_rates", {}).get("Y3", 0.0)),
                step=0.5,
                key=f"f3_{idx}",
            )
            y4_f = f_col3.number_input(
                f"Y4 Flex % ({op['name']})",
                value=float(op.get("flex_rates", {}).get("Y4", 0.0)),
                step=0.5,
                key=f"f4_{idx}",
            )
            y5_f = f_col4.number_input(
                f"Y5 Flex % ({op['name']})",
                value=float(op.get("flex_rates", {}).get("Y5", 0.0)),
                step=0.5,
                key=f"f5_{idx}",
            )

            if (
                y2_f != op["flex_rates"]["Y2"]
                or y3_f != op["flex_rates"]["Y3"]
                or y4_f != op["flex_rates"]["Y4"]
                or y5_f != op["flex_rates"]["Y5"]
            ):
                op["flex_rates"] = {"Y2": y2_f, "Y3": y3_f, "Y4": y4_f, "Y5": y5_f}
                m_data = op["matrix_data"]
                for r in range(12):
                    if f"Y2_M{r}" not in m_data["overwrites"]:
                        m_data["Y2"][r] = m_data["Y1"][r] * (1.0 + (y2_f / 100.0))
                    if f"Y3_M{r}" not in m_data["overwrites"]:
                        m_data["Y3"][r] = m_data["Y2"][r] * (1.0 + (y3_f / 100.0))
                    if f"Y4_M{r}" not in m_data["overwrites"]:
                        m_data["Y4"][r] = m_data["Y3"][r] * (1.0 + (y4_f / 100.0))
                    if f"Y5_M{r}" not in m_data["overwrites"]:
                        m_data["Y5"][r] = m_data["Y4"][r] * (1.0 + (y5_f / 100.0))
                st.rerun()

            months_index = [f"Month {str(m).zfill(2)}" for m in range(1, 13)]
            m_data = op["matrix_data"]
            df_matrix = pd.DataFrame(
                {
                    "Year 1 (Base)": m_data["Y1"],
                    "Year 2": m_data["Y2"],
                    "Year 3": m_data["Y3"],
                    "Year 4": m_data["Y4"],
                    "Year 5": m_data["Y5"],
                },
                index=months_index,
            )
            edited_matrix_df = st.data_editor(
                df_matrix,
                column_config={
                    col: st.column_config.NumberColumn(
                        col, format="£%,.2f", width="medium"
                    )
                    for col in df_matrix.columns
                },
                use_container_width=True,
                key=f"grid_ed_{idx}",
            )

            has_changed = False
            for r_idx in range(12):
                new_y1 = float(edited_matrix_df.iloc[r_idx, 0])
                new_y2 = float(edited_matrix_df.iloc[r_idx, 1])
                if new_y1 != m_data["Y1"][r_idx]:
                    m_data["Y1"][r_idx] = new_y1
                    has_changed = True
                    if f"Y2_M{r_idx}" not in m_data["overwrites"]:
                        m_data["Y2"][r_idx] = new_y1 * (1.0 + (y2_f / 100.0))
                if new_y2 != df_matrix.iloc[r_idx, 1]:
                    m_data["overwrites"][f"Y2_M{r_idx}"] = new_y2
                    m_data["Y2"][r_idx] = new_y2
                    has_changed = True

            if has_changed:
                op["matrix_data"] = m_data
                st.rerun()

with st.expander("🚜 5. THE FINANCED ASSET WIZARD", expanded=False):
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

with st.expander("🏢 6. THE OUTRIGHT CAPEX CARD", expanded=False):
    with st.form("outright_form", clear_on_submit=True):
        n = st.text_input(
            "Asset Specification Description:",
            placeholder="e.g. HQ Office Fit-out Furnishings",
        )
        amt = st.number_input(
            "Procurement Invoice Amount Value (£):", min_value=0.0, step=1000.0
        )
        m_buy = st.number_input(
            "Cash Drawdown Target Execution Month Index:",
            min_value=1,
            max_value=60,
            value=1,
        )
        asset_depr_rate = (
            st.number_input(
                "Asset-Specific Annual Depreciation Rate (% Straight-Line):",
                min_value=0.0,
                max_value=100.0,
                value=20.0,
                step=1.0,
            )
            / 100.0
        )

        if st.form_submit_button("➕ Append Direct CapEx Vector"):
            if n:
                st.session_state["active_data"]["outright_capex"].append(
                    {
                        "name": n,
                        "amount": amt,
                        "month": m_buy,
                        "depreciation_rate": asset_depr_rate,
                    }
                )
                st.rerun()

with st.expander("👥 7. THE PERSONNEL HORIZON DESK", expanded=False):
    with st.form("payroll_form", clear_on_submit=True):
        n = st.text_input("Operational Resource Designation:")
        hc = st.number_input("Workforce Headcount:", min_value=1, value=1)
        wage = st.number_input(
            "Individual Monthly Gross Salary (£):", min_value=0.0, step=100.0
        )
        m_in = st.slider("Onboarding Activation Start Month:", 1, 60, 1)
        flex = st.slider("Payroll Flex Indexation %:", -10, 30, 0, key="sl_p")
        if st.form_submit_button("➕ Launch Workforce Alignment Vector"):
            if n:
                st.session_state["active_data"]["payroll"].append(
                    {
                        "name": n,
                        "headcount": hc,
                        "monthly_wage": wage,
                        "start_month": m_in,
                        "end_month": 60,
                        "flex_pct": flex,
                    }
                )
                st.rerun()

with st.expander("💰 8. THE FUNDING & EQUITY CARD", expanded=False):
    with st.form("equity_form", clear_on_submit=True):
        n = st.text_input("Funding Tranche Origin Narrative Description:")
        amt = st.number_input(
            "Liquid Funding Quantum Inflow Amount (£):", min_value=0.0, step=10000.0
        )
        m_land = st.number_input(
            "Cash Clearing Target Allocation Month Index:",
            min_value=0,
            max_value=60,
            value=0,
        )
        if st.form_submit_button("➕ Authorise Capital Placement Infusion"):
            if n:
                st.session_state["active_data"]["equity_funding"].append(
                    {"name": n, "amount": amt, "month": m_land}
                )
                st.rerun()

# Unified sidebar navigation configuration
st.sidebar.markdown("### 🧭 Navigation Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")
