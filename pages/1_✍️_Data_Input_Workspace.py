# pages/1_✍️_Data_Input_Workspace.py

import os
import json
import streamlit as st
import pandas as pd
import google.generativeai as genai

# Enforce secure page rendering guards
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

st.title("✍️ Data Input Workspace & AI Ingestion Desk")
st.caption(f"Active Context: `{st.session_state.get('selected_project', 'None Activated')}`")
st.markdown("---")

# =========================================================================
# 🔮 STEP 1: GEMINI AI SYSTEMIC INGESTION DESK
# =========================================================================
st.subheader("🔮 Gemini AI Cognitive Data Parser")
st.markdown("""
Paste raw project summaries, commercial negotiation briefs, or engineering rollout notes below. 
Gemini will interpret the unstructured prose through a **REST** framework and distill it into precise financial parameters.
""")

# Fetch the local environment key safely
gemini_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

if not gemini_key:
    st.warning("⚠️ `GEMINI_API_KEY` environment variable not detected. The AI engine is currently offline. Please export your key to your terminal session.")

user_narrative = st.text_area(
    "Paste Commercial Project Notes / Engineering Manifests Here", 
    height=220,
    placeholder="Example: We are launching our AVAWT turbine trial next month. Raw structural components will cost £45,000 upfront. We have a contractual engineering overhead run-rate of £3,500 per month. We expect our first commercial lease contract to sign in Month 3 bringing in £18,000 monthly, but the client negotiated a 60-day cash payment lag..."
)

if st.button("🔮 Analyze & Distill Narrative with Gemini", disabled=not gemini_key, use_container_width=True):
    if not user_narrative.strip():
        st.error("Please provide a descriptive text narrative to interpret.")
    else:
        with st.spinner("Gemini is mapping systemic ripple effects and formatting data frames..."):
            try:
                # Configure the Gemini Engine Model
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                # Rigid prompt boundary enforcing JSON schema extraction
                system_prompt = f"""
                You are the financial modeling data extractor for STRATA, an enterprise 3-way cash-flow forecasting platform.
                Your task is to read the user's raw business narrative, analyze it using Ripple Effect Systems Thinking (REST), and extract any financial data lines.
                
                You MUST return your response as a valid JSON object matching this exact structural schema, and absolutely nothing else. Do not wrap the JSON in markdown code blocks like ```json.
                
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
                
                Analyze this text narrative carefully:
                "{user_narrative}"
                """
                
                # Request synthesis from Gemini
                response = model.generate_content(system_prompt)
                raw_json = response.text.strip()
                
                # Sanitize response strings if markdown boundaries leaked out
                if raw_json.startswith("```"):
                    raw_json = raw_json.split("\n", 1)[1].rsplit("\n", 1)[0].strip()
                if raw_json.startswith("json"):
                    raw_json = raw_json.split("\n", 1)[1].strip()
                    
                parsed_payload = json.loads(raw_json)
                
                # Hydrate variables straight into active session state
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
                    
                st.success(f"🔮 Gemini Translation Complete: Hydrated {injected_sales} Sales lines, {injected_opex} OpEx variables, and {injected_cap} Capital vectors directly into your data queue!")
                
            except Exception as ai_err:
                st.error(f"AI Parsing Matrix Failure: {str(ai_err)}")
                st.info("Ensure your response data string matches strict JSON compliance thresholds.")

st.markdown("---")

# =========================================================================
# 📊 STEP 2: ACTIVE REPOSITORIES & DATA TABLES VIEW
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