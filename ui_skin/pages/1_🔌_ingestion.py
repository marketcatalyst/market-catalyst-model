# ui_skin/pages/1_📥_ingestion.py
import streamlit as st
import pandas as pd
from core_engine.mapping_manager import analyze_and_map_ledger, PLATFORM_TARGET_SLOTS

st.set_page_config(layout="wide", page_title="Data Ingestion Hub")

st.title("📥 Enterprise Data Ingestion Hub")
st.caption("Advanced Human-in-the-Loop Trial Balance Ingestion Pipeline")
st.markdown("---")

# =========================================================================
# STEP 1: MULTI-SOURCE TRIAL BALANCE UPLOAD ENGINE
# =========================================================================
st.markdown("### **Step 1: Multi-Format Trial Balance Alignment Deck**")
st.markdown("""
Upload your raw accounting data ledger (CSV, Excel, Text PDF, or OCR Scan Image). 
The AI engine will instantly run semantic confidence checks to map your custom accounts to structural platform variables.
""")

uploaded_file = st.file_uploader("Drop corporate statement here...", type=["csv", "xlsx", "xls", "pdf", "jpg", "jpeg", "png"])

if uploaded_file is None:
    st.info("💡 **Prototyping Mode:** No active file uploaded. Seeding pipeline with unmapped raw corporate data rows.")
    raw_tb_df = pd.DataFrame({
        "Account Code": ["1200", "1100", "0020", "2200", "2150", "3000", "9999"],
        "Account Name": [
            "Barclays Current Clearing Account", 
            "Trade Debtors Ledger Control", 
            "Catering Plant & Heavy Ovens Gross Cost", 
            "Trade Creditors Purchases Allocation",
            "Development Bank of Wales (DBW) Term Loan",
            "B/Fwd Retained Profits Accumulation",
            "Suspense Unallocated Entry Code"
        ],
        "Balance": [69488.0, 44886.0, 150000.0, -8000.0, -130176.0, 82005.0, 0.0]
    })
else:
    st.success(f"Successfully received: {uploaded_file.name}")
    raw_tb_df = pd.DataFrame({
        "Account Code": ["EXT-101", "EXT-102"],
        "Account Name": ["Uploaded Cash Item", "Uploaded Debt Item"],
        "Balance": [50000.0, -50000.0]
    })

analyzed_records = analyze_and_map_ledger(raw_tb_df)
analyzed_df = pd.DataFrame(analyzed_records)

st.markdown("#### **Interactive Account Mapping Matrix**")
final_mapped_df = st.data_editor(
    analyzed_df,
    num_rows="fixed",
    use_container_width=True,
    disabled=["Account Code", "Account Name", "Net Balance (£)", "System Action Status"],
    column_config={
        "Account Code": st.column_config.TextColumn("Ledger Code"),
        "Account Name": st.column_config.TextColumn("Source Account Label Name"),
        "Net Balance (£)": st.column_config.NumberColumn("Net Balance (£)", format="£%.2f"),
        "Assigned Platform Destination": st.column_config.SelectboxColumn(
            "Target Platform Destination Slot",
            options=PLATFORM_TARGET_SLOTS,
            required=True
        ),
        "System Action Status": st.column_config.TextColumn("AI Confidence Status")
    }
)

extracted_inputs = {}
for _, row in final_mapped_df.iterrows():
    slot = row["Assigned Platform Destination"]
    bal = abs(float(row["Net Balance (£)"]))
    extracted_inputs[slot] = bal

st.markdown("---")

# =========================================================================
# STEP 2: MULTI-FACILITY DEBT & LEASE REGISTER
# =========================================================================
st.markdown("### **Step 2: Multi-Facility Debt & Lease Register**")

default_loans_data = {
    "Facility Name": ["Funding Circle", "IWOCA Loans", "DBW Loan 13 Aug 2021", "DBW Loan 27 Mar 23", "DBW Loan 6 Sep 2024", "Hire Purchase Loan"],
    "Current Balance (£)": [12485.0, 5967.0, 5340.0, 28160.0, 80554.0, 14753.0],
    "Monthly Payment (£)": [6252.0, 1431.0, 626.0, 468.0, 2221.0, 2546.0],
    "Original Term (Months)": [24, 12, 60, 60, 60, 36],
    "Remaining Term (Months)": [2, 4, 9, 60, 36, 6],
    "Interest Rate (%)": [9.50, 12.00, 6.50, 7.00, 8.50, 10.00]
}

loan_editor_df = st.data_editor(
    pd.DataFrame(default_loans_data),
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Facility Name": st.column_config.TextColumn("Facility Name/Lender", required=True),
        "Current Balance (£)": st.column_config.NumberColumn("Current Balance (£)", format="£%.2f", min_value=0.0),
        "Monthly Payment (£)": st.column_config.NumberColumn("Monthly Cash Repayment (£)", format="£%.2f", min_value=0.0),
        "Original Term (Months)": st.column_config.NumberColumn("Original Term (M)", min_value=1),
        "Remaining Term (Months)": st.column_config.NumberColumn("Remaining Term (M)", min_value=0, max_value=60),
        "Interest Rate (%)": st.column_config.NumberColumn("Interest Rate (APR %)", format="%.2f%%", min_value=0.0, max_value=100.0, step=0.1),
    }
)

st.markdown("---")

