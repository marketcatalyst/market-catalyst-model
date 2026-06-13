# pages/1_✍️_Data_Input_Workspace.py

import os
import sys
import json
import streamlit as st
import pandas as pd
import google.generativeai as genai
from pypdf import PdfReader
import tabulate

# =========================================================================
# 🔒 ENDPOINT SECURITY GUARDS
# =========================================================================
if not st.session_state.get("authenticated", False):
    st.error("🔒 Access Denied: Unauthorized Endpoints Locked")
    st.info("This environment is shielded by an enterprise security framework. You must log in via the main portal to open this workspace.")
    st.stop()

# Initialize empty ledger queues in session memory if not already present
if "manual_sales_entries" not in st.session_state:
    st.session_state.manual_sales_entries = []
if "manual_opex_entries" not in st.session_state:
    st.session_state.manual_opex_entries = []
if "manual_capital_entries" not in st.session_state:
    st.session_state.manual_capital_entries = []

st.title("✍️ Intelligent Data Input Workspace")
st.caption(f"Active Context: `{st.session_state.get('selected_project', 'None Activated')}`")
st.markdown("---")

# =========================================================================
# 🚀 UNIFIED COGNITIVE INGESTION GATEWAY
# =========================================================================
st.subheader("🔮 Universal AI Data Ingestion Desk")
st.markdown("Feed the STRATA forecasting engine by pasting narrative briefs **OR** dropping project files (PDF, CSV, Excel) directly into the system.")

gemini_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

if not gemini_key:
    st.warning("⚠️ `GEMINI_API_KEY` environment variable not detected. The AI engine is currently offline. Please export your key to your terminal session.")

# Layout splits input mechanics into two clean, side-by-side column bays
input_col1, input_col2 = st.columns([1, 1])

with input_col1:
    user_narrative = st.text_area(
        "Option 1: Paste Commercial / Engineering Notes", 
        height=180,
        placeholder="Example: We are launching our AVAWT turbine trial next month. Raw structural components will cost £45,000 upfront. We have an engineering overhead run-rate of £3,500 per month...",
        key="narrative_input"
    )

with input_col2:
    uploaded_file = st.file_uploader(
        "Option 2: Drop Project File (PDF Projections, CSV or Excel Logs)", 
        type=["pdf", "csv", "xlsx"]
    )
    if uploaded_file is not None:
        st.success(f"📎 Attached file: {uploaded_file.name}")

