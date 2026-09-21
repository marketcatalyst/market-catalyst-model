# pyright: reportMissingImports=false
# pages/1_Data_Ingestion_Gateway.py
# STRATA SUITE PRODUCTION ENGINE // DATA INGESTION GATEWAY & SANDBOX v7.4.2-PRODUCTION

import os
import sys
import json
import pandas as pd
import google.generativeai as genai
import re
import streamlit as st

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.scenario_manager import render_global_scenario_sidebar

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

active_sic = st.session_state.get(
    "sic_profile",
    {
        "sic_code": "71121",
        "sector": "Professional R&D Services (Default)",
        "default_vat_type": "Standard 20%",
        "base_er_nic_rate": 0.138,
    },
)

st.title("📥 Unstructured Data Ingestion Gateway")
st.markdown(
    f"🏭 **Active Industry Configuration:** Mapped to Code `{active_sic['sic_code']}` ({active_sic['sector']}) | "
    f"Default Tax Rule: `{active_sic.get('default_vat_type', 'Standard 20%')}`"
)
st.caption(
    "🛡️ Secure Sandbox Workspace // Data processed here is isolated inside volatile browser memory caches."
)
st.markdown("---")

col_info1, col_info2 = st.columns([7, 5])

with col_info1:
    st.markdown("### 💡 Ingestion Playbook & System Capabilities")
    st.markdown(
        "* **Multi-Format Scanning:** Drop raw transaction metrics, text-based PDFs, spreadsheets, or scanned image receipts (`JPEG`, `JPG`, `PNG`) safely.\n"
        "* **Month 00 Initialization:** Automatically isolates opening Trial Balance entries, capital injections, and setup costs specifically allocated to Month '00' preparation hooks.\n"
        "* **Automated Mapping:** Formulates standalone baseline target profiles for Years 1 through 3, matching active framework parameters behind the scenes."
    )

with col_info2:
    st.markdown("### 🔒 Data Sovereignty & Sandbox Safety")
    st.info(
        "🧠 **Isolated Memory Safeguard:** This page acts strictly as a temporary scratchpad. "
        "No uploaded files or AI interpretations are written to your permanent database project files. "
        "You have total control to review, edit, or delete items before officially pushing them into the workspace."
    )

st.markdown("---")

if "scratchpad_queue" not in st.session_state:
    st.session_state["scratchpad_queue"] = []

st.subheader("📂 Drag and Drop Documents or Scanned Images")
uploaded_file = st.file_uploader(
    "Upload Structural Corporate Document or Image (PDF, CSV, JPEG, JPG, PNG, TXT):",
    type=["pdf", "csv", "jpeg", "jpg", "png", "txt"],
    key="gateway_document_uploader",
)


def extract_clean_json(text: str):
    clean_text = text.strip()
    if clean_text.startswith("```"):
        clean_text = re.sub(r"^```(?:json)?\s*", "", clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r"\s*```$", "", clean_text)

    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        pass

    array_match = re.search(r"(\[.*\])", clean_text, re.DOTALL)
    if array_match:
        try:
            return json.loads(array_match.group(1))
        except json.JSONDecodeError:
            pass

    obj_match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
    if obj_match:
        return json.loads(obj_match.group(1))

    raise ValueError("No valid JSON structure found in cognitive payload.")


