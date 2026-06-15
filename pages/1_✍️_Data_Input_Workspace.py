# pages/1_✍️_Data_Input_Workspace.py

import os
import sys
import json
import streamlit as st
import pandas as pd
import google.generativeai as genai
from pypdf import PdfReader
from pathlib import Path

# Absolute project path resolution to handle multi-page layout shifts smoothly
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

if not st.session_state.get("authenticated", False):
    st.error("🔒 Access Denied: Unauthorized Endpoints Locked")
    st.stop()

PROJECTS_DIR = "saved_projects"
gemini_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

st.title("✍️ Data Input Workspace")
st.caption("Directly build your model rows, type parameters, or utilize the intelligent document analysis conduit.")
st.markdown("---")

# =========================================================================
# 🔮 OPTIONAL: INTELLIGENT ASSISTANT CONDUIT (EXPANDABLE)
# =========================================================================
with st.expander("✨ Open Intelligent Document Analysis Assistant", expanded=False):
    st.markdown("Drop project notes, balance sheet positions, or brief financial summaries here. The assistant will extract the parameters into your active workspace memory context.")
    
    if not gemini_key:
        st.warning("⚠️ Gemini API Key not detected in system environment variable configurations.")
    
    ai_col1, ai_col2 = st.columns([1, 1])
    with ai_col1:
        ai_narrative = st.text_area("Option A: Paste Explanatory Project Notes", height=120, placeholder="Paste brief text here...")
    with ai_col2:
        ai_file = st.file_uploader("Option B: Drop Project File (PDF Only)", type=["pdf"])
        
    if st.button("🔮 Analyze & Extract Parameters", use_container_width=True, disabled=not gemini_key):
        extracted_text = ""
        if ai_narrative.strip():
            extracted_text += f"\n[User Narrative Context]:\n{ai_narrative}\n"
        if ai_file is not None:
            try:
                reader = PdfReader(ai_file)
                pdf_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
                extracted_text += f"\n[Document Text Layers]:\n{pdf_text}\n"
            except Exception as ex:
                st.error(f"File reading fault: {str(ex)}")
                
        if not extracted_text.strip():
            st.error("Please supply a descriptive narrative or attach a PDF file first.")
        else:
            with st.spinner("Analyzing document structure..."):
                try:
                    genai.configure(api_key=gemini_key)
                    model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
                    
                    structural_prompt = f"""
                    You are a financial parsing assistant. Extract data lines into strict JSON format with these exact buckets:
                    - "sales": Recurring operational inflows. Include "name", "amount" (annualized), and "vat" (0.20 or 0.0).
                    - "opex": Recurring operational overheads. Include "name", "amount" (annualized), and "vat" (0.20).
                    - "capital": Non-recurring capital or asset rows. Include "name", "type" ("Fixed Asset Purchase", "Director / Equity Inflow", or "New Bank Loan Injection"), and "value" (total amount).
                    
                    Return ONLY valid raw JSON matching this schema exactly without markdown formatting wrappers:
                    {{"sales": [], "opex": [], "capital": []}}
                    
                    Text to parse:
                    {extracted_text}
                    """
                    response = model.generate_content(structural_prompt)
                    clean_res = response.text.strip().replace("```json", "").replace("```", "").strip()
                    payload = json.loads(clean_res)
                    
                    # Merge parsed rows directly into memory contexts cleanly
                    for s in payload.get("sales", []): st.session_state.manual_sales_entries.append(s)
                    for o in payload.get("opex", []): st.session_state.manual_opex_entries.append(o)
                    for c in payload.get("capital", []): 
                        c.update({"month": 1, "parameter": 10.0 if c.get("type") == "Fixed Asset Purchase" else 0.0})
                        st.session_state.manual_capital_entries.append(c)
                        
                    st.success("Analysis complete! Corporate data rows successfully appended below.")
                    st.rerun()
                except Exception as ai_err:
                    st.error(f"Intelligent Parsing Fault: {str(ai_err)}")

# =========================================================================
# ✍️ PANEL 2: MANUAL DIRECT DATA ENTRY FORMS
# =========================================================================
st.subheader("📝 Direct Parameter Setup Desks")
inc_col1, inc_col2, inc_col3 = st.columns(3)

with inc_col1:
    st.markdown("### 📊 Revenue Streams")
    s_name = st.text_input("Income Name / Description:", placeholder="e.g., Court Hire Fees", key="s_name")
    s_amt = st.number_input("Projected Annual Income (£):", min_value=0.0, step=5000.0, key="s_amt")
    s_vat = st.checkbox("Apply Standard 20% VAT?", value=True, key="s_vat")
    if st.button("➕ Add Income Row", use_container_width=True):
        if s_name.strip():
            st.session_state.manual_sales_entries.append({"name": s_name.strip(), "amount": float(s_amt), "vat": 0.20 if s_vat else 0.0})
            st.rerun()

with inc_col2:
    st.markdown("### 💸 Overhead Costs")
    o_name = st.text_input("Cost Name / Description:", placeholder="e.g., Site Utilities & Rent", key="o_name")
    o_amt = st.number_input("Projected Annual Cost (£):", min_value=0.0, step=1000.0, key="o_amt")
    if st.button("➕ Add Overhead Row", use_container_width=True):
        if o_name.strip():
            st.session_state.manual_opex_entries.append({"name": o_name.strip(), "amount": float(o_amt), "vat": 0.20})
            st.rerun()

