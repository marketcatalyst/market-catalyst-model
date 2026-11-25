# pyright: reportMissingImports=false
# pages/app.py
# STRATA SUITE PRODUCTION ENGINE // DATA ENTRY & VECTOR CONFIGURATION DESK v11.14-SSOT-STRICT

import os
import sys
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.scenario_manager import (
    DEFAULT_BLANK_SCENARIO,
    ENTRY_MODE_CURVE,
    ENTRY_MODE_FLAT,
    ENTRY_MODE_OVERRIDE,
    VALID_ENTRY_MODES,
    render_global_scenario_sidebar,
    save_scenario_to_disk,
)

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

if not st.session_state.get("authenticated"):
    st.title("🏛️ STRATA // Security Intercept")
    st.warning(
        "🔒 This workspace session is currently unauthenticated or has timed out."
    )
    if st.button("🔑 Return to Home Portal & Sign In", use_container_width=True):
        st.switch_page("home.py")
    st.stop()

# =========================================================================
# 🧭 SIDEBAR COMPASS & SCENARIO CONTROL DESK
# =========================================================================
st.sidebar.markdown("### Compass Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link(
    "pages/1_Data_Ingestion_Gateway.py", label="📥 Data Ingestion Gateway"
)
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry Panel")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")

render_global_scenario_sidebar()

# =========================================================================
# ✍️ DATA ENTRY & VECTOR CONFIGURATION DESK
# =========================================================================

active_project = st.session_state.get("active_project_name", DEFAULT_BLANK_SCENARIO)

st.title("✍️ Data Entry & Vector Configuration Desk")
st.caption(f"Active Scenario Context: `{active_project}`")
st.page_link("pages/reports.py", label="📊 Proceed to Performance Tab")
st.markdown("---")

if "active_data" not in st.session_state:
    st.session_state["active_data"] = {
        "sales": [],
        "cogs": [],
        "opex": [],
        "payroll": [],
        "financed_assets": [],
        "outright_capex": [],
        "equity_funding": [],
    }

active_data = st.session_state["active_data"]

for key in [
    "sales",
    "cogs",
    "opex",
    "payroll",
    "financed_assets",
    "outright_capex",
    "equity_funding",
]:
    if key not in active_data:
        active_data[key] = []

VAT_OPTIONS = ["Standard 20%", "Reduced 5%", "Zero-Rated 0%"]
CURVE_OPTIONS = ["Flat_Linear", "Winter_Peak", "Summer_Peak"] + sorted(
    [
        k
        for k in st.session_state.get("custom_curves", {}).keys()
        if k not in ["Flat_Linear", "Winter_Peak", "Summer_Peak"]
    ]
)


def resolve_mode_index(mode_val: str) -> int:
    if mode_val == "Annual Baseline + Seasonality Curve":
        mode_val = ENTRY_MODE_CURVE
    return VALID_ENTRY_MODES.index(mode_val) if mode_val in VALID_ENTRY_MODES else 0


def resolve_vat_index(vat_val: str) -> int:
    return VAT_OPTIONS.index(vat_val) if vat_val in VAT_OPTIONS else 0


def resolve_curve_index(curve_val: str) -> int:
    return CURVE_OPTIONS.index(curve_val) if curve_val in CURVE_OPTIONS else 0


tab_sales, tab_cogs, tab_opex, tab_payroll, tab_capex, tab_equity = st.tabs(
    [
        "📈 Sales & Revenue",
        "📦 COGS",
        "🏢 Overheads (OPEX)",
        "👥 Staff Payroll",
        "🚜 Capex & Leases",
        "💷 Equity Funding",
    ]
)

