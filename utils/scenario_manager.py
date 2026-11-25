# utils/scenario_manager.py
# STRATA SUITE SCENARIO MANAGEMENT & SCHEMA MIGRATION ENGINE // SSOT IMMUTABLE CONTRACT

import os
import json
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENARIOS_DIR = os.path.join(PROJECT_ROOT, "saved_scenarios")

DEFAULT_BLANK_SCENARIO = "New_Client_Baseline"

ENTRY_MODE_CURVE = "Annual Baseline + Monthly Distribution Curve"
ENTRY_MODE_OVERRIDE = "Manual Monthly Override"
ENTRY_MODE_FLAT = "Flat Linear Baseline"
VALID_ENTRY_MODES = [ENTRY_MODE_CURVE, ENTRY_MODE_OVERRIDE, ENTRY_MODE_FLAT]


def create_blank_scenario(scenario_name: str = DEFAULT_BLANK_SCENARIO) -> str:
    """
    Creates a clean, empty SSOT scenario file for a new client and sets it active.
    """
    clean_name = (scenario_name or "").strip().replace(
        " ", "_"
    ) or DEFAULT_BLANK_SCENARIO
    empty_data = {
        "sales": [],
        "cogs": [],
        "opex": [],
        "payroll": [],
        "financed_assets": [],
        "outright_capex": [],
        "equity_funding": [],
    }
    save_scenario_to_disk(clean_name, empty_data, {})
    st.session_state["active_project_name"] = clean_name
    st.session_state["active_data"] = empty_data
    st.session_state["custom_curves"] = {}
    st.session_state["vector_couplings"] = []
    st.session_state["cached_ai_analysis"] = ""
    return clean_name


def delete_scenario_from_disk(scenario_name: str) -> bool:
    """
    Deletes a scenario JSON file from disk if it exists.
    """
    os.makedirs(SCENARIOS_DIR, exist_ok=True)
    file_path = os.path.join(SCENARIOS_DIR, f"{scenario_name}.json")
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Failed to delete scenario {scenario_name}: {e}")
    return False