if uploaded_file is not None:
    if st.button(
        "🪄 Execute Cognitive Document Scan & Parse Vectors", use_container_width=True
    ):
        with st.spinner(
            "Processing document layers and structural schemas via Gemini multimodal engine..."
        ):
            try:
                g_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get(
                    "GEMINI_API_KEY", ""
                )
                if not g_key:
                    st.error(
                        "Missing Gemini API Key configuration token in environment secrets."
                    )
                else:
                    genai.configure(api_key=g_key)
                    file_extension = uploaded_file.name.split(".")[-1].lower()

                    if file_extension in ["jpeg", "jpg", "png", "pdf"]:
                        raw_bytes = uploaded_file.read()
                        mime_type = (
                            f"image/{file_extension}"
                            if file_extension != "pdf"
                            else "application/pdf"
                        )
                        file_payload = [{"mime_type": mime_type, "data": raw_bytes}]
                    else:
                        file_content = uploaded_file.read().decode(
                            "utf-8", errors="ignore"
                        )
                        file_payload = [file_content]

                    prompt = f"""
                    You are a professional corporate accounting data extraction engine. Process the attached business data, financial forecast, statement, image or opening trial balance ledger.
                    
                    CRITICAL DIRECTIONS:
                    1. Extract ALL primary income statement, direct cost, overhead, capex, and equity line items present in the document.
                    2. If the document represents an opening Trial Balance, setup expenditure, or pre-launch capital infusion meant for Month '00' initialization, explicitly assign starting values to Year 1 ('y1_baseline') and set target_month_index to 0.
                    3. Extract historical baselines or annual totals for up to 3 operating years ('y1_baseline', 'y2_baseline', 'y3_baseline'). If multi-year data is not provided, populate 'y1_baseline' with the annual total or run-rate and set y2..y3 to 0.0.
                    4. Valid 'type' values are strictly: "sales", "cogs", "opex", "equity_funding", or "outright_capex".
                    
                    Return a valid JSON ARRAY of objects matching this schema exactly:
                    [
                      {{
                        "type": "sales" or "cogs" or "opex" or "equity_funding" or "outright_capex",
                        "name": "Line item identifier name description",
                        "y1_baseline": float_value,
                        "y2_baseline": float_value,
                        "y3_baseline": float_value,
                        "target_month_index": 0 or 1,
                        "seasonality": "Flat_Linear" or "Winter_Peak" or "Summer_Peak",
                        "enable_seasonality": false
                      }}
                    ]
                    """

                    model = genai.GenerativeModel(
                        model_name="gemini-2.5-flash",
                        generation_config={"response_mime_type": "application/json"},
                    )
                    response = model.generate_content([prompt] + file_payload)
                    parsed_result = extract_clean_json(response.text)

                    items_to_process = (
                        [parsed_result]
                        if isinstance(parsed_result, dict)
                        else (parsed_result if isinstance(parsed_result, list) else [])
                    )

                    count_added = 0
                    for item in items_to_process:
                        if isinstance(item, dict) and "name" in item:
                            st.session_state["scratchpad_queue"].append(
                                {
                                    "type": item.get("type", "opex"),
                                    "name": f"[AI Scan] {item.get('name')}",
                                    "y1_baseline": float(
                                        item.get("y1_baseline", item.get("y1", 0.0))
                                    ),
                                    "y2_baseline": float(
                                        item.get("y2_baseline", item.get("y2", 0.0))
                                    ),
                                    "y3_baseline": float(
                                        item.get("y3_baseline", item.get("y3", 0.0))
                                    ),
                                    "target_month_index": int(
                                        item.get("target_month_index", 1)
                                    ),
                                    "seasonality": item.get(
                                        "seasonality", "Flat_Linear"
                                    ),
                                    "enable_seasonality": bool(
                                        item.get("enable_seasonality", False)
                                    ),
                                }
                            )
                            count_added += 1

                    if count_added > 0:
                        st.toast(
                            f"Successfully parsed {count_added} line items into sandbox queue!"
                        )
                        st.rerun()
                    else:
                        st.warning(
                            "AI scan completed but no structured line items were extracted."
                        )

            except Exception as e:
                st.error(f"Cognitive Pipeline Exception Encountered: {str(e)}")

