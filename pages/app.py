# pyright: reportMissingImports=false
# pages/app.py
# STRATA SUITE PRODUCTION ENGINE // DATA ENTRY & SCENARIO MANAGER v9.8.0-ENTERPRISE
# FULL UNABRIDGED SPECIFICATION: DISK PERSISTENCE, VECTOR COUPLINGS, MATRIX OVERRIDES, CUSTOM CURVES

import json
import os
import sys
import pandas as pd
import streamlit as st

# Inject project root into Python system path for pages/ directory imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Centralized Scenario Persistence Engine
from utils.scenario_manager import (
    load_scenario_from_disk,
    save_scenario_to_disk,
    render_global_scenario_sidebar,
)

# Clean layout styling
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
    if st.button("🔑 Return to Home Portal & Sign In", width="stretch"):
        st.switch_page("home.py")
    st.stop()

# Initialize Session State structures if absent
if "active_data" not in st.session_state:
    st.session_state["active_data"] = {
        "sales": [],
        "cogs": [],
        "opex": [],
        "payroll": [],
        "outright_capex": [],
        "financed_assets": [],
        "equity_funding": [],
    }

if "sic_profile" not in st.session_state:
    st.session_state["sic_profile"] = {
        "base_er_nic_rate": 0.138,
        "corp_tax_rate": 0.19,
        "supplier_credit_days": 30,
    }

if "custom_curves" not in st.session_state:
    st.session_state["custom_curves"] = {}

if "vector_couplings" not in st.session_state:
    st.session_state["vector_couplings"] = []

if "active_project_name" not in st.session_state:
    st.session_state["active_project_name"] = "Padel_Centre_Baseline"

active_data = st.session_state["active_data"]

# =========================================================================
# 🏛️ WORKSPACE TOP HEADER & NAVIGATION
# =========================================================================
st.title("✍️ Strategic Financial Parameter Desk")
st.caption(
    f"Active Scenario Working Context: `{st.session_state['active_project_name']}`"
)

c_nav1, c_nav2 = st.columns(2)
with c_nav1:
    st.page_link(
        "pages/reports.py",
        label="📊 View Reconciled Three-Way Statements & Checksum",
        icon="📈",
    )
with c_nav2:
    st.page_link("home.py", label="🏠 Return to Home Portal", icon="🏛️")

st.markdown("---")

# =========================================================================
# ⚙️ STATUTORY PARAMETERS & ECONOMIC BENCHMARKS
# =========================================================================
with st.expander(
    "⚖️ UK GAAP STATUTORY BENCHMARKS & WORKING CAPITAL TERMS", expanded=False
):
    st.caption("Underlying statutory tax rates and standard creditor settlement rules.")
    sic = st.session_state["sic_profile"]
    col_s1, col_s2, col_s3 = st.columns(3)
    sic["corp_tax_rate"] = col_s1.number_input(
        "Corporation Tax Rate (Dec)",
        value=float(sic.get("corp_tax_rate", 0.19)),
        step=0.01,
        format="%.2f",
    )
    sic["base_er_nic_rate"] = col_s2.number_input(
        "Employer NIC Rate (Dec)",
        value=float(sic.get("base_er_nic_rate", 0.138)),
        step=0.005,
        format="%.3f",
    )
    sic["supplier_credit_days"] = col_s3.selectbox(
        "Standard Supplier Settlement Terms",
        [0, 30, 60],
        index=(
            1
            if sic.get("supplier_credit_days", 30) == 30
            else (0 if sic.get("supplier_credit_days", 30) == 0 else 2)
        ),
        format_func=lambda x: f"{x} Days ({'Immediate Cash' if x==0 else 'Standard Month-End'})",
    )

