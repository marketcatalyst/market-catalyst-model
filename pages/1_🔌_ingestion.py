import sys
from pathlib import Path

# --- 1. CRITICAL PATH RESOLUTION ---
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List, Optional

st.set_page_config(layout="wide", page_title="STRATA Ingestion Engine")

# --- 2. SECURITY GATEKEEPER CONSTRAINT ---
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("🔒 **Access Denied: Unauthorized Endpoints Locked**")
    st.info("Please return to the main portal landing page and authenticate your corporate credentials to unlock this session.")
    if st.button("Return to Portal Landing Page", use_container_width=True):
        st.switch_page("home.py")
    st.stop()

st.title("🔌 Corporate Data Ingestion & Mapping Suite")
st.caption("Synchronize Trial Balances, Map Account Architectures, and Configure Location Tax Schedules")
st.markdown("---")

# --- 3. BULLETPROOF SESSION MEMORY SEEDING LAYER (PURGED TO CLEAN SLATE) ---
if "baseline_inputs" not in st.session_state:
    st.session_state["baseline_inputs"] = {}

inputs_ref = st.session_state["baseline_inputs"]

if "opening_cash_balance" not in inputs_ref: inputs_ref["opening_cash_balance"] = 0.00
if "opening_fixed_assets_nbv" not in inputs_ref: inputs_ref["opening_fixed_assets_nbv"] = 0.00
if "admin_overheads_monthly" not in inputs_ref: inputs_ref["admin_overheads_monthly"] = 0.00
if "base_monthly_gross_wages" not in inputs_ref: inputs_ref["base_monthly_gross_wages"] = 0.00
if "directors_salaries_monthly" not in inputs_ref: inputs_ref["directors_salaries_monthly"] = 0.00
if "pension_opt_out" not in inputs_ref: inputs_ref["pension_opt_out"] = True
if "y1_monthly_revenue_curve" not in inputs_ref: inputs_ref["y1_monthly_revenue_curve"] = [0.0] * 12

if "debt_facilities" not in inputs_ref:
    inputs_ref["debt_facilities"] = [
        {"Facility Name Description": "New Facility Entry", "Opening Principal Balance (£)": 0.00, "Annual Interest Rate (%)": 0.00, "Contractual Amortization Term (Months)": 12}
    ]

if "sales_locations" not in inputs_ref:
    inputs_ref["sales_locations"] = [
        {"Trading Location Name": "Primary Site", "Corporate Revenue Share (%)": 100.0, "Zero-Rated / Exempt Mix (%)": 0.0}
    ]

# --- 4. STRUCTURAL OCR SCHEMA ENFORCEMENT LAYER ---
class IngestedInvoiceItem(BaseModel):
    vendor_name: str = Field(description="Name of the corporate vendor issuing the transaction document.")
    document_date: Optional[str] = Field(description="The formal transaction or invoice date detected (YYYY-MM-DD format if possible).")
    net_amount: float = Field(description="Total operational balance excluding VAT / taxes.")
    vat_amount: float = Field(description="Total aggregated tax allocation value recorded.")
    gross_amount: float = Field(description="Total final transaction processing amount.")
    suggested_ledger_category: str = Field(description="Classification string, e.g., Admin Overheads, Staff Cost, Capital Asset, Debt Repayment.")

# --- 5. STEP 1: MULTIMODAL DATA & LEDGER INGESTION (OCR PIPELINE ACTIVE) ---
st.markdown("### **Step 1: Multimodal Ledger, Invoice, & Receipt Ingestion**")
st.caption("Upload structured tabular manifests (CSV/XLSX) or scan raw document layouts (PDF/JPEG/PNG) via the pipeline engine.")

uploaded_document = st.file_uploader(
    label="Drop Corporate Document Payload (CSV, XLSX, PDF, JPEG, PNG)",
    type=["csv", "xlsx", "pdf", "jpeg", "jpg", "png"],
    accept_multiple_files=False,
    key="strata_multimodal_uploader"
)

