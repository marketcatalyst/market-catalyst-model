# ui_skin/pages/1_📥_ingestion.py
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Data Ingestion Hub")

st.title("📥 Enterprise Data Ingestion Hub")
st.caption("Path A: Dynamic Trial Balance, Multi-Facility Debt Register, and Strategic Revenue Mapping")
st.markdown("---")

st.markdown("""
### **Step 1: Point-in-Time Opening Balance Sheet Seed**
Initialize the master calculation engine loop by confirming the historical opening positions.
""")

# Pre-seed defaults using the exact standalone balances found in AHOTG's May 2026 reports
col1, col2, col3 = st.columns(3)
with col1:
    opening_cash = st.number_input("Opening Bank Cash Clearing (£)", value=69488.0, step=1000.0, help="Liquid cash base inside the clearing accounts.")
    opening_ar = st.number_input("Opening Accounts Receivable (£)", value=44886.0, step=1000.0, help="Invoiced work currently awaiting client settlement.")
with col2:
    opening_fa = st.number_input("Opening Fixed Assets NBV (£)", value=150000.0, step=5000.0, help="Net Book Value of legacy plant, property, and equipment.")
    opening_ap = st.number_input("Opening Accounts Payable (£)", value=8000.0, step=1000.0, help="Unsettled supplier invoices currently on the desk.")
with col3:
    opening_debt_base = st.number_input("Opening Legacy Term Debt (£)", value=130176.0, step=5000.0, help="Cumulative payoff balance of existing historical facilities.")
    opening_re = st.number_input("Brought Forward Retained Earnings (£)", value=-82005.0, step=5000.0, help="Accumulated structural profit/loss reserve pool balance.")

st.markdown("---")

# --- 2. THE DYNAMIC MULTI-LOAN REGISTER GRID ---
st.markdown("### **Step 2: Multi-Facility Debt & Lease Register**")
st.markdown("Input active corporate credit lines, asset-backed tranches, or HP agreements. The engine automatically terminates cash outflows as remaining terms expire.")

# Core defaults extracted straight from AHOTG's legacy WinForecast schedules
default_loans_data = {
    "Facility Name": [
        "Funding Circle", 
        "IWOCA Loans", 
        "DBW Loan 13 Aug 2021", 
        "DBW Loan 27 Mar 23", 
        "DBW Loan 6 Sep 2024", 
        "Hire Purchase Loan"
    ],
    "Current Balance (£)": [12485.0, 5967.0, 5340.0, 28160.0, 80554.0, 14753.0],
    "Monthly Payment (£)": [6252.0, 1431.0, 626.0, 468.0, 2221.0, 2546.0],
    "Original Term (Months)": [24, 12, 60, 60, 60, 36],
    "Remaining Term (Months)": [2, 4, 9, 60, 36, 6]
}
default_loans_df = pd.DataFrame(default_loans_data)

loan_editor_df = st.data_editor(
    default_loans_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Facility Name": st.column_config.TextColumn("Facility Name/Lender", help="Name of the creditor institution", required=True),
        "Current Balance (£)": st.column_config.NumberColumn("Current Balance (£)", format="£%.2f", min_value=0.0),
        "Monthly Payment (£)": st.column_config.NumberColumn("Monthly Cash Repayment (£)", format="£%.2f", min_value=0.0),
        "Original Term (Months)": st.column_config.NumberColumn("Original Term (M)", min_value=1),
        "Remaining Term (Months)": st.column_config.NumberColumn("Remaining Term (M)", min_value=0, max_value=60),
    }
)

st.markdown("---")

# --- 3. GRANULAR REVENUE, COGS, & VAT RATE MAPPING GRID ---
st.markdown("### **Step 3: Strategic Profit Center & VAT Classification Matrix**")
st.markdown("Map individual commercial channels or regional sites. Tag tax classifications explicitly to automatically isolate net P&L performance from gross cash collections.")

# Pre-seed using the exact regional site layout seen in the AHOTG PDF
default_revenue_data = {
    "Channel / Site Name": [
        "Whitchurch Standard Rated Sales",
        "Whitchurch Zero Rated Sales",
        "Carmarthen Standard Rated Sales",
        "Carmarthen Zero Rated Sales",
        "Wellfield Road Standard Rated Sales",
        "Bridgend Town Centre Standard Rated Sales",
        "Cardiff Bay Standard Rated Sales",
        "Penarth Business Acquisition Sales"
    ],
    "Monthly Base Volume (£)": [15750.0, 16800.0, 14000.0, 26000.0, 31300.0, 45000.0, 34375.0, 29167.0],
    "Associated COGS Pool (£)": [6300.0, 6720.0, 5600.0, 10400.0, 12520.0, 18000.0, 13750.0, 11666.0],
    "VAT Tax Classification": [
        "Standard Rate (20%)",
        "Zero-Rated (0%)",
        "Standard Rate (20%)",
        "Zero-Rated (0%)",
        "Standard Rate (20%)",
        "Standard Rate (20%)",
        "Standard Rate (20%)",
        "Zero-Rated (0%)"
    ]
}
default_revenue_df = pd.DataFrame(default_revenue_data)

rev_editor_df = st.data_editor(
    default_revenue_df,
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "Channel / Site Name": st.column_config.TextColumn("Channel / Profit Center Destination", required=True),
        "Monthly Base Volume (£)": st.column_config.NumberColumn("Baseline Monthly Turnover (£)", format="£%.2f"),
        "Associated COGS Pool (£)": st.column_config.NumberColumn("Direct Production COGS (£)", format="£%.2f"),
        "VAT Tax Classification": st.column_config.SelectboxColumn(
            "Statutory VAT Status",
            options=["Standard Rate (20%)", "Zero-Rated (0%)", "Reduced Rate (5%)", "Exempt / Scope Out"],
            required=True
        )
    }
)

# --- 4. CONSOLIDATE AND COMMUTE TO GLOBAL MEMORY ---
# Deduce totals from live data frames to build baseline operational profiles
calculated_nominal_sales = float(rev_editor_df["Monthly Base Volume (£)"].sum())
calculated_nominal_cogs = float(rev_editor_df["Associated COGS Pool (£)"].sum())

baseline_package = {
    "nominal_seasonal_sales_base": calculated_nominal_sales / 2,
    "fixed_contractual_sales_base": calculated_nominal_sales / 2,
    "nominal_cogs_base": calculated_nominal_cogs,
    "base_monthly_gross_wages": 12000.0,
    "admin_overheads_monthly": 8000.0,
    "directors_salaries_monthly": 5150.0,  # Formal baseline assignment to clear static linter warnings
    "pension_opt_out": False,
    "seasonality_weights": [1.0] * 12,
    
    # Balance Sheet Seeds
    "opening_cash_balance": opening_cash,
    "opening_fixed_assets_nbv": opening_fa,
    "opening_accounts_receivable": opening_ar,
    "opening_accounts_payable": opening_ap,
    "opening_long_term_debt": loan_editor_df["Current Balance (£)"].sum(),
    "opening_retained_earnings": opening_re
}

# Bind into Streamlit memory state loops so screens 2 and 3 can access updates instantly
st.session_state["baseline_inputs"] = baseline_package
st.session_state["raw_loan_register"] = loan_editor_df
st.session_state["raw_revenue_matrix"] = rev_editor_df

st.success("⚡ **STRATA Data Engine Synchronized:** Ingestion configurations committed to global session state memory.")