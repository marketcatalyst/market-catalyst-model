# pages/1_Data_Ingestion_Gateway.py
# STRATA SUITE PRODUCTION ENGINE // DATA INGESTION GATEWAY & SANDBOX v7.3.5-PRODUCTION

import streamlit as st
import json
import os
import pandas as pd
import google.generativeai as genai
import re

# =========================================================================
# 🛡️ SECURITY INTERCEPT LAYER
# =========================================================================
if not st.session_state.get("authenticated"):
    st.warning("⚠️ **Security Intercept:** Route session token context not cleared.")
    st.page_link("home.py", label="↩️ Return to Access Gateway Portal")
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

# =========================================================================
# 🎛️ PORTAL FRONT-END USER INTERFACE CANVAS
# =========================================================================
st.set_page_config(page_title="STRATA Suite // Ingestion Gateway", layout="wide")

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
        "* **Automated Mapping:** Formulates standalone baseline target profiles for Years 1 through 5, matching active framework parameters behind the scenes."
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

# =========================================================================
# 📂 RESTORED MULTI-FORMAT FILE UPLOADER (PDF, CSV, JPEG, JPG, PNG)
# =========================================================================
st.subheader("📂 Drag and Drop Documents or Scanned Images")
uploaded_file = st.file_uploader(
    "Upload Structural Corporate Document or Image (PDF, CSV, JPEG, JPG, PNG, TXT):",
    type=["pdf", "csv", "jpeg", "jpg", "png", "txt"],
    key="gateway_document_uploader",
)

if uploaded_file is not None:
    if st.button(
        "🪄 Execute Cognitive Document Scan & Parse Vectors", use_container_width=True
    ):
        with st.spinner(
            "Processing asset layers and structural schemas via Gemini multimodal engine..."
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

                    # Handle file extraction types natively based on extension types
                    file_extension = uploaded_file.name.split(".")[-1].lower()

                    # Prepare the payload for Gemini (supporting text and multimodal image bytes)
                    if file_extension in ["jpeg", "jpg", "png", "pdf"]:
                        # Read raw binary data directly for image/multimodal processing
                        raw_bytes = uploaded_file.read()
                        mime_type = (
                            f"image/{file_extension}"
                            if file_extension != "pdf"
                            else "application/pdf"
                        )
                        file_payload = [{"mime_type": mime_type, "data": raw_bytes}]
                    else:
                        # Handle text/csv formats gracefully via string decode channels
                        file_content = uploaded_file.read().decode(
                            "utf-8", errors="ignore"
                        )
                        file_payload = [file_content]

                    # 🚀 SECURE 5-YEAR & MONTH 00 BALANCING SCHEMA INSTRUCTIONS
                    prompt = f"""
                    You are a professional corporate accounting data extraction engine. Process the attached business data, invoice, statement, image or opening trial balance ledger.
                    
                    CRITICAL DIRECTIONS:
                    1. If the document represents an opening Trial Balance, setup expenditure, or pre-launch capital infusion meant for Month '00' initialization, you must explicitly assign the starting values to Year 1 ('y1') and flag that it belongs to month index 0.
                    2. Extract historical baselines or forward projection vectors out to 5 full operating years.
                    
                    Return a valid JSON object matching this schema exactly:
                    {{
                        "type": "sales" or "opex" or "equity_funding" or "outright_capex",
                        "name": "Line item identifier name description",
                        "y1": float_value,
                        "y2": float_value,
                        "y3": float_value,
                        "y4": float_value,
                        "y5": float_value,
                        "target_month_index": 0 or 1,
                        "seasonality": "Flat_Linear" or "Winter_Peak" or "Summer_Peak"
                    }}
                    """

                    # Utilize the standard multimodal text/image model context channel
                    model = genai.GenerativeModel("gemini-1.5-flash")
                    response = model.generate_content([prompt] + file_payload)

                    json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group(0))

                        st.session_state["scratchpad_queue"].append(
                            {
                                "type": parsed.get("type", "opex"),
                                "name": f"[AI Scan] {parsed.get('name')}",
                                "y1": float(parsed.get("y1", 0.0)),
                                "y2": float(parsed.get("y2", 0.0)),
                                "y3": float(parsed.get("y3", 0.0)),
                                "y4": float(parsed.get("y4", 0.0)),
                                "y5": float(parsed.get("y5", 0.0)),
                                "target_month_index": int(
                                    parsed.get("target_month_index", 1)
                                ),
                                "seasonality": parsed.get("seasonality", "Flat_Linear"),
                            }
                        )
                        st.toast(
                            "Document parsed successfully and held in temporary sandbox queue!"
                        )
                        st.rerun()
                    else:
                        st.error(
                            "AI engine returned unparseable text structuring. Try uploading a cleaner text format."
                        )
            except Exception as e:
                st.error(f"Cognitive Pipeline Exception Encountered: {str(e)}")

# =========================================================================
# 📝 THE COGNITIVE SCRATCHPAD REVIEW INTERFACE
# =========================================================================
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
            options=["sales", "opex", "equity_funding", "outright_capex"],
            width="small",
        ),
        "name": st.column_config.TextColumn("Line Item Identifier", width="large"),
        "y1": st.column_config.NumberColumn("Year 1 Base (£)", format="£%,.2f"),
        "y2": st.column_config.NumberColumn("Year 2 Base (£)", format="£%,.2f"),
        "y3": st.column_config.NumberColumn("Year 3 Base (£)", format="£%,.2f"),
        "y4": st.column_config.NumberColumn("Year 4 Base (£)", format="£%,.2f"),
        "y5": st.column_config.NumberColumn("Year 5 Base (£)", format="£%,.2f"),
        "target_month_index": st.column_config.NumberColumn(
            "Target Month Index (e.g. 0 for Opening Balance)", format="%d"
        ),
        "seasonality": st.column_config.SelectboxColumn(
            "Timeline Seasonal Curve",
            options=["Flat_Linear", "Winter_Peak", "Summer_Peak"],
            width="medium",
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
            # Ensure workspace data keys are initialized cleanly
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

                # Dynamic structural translation dictionary logic routing
                if bucket == "equity_funding":
                    st.session_state["active_data"]["equity_funding"].append(
                        {
                            "name": str(r["name"]),
                            "amount": float(r["y1"]),
                            "month": int(r["target_month_index"]),
                        }
                    )
                elif bucket == "outright_capex":
                    st.session_state["active_data"]["outright_capex"].append(
                        {
                            "name": str(r["name"]),
                            "amount": float(r["y1"]),
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
                            "y1_baseline": float(r["y1"]),
                            "y2_baseline": float(r["y2"]),
                            "y3_baseline": float(r["y3"]),
                            "y4_baseline": float(r["y4"]),
                            "y5_baseline": float(r["y5"]),
                            "seasonality": str(r["seasonality"]),
                            "vat_rate_type": active_sic.get(
                                "default_vat_type", "Standard 20%"
                            ),
                            "payment_delay": 0,
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
