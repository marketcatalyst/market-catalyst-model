# ui_skin/pages/1_🔌_ingestion.py
import streamlit as st
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

st.set_page_config(layout="wide", page_title="Ledger Ingestion & Hub")

st.title("🔌 Ledger Ingestion & Voice Control Hub")
st.caption("Active Workspace Layer • Manual Adjustments & Native Google GenAI Automation Gateway")
st.markdown("---")

# ==========================================
# 🎤 1. LIVE GOOGLE-GENAI VOICE AUTOMATION
# ==========================================
st.subheader("🎙️ Voice Command Automation (Official Google GenAI SDK)")
st.markdown(
    "Record a voice note to add or adjust accounts automatically "
    "(e.g., *'Add a software account code 7500 for five hundred pounds under Indirect Overheads (OpEx)'*)."
)

st.caption("Click the microphone to record your voice command")
audio_data = st.audio_input("Record voice instruction input sequence:", label_visibility="collapsed")

# --- Define the Strict Target JSON Schema Structure via Pydantic ---
class AccountingIntent(BaseModel):
    account_code: str = Field(description="The unique numerical identifier code for the account ledger.")
    account_name: str = Field(description="The descriptive account title or transaction source label.")
    allocation_bucket: str = Field(description="Must map to one of: 'Revenue', 'Gross Wages', 'Direct Expenses (COGS)', 'Indirect Overheads (OpEx)', 'Fixed Assets', 'Current Assets', 'Prepayments', 'Current Liabilities', 'Long-Term Liabilities', 'Accruals', 'Equity & Reserves'.")
    amount: float = Field(description="The absolute numerical transaction or balance sheet allocation value in pounds sterling.")

# --- Real-Time Execution Pipeline ---
if audio_data is not None:
    st.info("⚡ Voice command captured successfully! Compiling multi-modal payload...")
    
    with st.spinner("Analyzing audio frequencies and running schema-enforced lexical parsing..."):
        try:
            # 1. Initialize the official GenAI SDK Client
            # The client automatically searches your environment for st.secrets["GEMINI_API_KEY"] or os.environ["GEMINI_API_KEY"]
            client = genai.Client()
            
            # 2. Extract raw file bytes directly from the front-end stream
            raw_audio_bytes = audio_data.read()
            
            # 3. Fire the request directly to the multi-modal flagship model
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(
                        data=raw_audio_bytes,
                        mime_type="audio/wav"
                    ),
                    "Analyze the provided accounting voice message. Extract the account code, description, target classification bucket, and numerical cash value. Map them strictly to the requested schema structure."
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AccountingIntent,
                    temperature=0.1  # Locked low for precise data extraction extraction stability
                ),
            )
            
            # 4. Parse the structurally validated response object back out
            parsed_json = response.parsed
            
            # Map structural tokens cleanly over to match our active DataFrame names
            structured_payload = {
                "Account Code": str(parsed_json.account_code),
                "Account Name": str(parsed_json.account_name),
                "Accounting Allocation Bucket": str(parsed_json.allocation_bucket),
                "Amount (£)": float(parsed_json.amount)
            }
            
            # Display real-time token breakdown metrics transparently to the user
            st.markdown("#### 🧠 Live AI SDK Structural Mapping Results")
            col_ai1, col_ai2, col_ai3, col_ai4 = st.columns(4)
            col_ai1.metric("Identified Code", structured_payload["Account Code"])
            col_ai2.metric("Parsed Name", structured_payload["Account Name"])
            col_ai3.metric("Mapped Bucket", structured_payload["Accounting Allocation Bucket"])
            col_ai4.metric("Extracted Value", f"£{structured_payload['Amount (£)']:,.2f}")
            
            # Merge parsed data straight into our persistent front-end session states
            if "trial_balance_matrix" in st.session_state:
                new_row = pd.DataFrame([structured_payload])
                # Duplication guard block checking account code constraints
                if not st.session_state.trial_balance_matrix["Account Code"].astype(str).eq(structured_payload["Account Code"]).any():
                    st.session_state.trial_balance_matrix = pd.concat(
                        [st.session_state.trial_balance_matrix, new_row], 
                        ignore_index=True
                    )
                    st.toast("🎯 Ledger table dynamically updated via Google GenAI!", icon="🎙️")
                    
        except Exception as ai_err:
            st.error(f"❌ SDK Automation Exception: {str(ai_err)}")
            st.info("💡 Ensure your 'GEMINI_API_KEY' is added to your local .env file or Streamlit Cloud Secrets management dashboard panel.")

st.markdown("---")

# ==========================================
# 📋 2. TRIAL BALANCE SHEET WITH UX POP-UP
# ==========================================
col_tb_title, col_tb_pop = st.columns([4, 1])

with col_tb_title:
    st.subheader("📋 Live Interactive Trial Balance Sheet")
    st.markdown("Modify account codes, edit tracking names, adjust amounts, or add rows directly inside the data spreadsheet below:")

with col_tb_pop:
    with st.popover("ℹ️ Ledger: What, When & Why?", use_container_width=True):
        st.markdown("### **📋 Ingestion Matrix Documentation**")
        st.markdown("---")
        st.markdown("**WHAT:** An interactive Trial Balance matrix connecting natural accounts directly to high-level financial tracking buckets.")
        st.markdown("**WHEN:** Adjust at baseline setup to map your company's actual opening balances or alter localized Chart of Accounts configurations.")
        st.markdown("**WHY:** Ensures accounting names match downstream database tracking requirements, preventing formula breaks across time horizons.")

if "trial_balance_matrix" not in st.session_state:
    st.session_state.trial_balance_matrix = pd.DataFrame([
        {"Account Code": "1000", "Account Name": "Gross Sales Turnover", "Accounting Allocation Bucket": "Revenue", "Amount (£)": 50000.00},
        {"Account Code": "7000", "Account Name": "Staff Salaries Base", "Accounting Allocation Bucket": "Gross Wages", "Amount (£)": 4500.00},
        {"Account Code": "2100", "Account Name": "Trade Creditors", "Accounting Allocation Bucket": "Current Liabilities", "Amount (£)": 1200.00}
    ])

edited_tb_df = st.data_editor(
    st.session_state.trial_balance_matrix,
    use_container_width=True,
    num_rows="dynamic",
    column_config={
        "Account Code": st.column_config.TextColumn("Account Code", help="Unique ledger chart of accounts identifier code"),
        "Account Name": st.column_config.TextColumn("Account Name", help="Description label tracking the financial transaction row source"),
        "Accounting Allocation Bucket": st.column_config.SelectboxColumn(
            "Accounting Allocation Bucket",
            options=[
                "Revenue", "Gross Wages", "Direct Expenses (COGS)", "Indirect Overheads (OpEx)",
                "Fixed Assets", "Current Assets", "Prepayments", "Current Liabilities", 
                "Long-Term Liabilities", "Accruals", "Equity & Reserves"
            ],
            required=True
        ),
        "Amount (£)": st.column_config.NumberColumn("Amount (£)", format="£%,.2f", min_value=0.00)
    },
    key="trial_balance_grid_editor"
)

if st.button("Commit Ledger Grid Modifications to Session Memory", use_container_width=False):
    st.session_state.trial_balance_matrix = edited_tb_df
    st.success("💾 Trial Balance states safely committed into central app session cache memory layers!")