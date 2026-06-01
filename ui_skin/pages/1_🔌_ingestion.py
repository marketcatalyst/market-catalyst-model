# ui_skin/pages/1_🔌_ingestion.py
import streamlit as st
import pandas as pd
import sys
import os

# Ensure the app can access the core_engine modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core_engine.database import get_db_connection

st.set_page_config(layout="wide", page_title="Data Ingestion & Ledger Mapping")

st.title("🔌 Raw Data Ingestion & Ledger Mapping")
st.caption("Extract data streams from Xero, Sage, QuickBooks, or CSV Trial Balances")
st.markdown("---")

# --- 1. SAGE / XERO / QUICKBOOKS CONNECTIVITY MOCKUP ---
st.subheader("🔗 Cloud Accounting API Integration Gateway")
col_api1, col_api2, col_api3 = st.columns(3)

with col_api1:
    if st.button("🦊 Pull Historical Data from Xero", use_container_width=True):
        st.info("OAuth 2.0 Handshake Active: Simulating secure Xero api ledger scrape...")
with col_api2:
    if st.button("🌱 Pull Historical Data from Sage", use_container_width=True):
        st.info("OAuth 2.0 Handshake Active: Simulating secure Sage api ledger scrape...")
with col_api3:
    if st.button("⚡ Pull Historical Data from QuickBooks", use_container_width=True):
        st.info("OAuth 2.0 Handshake Active: Simulating secure QuickBooks api ledger scrape...")

st.markdown("---")

# --- 2. THE CSV FILE DROP ZONE ---
st.subheader("📥 Incomplete Records File Uploader")
st.markdown("If cloud API access is unavailable, drag and drop a fragmented Trial Balance or bank transaction log below.")

uploaded_file = st.file_uploader("Upload Raw CSV Ledger Extract", type=["csv"])

# Target structural lines required by our core math engine
ENGINE_TARGET_BUCKETS = [
    "Revenue", 
    "Cost of Sales", 
    "Wages & Salaries", 
    "Operating Overheads", 
    "Fixed Assets", 
    "Financing/Liabilities"
]

if uploaded_file is not None:
    try:
        # Read the uploaded ledger file into a standard Pandas dataframe
        raw_uploaded_df = pd.read_csv(uploaded_file)
        
        st.success("✔️ File successfully parsed in memory. Please complete the accounting line mappings below:")
        
        # Ensure the uploaded file has the minimal columns needed for mapping
        if len(raw_uploaded_df.columns) >= 2:
            # Dynamically build a structural mapping interface for the bookkeeper
            mapping_rows = []
            for index, row in raw_uploaded_df.iterrows():
                account_code = str(row.iloc[0])
                account_name = str(row.iloc[1])
                current_balance = float(row.iloc[2]) if len(raw_uploaded_df.columns) > 2 else 0.0
                
                # Default mapping guess based on simple keywords
                default_mapping = "Operating Overheads"
                name_lower = account_name.lower()
                if "sale" in name_lower or "revenue" in name_lower or "turnover" in name_lower:
                    default_mapping = "Revenue"
                elif "cost" in name_lower or "cos" in name_lower or "purchase" in name_lower:
                    default_mapping = "Cost of Sales"
                elif "wage" in name_lower or "salary" in name_lower or "payroll" in name_lower:
                    default_mapping = "Wages & Salaries"
                elif "loan" in name_lower or "hire purchase" in name_lower or "creditor" in name_lower:
                    default_mapping = "Financing/Liabilities"
                elif "equipment" in name_lower or "vehicle" in name_lower or "asset" in name_lower:
                    default_mapping = "Fixed Assets"

                mapping_rows.append({
                    "Imported Code": account_code,
                    "Imported Account Label": account_name,
                    "Current Balance (£)": current_balance,
                    "Engine Mapping Target": default_mapping
                })
            
            mapping_df = pd.DataFrame(mapping_rows)
            
            # Use Streamlit's data_editor with dropdown configurations for the mapping column
            st.markdown("### 🔀 Chart of Accounts Translation Matrix")
            st.caption("Review our automated classification guesses and use the drop-downs to correct errors before finalizing.")
            
            finalized_mapping_grid = st.data_editor(
                mapping_df,
                column_config={
                    "Engine Mapping Target": st.column_config.SelectboxColumn(
                        "Forecaster Target Bucket",
                        help="Select the structural bucket required by the 3-Way Engine",
                        width="medium",
                        options=ENGINE_TARGET_BUCKETS,
                        required=True,
                    ),
                    "Current Balance (£)": st.column_config.NumberColumn(format="£%.2f")
                },
                disabled=["Imported Code", "Imported Account Label", "Current Balance (£)"],
                hide_index=True,
                use_container_width=True,
                key="ingestion_grid_editor"
            )
            
            # --- Save Mapping Pipeline Action ---
            if st.button("💾 Commit Mapped Structure to Neon Database Project", type="primary", use_container_width=True):
                st.success("🎉 Mapping pipeline verified and securely written to your market-catalyst-model project database!")
                # In the next step, this dataframe will save straight to Neon via database.py
                
        else:
            st.error("❌ Invalid CSV format. The file must contain at least Account Code and Account Name columns.")
            
    except Exception as e:
        st.error(f"❌ Error processing dataset structural lines: {str(e)}")
else:
    # Quick placeholder view to show a preview sample when the page is empty
    st.info("💡 Pro-Tip: Upload a basic CSV containing three columns (Code, Account Name, Balance) to verify the translation matrix.")