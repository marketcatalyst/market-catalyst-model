# ui_skin/pages/1_🔌_ingestion.py
import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

st.set_page_config(layout="wide", page_title="Data Ingestion Workshop")

st.title("🔌 Ledger Ingestion & Voice Control Hub")
st.caption("Active Workspace Layer • Manual Adjustments & Multi-Modal AI Automation Gateway")
st.markdown("---")

# Initialize a clean, persistent local ledger session state if empty
if "manual_ledger" not in st.session_state:
    st.session_state.manual_ledger = pd.DataFrame([
        {"Account Code": "1000", "Account Name": "Gross Sales Turnover", "Bucket": "Revenue", "Amount (£)": 50000.00},
        {"Account Code": "7000", "Account Name": "Staff Salaries Base", "Bucket": "Gross Wages", "Amount (£)": 4500.00},
        {"Account Code": "2100", "Account Name": "Trade Creditors", "Bucket": "Accruals", "Amount (£)": 1200.00}
    ])

# --- MODULE 1: VOICE INPUT WITH GEMINI API ---
st.subheader("🎙️ Voice Command Automation (Gemini Multimodal AI)")
st.markdown("Record a voice note to add or adjust accounts automatically (e.g., *'Add a software account code 7500 for five hundred pounds under Gross Wages'*).")

# Initialize Gemini Client safely using secrets
try:
    gemini_key = st.secrets["gemini"]["api_key"]
    ai_client = genai.Client(api_key=gemini_key)
except Exception:
    ai_client = None
    st.warning("🔒 Gemini API Key missing from secrets.toml. Voice automation module locked.")

# Streamlit native microphone component
recorded_audio = st.audio_input("Click the microphone to record your voice command")

if recorded_audio and ai_client:
    with st.spinner("Gemini is analyzing voice audio parameters..."):
        try:
            # Read raw bytes directly from user's web mic object
            audio_bytes = recorded_audio.read()
            
            # Formulate structural instructions utilizing Gemini's native audio parsing capabilities
            prompt = """
            You are a senior forensic accountant processing voice memos from a bookkeeper.
            Analyze the attached audio clip and extract any requested ledger adjustments.
            
            Return the result STRICTLY as a valid JSON object matching this dictionary format:
            {
                "status": "SUCCESS" or "ERROR",
                "account_code": "string or default empty",
                "account_name": "extracted name",
                "bucket": "Must be exactly one of: Revenue, Gross Wages, Accruals, Prepayments, Stock, WIP",
                "amount": float value
            }
            Do not wrap in markdown blocks, do not return anything except pure json text.
            """
            
            # Send audio directly to Gemini 2.5 Flash
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
                    prompt
                ]
            )
            
            # Parse the structured JSON response cleanly
            import json
            extracted_command = json.loads(response.text.strip())
            
            if extracted_command.get("status") == "SUCCESS":
                new_row = {
                    "Account Code": extracted_command.get("account_code", "9999"),
                    "Account Name": extracted_command.get("account_name", "Voice Added Account"),
                    "Bucket": extracted_command.get("bucket", "Revenue"),
                    "Amount (£)": float(extracted_command.get("amount", 0.00))
                }
                # Append voice row safely to state
                st.session_state.manual_ledger = pd.concat([
                    st.session_state.manual_ledger, 
                    pd.DataFrame([new_row])
                ], ignore_index=True)
                st.success(f"🤖 **Gemini Voice Match:** Added '{new_row['Account Name']}' (£{new_row['Amount (£)']}) to category '{new_row['Bucket']}'!")
            else:
                st.error("⚠️ Gemini heard the voice note but could not parse clear accounting variables. Please speak clearly using format: Account Name, Code, Amount, and Category.")
                
        except Exception as e:
            st.error(f"Failed to process voice matrix: {str(e)}")

st.markdown("---")

# --- MODULE 2: MANUAL SPREADSHEET EDITOR ---
st.subheader("📋 Live Interactive Trial Balance Sheet")
st.markdown("Modify account codes, edit tracking names, adjust amounts, or add rows directly inside the data spreadsheet below:")

# st.data_editor converts a flat dataframe into a live editable grid interface
updated_ledger = st.data_editor(
    st.session_state.manual_ledger,
    num_rows="dynamic", # ◄── Enables your user to hit "+" or highlight and delete entries manually
    use_container_width=True,
    column_config={
        "Bucket": st.column_config.SelectboxColumn(
            "Accounting Allocation Bucket",
            help="Maps the manual entry line item directly into the 3-Way Core Forecast Model formulas",
            options=["Revenue", "Gross Wages", "Accruals", "Prepayments", "Stock", "WIP"],
            required=True
        ),
        "Amount (£)": st.column_config.NumberColumn(
            "Amount (£)",
            format="£%.2f",
            min_value=0.00
        )
    }
)

# Sync edits back to state clipboard
if st.button("Commit Ledger Grid Modifications to Session Memory"):
    st.session_state.manual_ledger = updated_ledger
    st.success("💾 Trial Balance alterations safely written into global application workflow.")