if st.session_state["scratchpad_queue"]:
    st.markdown("---")
    st.subheader("📝 Sandbox Scratchpad Queue (Review & Verify Items)")
    st.caption(
        "Review the AI outputs below. You can change types, specify Month 0 allocations, or adjust targets before pushing to production."
    )

    df_scratch = pd.DataFrame(st.session_state["scratchpad_queue"])

    cfg = {
        "type": st.column_config.SelectboxColumn(
            "Classification Bucket",
            options=["sales", "cogs", "opex", "equity_funding", "outright_capex"],
            width="small",
        ),
        "name": st.column_config.TextColumn("Line Item Identifier", width="large"),
        "y1_baseline": st.column_config.NumberColumn(
            "Year 1 Base (£)", format="£%,.2f"
        ),
        "y2_baseline": st.column_config.NumberColumn(
            "Year 2 Base (£)", format="£%,.2f"
        ),
        "y3_baseline": st.column_config.NumberColumn(
            "Year 3 Base (£)", format="£%,.2f"
        ),
        "target_month_index": st.column_config.NumberColumn(
            "Target Month Index (0 for Opening)", format="%d"
        ),
        "seasonality": st.column_config.SelectboxColumn(
            "Timeline Seasonal Curve",
            options=["Flat_Linear", "Winter_Peak", "Summer_Peak"],
            width="medium",
        ),
        "enable_seasonality": st.column_config.CheckboxColumn(
            "Enable Seasonality Toggle", default=False
        ),
    }

    edited_grid = st.data_editor(
        df_scratch,
        column_config=cfg,
        use_container_width=True,
        num_rows="dynamic",
        key="sandbox_scratchpad_editor",
    )

    col_actions1, col_actions2 = st.columns([6, 6])

    with col_actions1:
        if st.button("❌ Purge Scratchpad Queue", use_container_width=True):
            st.session_state["scratchpad_queue"] = []
            st.toast("Scratchpad cleared!")
            st.rerun()

    with col_actions2:
        if st.button(
            "🚀 Authorize & Commit Staged Vectors to Command Center",
            use_container_width=True,
        ):
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

            for _, r in edited_grid.iterrows():
                bucket = str(r["type"])
                if bucket not in st.session_state["active_data"]:
                    st.session_state["active_data"][bucket] = []

                if bucket == "equity_funding":
                    st.session_state["active_data"]["equity_funding"].append(
                        {
                            "name": str(r["name"]),
                            "amount": float(r["y1_baseline"]),
                            "month": int(r["target_month_index"]),
                        }
                    )
                elif bucket == "outright_capex":
                    st.session_state["active_data"]["outright_capex"].append(
                        {
                            "name": str(r["name"]),
                            "amount": float(r["y1_baseline"]),
                            "month": (
                                int(r["target_month_index"])
                                if int(r["target_month_index"]) > 0
                                else 1
                            ),
                            "depreciation_rate": 0.20,
                        }
                    )
                else:
                    st.session_state["active_data"][bucket].append(
                        {
                            "name": str(r["name"]),
                            "y1_baseline": float(r["y1_baseline"]),
                            "y2_baseline": float(r["y2_baseline"]),
                            "y3_baseline": float(r["y3_baseline"]),
                            "seasonality": str(r["seasonality"]),
                            "enable_seasonality": bool(r["enable_seasonality"]),
                            "vat_rate_type": active_sic.get(
                                "default_vat_type", "Standard 20%"
                            ),
                            "payment_delay": 0,
                            "flex_pct": 0.0,
                            "overrides": {},
                        }
                    )

            st.session_state["scratchpad_queue"] = []
            st.success(
                "Vectors authorized and securely linked! Redirecting to Core Workspace..."
            )
            st.switch_page("pages/app.py")

st.markdown("---")
st.page_link(
    "pages/app.py", label="↩️ Skip Ingestion & Open Corporate Command Center Directly"
)

st.sidebar.markdown("### Compass Options")
st.sidebar.page_link("home.py", label="🏠 Home Portal")
st.sidebar.page_link(
    "pages/1_Data_Ingestion_Gateway.py", label="📥 Data Ingestion Gateway"
)
st.sidebar.page_link("pages/onboarding.py", label="🕸️ Data Input Parameters")
st.sidebar.page_link("pages/app.py", label="✍️ Data Entry Panel")
st.sidebar.page_link("pages/reports.py", label="📊 Performance Tab")

render_global_scenario_sidebar()