def normalize_scenario_payload(raw_data: dict, scenario_name: str) -> dict:
    normalized = {
        "project_name": raw_data.get("project_name", scenario_name),
        "sic_profile": raw_data.get(
            "sic_profile",
            {
                "sic_code": "71121",
                "sector": "Professional R&D Services (Default)",
                "default_vat_type": "Standard 20%",
                "base_er_nic_rate": 0.138,
                "corp_tax_rate": 0.19,
                "supplier_credit_days": 30,
            },
        ),
        "onboarding_config": raw_data.get(
            "onboarding_config",
            {
                "business_model": "Standard Commercial Enterprise",
                "default_currency": "GBP (£)",
                "working_capital_buffer": 25000.0,
            },
        ),
        "custom_curves": raw_data.get("custom_curves", {}),
        "vector_couplings": raw_data.get("vector_couplings", []),
        "active_data": {},
    }

    raw_active = raw_data.get("active_data", {})
    if not isinstance(raw_active, dict):
        raw_active = {}

    vector_keys = ["sales", "cogs", "opex"]
    for v_key in vector_keys:
        items = raw_active.get(v_key, [])
        cleaned_items = []
        if isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    continue
                raw_mode = str(item.get("entry_mode", ENTRY_MODE_CURVE))
                if raw_mode == "Annual Baseline + Seasonality Curve":
                    raw_mode = ENTRY_MODE_CURVE
                elif raw_mode not in VALID_ENTRY_MODES:
                    raw_mode = ENTRY_MODE_CURVE

                overrides = item.get("overrides", {})
                if not isinstance(overrides, dict):
                    overrides = {}

                matrix_data = item.get("matrix_data", {})
                if not isinstance(matrix_data, dict):
                    matrix_data = {}

                if raw_mode == ENTRY_MODE_OVERRIDE and overrides:
                    y1_arr = [
                        float(overrides.get(f"M{str(m).zfill(2)}", 0.0))
                        for m in range(1, 13)
                    ]
                    matrix_data["Y1"] = y1_arr
                    y1_base = sum(y1_arr)
                else:
                    y1_base = float(item.get("y1_baseline", item.get("y1", 0.0)))

                cleaned_items.append(
                    {
                        "name": str(item.get("name", "Unnamed Vector")),
                        "entry_mode": raw_mode,
                        "y1_baseline": y1_base,
                        "y2_baseline": float(
                            item.get("y2_baseline", item.get("y2", 0.0))
                        ),
                        "y3_baseline": float(
                            item.get("y3_baseline", item.get("y3", 0.0))
                        ),
                        "flex_pct": float(item.get("flex_pct", 0.0)),
                        "vat_rate_type": str(item.get("vat_rate_type", "Standard 20%")),
                        "payment_delay": int(item.get("payment_delay", 0)),
                        "seasonality": str(item.get("seasonality", "Flat_Linear")),
                        "overrides": overrides,
                        "matrix_data": matrix_data,
                    }
                )
        normalized["active_data"][v_key] = cleaned_items

    # Payroll normalization
    cleaned_payroll = []
    for p in raw_active.get("payroll", []):
        if isinstance(p, dict):
            cleaned_payroll.append(
                {
                    "name": str(p.get("name", "Unnamed Role")),
                    "headcount": int(p.get("headcount", 1)),
                    "monthly_wage": float(p.get("monthly_wage", 0.0)),
                    "start_month": int(p.get("start_month", 1)),
                    "end_month": int(p.get("end_month", 36)),
                }
            )
    normalized["active_data"]["payroll"] = cleaned_payroll

    # Outright CapEx normalization
    cleaned_capex = []
    for cap in raw_active.get("outright_capex", []):
        if isinstance(cap, dict):
            cleaned_capex.append(
                {
                    "name": str(cap.get("name", "CapEx Asset")),
                    "amount": float(cap.get("amount", 0.0)),
                    "month": int(cap.get("month", 1)),
                    "depreciation_basis": str(
                        cap.get("depreciation_basis", "straight_line")
                    ),
                    "depreciation_rate": float(cap.get("depreciation_rate", 0.20)),
                    "term_months": int(cap.get("term_months", 60)),
                    "residual_value": float(cap.get("residual_value", 0.0)),
                }
            )
    normalized["active_data"]["outright_capex"] = cleaned_capex

    # Financed Assets normalization
    cleaned_financed = []
    for fa in raw_active.get("financed_assets", []):
        if isinstance(fa, dict):
            cleaned_financed.append(
                {
                    "name": str(fa.get("name", "Financed Asset")),
                    "amount": float(fa.get("amount", 0.0)),
                    "month": int(fa.get("month", 1)),
                    "deposit_pct": float(fa.get("deposit_pct", 10.0)),
                    "term_months": int(fa.get("term_months", 36)),
                    "interest_rate": float(fa.get("interest_rate", 5.0)),
                    "depreciation_basis": str(
                        fa.get("depreciation_basis", "straight_line")
                    ),
                    "depreciation_rate": float(fa.get("depreciation_rate", 0.15)),
                    "residual_value": float(fa.get("residual_value", 0.0)),
                }
            )
    normalized["active_data"]["financed_assets"] = cleaned_financed

    # Equity Funding normalization
    cleaned_equity = []
    for eq in raw_active.get("equity_funding", []):
        if isinstance(eq, dict):
            cleaned_equity.append(
                {
                    "source": str(
                        eq.get("source", eq.get("name", "Shareholder Equity"))
                    ),
                    "name": str(eq.get("name", eq.get("source", "Shareholder Equity"))),
                    "amount": float(eq.get("amount", 0.0)),
                    "month": int(eq.get("month", 0)),
                }
            )
    normalized["active_data"]["equity_funding"] = cleaned_equity

    return normalized


def get_saved_scenarios():
    os.makedirs(SCENARIOS_DIR, exist_ok=True)
    files = [
        f.replace(".json", "") for f in os.listdir(SCENARIOS_DIR) if f.endswith(".json")
    ]
    if not files:
        create_blank_scenario(DEFAULT_BLANK_SCENARIO)
        files = [
            f.replace(".json", "")
            for f in os.listdir(SCENARIOS_DIR)
            if f.endswith(".json")
        ]
    return sorted(files) if files else [DEFAULT_BLANK_SCENARIO]


list_available_scenarios = get_saved_scenarios


