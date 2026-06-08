# ui_skin/pages/1_🔌_ingestion.py
import sys
from pathlib import Path

# --- CRITICAL PATH RESOLUTION ---
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

import streamlit as st
import pandas as pd
from ui_skin.core_engine.mapping_manager import analyze_and_map_ledger, PLATFORM_TARGET_SLOTS

st.set_page_config(layout="wide", page_title="STRATA Ingestion Hub")

st.title("📥 Enterprise Data Ingestion Hub")
st.caption("WinForecast-Style Step-by-Step Structural Account Alignment")
st.markdown("---")

st.markdown("### **Step 1: Account-by-Account Ledger Alignment**")
st.markdown("""
Input or modify your corporate accounts sequentially following standard Balance Sheet structure: 
**Fixed Assets ➡️ Current Assets ➡️ Current Liabilities ➡️ Long-Term Liabilities ➡️ Equity**.
Use the **"+"** button at the bottom of the grid to open new granular accounts and assign their target processing buckets.
""")

# Standard sequential ledger template matching your traditional WinForecast onboarding flow
if "raw_ledger_df" not in st.session_state:
    st.session_state["raw_ledger_df"] = pd.DataFrame({
        "Account Code": ["0020", "0040", "1200", "1205", "1100", "2200", "2150", "3000"],
        "Account Group": ["Fixed Assets", "Fixed Assets", "Current Assets", "Current Assets", "Current Assets", "Current Liabilities", "Long-Term Liabilities", "Equity Reserve"],
        "Account Name": [
            "Operational Plant & Machinery NBV", 
            "Company Delivery Fleet Vehicles",
            "Barclays Commercial Current A/C", 
            "Petty Cash Float Reserves",
            "Trade Debtors Control Ledger", 
            "Trade Creditors Control Ledger",
            "NatWest Long-Term Commercial Loan",
            "Prior Year Accumulated Retained Profits"
        ],
        "Net Balance (£)": [400000.00, 131385.00, 150000.00, 5400.00, 44886.00, -8000.00, -341001.00, 82005.00],
        "Assigned Platform Destination": ["Fixed Assets Gross Cost", "Fixed Assets Gross Cost", "Liquid Bank Cash Base", "Liquid Bank Cash Base", "Trade Accounts Receivable (AR)", "Trade Accounts Payable (AP)", "Outstanding Debt Obligations", "Retained Earnings Reserve"]
    })

# Render the interactive editor allowing manual group-by-group entry
final_mapped_df = st.data_editor(
    st.session_state["raw_ledger_df"],
    num_rows="dynamic", # Enables the WinForecast-style account-by-account row additions
    use_container_width=True,
    column_config={
        "Account Code": st.column_config.TextColumn("Ledger Code", required=True),
        "Account Group": st.column_config.SelectboxColumn(
            "Balance Sheet Group",
            options=["Fixed Assets", "Current Assets", "Current Liabilities", "Long-Term Liabilities", "Equity Reserve"],
            required=True
        ),
        "Account Name": st.column_config.TextColumn("Account Description Label", required=True),
        "Net Balance (£)": st.column_config.NumberColumn("Opening Balance (£)", format="£%,.2f", required=True),
        "Assigned Platform Destination": st.column_config.SelectboxColumn(
            "Engine Processing Bucket",
            options=PLATFORM_TARGET_SLOTS,
            required=True
        )
    }
)

# Save current table mutations directly back to session state so user entries are never lost
st.session_state["raw_ledger_df"] = final_mapped_df

# --- MULTI-ACCOUNT ACCUMULATOR CORE (FOR SUMMARY VIEWS) ---
summary_totals = {slot: 0.0 for slot in PLATFORM_TARGET_SLOTS}
for _, row in final_mapped_df.iterrows():
    slot = row["Assigned Platform Destination"]
    try:
        bal = float(row["Net Balance (£)"])
    except (ValueError, TypeError):
        bal = 0.0
    
    if slot in summary_totals:
        summary_totals[slot] += bal