# Single Processing Action Trigger
if st.button("🚀 Execute Intelligent System Ingestion", disabled=not gemini_key, use_container_width=True):
    
    # Track text payload across processing pathways
    text_to_analyze = ""
    
    # PATHWAY A: User provided manual narrative text
    if user_narrative.strip():
        text_to_analyze += f"\n[User Provided Narrative Brief]:\n{user_narrative}\n"
        
    # PATHWAY B: User uploaded a file binary
    if uploaded_file is not None:
        file_name = uploaded_file.name.lower()
        
        # Condition 1: Handle text-based PDF compilation
        if file_name.endswith(".pdf"):
            with st.spinner("Extracting structural document text layers behind the scenes..."):
                try:
                    reader = PdfReader(uploaded_file)
                    pdf_text = ""
                    for page_num, page in enumerate(reader.pages):
                        page_char = page.extract_text()
                        if page_char:
                            pdf_text += f"\n{page_char}\n"
                    if pdf_text.strip():
                        text_to_analyze += f"\n[System Extracted Document Content from PDF File '{uploaded_file.name}']:\n{pdf_text}\n"
                    else:
                        st.error("Uploaded PDF contained no detectable text layers. Is it an un-scanned photo image?")
                        st.stop()
                except Exception as e:
                    st.error(f"Failed parsing PDF attachment: {str(e)}")
                    st.stop()
                    
        # Condition 2: Handle straight grid spreadsheets (Convert to text layout for Gemini consumption)
        elif file_name.endswith(".csv") or file_name.endswith(".xlsx"):
            with st.spinner("Parsing raw data matrix values..."):
                try:
                    # If multi-tab excel spreadsheet, compile all tabs systematically into the markdown stream
                    if file_name.endswith(".xlsx"):
                        xls = pd.ExcelFile(uploaded_file)
                        for sheet in xls.sheet_names:
                            df_sheet = pd.read_excel(uploaded_file, sheet_name=sheet)
                            if not df_sheet.empty:
                                df_as_text = df_sheet.to_markdown(index=False)
                                text_to_analyze += f"\n[System Processed Data Spreadsheet Tab '{sheet}' from File '{uploaded_file.name}']:\n{df_as_text}\n"
                    else:
                        df_raw = pd.read_csv(uploaded_file)
                        df_as_text = df_raw.to_markdown(index=False)
                        text_to_analyze += f"\n[System Processed Data Spreadsheet Matrix from File '{uploaded_file.name}']:\n{df_as_text}\n"
                except Exception as e:
                    st.error(f"Failed parsing spreadsheet data: {str(e)}")
                    st.stop()

    # CORE EXECUTION LAYER: Send compiled data payload directly to Gemini REST Matrix
    if not text_to_analyze.strip():
        st.error("Processing failed: Please paste a text narrative or attach an operational file document first.")
    else:
        with st.spinner("Gemini is interpreting variables and mapping cash-flow ripple effects..."):
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
                
                system_prompt = f"""
                You are the financial modelling data extractor for STRATA, an enterprise 3-way cash-flow forecasting platform.
                Your task is to read the compiled data input text payload, analyse it using Ripple Effect Systems Thinking (REST), and extract any financial data lines.
                
                You MUST return your response as a valid JSON object matching this exact structural schema, and absolutely nothing else. Do not wrap the JSON in markdown code blocks.
                
                {{
                    "sales": [
                        {{"name": "Clear descriptive name", "amount": 15000.0, "vat": 0.20, "lag": 1}}
                    ],
                    "opex": [
                        {{"name": "Clear descriptive name", "amount": 3500.0, "vat": 0.20, "lag": 0}}
                    ],
                    "capital": [
                        {{"name": "Clear descriptive name", "type": "Fixed Asset Purchase", "value": 45000.0, "month": 2, "parameter": 10.0}}
                    ]
                }}
                
                Rules for schema mapping:
                1. "vat" must be a float (e.g., 0.20 for 20% standard rate, or 0.0 for zero-rated).
                2. "lag" profile means customer payment delays in months (0 for immediate cash, 1 for 30-day delay, 2 for 60-day delay).
                3. Capital "type" options must be exactly one of these: "Fixed Asset Purchase", "Hire Purchase (HP) Agreement", "New Bank Loan Injection", or "Director / Equity Inflow".
                4. Capital "parameter" is the sub-metric: annual depreciation rate % for assets, agreement term in months for loans or HP links.
                
                Carefully distil all parameters from this combined workspace data block:
                \"\"\"{text_to_analyze}\"\"\"
                """
                
                response = model.generate_content(system_prompt)
                raw_json = response.text.strip()
                
                if raw_json.startswith("```"):
                    raw_json = raw_json.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
                if raw_json.startswith("json"):
                    raw_json = raw_json.split("\n", 1)[1].strip()
                    
                parsed_payload = json.loads(raw_json)
                
                injected_sales = 0
                injected_opex = 0
                injected_cap = 0
                
                for s in parsed_payload.get("sales", []):
                    st.session_state.manual_sales_entries.append(s)
                    injected_sales += 1
                for o in parsed_payload.get("opex", []):
                    st.session_state.manual_opex_entries.append(o)
                    injected_opex += 1
                for c in parsed_payload.get("capital", []):
                    st.session_state.manual_capital_entries.append(c)
                    injected_cap += 1
                    
                st.success(f"🔮 Automated Ingestion Success: Hydrated {injected_sales} Sales lines, {injected_opex} OpEx variables, and {injected_cap} Capital vectors straight into your data registers!")
                st.rerun()
                
            except Exception as ai_err:
                st.error(f"AI Core Matrix Ingestion Fault: {str(ai_err)}")

st.markdown("---")

# =========================================================================
# ✍️ MANUAL STRUCTURAL ENTRY DESKS (RETAINED AS BACKUP OVERRIDES)
# =========================================================================
st.subheader("✍️ Manual Structural Entry Desks")
st.markdown("Use these dedicated forms to make individual line tweaks, adjustments, or input custom profiles manually.")

with st.expander("📈 Direct Sales / Contract Revenue Ingestion Form"):
    s_col1, s_col2, s_col3, s_col4 = st.columns(4)
    with s_col1:
        s_name = st.text_input("Contract / Revenue Line Name", placeholder="e.g., Phase 1 Turbine Lease")
    with s_col2:
        s_amount = st.number_input("Monthly Revenue Outlay (£ Ex VAT)", min_value=0.0, step=500.0, value=0.0)
    with s_col3:
        s_vat = st.selectbox("VAT Treatment Profile", options=[0.20, 0.05, 0.00], format_func=lambda x: f"{int(x*100)}% Rated")
    with s_col4:
        s_lag = st.selectbox("Debtor Cash Lag Delay Profile", options=[0, 1, 2], format_func=lambda x: "Immediate Cash" if x==0 else f"{x*30} Days Lag")
        
    if st.button("➕ Inject Manual Revenue Entry", use_container_width=True):
        if not s_name.strip():
            st.error("Please provide a description name for the revenue entry.")
        elif s_amount <= 0:
            st.error("Revenue value must be greater than zero.")
        else:
            st.session_state.manual_sales_entries.append({"name": s_name.strip(), "amount": s_amount, "vat": s_vat, "lag": s_lag})
            st.success(f"Added revenue line: {s_name}")
            st.rerun()