# =========================================================================
# 🌊 CUSTOM SEASONALITY SHAPING HUB
# =========================================================================
with st.expander("🌊 CUSTOM SEASONALITY SHAPING HUB", expanded=False):
    st.caption(
        "Define custom 12-month weight distributions for seasonal sporting demand."
    )
    seasonality_curves = st.session_state["custom_curves"]
    c_curve_name = st.text_input(
        "New Curve Profile Name", placeholder="e.g. Summer_Tournament_Spike"
    )
    if st.button("➕ Create Custom Seasonal Curve Profile"):
        if c_curve_name and c_curve_name not in seasonality_curves:
            seasonality_curves[c_curve_name] = [round(1 / 12, 4)] * 12
            st.rerun()

    for c_name, weights in list(seasonality_curves.items()):
        st.markdown(f"**Curve: `{c_name}`** (Sum must equal 1.00)")
        cols = st.columns(12)
        new_weights = []
        for m_idx in range(12):
            w = cols[m_idx].number_input(
                f"M{m_idx+1}",
                value=float(weights[m_idx]),
                step=0.01,
                format="%.3f",
                key=f"c_{c_name}_{m_idx}",
            )
            new_weights.append(w)
        total_w = sum(new_weights)
        if abs(total_w - 1.0) > 0.001:
            st.caption(f"⚠️ Total Weight: `{total_w:.3f}` (Adjust to sum to 1.000)")
        seasonality_curves[c_name] = new_weights
        if st.button(f"🗑️ Remove Profile {c_name}", key=f"del_c_{c_name}"):
            del seasonality_curves[c_name]
            st.rerun()

# =========================================================================
# 🔗 VECTOR DYNAMIC COUPLINGS HUB
# =========================================================================
with st.expander("🔗 DYNAMIC VECTOR COUPLINGS (SALES ➔ COGS LINKAGE)", expanded=False):
    st.caption(
        "Tie direct production expenses (ball supplies, court fees, coaching split) directly to revenue streams."
    )
    couplings = st.session_state["vector_couplings"]
    sales_names = [s.get("name", "") for s in active_data.get("sales", [])]
    cogs_names = [c.get("name", "") for c in active_data.get("cogs", [])]

    if sales_names and cogs_names:
        c_cp1, c_cp2, c_cp3, c_cp4 = st.columns([4, 4, 3, 2])
        d_sales = c_cp1.selectbox("Driver Sales Revenue", sales_names, key="coup_sales")
        t_cogs = c_cp2.selectbox("Target COGS Item", cogs_names, key="coup_cogs")
        coeff = (
            c_cp3.number_input("Variable Cost Ratio (% of Rev)", value=15.0, step=1.0)
            / 100.0
        )
        if c_cp4.button("➕ Link Vectors"):
            couplings.append(
                {"sales_driver": d_sales, "cogs_target": t_cogs, "coefficient": coeff}
            )
            st.rerun()

    for idx, cp in enumerate(couplings):
        st.write(
            f"• **{cp['cogs_target']}** automatically set to **{cp['coefficient']*100:.1f}%** of **{cp['sales_driver']}**"
        )
        if st.button(f"Disconnect Link #{idx+1}", key=f"del_coup_{idx}"):
            couplings.pop(idx)
            st.rerun()

st.markdown("---")

# =========================================================================
# 🎛️ CORE PARAMETER DESKS (DESKS 1 - 7)
# =========================================================================

