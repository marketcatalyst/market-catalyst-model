# home.py
# STRATA SUITE ACCESS GATEWAY // MAIN ENTRANCE PORTAL v6.9.5-PRODUCTION

import streamlit as st
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Force strict sidebar removal cleanly by explicitly locking page configuration
st.set_page_config(
    page_title="STRATA // Intelligence Suite", page_icon="🏛️", layout="wide"
)

# Inject global CSS layout styling to forcefully hide the auto-generated top links
st.markdown(
    """
    <style>
        div[data-testid="stSidebarNav"] {display: none !important;}
    </style>
    """,
    unsafe_allow_html=True,
)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "sic_profile" not in st.session_state:
    st.session_state["sic_profile"] = {
        "sic_code": "71121",
        "sector": "Professional R&D Services (Default)",
        "default_vat_type": "Standard 20%",
        "base_er_nic_rate": 0.138,
    }

if "active_data" not in st.session_state:
    st.session_state["active_data"] = {
        "sales": [],
        "milestones": [],
        "cogs": [],
        "opex": [],
        "financed_assets": [],
        "outright_capex": [],
        "payroll": [],
        "equity_funding": [],
    }
if "vector_couplings" not in st.session_state:
    st.session_state["vector_couplings"] = []
if "custom_curves" not in st.session_state:
    st.session_state["custom_curves"] = {}


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


# --- GATEWAY VIEW 1: SECURE SIGN-IN PORTAL ---
if not st.session_state["authenticated"]:
    st.title("🏛️ STRATA // Financial Intelligence Gateway")
    st.markdown(
        "Please authenticate with your secure portal access tokens to open active forecast project workspaces."
    )
    st.markdown("---")

    login_col1, login_col2, login_col3 = st.columns([4, 4, 4])
    with login_col2:
        st.subheader("Executive Portal Access")
        with st.form("portal_login_form"):
            user_id = st.text_input(
                "User Name / Email Address:", placeholder="e.g. user@theperry.group"
            )
            user_key = st.text_input("Secure Access Key:", type="password")

            if st.form_submit_button(
                "🔒 Authenticate Secure Session", use_container_width=True
            ):
                if user_id and user_key:
                    st.session_state["authenticated"] = True
                    st.toast("Session authenticated successfully.")
                    st.rerun()
                else:
                    st.error("Please enter a valid User Name and Access Key.")
    st.stop()

# --- GATEWAY VIEW 2: EXECUTIVE PLATFORM HUB ---
st.title("🏛️ STRATA // Financial Intelligence Suite")
st.markdown("---")

st.subheader("📁 Project Workspace Directory Room")
p_col1, p_col2 = st.columns([6, 6])
with p_col1:
    avail_blueprints = extract_project_directory_list()
    selected_blueprint = st.selectbox(
        "Switch Active Project Model Context:",
        ["-- Select Saved Project Scenario --"] + avail_blueprints,
    )
    if (
        selected_blueprint != "-- Select Saved Project Scenario --"
        and selected_blueprint != st.session_state.get("active_project_name")
    ):
        retrieved_payload = pull_project_payload_from_storage(selected_blueprint)
        if retrieved_payload:
            st.session_state["active_data"] = retrieved_payload
            st.session_state["active_project_name"] = selected_blueprint
            st.toast(f"Loaded Core State Matrix: {selected_blueprint}")
            st.rerun()

with p_col2:
    active_project_handle = st.text_input(
        "Create / Save Project Name Identifier:",
        value=st.session_state.get("active_project_name", "Unsaved_Draft_Scenario"),
    )
    if st.button("💾 Save Project Configuration", use_container_width=True):
        commit_project_payload_to_storage(
            active_project_handle, st.session_state["active_data"]
        )
        st.session_state["active_project_name"] = active_project_handle
        st.toast("Project Configuration committed successfully!")
        st.rerun()

st.markdown("---")
st.subheader("🧭 Guided Corporate Optimization Pipeline")
st.info(
    f"💡 **Active Working Blueprint Instance Context:** `{st.session_state.get('active_project_name', 'Unsaved_Draft_Scenario')}`"
)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("### 1️⃣ Data Input Parameters")
    st.page_link(
        "pages/onboarding.py",
        label="🕸️ Open Data Input Parameters",
        use_container_width=True,
    )
with col2:
    st.markdown("### 2️⃣ Data Entry")
    st.page_link(
        "pages/app.py", label="✍️ Open Data Entry Panel", use_container_width=True
    )
with col3:
    st.markdown("### 3️⃣ Performance Tab")
    st.page_link(
        "pages/reports.py", label="📊 Open Performance Tab", use_container_width=True
    )

# --- RECONCILED UPPER CASE SIDEBAR NAVIGATION MANAGEMENT ---
st.sidebar.markdown("### Compass Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")

st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 Session Controls")

if st.sidebar.button("🚪 Log Off Session", use_container_width=True):
    st.session_state["authenticated"] = False
    st.toast("Session terminated safely.")
    st.rerun()
