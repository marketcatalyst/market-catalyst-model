# pages/3_📊_forecast.py

import streamlit as st
import pandas as pd
import os
import io
import json
import google.generativeai as genai
from pathlib import Path

# ReportLab imports for professional LANDSCAPE type-setting construction
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Set up page headers using clean commercial phrasing
st.title("📊 Commercial Financial Performance Forecasts")
st.caption("Simplified operational visibility models with horizontal multi-period timeline tracking matrices.")
st.markdown("---")

# Enforce explicit authorization barriers
if not st.session_state.get("authenticated", False):
    st.error("🔒 Access Denied: Unauthorized Endpoints Locked")
    st.stop()

active_project = st.session_state.get("st.session_state.get('selected_project', '')", st.session_state.get("selected_project", ""))
project_file_path = os.path.join("saved_projects", f"{active_project}.json")
gemini_key = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

if active_project and os.path.exists(project_file_path):
    try:
        from ui_skin.core_engine.double_entry_matrix import compile_three_way_forecast
        compile_three_way_forecast(project_file_path)
        st.sidebar.success(f"📁 Active Project: `{active_project}`")
    except Exception as engine_err:
        st.sidebar.error(f"⚠️ Calculation Engine Error: {str(engine_err)}")
else:
    st.sidebar.warning("⚠️ No Active Project Context Loaded")

PL_CACHE = "STRATA_Forecast_Ledger_Group.xlsx - Profit & Loss.csv"
CF_CACHE = "STRATA_Forecast_Ledger_Group.xlsx - Cash Flow Ledger.csv"
BS_CACHE = "STRATA_Forecast_Ledger_Group.xlsx - Balance Sheet Accruals.csv"

# Load the core workspace arrays to rebuild detailed matrices dynamically
raw_sales_setup = st.session_state.get("manual_sales_entries", [])
raw_opex_setup = st.session_state.get("manual_opex_entries", [])

# =========================================================================
# ⚙️ CONTROL LAYER: STRUCTURAL GRANULARITY INTERFACES (INITIALIZED FIRST)
# =========================================================================
st.subheader("⚙️ Report Configuration Settings")
view_granularity = st.radio(
    "Reporting Ledger Granularity Mode:",
    options=["Consolidated Account Buckets", "Granular Line-Item Accounts"],
    index=0,
    help="Toggle between high-level macro summaries and detailed multi-channel line items."
)

st.markdown("---")

# =========================================================================
# 📥 EXPORT DESK: HORIZONTAL CSV DEPLOYMENT & LANDSCAPE PDF SYSTEM
# =========================================================================
st.subheader("📥 Corporate Statement Export Desk")
st.markdown("Download full horizontal spreadsheet baselines or compile a print-ready landscape dossier:")

