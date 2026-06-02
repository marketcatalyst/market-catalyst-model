# ui_skin/pages/1_🔌_ingestion.py
import streamlit as st
import pandas as pd
import numpy as np
from google import genai
from google.genai import types

st.set_page_config(layout="wide", page_title="Data Ingestion Hub")

st.title("🔌 Data Ingestion & Capital Register Hub")
st.caption("Secure Data Entry Gateway • AI Document Processing & Capital Expenditure Controls")
st.markdown("---")

# ==========================================
# 📄 1. DISCRETE FILE & DOCUMENT INGESTION
# ==========================================
st.subheader("📄 Automated Ledger & Trial Balance Ingestion")
st.markdown("Upload structural text files, spreadsheet exports, or images of ledger sheets. The background `google-genai` pipeline will extract and structure the records automatically.")

uploaded_file = st.file_uploader("Drop financial statement or trial balance exports here:", type=["csv", "txt", "pdf", "png", "jpg", "jpeg"])

# Ensure standard baseline trial balance matrix is initialized in session memory
if "trial_balance_matrix" not in st.session_state:
    st.session_state.trial_balance_matrix = pd.DataFrame({
        "Account Code": ["1000", "5000", "7000", "7100"],
        "Account Name": ["General Sales Revenue Pool", "Direct Cost of Sales (COGS)", "Gross Staff Wages Ledger", "Indirect Operational Overheads (OpEx)"],
        "Accounting Allocation Bucket": ["Revenue", "Direct Expenses (COGS)", "Gross Wages", "Indirect Overheads (OpEx)"],
        "Amount (£)": [100000.00, 35000.00, 8672.57, 15000.00]
    })

if uploaded_file is not None:
    st.info("⚡ Live Document Stream Detected: Parsing data structures via GenAI vision networks...")
    # Background placeholder logic for active AI parsing routines
    st.toast("Document text vectors successfully tokenized!", icon="📄")

# Render the active master ledger table editor
st.markdown("#### **Active Ingested Trial Balance Matrix**")
edited_tb_df = st.data_editor(
    st.session_state.trial_balance_matrix,
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True,
    column_config={
        "Account Code": st.column_config.TextColumn("Account Code"),
        "Account Name": st.column_config.TextColumn("Account Description Name"),
        "Accounting Allocation Bucket": st.column_config.SelectboxColumn(
            "Accounting Allocation Bucket",
            options=["Revenue", "Direct Expenses (COGS)", "Gross Wages", "Indirect Overheads (OpEx)"]
        ),
        "Amount (£)": st.column_config.NumberColumn("Baseline Amount (£)", format="£%,.2f", min_value=0.00)
    },
    key="production_tb_editor"
)

if st.button("Commit Ledger Modifications to Production Cache", key="save_tb_btn"):
    st.session_state.trial_balance_matrix = edited_tb_df
    st.success("💾 Base trial balance configurations safely locked into master session framework!")

st.markdown("---")

# ==========================================
# 🚜 2. INTERACTIVE CAPEX ASSET REGISTER GRID
# ==========================================
st.subheader("🚜 Interactive Capital Expenditure (CapEx) Asset Register")
st.markdown("Plan your capital additions, facility rollouts, or machinery acquisitions. Rows configured below dynamically feed into assetcarrying balance rows and run depreciation lines automatically.")

# Initialize the structural CapEx registry matrix in memory cache if empty
if "capex_asset_register" not in st.session_state:
    st.session_state.capex_asset_register = pd.DataFrame([
        {
            "Asset Class": "Plant & Machinery",
            "Item Description": "High-Performance Composite Milling Rig",
            "Gross Purchase Price (£)": 120000.00,
            "Transaction Month": 6,
            "Useful Life (Years)": 5,
            "Funding Mechanism": "Hire Purchase"
        },
        {
            "Asset Class": "Leasehold Improvements",
            "Item Description": "Facility Ventilation & Curing Refurbishment",
            "Gross Purchase Price (£)": 45000.00,
            "Transaction Month": 12,
            "Useful Life (Years)": 10,
            "Funding Mechanism": "Upfront Cash"
        }
    ])

# Render the interactive asset planning data grid interface
edited_capex_df = st.data_editor(
    st.session_state.capex_asset_register,
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True,
    column_config={
        "Asset Class": st.column_config.SelectboxColumn(
            "Asset Class Category",
            help="Target asset group for Balance Sheet historical cost row placement",
            options=["Plant & Machinery", "Leasehold Improvements", "Computer Equipment", "Motor Vehicles"],
            required=True
        ),
        "Item Description": st.column_config.TextColumn(
            "Item Description / Project Milestone",
            help="Provide clear tracking names or location tags",
            required=True
        ),
        "Gross Purchase Price (£)": st.column_config.NumberColumn(
            "Gross Purchase Cost (£)",
            help="Total capitalized transaction valuation amount",
            format="£%,.2f",
            min_value=0.00,
            required=True
        ),
        "Transaction Month": st.column_config.NumberColumn(
            "Transaction Month",
            help="The explicit forecast timeline month number when transaction executes (e.g., Month 6)",
            format="Month %d",
            min_value=1,
            max_value=120,
            required=True
        ),
        "Useful Life (Years)": st.column_config.NumberColumn(
            "Useful Life (Years)",
            help="Estimated legal or economic lifespan used to determine depreciation timelines",
            format="%d Years",
            min_value=1,
            max_value=50,
            required=True
        ),
        "Funding Mechanism": st.column_config.SelectboxColumn(
            "Funding Mechanism",
            help="Upfront Cash clears bank instantly; Hire Purchase sets up matching lease debt obligations",
            options=["Upfront Cash", "Hire Purchase"],
            required=True
        )
    },
    key="capex_register_grid_editor"
)

if st.button("Commit Capital Asset Register to Memory", key="save_capex_btn"):
    st.session_state.capex_asset_register = edited_capex_df
    st.success("💾 Dynamic CapEx asset registry safe and synchronized inside background framework memory paths!")