with tab_sales:
    st.subheader("Manage Sales & Turnover Vectors")
    sales_list = active_data["sales"]

    if st.button("➕ Add New Sales Vector"):
        sales_list.append(
            {
                "name": f"New_Sales_Vector_{len(sales_list)+1}",
                "entry_mode": ENTRY_MODE_CURVE,
                "y1_baseline": 0.0,
                "y2_baseline": 0.0,
                "y3_baseline": 0.0,
                "seasonality": "Flat_Linear",
                "vat_rate_type": "Standard 20%",
                "payment_delay": 0,
                "overrides": {},
                "matrix_data": {},
            }
        )
        st.rerun()

    for idx, item in enumerate(sales_list):
        with st.expander(f"Sales Vector: {item.get('name', 'Unnamed')}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                item["name"] = st.text_input(
                    "Vector Name:", value=item.get("name", ""), key=f"s_name_{idx}"
                )
                item["entry_mode"] = st.selectbox(
                    "Projection Methodology / Basis:",
                    options=VALID_ENTRY_MODES,
                    index=resolve_mode_index(item.get("entry_mode", ENTRY_MODE_CURVE)),
                    key=f"s_mode_{idx}",
                )
            with col2:
                item["vat_rate_type"] = st.selectbox(
                    "VAT Profile:",
                    options=VAT_OPTIONS,
                    index=resolve_vat_index(item.get("vat_rate_type", "Standard 20%")),
                    key=f"s_vat_{idx}",
                )
                item["payment_delay"] = st.number_input(
                    "Payment Terms Lag (Days):",
                    min_value=0,
                    step=30,
                    value=int(item.get("payment_delay", 0)),
                    key=f"s_lag_{idx}",
                )

            col3, col4, col5 = st.columns(3)
            with col3:
                item["y1_baseline"] = st.number_input(
                    "Year 1 Baseline (£):",
                    value=float(item.get("y1_baseline", 0.0)),
                    key=f"s_y1_{idx}",
                )
            with col4:
                item["y2_baseline"] = st.number_input(
                    "Year 2 Baseline (£):",
                    value=float(item.get("y2_baseline", 0.0)),
                    key=f"s_y2_{idx}",
                )
            with col5:
                item["y3_baseline"] = st.number_input(
                    "Year 3 Baseline (£):",
                    value=float(item.get("y3_baseline", 0.0)),
                    key=f"s_y3_{idx}",
                )

            if item["entry_mode"] == ENTRY_MODE_CURVE:
                item["seasonality"] = st.selectbox(
                    "Monthly Distribution Curve Profile:",
                    options=CURVE_OPTIONS,
                    index=resolve_curve_index(item.get("seasonality", "Flat_Linear")),
                    key=f"s_season_{idx}",
                )
            elif item["entry_mode"] == ENTRY_MODE_OVERRIDE:
                st.markdown("##### Year 1 Monthly Override Values (£)")
                if "overrides" not in item or not isinstance(item["overrides"], dict):
                    item["overrides"] = {}
                m_cols = st.columns(6)
                for m_i in range(1, 13):
                    m_lbl = f"M{str(m_i).zfill(2)}"
                    with m_cols[(m_i - 1) % 6]:
                        item["overrides"][m_lbl] = st.number_input(
                            f"{m_lbl}:",
                            value=float(item["overrides"].get(m_lbl, 0.0)),
                            key=f"s_ov_{idx}_{m_lbl}",
                        )
                item["y1_baseline"] = sum(
                    float(item["overrides"].get(f"M{str(m).zfill(2)}", 0.0))
                    for m in range(1, 13)
                )

            if st.button(f"🗑️ Delete Sales Vector {idx}", key=f"del_sales_{idx}"):
                sales_list.pop(idx)
                st.rerun()

