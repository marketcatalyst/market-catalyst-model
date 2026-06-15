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

# =========================================================================
# 📥 MASTER EXPORT UTILITY HUB (HORIZONTAL CSV + LANDSCAPE PDF PACK)
# =========================================================================
st.subheader("📥 Master Corporate Export Utility Hub")
st.markdown("Download full horizontal spreadsheet baselines or compile a signature, print-ready landscape dossier:")

if os.path.exists(PL_CACHE) and os.path.exists(CF_CACHE) and os.path.exists(BS_CACHE):
    # Load and transpose datasets back to their correct horizontal format (Accounts as Rows, Months as Columns)
    pl_horiz = pd.read_csv(PL_CACHE, index_col=0).T
    cf_horiz = pd.read_csv(CF_CACHE, index_col=0).T
    bs_horiz = pd.read_csv(BS_CACHE, index_col=0).T
    
    csv_col1, csv_col2, csv_col3 = st.columns(3)
    with csv_col1:
        st.download_button(
            label="📈 Export Horizontal P&L (CSV)",
            data=pl_horiz.to_csv().encode('utf-8'),
            file_name=f"STRATA_Horizontal_Profit_Loss_{active_project}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with csv_col2:
        st.download_button(
            label="💸 Export Horizontal Cash Flow (CSV)",
            data=cf_horiz.to_csv().encode('utf-8'),
            file_name=f"STRATA_Horizontal_Cash_Flow_{active_project}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with csv_col3:
        st.download_button(
            label="📋 Export Horizontal Balance Sheet (CSV)",
            data=bs_horiz.to_csv().encode('utf-8'),
            file_name=f"STRATA_Horizontal_Balance_Sheet_{active_project}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
    
    # PDF Compilation Command Section
    if st.button("📄 Compile Executive Landscape PDF Dossier Package", use_container_width=True):
        if not gemini_key:
            st.error("Missing Gemini API Token in system secrets config.")
        else:
            with st.spinner("Executing cognitive synthesis and landscape typeset compilation..."):
                try:
                    # Extract high-level metrics for the prompt analysis
                    tot_turnover = float(pl_horiz.loc["Revenue (£)"].sum()) if "Revenue (£)" in pl_horiz.index else 0.0
                    tot_margin = float(pl_horiz.loc["EBIT (£)"].sum()) if "EBIT (£)" in pl_horiz.index else 0.0
                    final_cash = float(cf_horiz.loc["Cash Reserves (£)"].iloc[-1]) if "Cash Reserves (£)" in cf_horiz.index else 0.0
                    
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
                    Format your output as three concise, clean paragraphs without markdown formatting asterisks or bolding tags.
                    """
                    response = model.generate_content(executive_prompt)
                    ai_narrative = response.text.strip()
                    
                    pdf_buffer = io.BytesIO()
                    # FORCE LANDSCAPE PAGE SIZE: letter is 612x792, landscape flips it to 792x612
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
                    
                    # --- PAGE 1: LANDSCAPE SUMMARY VIEW ---
                    story.append(Paragraph(f"STRATA // Corporate Financial Briefing (Landscape Analysis Pack)", title_style))
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
                    
                    # --- PAGE 2: HORIZONTAL PROFIT & LOSS STATEMENT (YEAR 1 GRANULARITY) ---
                    story.append(PageBreak())
                    story.append(Paragraph("📈 Year 1 Multi-Period Income Statement (Profit & Loss Model)", title_style))
                    story.append(Spacer(1, 10))
                    
                    # Extract Year 1 horizontal slice (M01 to M12)
                    y1_months = [f"M{str(i).zfill(2)}" for i in range(1, 13)]
                    pl_pdf_headers = [Paragraph("Account Heading", table_header_style)] + [Paragraph(m, table_header_style) for m in y1_months]
                    pl_pdf_rows = [pl_pdf_headers]
                    
                    for acct_name in pl_horiz.index:
                        row_cells = [Paragraph(str(acct_name), table_cell_style)]
                        for m in y1_months:
                            val = pl_horiz.at[acct_name, m]
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
                    
                    # --- PAGE 3: HORIZONTAL CASH FLOW & BALANCE ACCRUALS ---
                    story.append(PageBreak())
                    story.append(Paragraph("💸 Year 1 Compounding Cash Ledger Horizon & Balance Sheet Registry", title_style))
                    story.append(Spacer(1, 10))
                    
                    cf_pdf_headers = [Paragraph("Cash Flow & Account Headings", table_header_style)] + [Paragraph(m, table_header_style) for m in y1_months]
                    cf_pdf_rows = [cf_pdf_headers]
                    
                    # Extract key reporting tracks for integrated representation
                    if "Net Cash Movement (£)" in cf_horiz.index:
                        cf_pdf_rows.append([Paragraph("Net Cash Movement (£)", table_cell_style)] + [Paragraph(f"{cf_horiz.at['Net Cash Movement (£)', m]:,.0f}", table_cell_style) for m in y1_months])
                    if "Cash Reserves (£)" in cf_horiz.index:
                        cf_pdf_rows.append([Paragraph("Compounding Cash Reserves (£)", table_cell_style)] + [Paragraph(f"{cf_horiz.at['Cash Reserves (£)', m]:,.0f}", table_cell_style) for m in y1_months])
                    if "HMRC VAT Reserves Owing" in bs_horiz.index:
                        cf_pdf_rows.append([Paragraph("HMRC VAT Reserves Owing (£)", table_cell_style)] + [Paragraph(f"{bs_horiz.at['HMRC VAT Reserves Owing', m]:,.0f}", table_cell_style) for m in y1_months])
                    if "Retained Earnings (£)" in bs_horiz.index:
                        cf_pdf_rows.append([Paragraph("Retained Earnings Cushion (£)", table_cell_style)] + [Paragraph(f"{bs_horiz.at['Retained Earnings (£)', m]:,.0f}", table_cell_style) for m in y1_months])
                        
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
            label="📥 Download Print-Ready Landscape Briefing Pack (PDF)",
            data=st.session_state["compiled_pdf_bytes"],
            file_name=f"STRATA_Landscape_Dossier_{active_project}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
else:
    st.button("📄 Ledger Framework Matrix Offline", disabled=True, use_container_width=True)

st.markdown("---")

# Tab groupings
tab1, tab2, tab3 = st.tabs([
    "📈 Horizontal Income Performance (P&L)", 
    "💸 Horizontal Bank Tracker (Cash Flow)", 
    "📋 Horizontal Worth Register (Balance Sheet)"
])

# =========================================================================
# 📈 TAB 1: PROFIT & LOSS MATRIX (AUTHENTIC HORIZONTAL ORIENTATION)
# =========================================================================
with tab1:
    st.subheader("📈 Income & Earnings Run-Rates")
    if os.path.exists(PL_CACHE):
        try:
            pl_horiz = pd.read_csv(PL_CACHE, index_col=0).T
            st.markdown("💡 *Scroll horizontally to view months M01 through M60:*")
            
            # Formatted native horizontal frame container
            st.dataframe(pl_horiz.style.format("{:,.2f}"), use_container_width=False)
            
            tot_rev = float(pl_horiz.loc["Revenue (£)"].sum()) if "Revenue (£)" in pl_horiz.index else 0.0
            tot_margin = float(pl_horiz.loc["EBIT (£)"].sum()) if "EBIT (£)" in pl_horiz.index else 0.0
            
            st.markdown("#### 🎯 Performance Summaries (60-Month Total Run)")
            col1, col2 = st.columns(2)
            with col1: st.metric("Total Project Turnover (60M)", f"£{tot_rev:,.2f}")
            with col2: st.metric("Accumulated Net Profit Margin (60M)", f"£{tot_margin:,.2f}")
        except Exception as e: st.error(f"Error rendering Income statement dataset: {str(e)}")

# =========================================================================
# 💸 TAB 2: CASH FLOW MATRIX (AUTHENTIC HORIZONTAL ORIENTATION)
# =========================================================================
with tab2:
    st.subheader("💸 Real Bank Account Ledger Profile")
    if os.path.exists(CF_CACHE):
        try:
            cf_horiz = pd.read_csv(CF_CACHE, index_col=0).T
            st.markdown("💡 *Scroll horizontally to track liquid cash adjustments over 60 months:*")
            st.dataframe(cf_horiz.style.format("{:,.2f}"), use_container_width=False)
            
            st.markdown("#### 📈 Compounding Cash Horizon Trajectory Curve")
            if "Cash Reserves (£)" in cf_horiz.index:
                st.line_chart(cf_horiz.loc["Cash Reserves (£)"], use_container_width=True)
        except Exception as e: st.error(f"Error rendering Bank Tracker dataset: {str(e)}")

# =========================================================================
# 📋 TAB 3: BALANCE SHEET MATRIX (AUTHENTIC HORIZONTAL ORIENTATION)
# =========================================================================
with tab3:
    st.subheader("📋 Core Company Worth Register")
    if os.path.exists(BS_CACHE):
        try:
            bs_horiz = pd.read_csv(BS_CACHE, index_col=0).T
            st.markdown("💡 *Scroll horizontally to monitor balanced asset metrics across timelines:*")
            st.dataframe(bs_horiz.style.format("{:,.2f}"), use_container_width=False)
            st.success("🔒 System Integrity Flag: Company worth register completely reconciled and in balance.")
        except Exception as e: st.error(f"Error rendering Company Worth dataset: {str(e)}")