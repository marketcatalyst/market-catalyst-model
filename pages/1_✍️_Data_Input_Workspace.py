# pages/1_✍️_Data_Input_Workspace.py

import os
import sys
import json
import streamlit as st
import pandas as pd
import google.generativeai as genai
from pypdf import PdfReader

# =========================================================================
# 🔒 ENDPOINT SECURITY GUARDS
# =========================================================================
if not st.session_state.get("authenticated", False):
    st.error("🔒 Access Denied: Unauthorized Endpoints Locked")
    st.info("This environment is shielded by an enterprise security framework. You must log in via the main portal to open this workspace.")
    st.stop()

# Ensure local storage path for projects exists
PROJECTS_DIR = "saved_projects"
if not os.path.exists(PROJECTS_DIR):
    os.makedirs(PROJECTS_DIR)

# Initialize generic session state lists for dynamic data collection
if "manual_sales_entries" not in st.session_state:
    st.session_state.manual_sales_entries = []
if "manual_opex_entries" not in st.session_state:
    st.session_state.manual_opex_entries = []
if "manual_capital_entries" not in st.session_state:
    st.session_state.manual_capital_entries = []
if "active_project_name" not in st.session_state:
    st.session_state.active_project_name = ""

st.title("✍️ Intelligent Data Input Workspace")
st.markdown("---")

# =========================================================================
# 💾 PERSISTENT PROJECT MANAGEMENT PANEL
# =========================================================================
st.subheader("📁 Project Lifecycle Matrix")
st.markdown("Save your active data state or pull a historical forecasting project directly from disk storage.")

proj_col1, proj_col2 = st.columns([1, 1])

with proj_col1:
    saved_files = [f.replace(".json", "") for f in os.listdir(PROJECTS_DIR) if f.endswith(".json") and not f.startswith("SANDBOX_VARIANT_")]
    
    if saved_files:
        selected_to_load = st.selectbox("Select a Saved Project to Load", options=["-- Select --"] + saved_files)
        if selected_to_load != "-- Select --":
            if st.button("📂 Load Selected Project State", use_container_width=True):
                try:
                    filepath = os.path.join(PROJECTS_DIR, f"{selected_to_load}.json")
                    with open(filepath, "r") as pf:
                        payload = json.load(pf)
                    
                    st.session_state.manual_sales_entries = payload.get("sales", [])
                    st.session_state.manual_opex_entries = payload.get("opex", [])
                    st.session_state.manual_capital_entries = payload.get("capital", [])
                    st.session_state.active_project_name = selected_to_load
                    st.session_state.selected_project = selected_to_load
                    st.success(f"💾 Project state `{selected_to_load}` successfully restored into memory registers!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to load project file: {str(e)}")
    else:
        st.info("No saved project matrices detected on disk.")

with proj_col2:
    default_name = st.session_state.get("active_project_name", "")
    new_project_title = st.text_input("Project Name to Save/Export", value=default_name, placeholder="e.g., Project-Alpha-Run-1")
    
    if st.button("💾 Save Active Workspace State", use_container_width=True):
        if not new_project_title.strip():
            st.error("Please provide a valid project identifier name to execute the save routine.")
        else:
            clean_title = "".join(c for c in new_project_title if c.isalnum() or c in ("-", "_")).strip()
            project_data = {
                "sales": st.session_state.manual_sales_entries,
                "opex": st.session_state.manual_opex_entries,
                "capital": st.session_state.manual_capital_entries
            }
            try:
                filepath = os.path.join(PROJECTS_DIR, f"{clean_title}.json")
                with open(filepath, "w") as pf:
                    json.dump(project_data, pf, indent=4)
                st.session_state.active_project_name = clean_title
                st.session_state.selected_project = clean_title
                st.success(f"🚀 Project parameters committed cleanly to disk target: `{clean_title}.json`")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to commit data to file system: {str(e)}")

st.markdown("---")

# =========================================================================
# 🚀 UNIFIED COGNITIVE INGESTION GATEWAY (COGNITIVE ACCOUNTING SCHEMATIC)
# =========================================================================
st.subheader("🔮 Universal AI Data Ingestion Desk")
st.markdown("Feed the STRATA forecasting engine by pasting narrative briefs **OR** dropping project files directly into the system.")

gemini_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

if not gemini_key:
    st.warning("⚠️ `GEMINI_API_KEY` environment variable not detected. The AI engine is currently offline.")

input_col1, input_col2 = st.columns([1, 1])

with input_col1:
    user_narrative = st.text_area(
        "Option 1: Paste Commercial / Engineering Notes", 
        height=180,
        placeholder="Paste narrative text here...",
        key="narrative_input"
    )

with input_col2:
    uploaded_file = st.file_uploader(
        "Option 2: Drop Project File (PDF, CSV, or Excel)", 
        type=["pdf", "csv", "xlsx"]
    )
    if uploaded_file is not None:
        st.success(f"📎 Attached file: {uploaded_file.name}")