if uploaded_document is not None:
    file_ext = uploaded_document.name.split(".")[-1].lower()
    
    # Pathway A: Structured Tabular Parsers
    if file_ext in ["csv", "xlsx"]:
        try:
            if file_ext == "csv":
                parsed_df = pd.read_csv(uploaded_document)
            else:
                parsed_df = pd.read_excel(uploaded_document)
            
            st.success(f"✔️ **Tabular Parsing Successful:** '{uploaded_document.name}' mapped into staging memory space.")
            with st.expander("🔍 Preview Ingested Schema Structure"):
                st.dataframe(parsed_df.head(5), use_container_width=True)
            inputs_ref["raw_ingested_ledger_df"] = parsed_df
        except Exception as e:
            st.error(f"❌ **Data Ingestion Error:** Failed to map incoming ledger rows. Details: {str(e)}")
            
    # Pathway B: Multimodal GenAI OCR Pipeline Engine
    elif file_ext in ["pdf", "jpeg", "jpg", "png"]:
        # Verify API Environment Anchor Safely
        if "GENAI_API_KEY" not in st.secrets and not sys.environ.get("GEMINI_API_KEY"):
            st.error("⚠️ **OCR Credentials Fault:** No valid API keys found in runtime secrets configuration matrix.")
        else:
            with st.spinner("🧠 Initializing Multimodal OCR Analysis Engine..."):
                try:
                    # Instantiate client utilizing the modern SDK pattern
                    client = genai.Client()
                    file_bytes = uploaded_document.read()
                    
                    # Convert file extension to mime-type signatures
                    mime_map = {"pdf": "application/pdf", "jpeg": "image/jpeg", "jpg": "image/jpeg", "png": "image/png"}
                    mime_type = mime_map[file_ext]
                    
                    # Build Part objects for processing
                    document_part = types.Part.from_bytes(
                        data=file_bytes,
                        mime_type=mime_type,
                    )
                    
                    prompt = """
                    You are a premium corporate audit assistant. 
                    Examine this unstructured transactional document closely. Extract the core fiscal elements 
                    and categorize them precisely based on the requested structural output format parameters.
                    """
                    
                    # Call modern flagship engine forcing target strict structural constraints
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=[document_part, prompt],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=IngestedInvoiceItem,
                            temperature=0.1
                        ),
                    )
                    
                    # Parse validated response schema directly into data matrix
                    validated_output = IngestedInvoiceItem.model_validate_json(response.text)
                    
                    st.success(f"🔥 **OCR Extraction Complete:** Extracted unstructured artifacts with high confidence verification mapping.")
                    
                    # Display extracted variables as metrics fields
                    m_col1, m_col2, m_col3 = st.columns(3)
                    with m_col1:
                        st.metric(label="Vendor Identity", value=validated_output.vendor_name)
                        st.metric(label="Extracted Net Amount", value=f"£{validated_output.net_amount:,.2f}")
                    with m_col2:
                        st.metric(label="Transaction Date", value=str(validated_output.document_date))
                        st.metric(label="Extracted VAT Amount", value=f"£{validated_output.vat_amount:,.2f}")
                    with m_col3:
                        st.metric(label="Suggested Allocation", value=validated_output.suggested_ledger_category)
                        st.metric(label="Gross Amount", value=f"£{validated_output.gross_amount:,.2f}")
                    
                    # Cache structured data for system-wide accessibility loops
                    inputs_ref["last_ocr_extraction"] = validated_output.model_dump()
                    
                except Exception as e:
                    st.error(f"❌ **OCR Pipeline Execution Error:** Structural normalization failure. Details: {str(e)}")

st.markdown("---")

# --- 6. STEP 2: CORE OPERATIONS RUN-RATES ---
st.markdown("### **Step 2: Core Operations Run-Rates**")
col1, col2, col3 = st.columns(3)
with col1:
    admin_input = st.number_input("Monthly Admin Overheads (£):", value=float(inputs_ref["admin_overheads_monthly"]), step=500.0, format="%.2f")
with col2:
    wages_input = st.number_input("Monthly Gross Staff Wages (£):", value=float(inputs_ref["base_monthly_gross_wages"]), step=500.0, format="%.2f")
with col3:
    pension_toggle = st.checkbox("Statutory Auto-Enrolment Opt-Out", value=inputs_ref["pension_opt_out"])

# --- 7. STEP 3: DYNAMIC DEBT LIABILITIES CONFIGURATOR ---
st.markdown("---")
st.markdown("### **Step 3: Corporate Debt Liabilities Amortization Grid**")
current_debt_df = pd.DataFrame(inputs_ref["debt_facilities"])