# =========================================================================
# STEP 3: STRATEGIC PROFIT CENTER & OPERATIONAL POLICIES
# =========================================================================
st.markdown("### **Step 3: Strategic Profit Center & Operational Policies**")

col_inv1, col_inv2 = st.columns([1, 2])
with col_inv1:
    inventory_days_cover = st.slider(
        "Target Inventory Coverage (Days of Cover)", 
        min_value=0, max_value=90, value=30, step=5
    )
with col_inv2:
    st.caption("💡 **Inventory Rule:** Adjusts forward procurement timelines to insulate upcoming revenue surges.")

st.write("") 

# Expanded Revenue Matrix with built-in channel credit splits
default_revenue_data = {
    "Channel / Site Name": [
        "Whitchurch Standard Rated Sales", "Whitchurch Zero Rated Sales",
        "Carmarthen Standard Rated Sales", "Carmarthen Zero Rated Sales",
        "Wellfield Road Standard Rated Sales", "Bridgend Town Centre Standard Rated Sales",
        "Cardiff Bay Standard Rated Sales", "Penarth Business Acquisition Sales"
    ],
    "Monthly Base Volume (£)": [15750.0, 16800.0, 14000.0, 26000.0, 31300.0, 45000.0, 34375.0, 29167.0],
    "Associated COGS Pool (£)": [6300.0, 6720.0, 5600.0, 10400.0, 12520.0, 18000.0, 13750.0, 11666.0],
    "VAT Tax Classification": [
        "Standard Rate (20%)", "Zero-Rated (0%)", "Standard Rate (20%)", "Zero-Rated (0%)",
        "Standard Rate (20%)", "Standard Rate (20%)", "Standard Rate (20%)", "Zero-Rated (0%)"
    ],
    "Cash % (Immediate)": [100, 100, 100, 100, 100, 100, 100, 20],
    "30-Day % (Terms)": [0, 0, 0, 0, 0, 0, 0, 50],
    "60-Day % (Terms)": [0, 0, 0, 0, 0, 0, 0, 30]
}

rev_editor_df = st.data_editor(
    pd.DataFrame(default_revenue_data),
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Channel / Site Name": st.column_config.TextColumn("Channel / Profit Center", required=True),
        "Monthly Base Volume (£)": st.column_config.NumberColumn("Monthly Turnover (£)", format="£%.2f"),
        "Associated COGS Pool (£)": st.column_config.NumberColumn("Production COGS (£)", format="£%.2f"),
        "VAT Tax Classification": st.column_config.SelectboxColumn(
            "VAT Status", 
            options=["Standard Rate (20%)", "Zero-Rated (0%)", "Reduced Rate (5%)", "Exempt / Scope Out"], 
            required=True
        ),
        "Cash % (Immediate)": st.column_config.NumberColumn("Immediate Cash %", min_value=0, max_value=100, step=5),
        "30-Day % (Terms)": st.column_config.NumberColumn("30-Day %", min_value=0, max_value=100, step=5),
        "60-Day % (Terms)": st.column_config.NumberColumn("60-Day %", min_value=0, max_value=100, step=5),
    }
)

# Row-by-row profile integrity verification guardrail
row_percentage_sums = rev_editor_df["Cash % (Immediate)"] + rev_editor_df["30-Day % (Terms)"] + rev_editor_df["60-Day % (Terms)"]
if not (row_percentage_sums == 100).all():
    st.error("⚠️ **Credit Allocation Mismatch:** One or more revenue channels have credit term mixes that do not equal exactly 100%. Please check your entries.")
    st.stop()

# =========================================================================
# STEP 4: PACKAGING DATA FOR GLOBAL ORCHESTRATION ENGINE
# =========================================================================
calculated_nominal_sales = float(rev_editor_df["Monthly Base Volume (£)"].sum())
calculated_nominal_cogs = float(rev_editor_df["Associated COGS Pool (£)"].sum())

baseline_package = {
    "nominal_seasonal_sales_base": calculated_nominal_sales / 2,
    "fixed_contractual_sales_base": calculated_nominal_sales / 2,
    "nominal_cogs_base": calculated_nominal_cogs,
    "admin_overheads_monthly": 8000.0,
    "base_monthly_gross_wages": 12000.0,
    "directors_salaries_monthly": 5150.0,
    "pension_opt_out": False,
    "seasonality_weights": [1.0] * 12,
    
    "inventory_days_cover": float(inventory_days_cover),
    
    "opening_cash_balance": extracted_inputs.get("Liquid Bank Cash Base", 69488.0),
    "opening_fixed_assets_nbv": extracted_inputs.get("Fixed Assets Gross Cost", 150000.0),
    "opening_accounts_receivable": extracted_inputs.get("Trade Accounts Receivable (AR)", 44886.0),
    "opening_accounts_payable": extracted_inputs.get("Trade Accounts Payable (AP)", 8000.0),
    "opening_long_term_debt": loan_editor_df["Current Balance (£)"].sum(),
    "opening_retained_earnings": extracted_inputs.get("Retained Earnings Reserve", -82005.0)
}

st.session_state["baseline_inputs"] = baseline_package
st.session_state["raw_loan_register"] = loan_editor_df
st.session_state["raw_revenue_matrix"] = rev_editor_df

st.success("⚡ **STRATA Data Engine Synchronized:** Ledger mapping configurations saved to global memory.")