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

def render_polished_html_table(df_slice, headers_map):
    """
    Renders a beautifully responsive HTML table with absolute centered 
    headers and clean, right-aligned currency cells to bypass Streamlit grid limits.
    """
    # Shared enterprise styling block
    html_markup = """
    <style>
        .corporate-table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'Source Sans Pro', sans-serif;
            margin: 10px 0 25px 0;
        }
        .corporate-table th {
            background-color: #f0f2f6;
            color: #31333f;
            text-align: center !important;
            font-weight: 600;
            padding: 10px;
            border: 1px solid #dcdcdc;
        }
        .corporate-table td {
            padding: 10px;
            border: 1px solid #edf0f5;
            text-align: right;
        }
        .corporate-table td.timeline-cell {
            text-align: left;
            font-weight: bold;
            background-color: #fafafa;
            width: 10%;
        }
        .corporate-table tr:nth-child(even) {
            background-color: #f9fbfd;
        }
    </style>
    <table class="corporate-table">
        <thead>
            <tr>
                <th style="text-align: left !important;">Timeline</th>
    """
    
    # Append centered headers
    for original_col, clean_name in headers_map.items():
        html_markup += f"<th>{clean_name}</th>"
    html_markup += "</tr></thead><tbody>"
    
    # Append data rows with currency formatting
    for index, row in df_slice.iterrows():
        html_markup += f"<tr><td class='timeline-cell'>{index}</td>"
        for original_col in headers_map.keys():
            val = row[original_col]
            html_markup += f"<td>£ {val:,.0f}</td>"
        html_markup += "</tr>"
        
    html_markup += "</tbody></table>"
    st.markdown(html_markup, unsafe_allow_html=True)

# Display interactive reporting tables
tab1, tab2, tab3 = st.tabs(["📈 Profit & Loss", "💰 Cash Flow Runway", "🏛️ HMRC Tax & Debt Accruals"])

with tab1:
    st.subheader("60-Month Operating Income Statement")
    st.markdown("Tracks operational revenues, direct costs of goods sold, overhead run-rates, and calculated operating profit margins.")
    render_polished_html_table(
        forecast_df, 
        {"Revenue (£)": "Revenue", "COGS (£)": "COGS", "Opex (£)": "Opex", "EBIT (£)": "EBIT"}
    )

with tab2:
    st.subheader("Liquidity Profile & Bank Account Balances")
    st.markdown("Monitors real cash movements reflecting physical outlays, debt servicing burdens, and staggered statutory direct debits.")
    render_polished_html_table(
        forecast_df, 
        {
            "EBIT (£)": "EBIT", 
            "Debt Service Cash Outflow (£)": "Debt Service Outflow", 
            "VAT Cash Outflow (£)": "VAT Outflow", 
            "Cash Reserves (£)": "Cash Reserves"
        }
    )

with tab3:
    st.subheader("Statutory Balance Sheet Liabilities Tracking")
    st.markdown("Accumulates non-cash operational provisions, unpaid quarterly VAT blocks, and remaining contractual credit principals.")
    render_polished_html_table(
        forecast_df, 
        {
            "VAT Liability BS (£)": "VAT Liability", 
            "Tax Liability BS (£)": "Tax Liability", 
            "Outstanding Debt Balance (£)": "Outstanding Debt"
        }
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