# -------------------------------------------------------------------------
# DESK 1: SALES DRIVERS & MONTHLY OVERRIDES
# -------------------------------------------------------------------------
with st.expander("📈 1. THE SALES DRIVER DESK", expanded=True):
    st.caption(
        "Configure revenue streams, multi-year targets, flex scalars, and granular monthly overrides."
    )
    sales_list = active_data.get("sales", [])
    all_season_choices = ["Flat_Linear", "Winter_Peak", "Summer_Peak"] + list(
        st.session_state["custom_curves"].keys()
    )

    for i, s in enumerate(sales_list):
        st.markdown(f"#### Vector #{i+1}: `{s.get('name', f'Sales Item {i+1}')}`")
        c1, c2, c3, c4 = st.columns(4)
        s["name"] = c1.text_input(
            f"Item Name #{i+1}", value=s.get("name", ""), key=f"s_name_{i}"
        )
        s["y1_baseline"] = c2.number_input(
            f"Year 1 Target (£)",
            value=float(s.get("y1_baseline", 0.0)),
            step=1000.0,
            key=f"s_y1_{i}",
        )
        s["y2_baseline"] = c3.number_input(
            f"Year 2 Target (£)",
            value=float(s.get("y2_baseline", 0.0)),
            step=1000.0,
            key=f"s_y2_{i}",
        )
        s["y3_baseline"] = c4.number_input(
            f"Year 3 Target (£)",
            value=float(s.get("y3_baseline", 0.0)),
            step=1000.0,
            key=f"s_y3_{i}",
        )

        c5, c6, c7, c8 = st.columns(4)
        vat_options = ["Standard 20%", "Reduced 5%", "Zero-Rated / Exempt 0%"]
        cur_vat = s.get("vat_rate_type", "Standard 20%")
        vat_idx = vat_options.index(cur_vat) if cur_vat in vat_options else 0
        s["vat_rate_type"] = c5.selectbox(
            f"VAT Profile #{i+1}", vat_options, index=vat_idx, key=f"s_vat_{i}"
        )

        cur_season = s.get("seasonality", "Flat_Linear")
        season_idx = (
            all_season_choices.index(cur_season)
            if cur_season in all_season_choices
            else 0
        )
        s["seasonality"] = c6.selectbox(
            f"Seasonality #{i+1}",
            all_season_choices,
            index=season_idx,
            key=f"s_seas_{i}",
        )

        s["flex_pct"] = c7.number_input(
            f"Y2-Y3 Flex Scale (%)",
            value=float(s.get("flex_pct", 0.0)),
            step=1.0,
            key=f"s_flex_{i}",
        )
        s["payment_delay"] = c8.selectbox(
            f"Debtor Receipt Lag #{i+1}",
            [0, 30, 60],
            index=(
                0
                if s.get("payment_delay", 0) == 0
                else (1 if s.get("payment_delay", 0) == 30 else 2)
            ),
            format_func=lambda x: f"{x} Days ({'Instant Cash' if x==0 else 'Debtor Lag'})",
            key=f"s_delay_{i}",
        )

        # Monthly Override Grid
        with st.expander(
            f"⚙️ Granular Month-by-Month Overrides for {s.get('name')}", expanded=False
        ):
            st.caption("Leave at 0.00 to automatically use the annual baseline curve.")
            overrides = s.setdefault("overrides", {})
            ov_cols = st.columns(12)
            for m_idx in range(1, 13):
                m_key = f"M{str(m_idx).zfill(2)}"
                overrides[m_key] = ov_cols[m_idx - 1].number_input(
                    m_key,
                    value=float(overrides.get(m_key, 0.0)),
                    step=500.0,
                    key=f"ov_s_{i}_{m_key}",
                )
        st.markdown("---")

    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("➕ Add New Sales Revenue Vector", width="stretch"):
        sales_list.append(
            {
                "name": f"New Revenue Stream {len(sales_list)+1}",
                "y1_baseline": 50000.0,
                "y2_baseline": 60000.0,
                "y3_baseline": 70000.0,
                "vat_rate_type": "Standard 20%",
                "seasonality": "Flat_Linear",
                "flex_pct": 0.0,
                "payment_delay": 0,
                "overrides": {},
            }
        )
        st.rerun()

    if sales_list and col_btn2.button("🗑️ Remove Last Sales Vector", width="stretch"):
        sales_list.pop()
        st.rerun()