with inc_col3:
    st.markdown("### 🏛️ Cap-Ex & Finance")
    c_name = st.text_input("Asset Description / Capital Event:", placeholder="e.g., Core Court Infrastructure", key="c_name")
    c_type_display = st.selectbox("Classification Category:", [
        "New / Existing Fixed Asset CapEx", 
        "Equity Capital / Share Premium Injection", 
        "Commercial Debt / Facility Drawdown"
    ])
    c_val = st.number_input("Transaction Value (£):", min_value=0.0, step=5000.0, key="c_val")
    
    if st.button("➕ Add Capital Row", use_container_width=True):
        if c_name.strip():
            backend_type_map = {
                "New / Existing Fixed Asset CapEx": "Fixed Asset Purchase",
                "Equity Capital / Share Premium Injection": "Director / Equity Inflow",
                "Commercial Debt / Facility Drawdown": "New Bank Loan Injection"
            }
            mapped_type = backend_type_map[c_type_display]
            
            st.session_state.manual_capital_entries.append({
                "name": c_name.strip(), 
                "type": mapped_type, 
                "value": float(c_val), 
                "month": 1, 
                "parameter": 10.0 if mapped_type == "Fixed Asset Purchase" else 0.0
            })
            st.rerun()

st.markdown("---")

# =========================================================================
# 💾 PANEL 3: WORKSPACE EXPORTS
# =========================================================================
st.subheader("💾 Master Save Workspace Registry")
save_col1, save_col2 = st.columns([2, 1])
with save_col1:
    save_title = st.text_input("Project Filename Target Identifier:", value=st.session_state.get("selected_project", "My-Padel-Baseline"))
with save_col2:
    st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button("💾 Export Project to Secure File Target", use_container_width=True):
        clean_title = "".join(c for c in save_title if c.isalnum() or c in ("-", "_")).strip()
        if clean_title:
            project_payload = {"sales": st.session_state.manual_sales_entries, "opex": st.session_state.manual_opex_entries, "capital": st.session_state.manual_capital_entries}
            try:
                with open(os.path.join(PROJECTS_DIR, f"{clean_title}.json"), "w") as pf: json.dump(project_payload, pf, indent=4)
                st.session_state["selected_project"] = clean_title
                st.success(f"🚀 Active dataset saved as: `{clean_title}.json`")
                st.rerun()
            except Exception as e: st.error(f"Export error: {str(e)}")

st.markdown("---")

# =========================================================================
# 📁 PANEL 4: LIVE MONITOR TABLES
# =========================================================================
st.subheader("📁 Active Workspace Data Repositories")
tab1, tab2, tab3 = st.tabs(["📈 Income Streams", "💸 Overhead Costs", "🏛️ Cap-Ex & Capitalization Ledger"])

with tab1:
    if st.session_state.manual_sales_entries:
        df_sales = pd.DataFrame(st.session_state.manual_sales_entries)
        if len(df_sales.columns) == 3: df_sales.columns = ["Revenue Stream Name", "Annual Gross Amount (£)", "VAT Rate Fraction"]
        st.dataframe(df_sales.style.format({"Annual Gross Amount (£)": "{:,.2f}"}), use_container_width=True)
        if st.button("🗑️ Clear Income Rows", key="clear_s"): st.session_state.manual_sales_entries = []; st.rerun()
    else: st.caption("No revenue lines configured.")

with tab2:
    if st.session_state.manual_opex_entries:
        df_opex = pd.DataFrame(st.session_state.manual_opex_entries)
        if len(df_opex.columns) == 3: df_opex.columns = ["Overhead Cost Name", "Annual Running Rate (£)", "VAT Rate Fraction"]
        st.dataframe(df_opex.style.format({"Annual Running Rate (£)": "{:,.2f}"}), use_container_width=True)
        if st.button("🗑️ Clear Overhead Rows", key="clear_o"): st.session_state.manual_opex_entries = []; st.rerun()
    else: st.caption("No operational overhead lines configured.")

with tab3:
    if st.session_state.manual_capital_entries:
        df_cap = pd.DataFrame(st.session_state.manual_capital_entries)
        available_cols = [c for c in ["name", "type", "value", "month"] if c in df_cap.columns]
        df_cap = df_cap[available_cols]
        
        if not df_cap.empty:
            df_cap["type"] = df_cap["type"].str.replace("Fixed Asset Purchase", "Fixed Asset CapEx")\
                                           .str.replace("Director / Equity Inflow", "Equity Inflow")\
                                           .str.replace("New Bank Loan Injection", "Debt Facility")
        
        if len(df_cap.columns) == 4: df_cap.columns = ["Asset / Funding Source Name", "Structural Category", "Transaction Value (£)", "Target Month"]
        st.dataframe(df_cap.style.format({"Transaction Value (£)": "{:,.2f}"}), use_container_width=True)
        if st.button("🗑️ Clear Capital Rows", key="clear_c"): st.session_state.manual_capital_entries = []; st.rerun()
    else: st.caption("No asset allocations or long-term funding entries configured.")