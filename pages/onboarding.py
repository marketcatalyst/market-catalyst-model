# pages/onboarding.py
# STRATA SUITE // DATA INPUT PARAMETERS v6.9.2-PRODUCTION

import streamlit as st
import pandas as pd
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor

if not st.session_state.get("authenticated"):
    st.warning("⚠️ Please sign in via the main portal gateway.")
    st.stop()


def get_database_connection():
    db_url = (
        os.environ.get("DATABASE_URL")
        or st.secrets.get("DATABASE_URL", None)
        or st.secrets.get("CONNECTION_STRING", None)
    )
    if not db_url:
        return "MISSING_CREDENTIALS"
    try:
        return psycopg2.connect(db_url)
    except Exception as e:
        return f"CONNECTION_FAILED: {str(e)}"


def extract_project_directory_list():
    conn = get_database_connection()
    if conn and not isinstance(conn, str):
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        "SELECT project_name FROM strata_projects_v5 ORDER BY project_name ASC;"
                    )
                    rows = cur.fetchall()
            conn.close()
            return [r["project_name"] for r in rows]
        except Exception:
            pass
    return []


def commit_project_payload_to_storage(project_name, data_payload):
    payload_string = json.dumps(data_payload)
    conn = get_database_connection()
    if isinstance(conn, str):
        return conn
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO strata_projects_v5 (project_name, payload_data, last_updated)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (project_name) DO UPDATE 
                    SET payload_data = EXCLUDED.payload_data, last_updated = CURRENT_TIMESTAMP;
                """,
                    (str(project_name).strip(), payload_string),
                )
        conn.close()
        return "SUCCESS"
    except Exception as e:
        return f"WRITE_FAILED: {str(e)}"


def pull_project_payload_from_storage(project_name):
    conn = get_database_connection()
    if conn and not isinstance(conn, str):
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        "SELECT payload_data FROM strata_projects_v5 WHERE project_name = %s;",
                        (project_name,),
                    )
                    row = cur.fetchone()
            conn.close()
            if row:
                return json.loads(row["payload_data"])
        except Exception:
            pass
    return None


st.title("🕸️ STRATA // Data Input Parameters")
st.caption(
    f"Active Project Workspace Reference Context: `{st.session_state.get('active_project_name', 'Unsaved_Draft_Scenario')}`"
)
st.markdown("---")

p_col1, p_col2 = st.columns([6, 6])
with p_col1:
    avail = extract_project_directory_list()
    sel = st.selectbox(
        "Switch Active Project Model Context:",
        ["-- Select Saved Blueprint --"] + avail,
        help="Pull an existing historical parameter matrix projection context directly from cloud relational storage nodes.",
    )
    if sel != "-- Select Saved Blueprint --" and sel != st.session_state.get(
        "active_project_name"
    ):
        payload = pull_project_payload_from_storage(sel)
        if payload:
            st.session_state["active_data"] = payload
            st.session_state["active_project_name"] = sel
            st.toast(f"Loaded Core State: {sel}")
            st.rerun()
with p_col2:
    s_name = st.text_input(
        "Create / Save Project Name Identifier:",
        value=st.session_state.get("active_project_name", "Unsaved_Draft_Scenario"),
        help="Establish a new projection directory handle context.",
    )
    if st.button("💾 Save Project Configuration", use_container_width=True):
        commit_project_payload_to_storage(s_name, st.session_state["active_data"])
        st.session_state["active_project_name"] = s_name
        st.toast("Project Saved Successfully!")
        st.rerun()

st.markdown("---")

t1, t2, t3 = st.tabs(
    [
        "🏭 Industry Sector Parameters",
        "📊 Seasonality Curves",
        "🔗 Connected Account Formulae",
    ]
)

with t1:
    st.subheader("Industry Sector Parameters")
    with st.form("sector_form"):
        sic = st.text_input(
            "Target UK Standard Industrial Classification (SIC) Code:",
            value=st.session_state["sic_profile"]["sic_code"],
        )
        sector = st.text_input(
            "Operational Sector Designation Description:",
            value=st.session_state["sic_profile"]["sector"],
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
            [
                "Standard 20%",
                "Reduced 5%",
                "Reduced 5% (Commercial Energy Eligible)",
                "Exempt / Zero 0%",
            ],
        )

        if st.form_submit_button(
            "Confirm Global Framework Parameters",
            help="Commit framework values to memory loops.",
        ):
            st.session_state["sic_profile"] = {
                "sic_code": sic,
                "sector": sector,
                "default_vat_type": vat,
                "base_er_nic_rate": nic,
            }
            st.toast("Global parameters configured.")
            st.rerun()

with t2:
    st.subheader("Seasonality Curves")
    st.markdown("Define and lock down your custom timeline distribution patterns here.")

    with st.form("custom_curve_form"):
        curve_name = st.text_input(
            "Custom Curve Name / Identifier:",
            placeholder="e.g. Ammanford Phase 1 Build Pattern",
        )

        st.markdown(
            "**Enter 12 Monthly Distribution Percentage Weights (Must total exactly 100.0%):**"
        )
        w_cols = st.columns(6)
        w = []
        for i in range(12):
            val = w_cols[i % 6].number_input(
                f"Month {str(i+1).zfill(2)} %",
                min_value=0.0,
                max_value=100.0,
                value=8.33 if i < 11 else 8.37,
                step=0.1,
                key=f"m_wt_{i}",
            )
            w.append(val)

        total_weight = round(sum(w), 2)
        st.markdown(
            f"**Current Cumulative Total Distribution Weight Checksum:** `{total_weight}%`"
        )

        if st.form_submit_button("🔒 Save Seasonality Profile Curve"):
            if total_weight != 100.0:
                st.error(
                    f"❌ **Mathematical Checksum Integrity Failure:** Total weights sum to {total_weight}%. You must adjust values to equal exactly 100.0% before saving."
                )
            elif not curve_name:
                st.error(
                    "❌ Please provide a unique descriptive name for this seasonality curve profile."
                )
            else:
                st.session_state["custom_curves"][curve_name] = [
                    float(v) / 100.0 for v in w
                ]
                st.success(
                    f"✔️ Seasonality profile '{curve_name}' successfully added to the active project model registry."
                )

with t3:
    st.subheader("Connected Account Formulae")
    st.markdown(
        "Establish direct systemic dependencies between separate parameter descriptors."
    )

    st.markdown(
        "<div style='background-color:#f1f5f9; padding:20px; border-radius:8px; margin-bottom:20px; text-align:center; font-weight:bold; color:#1e3a8a Triton;' >"
        "[ Selected Cost Account ] &nbsp; = &nbsp; [ Chosen Sales Account Driver ] &nbsp; × &nbsp; [ Your Percentage Allocation Coefficient % ]"
        "</div>",
        unsafe_allow_html=True,
    )

    active_data = st.session_state.get("active_data", {})
    sales_lines = [s["name"] for s in active_data.get("sales", [])]
    cogs_lines = [c["name"] for c in active_data.get("cogs", [])]

    if sales_lines and cogs_lines:
        with st.form("formula_form"):
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
                15.0,
                step=0.5,
                help="Example: Setting Sales Commission to 5% of Core Product Sales will automatically populate the monthly rows whenever product sales scale.",
            )

            if st.form_submit_button("🔗 Link Connected Account Formula"):
                if "vector_couplings" not in st.session_state:
                    st.session_state["vector_couplings"] = []
                st.session_state["vector_couplings"].append(
                    {
                        "cogs_target": chosen_cogs,
                        "sales_driver": chosen_sales,
                        "coefficient": coupling_pct / 100.0,
                    }
                )
                st.toast("Connected Account Formula live and locked.")
    else:
        st.info(
            "💡 Please populate at least one active Sales Stream and one Direct Production Cost line inside Data Entry to map account formulae dependencies."
        )

# Sidebar case alignment protection
st.sidebar.markdown("### 🧭 Navigation Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")