# -------------------------------------------------------------------------
# DESK 2: PRODUCTION COGS & DIRECT EXPENSES
# -------------------------------------------------------------------------
with st.expander("📦 2. THE PRODUCTION COGS DESK", expanded=True):
    st.caption(
        "Direct operational costs (canteen, equipment, court coaches, direct court personnel)."
    )
    cogs_list = active_data.get("cogs", [])

    for i, c in enumerate(cogs_list):
        st.markdown(f"#### Cost Vector #{i+1}: `{c.get('name', f'Cost Item {i+1}')}`")
        c1, c2, c3, c4 = st.columns(4)
        c["name"] = c1.text_input(
            f"COGS Item Name #{i+1}", value=c.get("name", ""), key=f"c_name_{i}"
        )
        c["y1_baseline"] = c2.number_input(
            f"Year 1 Cost (£)",
            value=float(c.get("y1_baseline", 0.0)),
            step=1000.0,
            key=f"c_y1_{i}",
        )
        c["y2_baseline"] = c3.number_input(
            f"Year 2 Cost (£)",
            value=float(c.get("y2_baseline", 0.0)),
            step=1000.0,
            key=f"c_y2_{i}",
        )
        c["y3_baseline"] = c4.number_input(
            f"Year 3 Cost (£)",
            value=float(c.get("y3_baseline", 0.0)),
            step=1000.0,
            key=f"c_y3_{i}",
        )

        c5, c6, c7 = st.columns(3)
        vat_options = ["Standard 20%", "Commercial Energy 5%", "Zero-Rated / Exempt 0%"]
        cur_vat = c.get("vat_rate_type", "Standard 20%")
        vat_idx = vat_options.index(cur_vat) if cur_vat in vat_options else 0
        c["vat_rate_type"] = c5.selectbox(
            f"Input VAT Profile #{i+1}", vat_options, index=vat_idx, key=f"c_vat_{i}"
        )

        cur_season = c.get("seasonality", "Flat_Linear")
        season_idx = (
            all_season_choices.index(cur_season)
            if cur_season in all_season_choices
            else 0
        )
        c["seasonality"] = c6.selectbox(
            f"Cost Curve Profile #{i+1}",
            all_season_choices,
            index=season_idx,
            key=f"c_seas_{i}",
        )
        c["flex_pct"] = c7.number_input(
            f"Cost Flex Inflation (%)",
            value=float(c.get("flex_pct", 0.0)),
            step=1.0,
            key=f"c_flex_{i}",
        )

        # Monthly Override Grid
        with st.expander(
            f"⚙️ Month-by-Month Overrides for {c.get('name')}", expanded=False
        ):
            overrides = c.setdefault("overrides", {})
            ov_cols = st.columns(12)
            for m_idx in range(1, 13):
                m_key = f"M{str(m_idx).zfill(2)}"
                overrides[m_key] = ov_cols[m_idx - 1].number_input(
                    m_key,
                    value=float(overrides.get(m_key, 0.0)),
                    step=500.0,
                    key=f"ov_c_{i}_{m_key}",
                )
        st.markdown("---")

    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("➕ Add New COGS Direct Cost Vector", width="stretch"):
        cogs_list.append(
            {
                "name": f"New COGS Stream {len(cogs_list)+1}",
                "y1_baseline": 15000.0,
                "y2_baseline": 20000.0,
                "y3_baseline": 25000.0,
                "vat_rate_type": "Standard 20%",
                "seasonality": "Flat_Linear",
                "flex_pct": 0.0,
                "overrides": {},
            }
        )
        st.rerun()

    if cogs_list and col_btn2.button("🗑️ Remove Last COGS Vector", width="stretch"):
        cogs_list.pop()
        st.rerun()

# -------------------------------------------------------------------------
# DESK 3: OPERATIONAL OVERHEADS (OPEX)
# -------------------------------------------------------------------------
with st.expander("🏢 3. THE OPERATIONAL OVERHEADS DESK", expanded=False):
    st.caption(
        "Fixed overheads (ground rent, rates, power, insurance, advertising, IT)."
    )
    opex_list = active_data.get("opex", [])

    for i, op in enumerate(opex_list):
        c1, c2, c3, c4 = st.columns(4)
        op["name"] = c1.text_input(
            f"Overhead Item #{i+1}", value=op.get("name", ""), key=f"op_name_{i}"
        )
        op["y1_baseline"] = c2.number_input(
            f"Year 1 (£/yr)",
            value=float(op.get("y1_baseline", 0.0)),
            step=1000.0,
            key=f"op_y1_{i}",
        )
        op["y2_baseline"] = c3.number_input(
            f"Year 2 (£/yr)",
            value=float(op.get("y2_baseline", 0.0)),
            step=1000.0,
            key=f"op_y2_{i}",
        )
        op["y3_baseline"] = c4.number_input(
            f"Year 3 (£/yr)",
            value=float(op.get("y3_baseline", 0.0)),
            step=1000.0,
            key=f"op_y3_{i}",
        )

        c5, _ = st.columns([4, 8])
        vat_options = ["Standard 20%", "Commercial Energy 5%", "Zero-Rated / Exempt 0%"]
        cur_vat = op.get("vat_rate_type", "Standard 20%")
        vat_idx = vat_options.index(cur_vat) if cur_vat in vat_options else 0
        op["vat_rate_type"] = c5.selectbox(
            f"Input VAT Profile", vat_options, index=vat_idx, key=f"op_vat_{i}"
        )

    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("➕ Add Operational Overhead Line", width="stretch"):
        opex_list.append(
            {
                "name": f"Overhead Item {len(opex_list)+1}",
                "y1_baseline": 12000.0,
                "y2_baseline": 12000.0,
                "y3_baseline": 12000.0,
                "vat_rate_type": "Standard 20%",
            }
        )
        st.rerun()
    if opex_list and col_btn2.button("🗑️ Remove Last Overhead Line", width="stretch"):
        opex_list.pop()
        st.rerun()