if st.button("🚀 Execute Intelligent System Ingestion", disabled=not gemini_key, use_container_width=True):
    
    text_to_analyze = ""
    
    if user_narrative.strip():
        text_to_analyze += f"\n[User Provided Narrative Brief]:\n{user_narrative}\n"
        
    if uploaded_file is not None:
        file_name = uploaded_file.name.lower()
        
        if file_name.endswith(".pdf"):
            with st.spinner("Extracting structural document text layers..."):
                try:
                    reader = PdfReader(uploaded_file)
                    pdf_text = ""
                    for page in reader.pages:
                        page_char = page.extract_text()
                        if page_char:
                            pdf_text += f"\n{page_char}\n"
                    text_to_analyze += f"\n[System Extracted PDF Content]:\n{pdf_text}\n"
                except Exception as e:
                    st.error(f"Failed parsing PDF attachment: {str(e)}")
                    st.stop()
                    
        elif file_name.endswith(".csv") or file_name.endswith(".xlsx"):
            with st.spinner("Parsing data matrix values..."):
                try:
                    if file_name.endswith(".xlsx"):
                        xls = pd.ExcelFile(uploaded_file)
                        for sheet in xls.sheet_names:
                            df_sheet = pd.read_excel(uploaded_file, sheet_name=sheet)
                            if not df_sheet.empty:
                                text_to_analyze += f"\n[Tab '{sheet}']:\n{df_sheet.to_markdown(index=False)}\n"
                    else:
                        df_raw = pd.read_csv(uploaded_file)
                        text_to_analyze += f"\n[Spreadsheet Data]:\n{df_raw.to_markdown(index=False)}\n"
                except Exception as e:
                    st.error(f"Failed parsing spreadsheet data: {str(e)}")
                    st.stop()

    if not text_to_analyze.strip():
        st.error("Processing failed: Please paste a narrative or attach an operational document first.")
    else:
        with st.spinner("Gemini is extracting financial variables into structured accounting vectors..."):
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
                
                system_prompt = f"""
                You are the advanced STRATA cognitive financial extraction engine. 
                Analyze the provided text or data matrix and decompose the values into abstract, balanced accounting categories.

                CRITICAL CLASSIFICATION ARCHETYPES:
                1. "sales": Recurring operational inflows generated from core business activities during active trading.
                2. "opex": Recurring operational overhead expenditures required to maintain daily business run-rates.
                3. "capital": Non-recurring, fundamental balance sheet structural shifts. You MUST categorize items here if they match:
                   - Upfront capital cushions, director investments, equity injections, or loan additions (You MUST tag these exactly as "type": "Director / Equity Inflow" or "New Bank Loan Injection").
                   - Non-recurring infrastructure outlays, property acquisitions, building renovations, setups, or fixed equipment purchases (You MUST tag these exactly as "type": "Fixed Asset Purchase").

                Return a valid JSON object matching this schema precisely:
                {{
                    "sales": [
                        {{"name": "Description name", "amount": 10000.0, "vat": 0.20, "lag": 0}}
                    ],
                    "opex": [
                        {{"name": "Description name", "amount": 2500.0, "vat": 0.20, "lag": 0}}
                    ],
                    "capital": [
                        {{"name": "Description name", "type": "Fixed Asset Purchase", "value": 5000.0, "month": 1, "parameter": 10.0}}
                    ]
                }}

                Analyse the parameters from this text block:
                \"\"\"{text_to_analyze}\"\"\"
                """
                
                response = model.generate_content(system_prompt)
                raw_json = response.text.strip()
                
                if raw_json.startswith("```"):
                    raw_json = raw_json.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
                if raw_json.startswith("json"):
                    raw_json = raw_json.split("\n", 1)[1].strip()
                    
                parsed_payload = json.loads(raw_json)
                
                for s in parsed_payload.get("sales", []):
                    st.session_state.manual_sales_entries.append(s)
                for o in parsed_payload.get("opex", []):
                    st.session_state.manual_opex_entries.append(o)
                for c in parsed_payload.get("capital", []):
                    st.session_state.manual_capital_entries.append(c)
                
                st.success("🔮 Ingestion complete: Financial data vectors successfully mapped into memory queues.")
                st.rerun()
                
            except Exception as ai_err:
                st.error(f"AI Ingestion Fault: {str(ai_err)}")

st.markdown("---")

# =========================================================================
# 📂 ACTIVE REPOSITORIES VIEW WITH PERSISTENCE INVITATIONS
# =========================================================================
st.subheader("📂 Active Workspace Data Repositories")
st.markdown("Review the raw financial rows sitting inside the active workspace memory context:")

if (st.session_state.manual_sales_entries or 
    st.session_state.manual_opex_entries or 
    st.session_state.manual_capital_entries) and not st.session_state.get("active_project_name"):
    st.info("💡 **Unsaved Progress Warning:** You have active rows in memory. Enter a project name in the panel above and click save to protect your work.")

tab1, tab2, tab3 = st.tabs(["📊 Queued Revenues", "💸 Queued Expenses", "🏗️ Queued Capital Structures"])

with tab1:
    if st.session_state.manual_sales_entries:
        st.dataframe(pd.DataFrame(st.session_state.manual_sales_entries), use_container_width=True)
        if st.button("🗑️ Clear Revenue Queue", key="clear_s"):
            st.session_state.manual_sales_entries = []
            st.rerun()
    else:
        st.caption("No data currently tracking in this register.")

with tab2:
    if st.session_state.manual_opex_entries:
        st.dataframe(pd.DataFrame(st.session_state.manual_opex_entries), use_container_width=True)
        if st.button("🗑️ Clear Expense Queue", key="clear_o"):
            st.session_state.manual_opex_entries = []
            st.rerun()
    else:
        st.caption("No data currently tracking in this register.")

with tab3:
    if st.session_state.manual_capital_entries:
        st.dataframe(pd.DataFrame(st.session_state.manual_capital_entries), use_container_width=True)
        if st.button("🗑️ Clear Capital Queue", key="clear_c"):
            st.session_state.manual_capital_entries = []
            st.rerun()
    else:
        st.caption("No data currently tracking in this register.")