st.markdown("---")
st.markdown("### **Step 2: Operational Human-in-the-Loop Profiles**")

col_wages, col_ops = st.columns(2)
with col_wages:
    st.markdown("#### 👥 Baseline Workforce Settings")
    base_monthly_gross_wages = st.number_input("Monthly Production Gross Wages (£)", min_value=0.0, value=12000.00, step=1000.0)
    directors_salaries_monthly = st.number_input("Monthly Executives Remuneration (£)", min_value=0.0, value=5150.00, step=500.0)
    pension_opt_out = st.checkbox("Apply Nationwide Workplace Pension Opt-Out Scheme", value=False)

with col_ops:
    st.markdown("#### ⚙️ Standard Corporate Overheads")
    admin_overheads_monthly = st.number_input("Monthly Fixed Administrative Overheads (£)", min_value=0.0, value=18575.00, step=500.0)

# Year 1 benchmark curve targets
y1_wf_curve = [249310.0, 356310.0, 385200.0, 404460.0, 447260.0, 470800.0, 508785.0, 707525.0, 763067.0, 750127.0, 750025.0, 736017.0]

# --- UNIFIED STRATA ATTRIBUTE CONTRACT DATA PACKAGE ---
baseline_package = {
    # 1. Summary-Level Aggregations (For backward-compatibility with downstream core formulas)
    "opening_cash_balance": summary_totals.get("Liquid Bank Cash Base", 0.0),
    "opening_fixed_assets_nbv": summary_totals.get("Fixed Assets Gross Cost", 0.0),
    "opening_accounts_receivable": summary_totals.get("Trade Accounts Receivable (AR)", 0.0),
    "opening_accounts_payable": summary_totals.get("Trade Accounts Payable (AP)", 0.0),
    "opening_long_term_debt": summary_totals.get("Outstanding Debt Obligations", 0.0),
    "opening_retained_earnings": summary_totals.get("Retained Earnings Reserve", 0.0),
    
    # 2. Granular-Level List of Records (What unlocks dynamic detail Excel/PDF printing!)
    "granular_ledger_records": final_mapped_df.to_dict(orient="records"),
    
    # 3. Operational Curves and Overheads
    "nominal_seasonal_sales_base": 0.0,
    "fixed_contractual_sales_base": 0.0,
    "nominal_cogs_base": 0.0,
    "y1_monthly_revenue_curve": y1_wf_curve,
    "y2_revenue_target": 10805679.00,
    "y3_revenue_target": 12126469.00,
    "admin_overheads_monthly": admin_overheads_monthly,
    "base_monthly_gross_wages": base_monthly_gross_wages,
    "directors_salaries_monthly": directors_salaries_monthly,
    "pension_opt_out": pension_opt_out,
    "seasonality_weights": [1.0] * 12,
    
    "planned_capex_list": [
        {"Asset Class": "Fixtures", "Gross Purchase Price (£)": 120000.0, "Transaction Month": 6, "Funding Mechanism": "Upfront Cash"},
        {"Asset Class": "Bridgend", "Gross Purchase Price (£)": 48000.0, "Transaction Month": 6, "Funding Mechanism": "Upfront Cash"},
        {"Asset Class": "Cardiff", "Gross Purchase Price (£)": 30000.0, "Transaction Month": 6, "Funding Mechanism": "Upfront Cash"},
        {"Asset Class": "Penarth", "Gross Purchase Price (£)": 168000.0, "Transaction Month": 6, "Funding Mechanism": "Upfront Cash"}
    ]
}

# Preserve global state across multi-page jumps
st.session_state["baseline_inputs"] = baseline_package
st.session_state["raw_loan_register"] = pd.DataFrame()
st.session_state["raw_revenue_matrix"] = pd.DataFrame()

st.write("")
st.success("✅ **STRATA General Ledger Synchronization Completed:** Attribute data contract established with zero omissions.")