# -------------------------------------------------------------------------
# DESK 4: PERSONNEL & PAYROLL HORIZON
# -------------------------------------------------------------------------
with st.expander("👥 4. THE PERSONNEL HORIZON DESK", expanded=False):
    st.caption(
        "Administrative & management personnel held in Account 7000 (with Employer NIC)."
    )
    payroll_list = active_data.get("payroll", [])

    for i, p in enumerate(payroll_list):
        c1, c2, c3, c4, c5 = st.columns(5)
        p["name"] = c1.text_input(
            f"Role Title #{i+1}", value=p.get("name", ""), key=f"p_name_{i}"
        )
        p["headcount"] = c2.number_input(
            f"Headcount #{i+1}",
            value=int(p.get("headcount", 1)),
            min_value=1,
            step=1,
            key=f"p_hc_{i}",
        )
        p["monthly_wage"] = c3.number_input(
            f"Gross Wage (£/mo)",
            value=float(p.get("monthly_wage", 2500.0)),
            step=100.0,
            key=f"p_wage_{i}",
        )
        p["start_month"] = c4.number_input(
            f"Start Month",
            value=int(p.get("start_month", 1)),
            min_value=1,
            max_value=60,
            key=f"p_start_{i}",
        )
        p["end_month"] = c5.number_input(
            f"End Month",
            value=int(p.get("end_month", 60)),
            min_value=1,
            max_value=60,
            key=f"p_end_{i}",
        )

    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("➕ Add Salaried Staff Position", width="stretch"):
        payroll_list.append(
            {
                "name": "Operations Manager",
                "headcount": 1,
                "monthly_wage": 3000.0,
                "start_month": 1,
                "end_month": 36,
            }
        )
        st.rerun()
    if payroll_list and col_btn2.button("🗑️ Remove Last Personnel Position", width="stretch"):
        payroll_list.pop()
        st.rerun()

# -------------------------------------------------------------------------
# DESK 5: OUTRIGHT CAPITAL EXPENDITURE
# -------------------------------------------------------------------------
with st.expander("🚜 5. DIRECT INFRASTRUCTURE & OUTRIGHT CAPEX", expanded=False):
    st.caption("Purchased plant, courts, groundworks, and infrastructure assets.")
    capex_list = active_data.get("outright_capex", [])

    for i, cap in enumerate(capex_list):
        c1, c2, c3, c4 = st.columns(4)
        cap["name"] = c1.text_input(
            f"CapEx Name #{i+1}", value=cap.get("name", ""), key=f"cap_name_{i}"
        )
        cap["amount"] = c2.number_input(
            f"Capital Value (£)",
            value=float(cap.get("amount", 0.0)),
            step=5000.0,
            key=f"cap_amt_{i}",
        )
        cap["month"] = c3.number_input(
            f"Purchase Month",
            value=int(cap.get("month", 1)),
            min_value=0,
            max_value=60,
            key=f"cap_m_{i}",
        )
        cap["depreciation_rate"] = c4.number_input(
            f"Depreciation (p.a.)",
            value=float(cap.get("depreciation_rate", 0.20)),
            step=0.05,
            key=f"cap_dep_{i}",
        )

    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("➕ Register Direct CapEx Asset", width="stretch"):
        capex_list.append(
            {
                "name": "Canopy & Court Infrastructure",
                "amount": 100000.0,
                "month": 1,
                "depreciation_rate": 0.20,
            }
        )
        st.rerun()
    if capex_list and col_btn2.button("🗑️ Remove Last CapEx Asset", width="stretch"):
        capex_list.pop()
        st.rerun()

