# utils/scenario_manager.py
# STRATA SUITE SCENARIO MANAGEMENT & SCHEMA MIGRATION ENGINE // SSOT IMMUTABLE CONTRACT

import os
import json
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENARIOS_DIR = os.path.join(PROJECT_ROOT, "saved_scenarios")


def generate_standard_scenarios():
    """
    Programmatically generates and writes the 4 core canonical STRATA scenarios
    to disk with exact WinForecast monthly start-up arrays and robust delta-derived variants.
    """
    os.makedirs(SCENARIOS_DIR, exist_ok=True)

    mature_sales_curve = [
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083337,
    ]
    mature_cost_curve = [
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083333,
        0.083337,
    ]

    # Exact Year 1 monthly start-up arrays extracted from WinForecast PDF
    y1_court_fees = [
        0.0,
        6500.0,
        8125.0,
        8125.0,
        8125.0,
        8125.0,
        38220.0,
        40950.0,
        38220.0,
        42316.0,
        39586.0,
        42316.0,
    ]
    y1_events = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1500.0,
        1500.0,
        2500.0,
        2500.0,
        3500.0,
    ]
    y1_food_sales = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        8333.0,
        8333.0,
        12083.0,
        12917.0,
        12917.0,
    ]

    y1_padel_staff = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        15417.0,
        15416.0,
        15417.0,
        15417.0,
        15416.0,
        15417.0,
    ]
    y1_food_purchases = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        3333.0,
        3333.0,
        4834.0,
        5166.0,
        5167.0,
        0.0,
    ]
    y1_canteen_staff = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        2203.0,
        2203.0,
        4406.0,
        4406.0,
        4406.0,
    ]

    y1_maint = [
        1167.0,
        1166.0,
        1167.0,
        1167.0,
        1166.0,
        1167.0,
        1167.0,
        1166.0,
        1167.0,
        1167.0,
        1166.0,
        1167.0,
    ]
    y1_mktg = [
        0.0,
        0.0,
        0.0,
        0.0,
        2500.0,
        2500.0,
        2500.0,
        2500.0,
        2500.0,
        2500.0,
        2500.0,
        2500.0,
    ]
    y1_soft = [
        0.0,
        0.0,
        0.0,
        0.0,
        1000.0,
        1000.0,
        1000.0,
        1000.0,
        1000.0,
        1000.0,
        1000.0,
        1000.0,
    ]
    y1_admin = [
        0.0,
        0.0,
        0.0,
        0.0,
        1834.0,
        1833.0,
        1833.0,
        1834.0,
        1833.0,
        1833.0,
        1834.0,
        1833.0,
    ]
    y1_rent = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        4167.0,
        4167.0,
        4167.0,
        4167.0,
        4167.0,
        4167.0,
    ]
    y1_util = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        5833.0,
        5834.0,
        5833.0,
        5833.0,
        5834.0,
        5833.0,
    ]
    y1_ins = [
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1833.0,
        1834.0,
        1833.0,
        1833.0,
        1834.0,
        1833.0,
    ]

    base_sales = [
        {
            "name": "[AI Scan] Court Fees",
            "entry_mode": "Manual Monthly Override",
            "y1_baseline": sum(y1_court_fees),
            "y2_baseline": 529200.0,
            "y3_baseline": 586854.0,
            "seasonality": "Curve_court_fees",
            "vat_rate_type": "Standard 20%",
            "payment_delay": 0,
            "overrides": {
                f"M{str(i+1).zfill(2)}": val for i, val in enumerate(y1_court_fees)
            },
            "matrix_data": {
                "Y1": y1_court_fees,
                "Y2": [529200.0 / 12] * 12,
                "Y3": [586854.0 / 12] * 12,
            },
        },
        {
            "name": "[AI Scan] Events & Room Hire",
            "entry_mode": "Manual Monthly Override",
            "y1_baseline": sum(y1_events),
            "y2_baseline": 42000.0,
            "y3_baseline": 43470.0,
            "seasonality": "Curve_events_and_room_hire",
            "vat_rate_type": "Standard 20%",
            "payment_delay": 0,
            "overrides": {
                f"M{str(i+1).zfill(2)}": val for i, val in enumerate(y1_events)
            },
            "matrix_data": {
                "Y1": y1_events,
                "Y2": [42000.0 / 12] * 12,
                "Y3": [43470.0 / 12] * 12,
            },
        },
        {
            "name": "[AI Scan] Food and Drink Sales",
            "entry_mode": "Manual Monthly Override",
            "y1_baseline": sum(y1_food_sales),
            "y2_baseline": 155836.0,
            "y3_baseline": 129863.0,
            "seasonality": "Curve_food_and_drink_sales",
            "vat_rate_type": "Standard 20%",
            "payment_delay": 0,
            "overrides": {
                f"M{str(i+1).zfill(2)}": val for i, val in enumerate(y1_food_sales)
            },
            "matrix_data": {
                "Y1": y1_food_sales,
                "Y2": [155836.0 / 12] * 12,
                "Y3": [129863.0 / 12] * 12,
            },
        },
    ]

    base_cogs = [
        {
            "name": "[AI Scan] Padel Court Staff",
            "entry_mode": "Manual Monthly Override",
            "y1_baseline": sum(y1_padel_staff),
            "y2_baseline": 185000.0,
            "y3_baseline": 191475.0,
            "seasonality": "Curve_padel_court_staff",
            "vat_rate_type": "Standard 20%",
            "payment_delay": 0,
            "overrides": {
                f"M{str(i+1).zfill(2)}": val for i, val in enumerate(y1_padel_staff)
            },
            "matrix_data": {
                "Y1": y1_padel_staff,
                "Y2": [185000.0 / 12] * 12,
                "Y3": [191475.0 / 12] * 12,
            },
        },
        {
            "name": "[AI Scan] Food & Drink Purchases",
            "entry_mode": "Manual Monthly Override",
            "y1_baseline": sum(y1_food_purchases),
            "y2_baseline": 62335.0,
            "y3_baseline": 51945.0,
            "seasonality": "Curve_food_and_drink_purchases",
            "vat_rate_type": "Standard 20%",
            "payment_delay": 0,
            "overrides": {
                f"M{str(i+1).zfill(2)}": val for i, val in enumerate(y1_food_purchases)
            },
            "matrix_data": {
                "Y1": y1_food_purchases,
                "Y2": [62335.0 / 12] * 12,
                "Y3": [51945.0 / 12] * 12,
            },
        },
        {
            "name": "[AI Scan] Canteen Staff",
            "entry_mode": "Manual Monthly Override",
            "y1_baseline": sum(y1_canteen_staff),
            "y2_baseline": 52872.0,
            "y3_baseline": 54723.0,
            "seasonality": "Curve_canteen_staff",
            "vat_rate_type": "Standard 20%",
            "payment_delay": 0,
            "overrides": {
                f"M{str(i+1).zfill(2)}": val for i, val in enumerate(y1_canteen_staff)
            },
            "matrix_data": {
                "Y1": y1_canteen_staff,
                "Y2": [52872.0 / 12] * 12,
                "Y3": [54723.0 / 12] * 12,
            },
        },
    ]

    base_opex = [
        {
            "name": "[AI Scan] Rent",
            "entry_mode": "Manual Monthly Override",
            "y1_baseline": sum(y1_rent),
            "y2_baseline": 50004.0,
            "y3_baseline": 50004.0,
            "vat_rate_type": "Standard 20%",
            "seasonality": "Curve_rent",
            "overrides": {
                f"M{str(i+1).zfill(2)}": val for i, val in enumerate(y1_rent)
            },
            "matrix_data": {
                "Y1": y1_rent,
                "Y2": [50004.0 / 12] * 12,
                "Y3": [50004.0 / 12] * 12,
            },
        },
        {
            "name": "[AI Scan] Utility Costs",
            "entry_mode": "Manual Monthly Override",
            "y1_baseline": sum(y1_util),
            "y2_baseline": 70000.0,
            "y3_baseline": 72036.0,
            "vat_rate_type": "Standard 20%",
            "seasonality": "Curve_utility_costs",
            "overrides": {
                f"M{str(i+1).zfill(2)}": val for i, val in enumerate(y1_util)
            },
            "matrix_data": {
                "Y1": y1_util,
                "Y2": [70000.0 / 12] * 12,
                "Y3": [72036.0 / 12] * 12,
            },
        },
        {
            "name": "[AI Scan] Insurances",
            "entry_mode": "Manual Monthly Override",
            "y1_baseline": sum(y1_ins),
            "y2_baseline": 22000.0,
            "y3_baseline": 22770.0,
            "vat_rate_type": "Standard 20%",
            "seasonality": "Curve_insurances",
            "overrides": {f"M{str(i+1).zfill(2)}": val for i, val in enumerate(y1_ins)},
            "matrix_data": {
                "Y1": y1_ins,
                "Y2": [22000.0 / 12] * 12,
                "Y3": [22770.0 / 12] * 12,
            },
        },
        {
            "name": "[AI Scan] Maintenance Costs",
            "entry_mode": "Manual Monthly Override",
            "y1_baseline": sum(y1_maint),
            "y2_baseline": 28000.0,
            "y3_baseline": 28980.0,
            "vat_rate_type": "Standard 20%",
            "seasonality": "Curve_maintenance_costs",
            "overrides": {
                f"M{str(i+1).zfill(2)}": val for i, val in enumerate(y1_maint)
            },
            "matrix_data": {
                "Y1": y1_maint,
                "Y2": [28000.0 / 12] * 12,
                "Y3": [28980.0 / 12] * 12,
            },
        },
        {
            "name": "[AI Scan] Marketing Costs",
            "entry_mode": "Manual Monthly Override",
            "y1_baseline": sum(y1_mktg),
            "y2_baseline": 30000.0,
            "y3_baseline": 31050.0,
            "vat_rate_type": "Standard 20%",
            "seasonality": "Curve_marketing_costs",
            "overrides": {
                f"M{str(i+1).zfill(2)}": val for i, val in enumerate(y1_mktg)
            },
            "matrix_data": {
                "Y1": y1_mktg,
                "Y2": [30000.0 / 12] * 12,
                "Y3": [31050.0 / 12] * 12,
            },
        },
        {
            "name": "[AI Scan] Software & Booking System",
            "entry_mode": "Manual Monthly Override",
            "y1_baseline": sum(y1_soft),
            "y2_baseline": 12000.0,
            "y3_baseline": 12420.0,
            "vat_rate_type": "Standard 20%",
            "seasonality": "Curve_software_and_booking_system",
            "overrides": {
                f"M{str(i+1).zfill(2)}": val for i, val in enumerate(y1_soft)
            },
            "matrix_data": {
                "Y1": y1_soft,
                "Y2": [12000.0 / 12] * 12,
                "Y3": [12420.0 / 12] * 12,
            },
        },
        {
            "name": "[AI Scan] Administration & Supplies",
            "entry_mode": "Manual Monthly Override",
            "y1_baseline": sum(y1_admin),
            "y2_baseline": 21996.0,
            "y3_baseline": 22766.0,
            "vat_rate_type": "Standard 20%",
            "seasonality": "Curve_administration_and_supplies",
            "overrides": {
                f"M{str(i+1).zfill(2)}": val for i, val in enumerate(y1_admin)
            },
            "matrix_data": {
                "Y1": y1_admin,
                "Y2": [21996.0 / 12] * 12,
                "Y3": [22766.0 / 12] * 12,
            },
        },
    ]

    custom_curves = {
        "Curve_court_fees": mature_sales_curve,
        "Curve_events_and_room_hire": mature_sales_curve,
        "Curve_food_and_drink_sales": mature_sales_curve,
        "Curve_padel_court_staff": mature_cost_curve,
        "Curve_food_and_drink_purchases": mature_cost_curve,
        "Curve_canteen_staff": mature_cost_curve,
        "Curve_rent": mature_cost_curve,
        "Curve_utility_costs": mature_cost_curve,
        "Curve_insurances": mature_cost_curve,
        "Curve_maintenance_costs": mature_cost_curve,
        "Curve_marketing_costs": mature_cost_curve,
        "Curve_software_and_booking_system": mature_cost_curve,
        "Curve_administration_and_supplies": mature_cost_curve,
    }

    # Scenario 0: Padel_Centre_Baseline
    s0_data = {
        "sales": base_sales,
        "cogs": base_cogs,
        "opex": base_opex,
        "payroll": [],
        "financed_assets": [],
        "outright_capex": [],
        "equity_funding": [],
    }
    save_scenario_to_disk("Padel_Centre_Baseline", s0_data, custom_curves)

    # Scenario 1: DBW_Mild_Downside (Derived via deep clone delta)
    s1_sales = []
    for item in base_sales:
        copied_item = json.loads(json.dumps(item))
        if "[AI Scan] Court Fees" in copied_item["name"]:
            copied_item["y1_baseline"] *= 0.8
            copied_item["y2_baseline"] *= 0.8
            copied_item["y3_baseline"] *= 0.8
            if "matrix_data" in copied_item:
                for yr in copied_item["matrix_data"]:
                    copied_item["matrix_data"][yr] = [
                        val * 0.8 for val in copied_item["matrix_data"][yr]
                    ]
            if "overrides" in copied_item:
                copied_item["overrides"] = {
                    k: v * 0.8 for k, v in copied_item["overrides"].items()
                }
        elif "[AI Scan] Events & Room Hire" in copied_item["name"]:
            copied_item["y1_baseline"] = 0.0
            copied_item["y2_baseline"] *= 0.5
            if "matrix_data" in copied_item:
                if "Y1" in copied_item["matrix_data"]:
                    copied_item["matrix_data"]["Y1"] = [0.0] * 12
                if "Y2" in copied_item["matrix_data"]:
                    copied_item["matrix_data"]["Y2"] = [
                        val * 0.5 for val in copied_item["matrix_data"]["Y2"]
                    ]
            if "overrides" in copied_item:
                copied_item["overrides"] = {k: 0.0 for k in copied_item["overrides"]}
        s1_sales.append(copied_item)

    s1_data = {
        "sales": s1_sales,
        "cogs": base_cogs,
        "opex": base_opex,
        "payroll": [],
        "financed_assets": [],
        "outright_capex": [],
        "equity_funding": [],
    }
    save_scenario_to_disk("DBW_Mild_Downside", s1_data, custom_curves)

    # Scenario 2: DBW_Moderate_Downside (Derived via deep clone delta)
    s2_cogs = []
    for item in base_cogs:
        copied_item = json.loads(json.dumps(item))
        if "Staff" in copied_item["name"]:
            copied_item["y1_baseline"] *= 1.1
            copied_item["y2_baseline"] *= 1.1
            copied_item["y3_baseline"] *= 1.1
            if "matrix_data" in copied_item:
                for yr in copied_item["matrix_data"]:
                    copied_item["matrix_data"][yr] = [
                        val * 1.1 for val in copied_item["matrix_data"][yr]
                    ]
            if "overrides" in copied_item:
                copied_item["overrides"] = {
                    k: v * 1.1 for k, v in copied_item["overrides"].items()
                }
        s2_cogs.append(copied_item)

    s2_data = {
        "sales": base_sales,
        "cogs": s2_cogs,
        "opex": base_opex,
        "payroll": [],
        "financed_assets": [],
        "outright_capex": [],
        "equity_funding": [],
    }
    save_scenario_to_disk("DBW_Moderate_Downside", s2_data, custom_curves)

    # Scenario 3: DBW_Severe_Stress (Combined S1 sales + S2 cogs)
    s3_data = {
        "sales": s1_sales,
        "cogs": s2_cogs,
        "opex": base_opex,
        "payroll": [],
        "financed_assets": [],
        "outright_capex": [],
        "equity_funding": [],
    }
    save_scenario_to_disk("DBW_Severe_Stress", s3_data, custom_curves)


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
        "custom_curves": raw_data.get("custom_curves", {}),
        "vector_couplings": raw_data.get("vector_couplings", []),
        "active_data": {},
    }

    raw_active = raw_data.get("active_data", {})
    if not isinstance(raw_active, dict):
        raw_active = {}

    list_keys = [
        "sales",
        "cogs",
        "opex",
        "payroll",
        "financed_assets",
        "outright_capex",
        "equity_funding",
    ]

    for l_key in list_keys:
        items = raw_active.get(l_key, [])
        cleaned_items = []
        if isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    continue
                clean_item = {
                    "name": str(item.get("name", "Unnamed Vector")),
                    "entry_mode": str(
                        item.get(
                            "entry_mode", "Annual Baseline + Monthly Distribution Curve"
                        )
                    ),
                    "y1_baseline": float(item.get("y1_baseline", item.get("y1", 0.0))),
                    "y2_baseline": float(item.get("y2_baseline", item.get("y2", 0.0))),
                    "y3_baseline": float(item.get("y3_baseline", item.get("y3", 0.0))),
                    "vat_rate_type": str(item.get("vat_rate_type", "Standard 20%")),
                    "payment_delay": int(item.get("payment_delay", 0)),
                    "seasonality": str(item.get("seasonality", "Flat_Linear")),
                    "overrides": item.get("overrides", {}),
                    "matrix_data": item.get("matrix_data", {}),
                }
                if not isinstance(clean_item["overrides"], dict):
                    clean_item["overrides"] = {}
                cleaned_items.append(clean_item)
        normalized["active_data"][l_key] = cleaned_items

    return normalized