def load_scenario_from_disk(scenario_name: str):
    os.makedirs(SCENARIOS_DIR, exist_ok=True)
    file_path = os.path.join(SCENARIOS_DIR, f"{scenario_name}.json")
    if not os.path.exists(file_path):
        existing = [
            f.replace(".json", "")
            for f in os.listdir(SCENARIOS_DIR)
            if f.endswith(".json")
        ]
        if existing:
            scenario_name = sorted(existing)[0]
            file_path = os.path.join(SCENARIOS_DIR, f"{scenario_name}.json")
        else:
            scenario_name = create_blank_scenario(DEFAULT_BLANK_SCENARIO)
            file_path = os.path.join(SCENARIOS_DIR, f"{scenario_name}.json")

    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                raw_data = json.load(f)
                normalized_data = normalize_scenario_payload(raw_data, scenario_name)
                with open(file_path, "w", encoding="utf-8") as wf:
                    json.dump(normalized_data, wf, indent=4)
                return normalized_data
        except Exception as e:
            print(f"Schema migration error for {scenario_name}: {e}")
    return None


def save_scenario_to_disk(
    scenario_name: str, state_data: dict = None, custom_curves: dict = None
):
    os.makedirs(SCENARIOS_DIR, exist_ok=True)
    file_path = os.path.join(SCENARIOS_DIR, f"{scenario_name}.json")

    active_payload = state_data or st.session_state.get("active_data", {})
    raw_payload = {
        "project_name": scenario_name,
        "sic_profile": st.session_state.get("sic_profile", {}),
        "onboarding_config": st.session_state.get("onboarding_config", {}),
        "custom_curves": custom_curves or st.session_state.get("custom_curves", {}),
        "vector_couplings": st.session_state.get("vector_couplings", []),
        "active_data": active_payload,
    }

    normalized_payload = normalize_scenario_payload(raw_payload, scenario_name)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(normalized_payload, f, indent=4)
        return True
    except Exception as e:
        print(f"Failed to persist scenario: {e}")
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
            st.session_state["vector_couplings"] = loaded_data.get(
                "vector_couplings", []
            )
            st.session_state["sic_profile"] = loaded_data.get(
                "sic_profile", st.session_state.get("sic_profile", {})
            )
            st.session_state["onboarding_config"] = loaded_data.get(
                "onboarding_config", st.session_state.get("onboarding_config", {})
            )
        else:
            st.session_state["active_data"] = {}
            st.session_state["custom_curves"] = {}

        st.session_state["cached_ai_analysis"] = ""
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("##### 💾 Scenario Actions")
    new_scenario_name = st.sidebar.text_input(
        "Client / Scenario Name:", key="sidebar_new_scenario_input"
    )

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Save Current", use_container_width=True):
            if current_active:
                save_scenario_to_disk(
                    current_active,
                    st.session_state.get("active_data", {}),
                    st.session_state.get("custom_curves", {}),
                )
                st.sidebar.success(f"Saved '{current_active}'")
    with col2:
        if st.button("Clone / New", use_container_width=True):
            if new_scenario_name.strip():
                clean_name = new_scenario_name.strip().replace(" ", "_")
                base_data = st.session_state.get("active_data", {})
                base_curves = st.session_state.get("custom_curves", {})
                save_scenario_to_disk(clean_name, base_data, base_curves)
                st.session_state["active_project_name"] = clean_name
                st.session_state["active_data"] = base_data
                st.session_state["custom_curves"] = base_curves
                st.session_state["cached_ai_analysis"] = ""
                st.rerun()

    col3, col4 = st.sidebar.columns(2)
    with col3:
        if st.button("Blank Client", use_container_width=True):
            create_blank_scenario(new_scenario_name or DEFAULT_BLANK_SCENARIO)
            st.rerun()
    with col4:
        if st.button("Delete Active", use_container_width=True):
            if current_active:
                delete_scenario_from_disk(current_active)
                remaining = get_saved_scenarios()
                next_scen = remaining[0]
                st.session_state["active_project_name"] = next_scen
                loaded = load_scenario_from_disk(next_scen)
                if loaded:
                    st.session_state["active_data"] = loaded.get("active_data", {})
                    st.session_state["custom_curves"] = loaded.get("custom_curves", {})
                    st.session_state["vector_couplings"] = loaded.get(
                        "vector_couplings", []
                    )
                    st.session_state["sic_profile"] = loaded.get("sic_profile", {})
                st.session_state["cached_ai_analysis"] = ""
                st.rerun()
