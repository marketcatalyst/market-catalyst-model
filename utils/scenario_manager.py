# utils/scenario_manager.py
# STRATA SUITE // UNIFIED SCENARIO PERSISTENCE ENGINE

import json
import os
import streamlit as st

# Find repository root regardless of launch location
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENARIOS_DIR = os.path.join(PROJECT_ROOT, "saved_scenarios")
os.makedirs(SCENARIOS_DIR, exist_ok=True)


def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in ("-", "_")).strip()


def list_saved_scenarios():
    if not os.path.exists(SCENARIOS_DIR):
        return []
    return sorted(
        [
            f.replace(".json", "")
            for f in os.listdir(SCENARIOS_DIR)
            if f.endswith(".json")
        ]
    )


def save_scenario_to_disk(scenario_name: str) -> bool:
    if not scenario_name:
        return False
    clean_name = sanitize_filename(scenario_name)
    file_path = os.path.join(SCENARIOS_DIR, f"{clean_name}.json")
    payload = {
        "project_name": scenario_name,
        "sic_profile": st.session_state.get("sic_profile", {}),
        "custom_curves": st.session_state.get("custom_curves", {}),
        "vector_couplings": st.session_state.get("vector_couplings", []),
        "active_data": st.session_state.get("active_data", {}),
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    st.session_state["active_project_name"] = scenario_name
    return True


def load_scenario_from_disk(scenario_name: str) -> bool:
    clean_name = sanitize_filename(scenario_name)
    file_path = os.path.join(SCENARIOS_DIR, f"{clean_name}.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        st.session_state["active_project_name"] = payload.get(
            "project_name", scenario_name
        )
        st.session_state["sic_profile"] = payload.get("sic_profile", {})
        st.session_state["custom_curves"] = payload.get("custom_curves", {})
        st.session_state["vector_couplings"] = payload.get("vector_couplings", [])
        st.session_state["active_data"] = payload.get("active_data", {})
        return True
    return False


def render_global_scenario_sidebar():
    """
    Renders a unified scenario persistence interface in the sidebar.
    Available across home.py, pages/app.py, and pages/reports.py.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🗂️ Scenario Control Desk")

    saved_list = list_saved_scenarios()
    curr_active = st.session_state.get("active_project_name", "Padel_Centre_Baseline")

    options = ["-- Select Scenario --"] + saved_list
    def_idx = options.index(curr_active) if curr_active in options else 0

    selected = st.sidebar.selectbox(
        "Active Scenario:",
        options=options,
        index=def_idx,
        key="global_scenario_select",
    )

    c_btn1, c_btn2 = st.sidebar.columns(2)
    if c_btn1.button("📥 Load", width="stretch"):
        if selected != "-- Select Scenario --":
            if load_scenario_from_disk(selected):
                st.sidebar.success(f"Loaded {selected}")
                st.rerun()
            else:
                st.sidebar.error("Failed to load scenario.")

    if c_btn2.button("💾 Save", width="stretch"):
        if save_scenario_to_disk(curr_active):
            st.sidebar.success("Saved")
            st.rerun()

    with st.sidebar.expander("💾 Save / Duplicate As..."):
        new_name = st.text_input(
            "Scenario Name:", value=curr_active, key="global_save_as_name"
        )
        if st.button("Save As New", width="stretch", key="global_save_as_btn"):
            if new_name.strip():
                save_scenario_to_disk(new_name.strip())
                st.rerun()