with tab_cogs:
    st.subheader("Manage Cost of Goods Sold (COGS)")
    cogs_list = active_data["cogs"]

    if st.button("➕ Add New COGS Item"):
        cogs_list.append(
            {
                "name": f"New_COGS_{len(cogs_list)+1}",
                "entry_mode": ENTRY_MODE_CURVE,
                "y1_baseline": 0.0,
                "y2_baseline": 0.0,
                "y3_baseline": 0.0,
                "seasonality": "Flat_Linear",
                "vat_rate_type": "Standard 20%",
                "payment_delay": 0,
                "overrides": {},
                "matrix_data": {},
            }
        )
        st.rerun()

    for idx, item in enumerate(cogs_list):
        with st.expander(f"COGS Item: {item.get('name', 'Unnamed')}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                item["name"] = st.text_input(
                    "COGS Name:", value=item.get("name", ""), key=f"c_name_{idx}"
                )
                item["entry_mode"] = st.selectbox(
                    "Projection Methodology / Basis:",
                    options=VALID_ENTRY_MODES,
                    index=resolve_mode_index(item.get("entry_mode", ENTRY_MODE_CURVE)),
                    key=f"c_mode_{idx}",
                )
            with col2:
                item["vat_rate_type"] = st.selectbox(
                    "VAT Profile:",
                    options=VAT_OPTIONS,
                    index=resolve_vat_index(item.get("vat_rate_type", "Standard 20%")),
                    key=f"c_vat_{idx}",
                )

            col3, col4, col5 = st.columns(3)
            with col3:
                item["y1_baseline"] = st.number_input(
                    "Year 1 Baseline (£):",
                    value=float(item.get("y1_baseline", 0.0)),
                    key=f"c_y1_{idx}",
                )
            with col4:
                item["y2_baseline"] = st.number_input(
                    "Year 2 Baseline (£):",
                    value=float(item.get("y2_baseline", 0.0)),
                    key=f"c_y2_{idx}",
                )
            with col5:
                item["y3_baseline"] = st.number_input(
                    "Year 3 Baseline (£):",
                    value=float(item.get("y3_baseline", 0.0)),
                    key=f"c_y3_{idx}",
                )

            if item["entry_mode"] == ENTRY_MODE_CURVE:
                item["seasonality"] = st.selectbox(
                    "Monthly Distribution Curve Profile:",
                    options=CURVE_OPTIONS,
                    index=resolve_curve_index(item.get("seasonality", "Flat_Linear")),
                    key=f"c_season_{idx}",
                )
            elif item["entry_mode"] == ENTRY_MODE_OVERRIDE:
                st.markdown("##### Year 1 Monthly Override Values (£)")
                if "overrides" not in item or not isinstance(item["overrides"], dict):
                    item["overrides"] = {}
                m_cols = st.columns(6)
                for m_i in range(1, 13):
                    m_lbl = f"M{str(m_i).zfill(2)}"
                    with m_cols[(m_i - 1) % 6]:
                        item["overrides"][m_lbl] = st.number_input(
                            f"{m_lbl}:",
                            value=float(item["overrides"].get(m_lbl, 0.0)),
                            key=f"c_ov_{idx}_{m_lbl}",
                        )
                item["y1_baseline"] = sum(
                    float(item["overrides"].get(f"M{str(m).zfill(2)}", 0.0))
                    for m in range(1, 13)
                )

            if st.button(f"🗑️ Delete COGS Item {idx}", key=f"del_cogs_{idx}"):
                cogs_list.pop(idx)
                st.rerun()