with st.expander("💸 Direct Operating Expenditure (OpEx) Overhead Form"):
    o_col1, o_col2, o_col3, o_col4 = st.columns(4)
    with o_col1:
        o_name = st.text_input("Overhead / Expense Account Description", placeholder="e.g., Composite Logistics")
    with o_col2:
        o_amount = st.number_input("Monthly Expense Outlay (£ Ex VAT)", min_value=0.0, step=100.0, value=0.0)
    with o_col3:
        o_vat = st.selectbox("Creditor VAT Profile", options=[0.20, 0.05, 0.00], format_func=lambda x: f"{int(x*100)}% Input Reclaim", key="o_vat")
    with o_col4:
        o_lag = st.selectbox("Creditor Settlement Delay Profile", options=[0, 1, 2], format_func=lambda x: "Immediate Payout" if x==0 else f"{x*30} Days Credit Window", key="o_lag")
        
    if st.button("➕ Inject Manual Overhead Entry", use_container_width=True):
        if not o_name.strip():
            st.error("Please provide a description name for the expenditure line.")
        elif o_amount <= 0:
            st.error("Expense value must be greater than zero.")
        else:
            st.session_state.manual_opex_entries.append({"name": o_name.strip(), "amount": o_amount, "vat": o_vat, "lag": o_lag})
            st.success(f"Added expenditure line: {o_name}")
            st.rerun()

with st.expander("🏗️ Direct Capital, Asset Funding & Corporate Finance Desk"):
    c_col1, c_col2, c_col3, c_col4 = st.columns(4)
    with c_col1:
        c_name = st.text_input("Facility / Asset Line Identification", placeholder="e.g., AEGIS Patent")
    with c_col2:
        c_type = st.selectbox("Structural Transaction Classification", options=[
            "Fixed Asset Purchase", 
            "Hire Purchase (HP) Agreement", 
            "New Bank Loan Injection", 
            "Director / Equity Inflow"
        ])
    with c_col3:
        c_value = st.number_input("Principal Capital Value Transacted (£)", min_value=0.0, step=1000.0, value=0.0)
    with c_col4:
        c_month = st.number_input("Target Model Milestone Month", min_value=1, max_value=12, step=1, value=1)
        
    if c_type == "Fixed Asset Purchase":
        c_param = st.slider("Target Annual Straight-Line Depreciation Rate (%)", min_value=0, max_value=100, value=20, step=5)
    elif c_type in ["New Bank Loan Injection", "Hire Purchase (HP) Agreement"]:
        c_param = st.number_input("Contractual Financing Repayment Term (Months)", min_value=1, max_value=60, value=36, step=1)
    else:
        c_param = 0.0

    if st.button("➕ Inject Manual Capital Component", use_container_width=True):
        if not c_name.strip():
            st.error("Please provide an identification name for this capital transaction.")
        elif c_value <= 0:
            st.error("Transaction principal value must be greater than zero.")
        else:
            st.session_state.manual_capital_entries.append({
                "name": c_name.strip(), 
                "type": c_type, 
                "value": c_value, 
                "month": int(c_month), 
                "parameter": float(c_param)
            })
            st.success(f"Added capital element: {c_name} [{c_type}]")
            st.rerun()

st.markdown("---")

# =========================================================================
# 📂 STEP 3: ACTIVE REPOSITORIES & DATA TABLES VIEW
# =========================================================================
st.subheader("📂 Active Workspace Data Repositories")
st.markdown("Review the lines currently queued to feed your active Sandbox and Forecast calculation modules:")

tab1, tab2, tab3 = st.tabs(["📊 Queued Revenues", "💸 Queued Expenses", "🏗️ Queued Capital Structures"])

with tab1:
    if st.session_state.manual_sales_entries:
        df_s = pd.DataFrame(st.session_state.manual_sales_entries)
        st.dataframe(df_s, use_container_width=True)
        if st.button("🗑️ Clear Revenue Queue", key="clear_s"):
            st.session_state.manual_sales_entries = []
            st.rerun()
    else:
        st.caption("No dynamic sales lines currently tracking in this environment context.")

with tab2:
    if st.session_state.manual_opex_entries:
        df_o = pd.DataFrame(st.session_state.manual_opex_entries)
        st.dataframe(df_o, use_container_width=True)
        if st.button("🗑️ Clear Expense Queue", key="clear_o"):
            st.session_state.manual_opex_entries = []
            st.rerun()
    else:
        st.caption("No dynamic operating expense lines currently tracking in this environment context.")

with tab3:
    if st.session_state.manual_capital_entries:
        df_c = pd.DataFrame(st.session_state.manual_capital_entries)
        st.dataframe(df_c, use_container_width=True)
        if st.button("🗑️ Clear Capital Queue", key="clear_c"):
            st.session_state.manual_capital_entries = []
            st.rerun()
    else:
        st.caption("No dynamic capital structural lines currently tracking in this environment context.")