# -------------------------------------------------------------------------
# DESK 6: FINANCED CAPITAL ASSETS (HP & LEASES)
# -------------------------------------------------------------------------
with st.expander("📑 6. FINANCED ASSETS & FACILITY LIABILITIES", expanded=False):
    st.caption("Hire purchase / asset finance facilities held in Account 2300.")
    fin_list = active_data.get("financed_assets", [])

    for i, fin in enumerate(fin_list):
        c1, c2, c3, c4, c5 = st.columns(5)
        fin["name"] = c1.text_input(
            f"Facility Name #{i+1}", value=fin.get("name", ""), key=f"fin_name_{i}"
        )
        fin["amount"] = c2.number_input(
            f"Total Facility (£)",
            value=float(fin.get("amount", 0.0)),
            step=5000.0,
            key=f"fin_amt_{i}",
        )
        fin["deposit_pct"] = c3.number_input(
            f"Deposit Paid (%)",
            value=float(fin.get("deposit_pct", 10.0)),
            step=5.0,
            key=f"fin_dp_{i}",
        )
        fin["term_months"] = c4.number_input(
            f"Term (Months)",
            value=int(fin.get("term_months", 36)),
            min_value=12,
            max_value=120,
            key=f"fin_term_{i}",
        )
        fin["interest_rate"] = c5.number_input(
            f"APR Rate (%)",
            value=float(fin.get("interest_rate", 5.0)),
            step=0.5,
            key=f"fin_apr_{i}",
        )

    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("➕ Register Financed HP Facility", width="stretch"):
        fin_list.append(
            {
                "name": "Court Lighting HP Facility",
                "amount": 50000.0,
                "month": 1,
                "deposit_pct": 10.0,
                "term_months": 36,
                "interest_rate": 6.5,
                "depreciation_rate": 0.15,
            }
        )
        st.rerun()
    if fin_list and col_btn2.button("🗑️ Remove Last Financed Facility", width="stretch"):
        fin_list.pop()
        st.rerun()

# -------------------------------------------------------------------------
# DESK 7: EQUITY & CAPITAL RESERVES
# -------------------------------------------------------------------------
with st.expander("🏛️ 7. SHAREHOLDER EQUITY & SEED FUNDING", expanded=False):
    st.caption(
        "Shareholder capital injections credited to Share Capital (Account 3000)."
    )
    eq_list = active_data.get("equity_funding", [])

    for i, eq in enumerate(eq_list):
        c1, c2, c3 = st.columns(3)
        eq["name"] = c1.text_input(
            f"Funding Tranche #{i+1}",
            value=eq.get("name", "Founder Seed Equity"),
            key=f"eq_name_{i}",
        )
        eq["amount"] = c2.number_input(
            f"Injected Capital (£)",
            value=float(eq.get("amount", 0.0)),
            step=5000.0,
            key=f"eq_amt_{i}",
        )
        eq["month"] = c3.number_input(
            f"Injection Month",
            value=int(eq.get("month", 0)),
            min_value=0,
            max_value=60,
            key=f"eq_m_{i}",
        )

    col_btn1, col_btn2 = st.columns(2)
    if col_btn1.button("➕ Add Equity Funding Inflow", width="stretch"):
        eq_list.append(
            {
                "name": f"Investor Round {len(eq_list)+1}",
                "amount": 50000.0,
                "month": 0,
            }
        )
        st.rerun()
    if eq_list and col_btn2.button("🗑️ Remove Last Equity Tranche", width="stretch"):
        eq_list.pop()
        st.rerun()

# =========================================================================
# 🚀 ACTION FOOTER & PERMANENT COMMIT BAR
# =========================================================================
b_save, b_rep = st.columns(2)
with b_save:
    if st.button("💾 Persist Current Working State to Disk", width="stretch"):
        cur_scen = st.session_state.get("active_project_name", "Padel_Centre_Baseline")
        if save_scenario_to_disk(cur_scen):
            st.success(f"✔️ Active data successfully written to disk as `{cur_scen}`.")
with b_rep:
    if st.button("🚀 Calculate & View Reconciled Reports", width="stretch"):
        st.switch_page("pages/reports.py")

# =========================================================================
# 🧭 FIXED SIDEBAR COMPASS & UNIFIED SCENARIO CONTROLS
# =========================================================================
st.sidebar.markdown("### Compass Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link(
    "pages/1_Data_Ingestion_Gateway.py", label="📥 Data Ingestion Gateway"
)
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry Panel")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")

# Unified Global Scenario Manager
render_global_scenario_sidebar()