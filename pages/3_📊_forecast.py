# pages/3_📊_forecast.py
import streamlit as st
import sys
from pathlib import Path

# Absolute project path resolution to handle multi-page layout shifts smoothly
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from ui_skin.core_engine.master_model import generate_integrated_3way_forecast
from ui_skin.core_engine.report_generator import export_forecast_to_excel
from ui_skin.core_engine.pdf_generator import generate_pdf_executive_summary

# Line 1 Gatekeeper Execution Shield
if not st.session_state.get("authenticated", False) or "baseline_inputs" not in st.session_state:
    st.warning("🛡️ Active session credentials or project data missing. Re-authenticate via the Security Gateway.")
    st.stop()

st.title("📊 Integrated Financial Forecast Ledger")
st.caption(f"Active Environment: {st.session_state.get('username', 'Standard Admin').capitalize()} Management Matrix")

# Global CSS override injector to force absolute centering on dataframe column headers
st.markdown(
    """
    <style>
        /* Target Streamlit's custom data grid table column headers */
        th [data-testid="stHeaderBlock"] {
            justify-content: center !important;
            text-align: center !important;
        }
        /* Fallback alignment selector for basic data rendering blocks */
        .stDataFrame th {
            text-align: center !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

inputs = st.session_state["baseline_inputs"]

# Check for manual overrides from the sandbox session if they exist
overrides = {
    "volume_delta": st.session_state.get("sandbox_volume_delta", 0.0),
    "opex_delta": st.session_state.get("sandbox_opex_delta", 0.0)
}

# Run the integration calculation pipeline
with st.spinner("Compiling multi-shop three-way projections..."):
    try:
        forecast_df = generate_integrated_3way_forecast(inputs, overrides)
    except Exception as calc_error:
        st.error(f"Engine Calculation Error: {str(calc_error)}")
        st.stop()

# Programmatic NumberColumn configurations to handle formatting and headers cleanly
currency_formatter = {
    "Revenue (£)": st.column_config.NumberColumn("Revenue", format="£ %,.0f"),
    "COGS (£)": st.column_config.NumberColumn("COGS", format="£ %,.0f"),
    "Opex (£)": st.column_config.NumberColumn("Opex", format="£ %,.0f"),
    "EBIT (£)": st.column_config.NumberColumn("EBIT", format="£ %,.0f"),
    "Debt Service Cash Outflow (£)": st.column_config.NumberColumn("Debt Service Outflow", format="£ %,.0f"),
    "VAT Cash Outflow (£)": st.column_config.NumberColumn("VAT Outflow", format="£ %,.0f"),
    "Cash Reserves (£)": st.column_config.NumberColumn("Cash Reserves", format="£ %,.0f"),
    "VAT Liability BS (£)": st.column_config.NumberColumn("VAT Liability", format="£ %,.0f"),
    "Tax Liability BS (£)": st.column_config.NumberColumn("Tax Liability", format="£ %,.0f"),
    "Outstanding Debt Balance (£)": st.column_config.NumberColumn("Outstanding Debt", format="£ %,.0f")
}

# Display interactive reporting tables
tab1, tab2, tab3 = st.tabs(["📈 Profit & Loss", "💰 Cash Flow Runway", "🏛️ HMRC Tax & Debt Accruals"])

with tab1:
    st.subheader("60-Month Operating Income Statement")
    st.markdown("Tracks operational revenues, direct costs of goods sold, overhead run-rates, and calculated operating profit margins.")
    st.dataframe(
        forecast_df[["Revenue (£)", "COGS (£)", "Opex (£)", "EBIT (£)"]],
        column_config=currency_formatter,
        use_container_width=True
    )

with tab2:
    st.subheader("Liquidity Profile & Bank Account Balances")
    st.markdown("Monitors real cash movements reflecting physical outlays, debt servicing burdens, and staggered statutory direct debits.")
    st.dataframe(
        forecast_df[["EBIT (£)", "Debt Service Cash Outflow (£)", "VAT Cash Outflow (£)", "Cash Reserves (£)"]],
        column_config=currency_formatter,
        use_container_width=True
    )

with tab3:
    st.subheader("Statutory Balance Sheet Liabilities Tracking")
    st.markdown("Accumulates non-cash operational provisions, unpaid quarterly VAT blocks, and remaining contractual credit principals.")
    st.dataframe(
        forecast_df[["VAT Liability BS (£)", "Tax Liability BS (£)", "Outstanding Debt Balance (£)"]],
        column_config=currency_formatter,
        use_container_width=True
    )

st.markdown("---")
st.subheader("💾 Export Financial Intelligence Report")
st.markdown("Compile and download active scenario configurations as formatted corporate-ready outputs.")

# Extract trading name safe string for filename labeling
trading_name = "Group"
if "sales_locations" in inputs and inputs["sales_locations"]:
    trading_name = inputs["sales_locations"][0].get("Trading Location Name", "Group")
elif "sales_locations_clean" in inputs and inputs["sales_locations_clean"]:
    trading_name = inputs["sales_locations_clean"][0].get("site_name", "Group")
safe_trading_string = trading_name.replace(' ', '_')

# Create two clean distribution columns for buttons
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    try:
        excel_data = export_forecast_to_excel(inputs, overrides)
        st.download_button(
            label="📥 Export Complete Ledger (.xlsx)",
            data=excel_data,
            file_name=f"STRATA_Forecast_Ledger_{safe_trading_string}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Excel Generator Error: {str(e)}")

with btn_col2:
    try:
        pdf_data = generate_pdf_executive_summary(inputs, overrides)
        st.download_button(
            label="📄 Export Executive Briefing (.pdf)",
            data=pdf_data,
            file_name=f"STRATA_Executive_Summary_{safe_trading_string}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"PDF Generator Error: {str(e)}")