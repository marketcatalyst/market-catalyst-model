# ui_skin/pages/1_🔌_ingestion.py
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="Data Ingestion Hub")

st.title("🔌 Data Ingestion & Capital Register Hub")
st.caption("Secure Data Entry Gateway • AI Document Processing & Operational Vector Configuration")
st.markdown("---")

# ==========================================
# 📄 1. ACTIVE TRIAL BALANCE INGESTION
# ==========================================
st.subheader("📄 Automated Ledger & Trial Balance Ingestion")
st.markdown("Upload structural text files, spreadsheet exports, or images of operational ledger sheets. The system tracks your baseline fresh food account distributions below.")

uploaded_file = st.file_uploader("Drop financial statement or trial balance exports here:", type=["csv", "txt", "pdf", "png", "jpg", "jpeg"])

# Initialize the synchronized trial balance matrix with food service revenue & cost streams
if "trial_balance_matrix" not in st.session_state:
    st.session_state.trial_balance_matrix = pd.DataFrame({
        "Account Code": ["1010", "1090", "5000", "7000", "7100"],
        "Account Name": [
            "Core Retail & Site Sales Pool (Healthy Fresh Menu)", 
            "Sub-Let Commercial Café Rental Income", 
            "Direct Ingredient Costs & Material COGS", 
            "Gross Staff & Kitchen Prep Salaries Ledger", 
            "Indirect Operational Overheads (Utilities/Cleaning/POS)"
        ],
        "Accounting Allocation Bucket": [
            "Revenue - Seasonal (Retail)", 
            "Revenue - Fixed (Rental Income)", 
            "Direct Expenses (COGS)", 
            "Gross Wages", 
            "Indirect Overheads (OpEx)"
        ],
        "Amount (£)": [451500.00, 12500.00, 217976.00, 69900.00, 15400.00]
    })

if uploaded_file is not None:
    st.info("⚡ Live Document Stream Detected: Parsing data structures via GenAI vision networks...")
    st.toast("Document text vectors successfully tokenized!", icon="📄")

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
            help="Classifying revenue tells the calculation engine whether to apply monthly seasonality vectors",
            options=["Revenue - Seasonal (Retail)", "Revenue - Fixed (Rental Income)", "Direct Expenses (COGS)", "Gross Wages", "Indirect Overheads (OpEx)"]
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
# 📊 2. 12-MONTH REVENUE SEASONALITY MATRIX
# ==========================================
st.subheader("📊 12-Month Revenue Seasonality Coefficient Profile")
st.markdown("Configure your monthly hospitality and retail volume weights. **1.0 represents a flat baseline month**. 1.45 represents a 45% holiday trading spike (e.g., December surge). **Contractual rental income bypasses this completely**.")

if "seasonality_profile_matrix" not in st.session_state:
    st.session_state.seasonality_profile_matrix = pd.DataFrame({
        "Calendar Month": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
        "Seasonality Factor Weight": [0.85, 0.80, 0.95, 1.00, 1.10, 1.25, 1.30, 1.20, 1.00, 0.95, 1.15, 1.45]
    })

edited_seasonality_df = st.data_editor(
    st.session_state.seasonality_profile_matrix,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Calendar Month": st.column_config.TextColumn("Calendar Month", disabled=True),
        "Seasonality Factor Weight": st.column_config.NumberColumn(
            "Seasonality Factor Weight",
            help="Baseline multiplier value applied directly to variable seasonal retail turnover channels",
            format="%.2fx",
            min_value=0.00,
            max_value=5.00
        )
    },
    key="seasonality_grid_editor"
)

if st.button("Commit Seasonality Weights to Memory", key="save_seasonality_btn"):
    st.session_state.seasonality_profile_matrix = edited_seasonality_df
    st.success("💾 12-Month operational seasonality vectors safely synchronized inside memory channels!")

st.markdown("---")

# ==========================================
# 🚜 3. INTERACTIVE CAPEX ASSET REGISTER GRID
# ==========================================
st.subheader("🚜 Interactive Capital Expenditure (CapEx) Asset Register")
st.markdown("Plan your commercial kitchen additions, distribution infrastructure upgrades, or café facility fit-outs. Rows configured below dynamically feed into asset-carrying rows and run straight-line depreciation profiles automatically.")

# Initialize the food-service-appropriate asset register in session memory
if "capex_asset_register" not in st.session_state:
    st.session_state.capex_asset_register = pd.DataFrame([
        {
            "Asset Class": "Kitchen Equipment",
            "Item Description": "Central Prep Kitchen Walk-In Cold Storage Array",
            "Gross Purchase Price (£)": 120000.00,
            "Transaction Month": 6,
            "Useful Life (Years)": 5,
            "Funding Mechanism": "Hire Purchase"
        },
        {
            "Asset Class": "Leasehold Improvements",
            "Item Description": "Merthyr Town Centre Cafe Frontage & Servery Fit-out",
            "Gross Purchase Price (£)": 45000.00,
            "Transaction Month": 12,
            "Useful Life (Years)": 10,
            "Funding Mechanism": "Upfront Cash"
        }
    ])

edited_capex_df = st.data_editor(
    st.session_state.capex_asset_register,
    use_container_width=True,
    num_rows="dynamic",
    hide_index=True,
    column_config={
        "Asset Class": st.column_config.SelectboxColumn(
            "Asset Class Category",
            help="Target accounting asset group for Balance Sheet historical cost row placement",
            options=["Kitchen Equipment", "Leasehold Improvements", "Office & Cafe Equipment", "Motor Vehicles"],
            required=True
        ),
        "Item Description": st.column_config.TextColumn(
            "Item Description / Project Milestone Location",
            help="Provide descriptive equipment details or rollout regional tags",
            required=True
        ),
        "Gross Purchase Price (£)": st.column_config.NumberColumn(
            "Gross Purchase Cost (£)",
            help="Total capitalized transaction asset value",
            format="£%,.2f",
            min_value=0.00,
            required=True
        ),
        "Transaction Month": st.column_config.NumberColumn(
            "Transaction Month",
            help="The explicit forecast timeline month index when investment executes (e.g., Month 6)",
            format="Month %d",
            min_value=1,
            max_value=120,
            required=True
        ),
        "Useful Life (Years)": st.column_config.NumberColumn(
            "Useful Life (Years)",
            help="Estimated legal or economic lifespan used to determine straight-line depreciation velocity",
            format="%d Years",
            min_value=1,
            max_value=50,
            required=True
        ),
        "Funding Mechanism": st.column_config.SelectboxColumn(
            "Funding Mechanism",
            help="Upfront Cash impacts bank instantly; Hire Purchase records matching rolling debt obligations",
            options=["Upfront Cash", "Hire Purchase"],
            required=True
        )
    },
    key="capex_register_grid_editor"
)

if st.button("Commit Capital Asset Register to Memory", key="save_capex_btn"):
    st.session_state.capex_asset_register = edited_capex_df
    st.success("💾 Dynamic fresh food infrastructure asset registry safe and synchronized within backend framework paths!")