def get_saved_scenarios():
    os.makedirs(SCENARIOS_DIR, exist_ok=True)
    files = [
        f.replace(".json", "") for f in os.listdir(SCENARIOS_DIR) if f.endswith(".json")
    ]
    if not files:
        generate_standard_scenarios()
        files = [
            f.replace(".json", "")
            for f in os.listdir(SCENARIOS_DIR)
            if f.endswith(".json")
        ]
    return sorted(files) if files else ["Padel_Centre_Baseline"]


list_available_scenarios = get_saved_scenarios


def load_scenario_from_disk(scenario_name: str):
    os.makedirs(SCENARIOS_DIR, exist_ok=True)
    file_path = os.path.join(SCENARIOS_DIR, f"{scenario_name}.json")
    if not os.path.exists(file_path):
        generate_standard_scenarios()

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
    for category, items in active_payload.items():
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    for k in [
                        "y1_baseline",
                        "y2_baseline",
                        "y3_baseline",
                        "monthly_wage",
                        "amount",
                        "headcount",
                    ]:
                        if k in item:
                            try:
                                item[k] = (
                                    float(item[k]) if k != "headcount" else int(item[k])
                                )
                            except (ValueError, TypeError):
                                pass

    raw_payload = {
        "project_name": scenario_name,
        "sic_profile": st.session_state.get("sic_profile", {}),
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
        else:
            st.session_state["active_data"] = {}
            st.session_state["custom_curves"] = {}

        st.session_state["cached_ai_analysis"] = ""
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.markdown("##### 💾 Scenario Actions")
    new_scenario_name = st.sidebar.text_input(
        "New Scenario Name:", key="sidebar_new_scenario_input"
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
        if st.button("Create New", use_container_width=True):
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