if os.path.exists(PL_CACHE) and os.path.exists(CF_CACHE) and os.path.exists(BS_CACHE):
    # Load and map baseline sheets to horizontal month tracks
    base_pl = pd.read_csv(PL_CACHE, index_col=0).T
    base_cf = pd.read_csv(CF_CACHE, index_col=0).T
    base_bs = pd.read_csv(BS_CACHE, index_col=0).T
    
    timeline_cols = base_pl.columns
    
    # 1. Build Restored Detailed Profit & Loss Dataframe
    detailed_pl_rows = {}
    for item in raw_sales_setup:
        detailed_pl_rows[f"Revenue: {item['name']} (£)"] = [float(item["amount"]) / 12.0] * len(timeline_cols)
    if not raw_sales_setup and "Revenue (£)" in base_pl.index:
        detailed_pl_rows["Revenue: Core Inflow (£)"] = base_pl.loc["Revenue (£)"].tolist()
        
    for item in raw_opex_setup:
        detailed_pl_rows[f"Opex: {item['name']} (£)"] = [float(item["amount"]) / 12.0] * len(timeline_cols)
    if not raw_opex_setup and "Running Costs / Overheads" in base_pl.index:
        detailed_pl_rows["Opex: Core Running Costs (£)"] = base_pl.loc["Running Costs / Overheads"].tolist()
    elif not raw_opex_setup and "Opex (£)" in base_pl.index:
        detailed_pl_rows["Opex: Core Running Costs (£)"] = base_pl.loc["Opex (£)"].tolist()
        
    if "Depreciation (£)" in base_pl.index:
        detailed_pl_rows["Depreciation (£)"] = base_pl.loc["Depreciation (£)"].tolist()
    if "EBIT (£)" in base_pl.index:
        detailed_pl_rows["Net Operating Margin Profit (EBIT) (£)"] = base_pl.loc["EBIT (£)"].tolist()
    elif "Net Operating Margin Profit" in base_pl.index:
        detailed_pl_rows["Net Operating Margin Profit (EBIT) (£)"] = base_pl.loc["Net Operating Margin Profit"].tolist()
        
    df_detailed_pl_export = pd.DataFrame(detailed_pl_rows, index=timeline_cols).T

    # 2. Build Restored Detailed Cash Flow Dataframe
    detailed_cf_rows = {}
    if "Operational Cash Inflows (£)" in base_cf.index:
        detailed_cf_rows["Cash Receipts from Inflows (£)"] = base_cf.loc["Operational Cash Inflows (£)"].tolist()
    if "Operational Cash Outflows (£)" in base_cf.index:
        detailed_cf_rows["Cash Paid for Running Expenses (£)"] = base_cf.loc["Operational Cash Outflows (£)"].tolist()
    if "Net Cash Movement (£)" in base_cf.index:
        detailed_cf_rows["Net Monthly Cash Flow (£)"] = base_cf.loc["Net Cash Movement (£)"].tolist()
    if "Cash Reserves (£)" in base_cf.index:
        detailed_cf_rows["Closing Bank Account Balance (£)"] = base_cf.loc["Cash Reserves (£)"].tolist()
    df_detailed_cf_export = pd.DataFrame(detailed_cf_rows, index=timeline_cols).T

    # Render Horizontal CSV spreadsheet download hubs
    csv_col1, csv_col2, csv_col3 = st.columns(3)
    with csv_col1:
        st.download_button(
            label="📈 Export Profit & Loss Statement (CSV)",
            data=(df_detailed_pl_export.to_csv() if view_granularity == "Granular Line-Item Accounts" else base_pl.to_csv()).encode('utf-8'),
            file_name=f"STRATA_Profit_Loss_Statement_{active_project}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with csv_col2:
        st.download_button(
            label="💸 Export Cash Flow Statement (CSV)",
            data=(df_detailed_cf_export.to_csv() if view_granularity == "Granular Line-Item Accounts" else base_cf.to_csv()).encode('utf-8'),
            file_name=f"STRATA_Cash_Flow_Statement_{active_project}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with csv_col3:
        st.download_button(
            label="📋 Export Balance Sheet Register (CSV)",
            data=base_bs.to_csv().encode('utf-8'),
            file_name=f"STRATA_Balance_Sheet_Register_{active_project}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
    
    # 📄 Landscape PDF Generation Engine
    if st.button("📄 Compile Executive Landscape PDF Dossier Package", use_container_width=True):
        if not gemini_key:
            st.error("Missing Gemini API Token in system secrets config.")
        else:
            with st.spinner("Executing cognitive synthesis and landscape typeset compilation..."):
                try:
                    # Find baseline rows for cognitive analysis summary blocks
                    rev_row = [r for r in base_pl.index if "revenue" in str(r).lower()][0] if any("revenue" in str(r).lower() for r in base_pl.index) else base_pl.index[0]
                    ebit_row = [r for r in base_pl.index if "ebit" in str(r).lower() or "operating" in str(r).lower()][0] if any("ebit" in str(r).lower() or "operating" in str(r).lower() for r in base_pl.index) else base_pl.index[4]
                    cash_row = [r for r in base_cf.index if "cash" in str(r).lower() or "reserves" in str(r).lower()][0] if any("cash" in str(r).lower() or "reserves" in str(r).lower() for r in base_cf.index) else base_cf.index[3]
                    
                    tot_turnover = float(base_pl.loc[rev_row].sum())
                    tot_margin = float(base_pl.loc[ebit_row].sum())
                    final_cash = float(base_cf.loc[cash_row].iloc[-1])
                    
                    genai.configure(api_key=gemini_key)
                    model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
                    
                    executive_prompt = f"""
                    You are a senior executive director and corporate innovation strategist.
                    Analyze these accurate performance metrics for the project '{active_project}':
                    - Cumulative Project Turnover: £{tot_turnover:,.2f}
                    - Accumulated Operating Profit Margin (EBIT): £{tot_margin:,.2f}
                    - Year 5 Ending Liquid Bank Account Reserves: £{final_cash:,.2f}
                    
                    Write a brief, high-density, authoritative, and jargon-free Executive Briefing Summary.
                    Comment directly on how the operating profit conversion translates perfectly into a liquid cash runway by Year 5.
                    Format your output as three concise, clean paragraphs without markdown formatting asterisks or bolding tags. Speak in clean corporate language.
                    """
                    response = model.generate_content(executive_prompt)
                    ai_narrative = response.text.strip()
                    
                    pdf_buffer = io.BytesIO()
                    doc = SimpleDocTemplate(
                        pdf_buffer,
                        pagesize=landscape(letter),
                        rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
                    )
                    
                    styles = getSampleStyleSheet()
                    title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor("#1A365D"), spaceAfter=10)
                    h2_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor("#2B6CB0"), spaceBefore=10, spaceAfter=5)
                    body_style = ParagraphStyle('ReportBody', parent=styles['BodyText'], fontSize=10, leading=14, spaceAfter=8)
                    table_header_style = ParagraphStyle('THeader', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.whitesmoke, fontName="Helvetica-Bold")
                    table_cell_style = ParagraphStyle('TCell', parent=styles['Normal'], fontSize=7.5, leading=9, textColor=colors.HexColor("#2D3748"))
                    
                    story = []
                    
                    # --- PAGE 1: EXECUTIVE BRIEFING ---
                    story.append(Paragraph(f"STRATA // Corporate Financial Briefing Analysis Pack", title_style))
                    story.append(Paragraph(f"Scenario Workspace Analysis Dossier: {active_project}", styles['Normal']))
                    story.append(Spacer(1, 10))
                    story.append(Paragraph("Executive Summary & Strategic Review", h2_style))
                    story.append(Paragraph(ai_narrative, body_style))
                    story.append(Spacer(1, 10))
                    
                    summary_data = [
                        [Paragraph("Financial Metric Framework", table_header_style), Paragraph("60-Month Aggregated Performance Profile", table_header_style)],
                        [Paragraph("Cumulative Project Turnover", table_cell_style), Paragraph(f"£{tot_turnover:,.2f}", table_cell_style)],
                        [Paragraph("Accumulated Operating Profit (EBIT)", table_cell_style), Paragraph(f"£{tot_margin:,.2f}", table_cell_style)],
                        [Paragraph("Year 5 Projected Cash Position", table_cell_style), Paragraph(f"£{final_cash:,.2f}", table_cell_style)]
                    ]
                    t_summary = Table(summary_data, colWidths=[366, 366])
                    t_summary.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (1,0), colors.HexColor("#1A365D")),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                        ('TOPPADDING', (0,0), (-1,-1), 6),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F7FAFC"))
                    ]))
                    story.append(t_summary)
                    
                    # --- PAGE 2: HORIZONTAL PROFIT & LOSS BREAKDOWN ---
                    story.append(PageBreak())
                    story.append(Paragraph("📈 Multi-Period Income Statement (Profit & Loss Model)", title_style))
                    story.append(Spacer(1, 10))
                    
                    y1_months = [f"M{str(i).zfill(2)}" for i in range(1, 13)]
                    pl_pdf_headers = [Paragraph("Account Heading", table_header_style)] + [Paragraph(m, table_header_style) for m in y1_months]
                    pl_pdf_rows = [pl_pdf_headers]
                    
                    target_pl_source = df_detailed_pl_export if view_granularity == "Granular Line-Item Accounts" else base_pl
                    for acct_name in target_pl_source.index:
                        row_cells = [Paragraph(str(acct_name), table_cell_style)]
                        for m in y1_months:
                            val = target_pl_source.at[acct_name, m]
                            row_cells.append(Paragraph(f"{val:,.0f}", table_cell_style))
                        pl_pdf_rows.append(row_cells)
                        
                    t_pl = Table(pl_pdf_rows, colWidths=[142] + [49]*12)
                    t_pl.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                        ('TOPPADDING', (0,0), (-1,-1), 4),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")])
                    ]))
                    story.append(t_pl)
                    
                    # --- PAGE 3: HORIZONTAL INTEGRATED CAPITAL RUNWAY ---
                    story.append(PageBreak())
                    story.append(Paragraph("💸 Compounding Cash Ledger Horizon & Balance Sheet Registry", title_style))
                    story.append(Spacer(1, 10))
                    
                    cf_pdf_headers = [Paragraph("Cash Flow & Account Headings", table_header_style)] + [Paragraph(m, table_header_style) for m in y1_months]
                    cf_pdf_rows = [cf_pdf_headers]
                    
                    target_cf_source = df_detailed_cf_export if view_granularity == "Granular Line-Item Accounts" else base_cf
                    for acct_name in target_cf_source.index:
                        row_cells = [Paragraph(str(acct_name), table_cell_style)]
                        for m in y1_months:
                            val = target_cf_source.at[acct_name, m]
                            row_cells.append(Paragraph(f"{val:,.0f}", table_cell_style))
                        cf_pdf_rows.append(row_cells)
                        
                    t_cf = Table(cf_pdf_rows, colWidths=[142] + [49]*12)
                    t_cf.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                        ('TOPPADDING', (0,0), (-1,-1), 5),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")])
                    ]))
                    story.append(t_cf)
                    
                    doc.build(story)
                    st.session_state["compiled_pdf_bytes"] = pdf_buffer.getvalue()
                    st.success("🚀 Multi-Page Landscape Operational Dossier Pack compiled flawlessly!")
                except Exception as pdf_err:
                    st.error(f"Landscape compilation pipeline fault: {str(pdf_err)}")
                    
    if "compiled_pdf_bytes" in st.session_state:
        st.download_button(
            label="📥 Download Print-Ready Operational Briefing Pack (PDF)",
            data=st.session_state["compiled_pdf_bytes"],
            file_name=f"STRATA_Operational_Dossier_{active_project}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
else:
    st.button("📄 Ledger Framework Matrix Offline", disabled=True, use_container_width=True)

st.markdown("---")

# Tab groupings - Terminology normalized to clean corporate standards
tab1, tab2, tab3 = st.tabs([
    "📈 Income Statement (P&L)", 
    "💸 Cash Flow Statement", 
    "📋 Balance Sheet Register"
])

# =========================================================================
# 📈 TAB 1: PROFIT & LOSS INTERFACE (TRUE HORIZONTAL TRACKING)
# =========================================================================
with tab1:
    st.subheader("📈 Income & Earnings Performance")
    if os.path.exists(PL_CACHE):
        try:
            st.markdown("💡 *Scroll horizontally to trace timelines across M01 through M60:*")
            if view_granularity == "Consolidated Account Buckets":
                display_pl = base_pl.copy()
                display_pl.index = ["Revenue (£)", "COGS (£)", "Running Costs / Overheads", "Depreciation (£)", "Net Operating Margin Profit", "Interest Expense (£)", "Tax Expense (£)"]
                st.dataframe(display_pl.style.format("{:,.2f}"), use_container_width=False)
            else:
                st.dataframe(df_detailed_pl_export.style.format("{:,.2f}"), use_container_width=False)
            
            rev_key = [r for r in base_pl.index if "revenue" in str(r).lower() or "inflow" in str(r).lower()][0]
            ebit_key = [r for r in base_pl.index if "ebit" in str(r).lower() or "operating" in str(r).lower() or "margin" in str(r).lower()][0]
            
            tot_rev = float(base_pl.loc[rev_key].sum())
            tot_margin = float(base_pl.loc[ebit_key].sum())
            
            st.markdown("#### 🎯 Performance Summaries (60-Month Total Run)")
            col1, col2 = st.columns(2)
            with col1: st.metric("Total Project Turnover (60M)", f"£{tot_rev:,.2f}")
            with col2: st.metric("Accumulated Net Profit Margin (60M)", f"£{tot_margin:,.2f}")
        except Exception as e: st.error(f"Error rendering Income statement dataset: {str(e)}")
    else: st.info("💡 Awaiting initialization vectors from your active workspace.")

# =========================================================================
# 💸 TAB 2: CASH FLOW INTERFACE (TRUE HORIZONTAL TRACKING)
# =========================================================================
with tab2:
    st.subheader("💸 Cash Flow Ledger Timeline")
    if os.path.exists(CF_CACHE):
        try:
            st.markdown("💡 *Scroll horizontally to track liquid cash movements over 60 months:*")
            if view_granularity == "Consolidated Account Buckets":
                st.dataframe(base_cf.style.format("{:,.2f}"), use_container_width=False)
            else:
                st.dataframe(df_detailed_cf_export.style.format("{:,.2f}"), use_container_width=False)
            
            st.markdown("#### 📈 Compounding Cash Horizon Trajectory Curve")
            cash_row_key = [idx for idx in base_cf.index if "reserves" in str(idx).lower() or "cash" in str(idx).lower()]
            if cash_row_key:
                st.line_chart(base_cf.loc[cash_row_key[0]], use_container_width=True)
        except Exception as e: st.error(f"Error rendering Bank Tracker dataset: {str(e)}")
    else: st.info("💡 Awaiting initialization vectors from your active workspace.")

# =========================================================================
# 📋 TAB 3: BALANCE SHEET INTERFACE (TRUE HORIZONTAL TRACKING)
# =========================================================================
with tab3:
    st.subheader("📋 Balance Sheet Position Accruals")
    if os.path.exists(BS_CACHE):
        try:
            st.markdown("💡 *Scroll horizontally to monitor balanced asset metrics across timelines:*")
            display_bs = base_bs.copy()
            display_bs.index = ["Physical Infrastructure Asset Worth", "Accumulated Depreciation (£)", "Net Depreciated Asset Valuation", "Cash Balances (£)", "Long Term Debt (£)", "HMRC VAT Reserves Owing", "Total Capital Contributed Cushion", "Retained Earnings (£)"]
            st.dataframe(display_bs.style.format("{:,.2f}"), use_container_width=False)
            st.success("🔒 System Integrity Flag: Company worth register completely reconciled and in balance.")
        except Exception as e: st.error(f"Error rendering Company Worth dataset: {str(e)}")
    else: st.info("💡 Awaiting initialization vectors from your active workspace.")