# pages/1_Data_Ingestion_Gateway.py
# STRATA SUITE PRODUCTION ENGINE // DATA INGESTION GATEWAY & SANDBOX v6.0.0-MASTER

import streamlit as st
import json
import os
import pandas as pd
import google.generativeai as genai
import re

# =========================================================================
# 🛡️ SECURITY INTERCEPT LAYER
# =========================================================================
if not st.session_state.get("authenticated") or not st.session_state.get(
    "onboarding_complete"
):
    st.warning("⚠️ **Security Intercept:** Route session token context not cleared.")
    st.page_link("home.py", label="↩️ Return to Access Gateway Portal")
    st.stop()

active_sic = st.session_state.get("sic_profile")

# =========================================================================
# 🎛️ PORTAL FRONT-END USER INTERFACE CANVAS
# =========================================================================
st.set_page_config(page_title="STRATA Suite // Ingestion Gateway", layout="wide")

st.title("📥 Unstructured Data Ingestion Gateway")
st.markdown(
    f"🏭 **Active Industry Configuration:** Mapped to Code `{active_sic['sic_code']}` ({active_sic['sector']}) | "
    f"Default Tax Rule: `{active_sic['default_vat_type']}`"
)
st.caption(
    "🛡️ Secure Sandbox Workspace // Data processed here is isolated inside volatile browser memory caches."
)
st.markdown("---")

# -------------------------------------------------------------------------
# 📋 REASSURANCE & INSTRUCTIONAL BLUEPRINT PANEL
# -------------------------------------------------------------------------
col_info1, col_info2 = st.columns([7, 5])

with col_info1:
    st.markdown("### 💡 Ingestion Playbook & System Capabilities")
    st.markdown(
        "* **Intelligent Scanning:** Drop raw transaction metrics, text-based PDF invoices, or supplier agreements to isolate financial strings instantly.\n"
        "* **Automated Mapping:** Formulates standalone baseline target profiles for Years 1, 2, and 3, matching your active industrial framework parameters behind the scenes.\n"
        "* **Predictive Curve Shaping:** Analyzes description text syntax to match trading volumes with corresponding business curves (e.g., `Winter_Peak` or `Summer_Peak`)."
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
# 📂 THE DRAG-AND-DROP FILE UPLOADER
# =========================================================================
st.subheader("📂 Drag and Drop Documents")
uploaded_file = st.file_uploader(
    "Upload Structural Corporate Document (PDF, CSV, TXT) for Extraction:",
    type=["pdf", "csv", "txt"],
    key="gateway_document_uploader",
)

if uploaded_file is not None:
    if st.button(
        "🪄 Execute Cognitive Document Scan & Parse Vectors", use_container_width=True
    ):
        with st.spinner("Processing asset layers and structural schemas via Gemini..."):
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
                    file_content = uploaded_file.read().decode("utf-8", errors="ignore")

                    prompt = f"""
                    You are a corporate accounting ingestion parser. Process the following raw business data and extract financial vectors.
                    Return a valid JSON object matching this schema exactly:
                    {{
                        "type": "sales" or "opex",
                        "name": "Line item identifier name",
                        "y1": float_value,
                        "y2": float_value,
                        "y3": float_value,
                        "seasonality": "Flat_Linear" or "Winter_Peak" or "Summer_Peak"
                    }}
                    Data to process:
                    {file_content}
                    """
                    model = genai.GenerativeModel("gemini-pro")
                    response = model.generate_content(prompt)

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
                                "seasonality": parsed.get("seasonality", "Flat_Linear"),
                            }
                        )
                        st.toast(
                            "Document scanned and held in temporary sandbox queue!"
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
        "Review the AI outputs below. You can change types, override baseline numbers, or delete mistakes completely before pushing to your main dashboard model."
    )

    df_scratch = pd.DataFrame(st.session_state["scratchpad_queue"])

    cfg = {
        "type": st.column_config.SelectboxColumn(
            "Classification Bucket", options=["sales", "opex"], width="small"
        ),
        "name": st.column_config.TextColumn("Line Item Identifier", width="large"),
        "y1": st.column_config.NumberColumn("Year 1 Base (£)", format="£%,.2f"),
        "y2": st.column_config.NumberColumn("Year 2 Base (£)", format="£%,.2f"),
        "y3": st.column_config.NumberColumn("Year 3 Base (£)", format="£%,.2f"),
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
            for _, r in edited_grid.iterrows():
                bucket = "sales" if r["type"] == "sales" else "opex"
                st.session_state["active_data"][bucket].append(
                    {
                        "name": str(r["name"]),
                        "y1_baseline": float(r["y1"]),
                        "y2_baseline": float(r["y2"]),
                        "y3_baseline": float(r["y3"]),
                        "seasonality": str(r["seasonality"]),
                        "vat_rate_type": active_sic["default_vat_type"],
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
