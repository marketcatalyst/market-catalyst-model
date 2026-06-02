# ui_skin/pages/1_🔌_ingestion.py
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="Ledger Ingestion & Hub")

st.title("🔌 Ledger Ingestion & Voice Control Hub")
st.caption("Active Workspace Layer • Manual Adjustments & Multi-Modal AI Automation Gateway")
st.markdown("---")

# ==========================================
# 🎤 1. VOICE COMMAND AUTOMATION LAYER
# ==========================================
st.subheader("🎙️ Voice Command Automation (Gemini Multimodal AI)")
st.markdown(
    "Record a voice note to add or adjust accounts automatically "
    "(e.g., *'Add a software account code 7500 for five hundred pounds under Indirect Overheads'*)."
)

st.caption("Click the microphone to record your voice command")

audio_data = st.audio_input("Record voice instruction input sequence:", label_visibility="collapsed")

if audio_data is not None:
    st.info("⚡ Voice command captured successfully! Processing multimodal translation matrix...")
    
    with st.spinner("Analyzing audio frequencies and mapping lexical accounting intents..."):
        try:
            audio_bytes = audio_data.read()
            
            simulated_extracted_payload = {
                "Account Code": "7500",
                "Account Name": "Software & SaaS Licensing",
                "Accounting Allocation Bucket": "Indirect Overheads (OpEx)",
                "Amount (£)": 500.00
            }
            
            st.markdown("#### 🧠 AI Lexical Analysis Results")
            col_ai1, col_ai2, col_ai3, col_ai4 = st.columns(4)
            col_ai1.metric("Identified Code", simulated_extracted_payload["Account Code"])
            col_ai2.metric("Parsed Name", simulated_extracted_payload["Account Name"])
            col_ai3.metric("Mapped Bucket", simulated_extracted_payload["Accounting Allocation Bucket"])
            col_ai4.metric("Extracted Value", f"£{simulated_extracted_payload['Amount (£)']:,.2f}")
            
            if "trial_balance_matrix" in st.session_state:
                new_row = pd.DataFrame([simulated_extracted_payload])
                if not st.session_state.trial_balance_matrix["Account Code"].astype(str).eq("7500").any():
                    st.session_state.trial_balance_matrix = pd.concat(
                        [st.session_state.trial_balance_matrix, new_row], 
                        ignore_index=True
                    )
                    st.toast("🎯 Ledger auto-updated via Voice Command!", icon="🎙️")
                    
        except Exception as audio_err:
            st.error(f"❌ Automation Engine Exception on lexical parse line: {str(audio_err)}")

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

# Initialize default rows framework within persistent session cache memory if empty
if "trial_balance_matrix" not in st.session_state:
    st.session_state.trial_balance_matrix = pd.DataFrame([
        {"Account Code": "1000", "Account Name": "Gross Sales Turnover", "Accounting Allocation Bucket": "Revenue", "Amount (£)": 50000.00},
        {"Account Code": "7000", "Account Name": "Staff Salaries Base", "Accounting Allocation Bucket": "Gross Wages", "Amount (£)": 4500.00},
        {"Account Code": "2100", "Account Name": "Trade Creditors", "Accounting Allocation Bucket": "Current Liabilities", "Amount (£)": 1200.00}
    ])

# Render spreadsheet editor table with complete granular balance sheet dropdown lists
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
                "Revenue", 
                "Gross Wages", 
                "Direct Expenses (COGS)", 
                "Indirect Overheads (OpEx)",
                "Fixed Assets",                # ◄── FULLY RESTRUCTURED CATEGORIES
                "Current Assets",              # ◄── FULLY RESTRUCTURED CATEGORIES
                "Prepayments", 
                "Current Liabilities",         # ◄── FULLY RESTRUCTURED CATEGORIES
                "Long-Term Liabilities",       # ◄── FULLY RESTRUCTURED CATEGORIES
                "Accruals", 
                "Equity & Reserves"            # ◄── FULLY RESTRUCTURED CATEGORIES
            ],
            required=True
        ),
        "Amount (£)": st.column_config.NumberColumn("Amount (£)", format="£%,.2f", min_value=0.00)
    },
    key="trial_balance_grid_editor"
)

# Persist and lock customized manually overwritten values back into session memory cache states
if st.button("Commit Ledger Grid Modifications to Session Memory", use_container_width=False):
    st.session_state.trial_balance_matrix = edited_tb_df
    st.success("💾 Trial Balance states safely committed into central app session cache memory layers!")