edited_debt_df = st.data_editor(
    current_debt_df, num_rows="dynamic", use_container_width=True, key="debt_editor_v3",
    column_config={
        "Facility Name Description": st.column_config.TextColumn("Facility Name Description", required=True),
        "Opening Principal Balance (£)": st.column_config.NumberColumn("Opening Principal Balance (£)", format="£%,.2f", min_value=0.0, required=True),
        "Annual Interest Rate (%)": st.column_config.NumberColumn("Annual Interest Rate (%)", format="%.2f%%", min_value=0.0, required=True),
        "Contractual Amortization Term (Months)": st.column_config.NumberColumn("Contractual Amortization Term (Months)", format="%d", min_value=1, required=True),
    }
)

# --- 8. STEP 4: DYNAMIC MULTI-SHOP SALES TRACKER ---
st.markdown("---")
st.markdown("### **Step 4: Multi-Shop Revenue & VAT Profile Allocation**")
st.caption("Allocate corporate revenue share weights and local tax attributes. Total Corporate Revenue Share MUST sum to 100%.")

current_locations_df = pd.DataFrame(inputs_ref["sales_locations"])
edited_locations_df = st.data_editor(
    current_locations_df, num_rows="dynamic", use_container_width=True, key="location_editor_v3",
    column_config={
        "Trading Location Name": st.column_config.TextColumn("Trading Location Name", required=True),
        "Corporate Revenue Share (%)": st.column_config.NumberColumn("Corporate Revenue Share (%)", format="%.1f%%", min_value=0.0, max_value=100.0, required=True),
        "Zero-Rated / Exempt Mix (%)": st.column_config.NumberColumn("Zero-Rated / Exempt Mix (%)", format="%.1f%%", min_value=0.0, max_value=100.0, required=True),
    }
)

total_share_entered = edited_locations_df["Corporate Revenue Share (%)"].sum() if not edited_locations_df.empty else 0
if abs(total_share_entered - 100.0) > 0.01:
    st.warning(f"⚠️ **Total Revenue Share Warning:** Your current location shares total **{total_share_entered:.1f}%**. Please adjust rows so they sum up to exactly 100.0%.")

# --- 9. SAVE AND EMIT INPUTS PIPELINE ---
st.markdown("---")
if st.button("💾 Lock and Synchronize System Attributes", use_container_width=True):
    # Process Debt Rows Defensively
    formatted_debt_list = []
    for _, row in edited_debt_df.iterrows():
        name = row.get("Facility Name Description", row.get("Facility Name", "Corporate Loan"))
        bal = row.get("Opening Principal Balance (£)", row.get("Opening Balance (£)", 0.0))
        rate = row.get("Annual Interest Rate (%)", 0.0)
        term = row.get("Contractual Amortization Term (Months)", row.get("Term (Months)", 60))
        
        formatted_debt_list.append({
            "facility_name": name, 
            "opening_balance": float(bal),
            "interest_rate_annual": float(rate) / 100.0, 
            "term_months": int(term)
        })
        
    # Process Location Rows Defensively
    formatted_locations_list = []
    for _, row in edited_locations_df.iterrows():
        name = row.get("Trading Location Name", row.get("Site Location Name", "Retail Outlet"))
        share = row.get("Corporate Revenue Share (%)", 0.0)
        zero_mix = row.get("Zero-Rated / Exempt Mix (%)", row.get("Zero-Rated Mix (%)", 0.0))
        
        std_share = (100.0 - float(zero_mix)) / 100.0
        formatted_locations_list.append({
            "site_name": name,
            "revenue_share": float(share) / 100.0,
            "standard_rated_share": std_share
        })
        
    # Commit directly to the persistent master state dictionary
    inputs_ref["admin_overheads_monthly"] = admin_input
    inputs_ref["base_monthly_gross_wages"] = wages_input
    inputs_ref["pension_opt_out"] = pension_toggle
    inputs_ref["debt_facilities"] = edited_debt_df.to_dict(orient="records")
    inputs_ref["debt_facilities_clean"] = formatted_debt_list
    inputs_ref["sales_locations"] = edited_locations_df.to_dict(orient="records")
    inputs_ref["sales_locations_clean"] = formatted_locations_list
    
    st.success("🎉 System parameters synchronized! Multi-shop location profiles and local VAT mixes successfully locked down.")