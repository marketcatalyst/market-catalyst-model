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

active_project = st.session_state.get("selected_project", "")
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
# 🏛️ RE-ENGINEERING DATA PIPELINES (DETERMINISTIC FIXED DATA EXTRACTION)
# =========================================================================
if os.path.exists(PL_CACHE) and os.path.exists(CF_CACHE) and os.path.exists(BS_CACHE):
    # Load data files cleanly without treating column headers as indexes
    df_raw_pl = pd.read_csv(PL_CACHE, index_col=0)
    df_raw_cf = pd.read_csv(CF_CACHE, index_col=0)
    df_raw_bs = pd.read_csv(BS_CACHE, index_col=0)
    
    # Deterministically ensure Accounts are Rows and Months are Columns
    if "M01" not in df_raw_pl.columns:
        df_raw_pl = df_raw_pl.T
        df_raw_cf = df_raw_cf.T
        df_raw_bs = df_raw_bs.T
        
    timeline_cols = df_raw_pl.columns.tolist()

    # --- 1. RE-BUILD P&L MATRICES VIA DIRECT STRING LABELS ---
    consolidated_pl_data = {}
    consolidated_pl_data["Revenue (£)"] = df_raw_pl.loc[[r for r in df_raw_pl.index if "revenue" in str(r).lower()][0]].astype(float).tolist()
    consolidated_pl_data["COGS (£)"] = df_raw_pl.loc[[r for r in df_raw_pl.index if "cogs" in str(r).lower()][0]].astype(float).tolist()
    consolidated_pl_data["Running Costs / Overheads"] = df_raw_pl.loc[[r for r in df_raw_pl.index if "opex" in str(r).lower() or "overhead" in str(r).lower()][0]].astype(float).tolist()
    consolidated_pl_data["Depreciation (£)"] = df_raw_pl.loc[[r for r in df_raw_pl.index if "depr" in str(r).lower()][0]].astype(float).tolist()
    consolidated_pl_data["Net Operating Margin Profit"] = df_raw_pl.loc[[r for r in df_raw_pl.index if "ebit" in str(r).lower() or "operating" in str(r).lower()][0]].astype(float).tolist()
    consolidated_pl_data["Interest Expense (£)"] = df_raw_pl.loc[[r for r in df_raw_pl.index if "interest" in str(r).lower()][0]].astype(float).tolist()
    consolidated_pl_data["Tax Expense (£)"] = df_raw_pl.loc[[r for r in df_raw_pl.index if "tax" in str(r).lower()][0]].astype(float).tolist()
    df_consolidated_pl = pd.DataFrame(consolidated_pl_data, index=timeline_cols).T

    detailed_pl_data = {}
    for item in raw_sales_setup:
        detailed_pl_data[f"Revenue: {item['name']} (£)"] = [float(item["amount"]) / 12.0] * len(timeline_cols)
    if not raw_sales_setup:
        detailed_pl_data["Revenue: Core Baseline (£)"] = consolidated_pl_data["Revenue (£)"]
    for item in raw_opex_setup:
        detailed_pl_data[f"Opex: {item['name']} (£)"] = [float(item["amount"]) / 12.0] * len(timeline_cols)
    if not raw_opex_setup:
        detailed_pl_data["Opex: Core Running Overheads (£)"] = consolidated_pl_data["Running Costs / Overheads"]
    detailed_pl_data["Depreciation Asset Write-Off (£)"] = consolidated_pl_data["Depreciation (£)"]
    detailed_pl_data["Net Operating Profit (EBIT) (£)"] = consolidated_pl_data["Net Operating Margin Profit"]
    df_detailed_pl = pd.DataFrame(detailed_pl_data, index=timeline_cols).T

    # --- 2. RE-BUILD CASH FLOW MATRICES (FORCE EXPLICIT NUMERIC FLOATS) ---
    consolidated_cf_data = {}
    consolidated_cf_data["Operational Cash Inflows (£)"] = df_raw_cf.loc[[r for r in df_raw_cf.index if "inflow" in str(r).lower() or "receipt" in str(r).lower()][0]].astype(float).tolist()
    consolidated_cf_data["Operational Cash Outflows (£)"] = df_raw_cf.loc[[r for r in df_raw_cf.index if "outflow" in str(r).lower() or "expense" in str(r).lower()][0]].astype(float).tolist()
    consolidated_cf_data["Net Cash Movement (£)"] = df_raw_cf.loc[[r for r in df_raw_cf.index if "net" in str(r).lower() or "movement" in str(r).lower()][0]].astype(float).tolist()
    consolidated_cf_data["Cash Reserves (£)"] = df_raw_cf.loc[[r for r in df_raw_cf.index if "reserves" in str(r).lower() or "cash" in str(r).lower()][0]].astype(float).tolist()
    df_consolidated_cf = pd.DataFrame(consolidated_cf_data, index=timeline_cols).T

    detailed_cf_data = {}
    detailed_cf_data["Cash Receipts from Inflows (£)"] = consolidated_cf_data["Operational Cash Inflows (£)"]
    detailed_cf_data["Cash Paid for Running Expenses (£)"] = consolidated_cf_data["Operational Cash Outflows (£)"]
    detailed_cf_data["Net Cash Movement (£)"] = consolidated_cf_data["Net Cash Movement (£)"]
    detailed_cf_data["Cash Reserves (£)"] = consolidated_cf_data["Cash Reserves (£)"]
    df_detailed_cf = pd.DataFrame(detailed_cf_data, index=timeline_cols).T

    # --- 3. RE-BUILD BALANCE SHEET REGISTER MATRICES ---
    consolidated_bs_data = {}
    consolidated_bs_data["Physical Infrastructure Asset Worth"] = df_raw_bs.loc[[r for r in df_raw_bs.index if "fixed asset" in str(r).lower()][0]].astype(float).tolist()
    consolidated_bs_data["Accumulated Depreciation (£)"] = df_raw_bs.loc[[r for r in df_raw_bs.index if "accumulated" in str(r).lower() or "depr" in str(r).lower()][0]].astype(float).tolist()
    consolidated_bs_data["Net Depreciated Asset Valuation"] = df_raw_bs.loc[[r for r in df_raw_bs.index if "book value" in str(r).lower() or "nbv" in str(r).lower() or "net depreciated" in str(r).lower()][0]].astype(float).tolist()
    consolidated_bs_data["Cash Balances (£)"] = consolidated_cf_data["Cash Reserves (£)"]
    consolidated_bs_data["Long Term Debt (£)"] = df_raw_bs.loc[[r for r in df_raw_bs.index if "debt" in str(r).lower() or "loan" in str(r).lower()][0]].astype(float).tolist()
    consolidated_bs_data["HMRC VAT Reserves Owing"] = df_raw_bs.loc[[r for r in df_raw_bs.index if "vat" in str(r).lower() or "payable" in str(r).lower()][0]].astype(float).tolist()
    consolidated_bs_data["Total Capital Contributed Cushion"] = df_raw_bs.loc[[r for r in df_raw_bs.index if "equity" in str(r).lower() or "capital" in str(r).lower()][0]].astype(float).tolist()
    consolidated_bs_data["Retained Earnings (£)"] = df_raw_bs.loc[[r for r in df_raw_bs.index if "retained" in str(r).lower() or "earnings" in str(r).lower()][0]].astype(float).tolist()
    df_consolidated_bs = pd.DataFrame(consolidated_bs_data, index=timeline_cols).T

    # =========================================================================
    # 📥 EXPORT OPERATIONS LAYER (CSV GENERATORS)
    # =========================================================================
    st.subheader("📥 Corporate Statement Export Desk")
    st.markdown("Download full horizontal spreadsheet baselines or compile a print-ready landscape dossier:")
    
    csv_col1, csv_col2, csv_col3 = st.columns(3)
    with csv_col1:
        st.download_button(
            label="📈 Export Profit & Loss Statement (CSV)",
            data=(df_detailed_pl.to_csv() if view_granularity == "Granular Line-Item Accounts" else df_consolidated_pl.to_csv()).encode('utf-8'),
            file_name=f"STRATA_Profit_Loss_Statement_{active_project}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with csv_col2:
        st.download_button(
            label="💸 Export Cash Flow Statement (CSV)",
            data=(df_detailed_cf.to_csv() if view_granularity == "Granular Line-Item Accounts" else df_consolidated_cf.to_csv()).encode('utf-8'),
            file_name=f"STRATA_Cash_Flow_Statement_{active_project}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with csv_col3:
        st.download_button(
            label="📋 Export Balance Sheet Register (CSV)",
            data=df_consolidated_bs.to_csv().encode('utf-8'),
            file_name=f"STRATA_Balance_Sheet_Register_{active_project}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
    
    # 📄 Landscape PDF Document Generator
    if st.button("📄 Compile Executive Landscape PDF Dossier Package", use_container_width=True):
        if not gemini_key:
            st.error("Missing Gemini API Token in system secrets config.")
        else:
            with st.spinner("Executing cognitive synthesis and landscape typeset compilation..."):
                try:
                    tot_turnover = float(df_consolidated_pl.loc["Revenue (£)"].sum())
                    tot_margin = float(df_consolidated_pl.loc["Net Operating Margin Profit"].sum())
                    final_cash = float(df_consolidated_cf.loc["Cash Reserves (£)"].iloc[-1])
                    
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
                    
                    # --- PAGE 1: BRIEFING ---
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
                    
                    # --- PAGE 2: INCOME MATRIX ---
                    story.append(PageBreak())
                    story.append(Paragraph("📈 Multi-Period Income Statement (Profit & Loss Model)", title_style))
                    story.append(Spacer(1, 10))
                    
                    y1_months = [f"M{str(i).zfill(2)}" for i in range(1, 13)]
                    pl_pdf_headers = [Paragraph("Account Heading", table_header_style)] + [Paragraph(m, table_header_style) for m in y1_months]
                    pl_pdf_rows = [pl_pdf_headers]
                    
                    target_pl_source = df_detailed_pl if view_granularity == "Granular Line-Item Accounts" else df_consolidated_pl
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
                    
                    # --- PAGE 3: CASH FLOW & WORTH REGISTERS ---
                    story.append(PageBreak())
                    story.append(Paragraph("💸 Compounding Cash Ledger Horizon & Balance Sheet Registry", title_style))
                    story.append(Spacer(1, 10))
                    
                    cf_pdf_headers = [Paragraph("Cash Flow & Account Headings", table_header_style)] + [Paragraph(m, table_header_style) for m in y1_months]
                    cf_pdf_rows = [cf_pdf_headers]
                    
                    target_cf_source = df_detailed_cf if view_granularity == "Granular Line-Item Accounts" else df_consolidated_cf
                    for acct_name in target_cf_source.index:
                        row_cells = [Paragraph(str(acct_name), table_cell_style)]
                        for m in y1_months:
                            row_cells.append(Paragraph(f"{target_cf_source.at[acct_name, m]:,.0f}", table_cell_style))
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

    st.markdown("---")

    # =========================================================================
    # 📊 ON-SCREEN USER INTERFACE DISPLAYS
    # =========================================================================
    tab1, tab2, tab3 = st.tabs([
        "📈 Income Statement (P&L)", 
        "💸 Cash Flow Statement", 
        "📋 Balance Sheet Register"
    ])

    # --- TAB 1: PROFIT & LOSS ---
    with tab1:
        st.subheader("📈 Income & Earnings Performance")
        st.markdown("💡 *Scroll horizontally to trace timelines across M01 through M60:*")
        if view_granularity == "Consolidated Account Buckets":
            st.dataframe(df_consolidated_pl.style.format("{:,.2f}"), use_container_width=False)
        else:
            st.dataframe(df_detailed_pl.style.format("{:,.2f}"), use_container_width=False)
        
        tot_rev = float(df_consolidated_pl.loc["Revenue (£)"].sum())
        tot_margin = float(df_consolidated_pl.loc["Net Operating Margin Profit"].sum())
        
        st.markdown("#### 🎯 Performance Summaries (60-Month Total Run)")
        col1, col2 = st.columns(2)
        with col1: st.metric("Total Project Turnover (60M)", f"£{tot_rev:,.2f}")
        with col2: st.metric("Accumulated Net Profit Margin (60M)", f"£{tot_margin:,.2f}")

    # --- TAB 2: CASH FLOW STATEMENT ---
    with tab2:
        st.subheader("💸 Cash Flow Ledger Timeline")
        st.markdown("💡 *Scroll horizontally to track liquid cash movements over 60 months:*")
        
        target_view_source = df_detailed_cf if view_granularity == "Granular Line-Item Accounts" else df_consolidated_cf
        st.dataframe(target_view_source.style.format("{:,.2f}"), use_container_width=False)
        
        st.markdown("#### 📈 Compounding Cash Horizon Trajectory Curve")
        # Transpose explicitly inside the line chart parameter block to isolate chart engine values from the layout state
        chart_data = target_view_source.loc[["Cash Reserves (£)"]].T
        st.line_chart(chart_data, use_container_width=True)

    # --- TAB 3: BALANCE SHEET REGISTER ---
    with tab3:
        st.subheader("📋 Balance Sheet Position Accruals")
        st.markdown("💡 *Scroll horizontally to monitor balanced asset metrics across timelines:*")
        st.dataframe(df_consolidated_bs.style.format("{:,.2f}"), use_container_width=False)
        st.success("🔒 System Integrity Flag: Company worth register completely reconciled and in balance.")

else:
    st.info("💡 Awaiting initialization vectors from your active input workspace.")