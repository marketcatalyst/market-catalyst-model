# utils/scenario_manager.py
# STRATA SUITE SCENARIO MANAGEMENT ENGINE // SINGLE SOURCE OF TRUTH PERSISTENCE

import os
import json
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENARIOS_DIR = os.path.join(PROJECT_ROOT, "saved_scenarios")


def get_saved_scenarios():
    os.makedirs(SCENARIOS_DIR, exist_ok=True)
    files = [
        f.replace(".json", "") for f in os.listdir(SCENARIOS_DIR) if f.endswith(".json")
    ]
    return sorted(files) if files else ["Default_Baseline"]


def load_scenario_from_disk(scenario_name: str):
    os.makedirs(SCENARIOS_DIR, exist_ok=True)
    file_path = os.path.join(SCENARIOS_DIR, f"{scenario_name}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                return data
        except Exception:
            pass
    return None


def save_scenario_to_disk(
    scenario_name: str, state_data: dict, custom_curves: dict = None
):
    os.makedirs(SCENARIOS_DIR, exist_ok=True)
    file_path = os.path.join(SCENARIOS_DIR, f"{scenario_name}.json")
    payload = {
        "active_ project_name": scenario_name,
        "active_data": state_data,
        "custom_curves": custom_curves or st.session_state.get("custom_curves", {}),
    }
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)
        return True
    except Exception as e:
        print(f"Failed to save scenario: {e}")
        return False


def render_global_scenario_sidebar():
    st.sidebar.markdown("### 🏛️ Scenario Command Desk")

    saved_files = get_saved_scenarios()
    current_active = st.session_state.get("active_project_name", saved_files[0])

    if current_active not in saved_files:
        saved_files.append(current_active)

    selected_scenario = st.sidebar.selectbox(
        "Active Scenario Context:",
        options=saved_files,
        index=saved_files.index(current_active) if current_active in saved_files else 0,
        key="global_scenario_selectbox",
    )

    if selected_scenario != current_active:
        st.session_state["active_project_name"] = selected_scenario
        loaded_data = load_scenario_from_disk(selected_scenario)
        if loaded_data:
            st.session_state["active_data"] = loaded_data.get("active_data", {})
            st.session_state["custom_curves"] = loaded_data.get("custom_curves", {})
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("##### 💾 Scenario Actions")
    new_scenario_name = st.sidebar.text_input(
        "New Scenario Name:", key="sidebar_new_scenario_input"
    )

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Save Current", width="stretch"):
            if current_active:
                save_scenario_to_disk(
                    current_active, st.session_state.get("active_data", {})
                )
                st.sidebar.success(f"Saved '{current_active}'")
    with col2:
        if st.button("Create New", width="stretch"):
            if new_scenario_name.strip():
                clean_name = new_scenario_name.strip().replace(" ", "_")
                base_data = st.session_state.get("active_data", {})
                save_scenario_to_disk(clean_name, base_data)
                st.session_state["active_project_name"] = clean_name
                st.rerun()