with tab_opex:
    st.subheader("Manage Operational Overheads (OPEX)")
    opex_list = active_data["opex"]

    if st.button("➕ Add New Overhead Item"):
        opex_list.append(
            {
                "name": f"New_Overhead_{len(opex_list)+1}",
                "entry_mode": ENTRY_MODE_CURVE,
                "y1_baseline": 0.0,
                "y2_baseline": 0.0,
                "y3_baseline": 0.0,
                "seasonality": "Flat_Linear",
                "vat_rate_type": "Standard 20%",
                "overrides": {},
                "matrix_data": {},
            }
        )
        st.rerun()

    for idx, item in enumerate(opex_list):
        with st.expander(f"Overhead: {item.get('name', 'Unnamed')}", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                item["name"] = st.text_input(
                    "Overhead Name:", value=item.get("name", ""), key=f"op_name_{idx}"
                )
                item["entry_mode"] = st.selectbox(
                    "Projection Methodology / Basis:",
                    options=VALID_ENTRY_MODES,
                    index=resolve_mode_index(item.get("entry_mode", ENTRY_MODE_CURVE)),
                    key=f"op_mode_{idx}",
                )
            with col2:
                item["vat_rate_type"] = st.selectbox(
                    "VAT Profile:",
                    options=VAT_OPTIONS,
                    index=resolve_vat_index(item.get("vat_rate_type", "Standard 20%")),
                    key=f"op_vat_{idx}",
                )

            col3, col4, col5 = st.columns(3)
            with col3:
                item["y1_baseline"] = st.number_input(
                    "Year 1 Baseline (£):",
                    value=float(item.get("y1_baseline", 0.0)),
                    key=f"op_y1_{idx}",
                )
            with col4:
                item["y2_baseline"] = st.number_input(
                    "Year 2 Baseline (£):",
                    value=float(item.get("y2_baseline", 0.0)),
                    key=f"op_y2_{idx}",
                )
            with col5:
                item["y3_baseline"] = st.number_input(
                    "Year 3 Baseline (£):",
                    value=float(item.get("y3_baseline", 0.0)),
                    key=f"op_y3_{idx}",
                )

            if item["entry_mode"] == ENTRY_MODE_CURVE:
                item["seasonality"] = st.selectbox(
                    "Monthly Distribution Curve Profile:",
                    options=CURVE_OPTIONS,
                    index=resolve_curve_index(item.get("seasonality", "Flat_Linear")),
                    key=f"op_season_{idx}",
                )
            elif item["entry_mode"] == ENTRY_MODE_OVERRIDE:
                st.markdown("##### Year 1 Monthly Override Values (£)")
                if "overrides" not in item or not isinstance(item["overrides"], dict):
                    item["overrides"] = {}
                m_cols = st.columns(6)
                for m_i in range(1, 13):
                    m_lbl = f"M{str(m_i).zfill(2)}"
                    with m_cols[(m_i - 1) % 6]:
                        item["overrides"][m_lbl] = st.number_input(
                            f"{m_lbl}:",
                            value=float(item["overrides"].get(m_lbl, 0.0)),
                            key=f"op_ov_{idx}_{m_lbl}",
                        )
                item["y1_baseline"] = sum(
                    float(item["overrides"].get(f"M{str(m).zfill(2)}", 0.0))
                    for m in range(1, 13)
                )

            if st.button(f"🗑️ Delete Overhead {idx}", key=f"del_opex_{idx}"):
                opex_list.pop(idx)
                st.rerun()

with tab_payroll:
    st.subheader("Manage Staff Payroll & Salaried Roles")
    payroll_list = active_data["payroll"]
    if st.button("➕ Add New Payroll Role"):
        payroll_list.append(
            {
                "name": f"Role_{len(payroll_list)+1}",
                "headcount": 1,
                "monthly_wage": 2500.0,
                "start_month": 1,
                "end_month": 36,
            }
        )
        st.rerun()

    for idx, item in enumerate(payroll_list):
        with st.expander(f"Role: {item.get('name', 'Unnamed')}", expanded=True):
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                item["name"] = st.text_input(
                    "Role Title:", value=item.get("name", ""), key=f"p_name_{idx}"
                )
            with col2:
                item["headcount"] = st.number_input(
                    "Headcount:",
                    min_value=1,
                    step=1,
                    value=int(item.get("headcount", 1)),
                    key=f"p_hc_{idx}",
                )
            with col3:
                item["monthly_wage"] = st.number_input(
                    "Gross Monthly Wage (£):",
                    value=float(item.get("monthly_wage", 0.0)),
                    key=f"p_wage_{idx}",
                )
            with col4:
                item["start_month"] = st.number_input(
                    "Start Month:",
                    min_value=1,
                    value=int(item.get("start_month", 1)),
                    key=f"p_start_{idx}",
                )
            with col5:
                item["end_month"] = st.number_input(
                    "End Month:",
                    min_value=1,
                    value=int(item.get("end_month", 36)),
                    key=f"p_end_{idx}",
                )

            if st.button(f"🗑️ Delete Role {idx}", key=f"del_pay_{idx}"):
                payroll_list.pop(idx)
                st.rerun()

with tab_capex:
    st.subheader("Manage Outright Capex & Financed Assets")
    capex_list = active_data["outright_capex"]
    if st.button("➕ Add Outright Capex Purchase"):
        capex_list.append(
            {
                "name": f"Asset_{len(capex_list)+1}",
                "amount": 10000.0,
                "month": 1,
                "depreciation_basis": "straight_line",
                "depreciation_rate": 0.20,
                "term_months": 60,
                "residual_value": 0.0,
            }
        )
        st.rerun()

    for idx, item in enumerate(capex_list):
        with st.expander(f"Capex Asset: {item.get('name', 'Unnamed')}", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                item["name"] = st.text_input(
                    "Asset Description:",
                    value=item.get("name", ""),
                    key=f"cap_name_{idx}",
                )
            with col2:
                item["amount"] = st.number_input(
                    "Total Cost (£):",
                    value=float(item.get("amount", 0.0)),
                    key=f"cap_amt_{idx}",
                )
            with col3:
                item["month"] = st.number_input(
                    "Purchase Month:",
                    min_value=1,
                    value=int(item.get("month", 1)),
                    key=f"cap_m_{idx}",
                )
            with col4:
                item["depreciation_rate"] = (
                    st.number_input(
                        "Annual Depr. Rate (%):",
                        min_value=0.0,
                        max_value=100.0,
                        value=float(item.get("depreciation_rate", 0.20)) * 100.0,
                        key=f"cap_rate_{idx}",
                    )
                    / 100.0
                )

            if st.button(f"🗑️ Delete Capex {idx}", key=f"del_cap_{idx}"):
                capex_list.pop(idx)
                st.rerun()

with tab_equity:
    st.subheader("Manage Equity Funding Injections")
    eq_list = active_data["equity_funding"]
    if st.button("➕ Add Equity Funding Injection"):
        eq_list.append(
            {
                "month": 0,
                "amount": 50000.0,
                "source": "Founder Investment",
                "name": "Founder Investment",
            }
        )
        st.rerun()

    for idx, item in enumerate(eq_list):
        with st.expander(f"Equity Injection {idx+1}", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                src = st.text_input(
                    "Investor / Source:",
                    value=item.get("source", item.get("name", "")),
                    key=f"eq_src_{idx}",
                )
                item["source"] = src
                item["name"] = src
            with col2:
                item["amount"] = st.number_input(
                    "Injection Amount (£):",
                    value=float(item.get("amount", 0.0)),
                    key=f"eq_amt_{idx}",
                )
            with col3:
                item["month"] = st.number_input(
                    "Injection Month (0 = Opening):",
                    min_value=0,
                    value=int(item.get("month", 0)),
                    key=f"eq_m_{idx}",
                )

            if st.button(f"🗑️ Delete Equity {idx}", key=f"del_eq_{idx}"):
                eq_list.pop(idx)
                st.rerun()

st.markdown("---")
if st.button("💾 Persist Current Working State to Disk", use_container_width=True):
    current_name = st.session_state.get("active_project_name", DEFAULT_BLANK_SCENARIO)
    success = save_scenario_to_disk(
        current_name, active_data, st.session_state.get("custom_curves", {})
    )
    if success:
        st.success(f"Successfully committed scenario '{current_name}' to disk!")
        st.rerun()
    else:
        st.error("Failed to commit scenario to disk.")
