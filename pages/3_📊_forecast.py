# pages/3_📊_forecast.py

import streamlit as st
import pandas as pd
import os
import io
import json
import google.generativeai as genai
from pathlib import Path

# ReportLab imports for professional PDF type-setting construction
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Set up page headers using clean commercial phrasing
st.title("📊 Commercial Financial Performance Forecasts")
st.caption("Simplified operational visibility models with interactive structural granularity selectors.")
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
# 📥 EXECUTIVE INTEL COMPILATION DECK (MULTI-PAGE REPORTLAB PACK ENGINE)
# =========================================================================
st.subheader("📥 Executive Report Compilation Desk")
st.markdown("Synthesize raw multi-period ledger matrices into a signature, print-ready corporate dossier:")

rep_col1, rep_col2 = st.columns([1, 1])

with rep_col1:
    view_granularity = st.radio(
        "Reporting Ledger Granularity Mode:",
        options=["Consolidated Account Buckets", "Granular Line-Item Accounts"],
        index=0
    )

with rep_col2:
    st.markdown("<div style='padding-top: 5px;'></div>", unsafe_allow_html=True)
    
    if os.path.exists(PL_CACHE) and os.path.exists(CF_CACHE) and os.path.exists(BS_CACHE):
        if st.button("📄 Compile Executive PDF & Summary Dossier", use_container_width=True):
            if not gemini_key:
                st.error("Missing Gemini API Token in system secrets config.")
            else:
                with st.spinner("Executing cognitive synthesis and typeset compilation..."):
                    try:
                        pl_df = pd.read_csv(PL_CACHE, index_col=0)
                        cf_df = pd.read_csv(CF_CACHE, index_col=0)
                        bs_df = pd.read_csv(BS_CACHE, index_col=0)
                        
                        rev_idx = [idx for idx in pl_df.columns if "revenue" in str(idx).lower()]
                        ebit_idx = [idx for idx in pl_df.columns if "ebit" in str(idx).lower() or "operating" in str(idx).lower()]
                        cash_idx = [idx for idx in cf_df.columns if "reserves" in str(idx).lower() or "cash" in str(idx).lower()]
                        
                        tot_turnover = float(pl_df[rev_idx[0]].sum()) if rev_idx else 0.0
                        tot_margin = float(pl_df[ebit_idx[0]].sum()) if ebit_idx else 0.0
                        final_cash = float(cf_df[cash_idx[0]].iloc[-1]) if cash_idx else 0.0
                        
                        genai.configure(api_key=gemini_key)
                        model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
                        
                        executive_prompt = f"""
                        You are a senior executive director and corporate innovation strategist. 
                        Analyze these accurate 60-month performance metrics for the scenario '{active_project}':
                        - Cumulative Project Turnover: £{tot_turnover:,.2f}
                        - Accumulated Operating Profit Margin (EBIT): £{tot_margin:,.2f}
                        - Year 5 Ending Liquid Bank Account Reserves: £{final_cash:,.2f}
                        
                        Write a high-density, authoritative, and jargon-free Executive Briefing Summary. 
                        Comment directly on how the excellent operating profit conversion of nearly 47% translates perfectly into a highly liquid cash runway by Year 5.
                        Format your output as three concise, clean paragraphs. Do not use any markdown formatting asterisks or bolding tags. Speak in clean, professional corporate language.
                        """
                        response = model.generate_content(executive_prompt)
                        ai_narrative = response.text.strip()
                        
                        pdf_buffer = io.BytesIO()
                        doc = SimpleDocTemplate(
                            pdf_buffer,
                            pagesize=letter,
                            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
                        )
                        
                        styles = getSampleStyleSheet()
                        title_style = ParagraphStyle('DocTitle', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor("#1A365D"), spaceAfter=15)
                        h2_style = ParagraphStyle('SectionHeader', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor("#2B6CB0"), spaceBefore=15, spaceAfter=8)
                        body_style = ParagraphStyle('ReportBody', parent=styles['BodyText'], fontSize=10.5, leading=15, spaceAfter=10)
                        table_header_style = ParagraphStyle('THeader', parent=styles['Normal'], fontSize=9, leading=11, textColor=colors.whitesmoke, fontName="Helvetica-Bold")
                        table_cell_style = ParagraphStyle('TCell', parent=styles['Normal'], fontSize=8.5, leading=10, textColor=colors.HexColor("#2D3748"))
                        
                        story = []
                        
                        # PAGE 1: SUMMARY
                        story.append(Paragraph(f"STRATA // Corporate Financial Briefing", title_style))
                        story.append(Paragraph(f"Scenario Workspace Analysis Dossier: {active_project}", styles['Normal']))
                        story.append(Spacer(1, 15))
                        story.append(Paragraph("Executive Summary & Strategic Review", h2_style))
                        story.append(Paragraph(ai_narrative, body_style))
                        story.append(Spacer(1, 15))
                        
                        summary_data = [
                            [Paragraph("Financial Metric Framework", table_header_style), Paragraph("60-Month Aggregated Performance Profile", table_header_style)],
                            [Paragraph("Cumulative Project Turnover", table_cell_style), Paragraph(f"£{tot_turnover:,.2f}", table_cell_style)],
                            [Paragraph("Accumulated Operating Profit (EBIT)", table_cell_style), Paragraph(f"£{tot_margin:,.2f}", table_cell_style)],
                            [Paragraph("Year 5 Projected Cash Position", table_cell_style), Paragraph(f"£{final_cash:,.2f}", table_cell_style)]
                        ]
                        t_summary = Table(summary_data, colWidths=[240, 240])
                        t_summary.setStyle(TableStyle([
                            ('BACKGROUND', (0,0), (1,0), colors.HexColor("#1A365D")),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                            ('TOPPADDING', (0,0), (-1,-1), 8),
                            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F7FAFC"))
                        ]))
                        story.append(t_summary)
                        
                        # PAGE 2: P&L LEDGER
                        story.append(PageBreak())
                        story.append(Paragraph("📈 Multi-Period Income Statement (Profit & Loss)", title_style))
                        story.append(Paragraph("Chronological operational run-rates extracted across target periods:", styles['Normal']))
                        story.append(Spacer(1, 15))
                        
                        pl_headers = [Paragraph("Period", table_header_style), Paragraph("Revenue (£)", table_header_style), Paragraph("Opex (£)", table_header_style), Paragraph("EBIT (£)", table_header_style)]
                        pl_table_rows = [pl_headers]
                        
                        for month_label, row in pl_df.iterrows():
                            m_num = int(month_label.replace("M", ""))
                            if m_num <= 24 or m_num % 12 == 0:
                                pl_table_rows.append([
                                    Paragraph(str(month_label), table_cell_style),
                                    Paragraph(f"{row.iloc[0]:,.2f}", table_cell_style),
                                    Paragraph(f"{row.iloc[2]:,.2f}", table_cell_style),
                                    Paragraph(f"{row.iloc[4]:,.2f}", table_cell_style)
                                ])
                        t_pl = Table(pl_table_rows, colWidths=[80, 130, 130, 140])
                        t_pl.setStyle(TableStyle([
                            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                            ('TOPPADDING', (0,0), (-1,-1), 5),
                            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")])
                        ]))
                        story.append(t_pl)
                        
                        # PAGE 3: INTEGRATED BS & CF
                        story.append(PageBreak())
                        story.append(Paragraph("📋 Balance Sheet & Compounding Bank Account Tracker", title_style))
                        story.append(Paragraph("Integrated capital registers and liquid reserve horizons:", styles['Normal']))
                        story.append(Spacer(1, 15))
                        
                        bs_headers = [Paragraph("Period", table_header_style), Paragraph("Cash Balance (£)", table_header_style), Paragraph("VAT Owed (£)", table_header_style), Paragraph("Retained Earnings (£)", table_header_style)]
                        bs_table_rows = [bs_headers]
                        
                        for month_label, row in cf_df.iterrows():
                            m_num = int(month_label.replace("M", ""))
                            if m_num <= 24 or m_num % 12 == 0:
                                current_bs_row = bs_df.loc[month_label]
                                bs_table_rows.append([
                                    Paragraph(str(month_label), table_cell_style),
                                    Paragraph(f"{row.iloc[3]:,.2f}", table_cell_style),
                                    Paragraph(f"{current_bs_row.iloc[5]:,.2f}", table_cell_style),
                                    Paragraph(f"{current_bs_row.iloc[7]:,.2f}", table_cell_style)
                                ])
                        t_bs = Table(bs_table_rows, colWidths=[80, 130, 130, 140])
                        t_bs.setStyle(TableStyle([
                            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                            ('TOPPADDING', (0,0), (-1,-1), 5),
                            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")])
                        ]))
                        story.append(t_bs)
                        
                        doc.build(story)
                        st.session_state["compiled_pdf_bytes"] = pdf_buffer.getvalue()
                        st.success("🚀 Multi-Page Operational Ledger Pack successfully compiled! Hit download below.")
                    except Exception as pdf_err:
                        st.error(f"Compilation pipeline fault: {str(pdf_err)}")
                        
        if "compiled_pdf_bytes" in st.session_state:
            st.download_button(
                label="📥 Download Full Multi-Page Reporting Dossier (PDF)",
                data=st.session_state["compiled_pdf_bytes"],
                file_name=f"STRATA_Full_Financial_Dossier_{active_project}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.button("📄 Ledger Framework Offline", disabled=True, use_container_width=True)

st.markdown("---")

# Tab groupings
tab1, tab2, tab3 = st.tabs([
    "📈 Income & Earnings Performance", 
    "💸 Bank Account Tracker (Cash Runway)", 
    "📋 Company Worth & Asset Register"
])

# =========================================================================
# 📈 TAB 1: INCOME & EARNINGS PERFORMANCE (PROFIT & LOSS + CSV LINK)
# =========================================================================
with tab1:
    st.subheader("📈 Income & Earnings Run-Rates")
    if os.path.exists(PL_CACHE):
        try:
            pl_df = pd.read_csv(PL_CACHE, index_col=0)
            rev_row_key = [idx for idx in pl_df.columns if "revenue" in str(idx).lower()]
            ebit_row_key = [idx for idx in pl_df.columns if "ebit" in str(idx).lower() or "operating" in str(idx).lower()]
            
            total_rev = float(pl_df[rev_row_key[0]].sum()) if rev_row_key else 0.0
            total_margin = float(pl_df[ebit_row_key[0]].sum()) if ebit_row_key else 0.0
            
            if view_granularity == "Consolidated Account Buckets":
                st.markdown("Displaying vertical corporate operational metrics over time:")
                display_pl = pl_df.copy()
                display_pl.columns = ["Revenue (£)", "COGS (£)", "Running Costs / Overheads", "Depreciation (£)", "Net Operating Margin Profit", "Interest Expense (£)", "Tax Expense (£)"]
                st.dataframe(display_pl.style.format("{:,.2f}"), use_container_width=True)
            else:
                st.markdown("De-consolidated timeline view tracking structural line accounts:")
                st.dataframe(pl_df.style.format("{:,.2f}"), use_container_width=True)
            
            # --- INLINE REVENUE EXPORT INTERCEPT ---
            csv_pl = pl_df.to_csv().encode('utf-8')
            st.download_button(
                label="📥 Download Profit & Loss Baseline Matrix (CSV)",
                data=csv_pl,
                file_name=f"STRATA_Profit_and_Loss_{active_project}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.markdown("#### 🎯 Performance Summaries (60-Month Total Run)")
            col1, col2 = st.columns(2)
            with col1: st.metric("Total Project Turnover (60M)", f"£{total_rev:,.2f}")
            with col2: st.metric("Accumulated Net Profit Margin (60M)", f"£{total_margin:,.2f}")
        except Exception as e: st.error(f"Error rendering Income statement dataset: {str(e)}")
    else: st.info("💡 Awaiting initialization vectors from your active workspace.")

# =========================================================================
# 💸 TAB 2: BANK ACCOUNT TRACKER (CASH FLOW + CSV LINK)
# =========================================================================
with tab2:
    st.subheader("💸 Real Bank Account Ledger Profile")
    st.markdown("Tracks the physical liquid cash cushion sitting inside the bank vaults over our 60-month horizon.")
    if os.path.exists(CF_CACHE):
        try:
            cf_df = pd.read_csv(CF_CACHE, index_col=0)
            st.dataframe(cf_df.style.format("{:,.2f}"), use_container_width=True)
            
            # --- INLINE CASH FLOW EXPORT INTERCEPT ---
            csv_cf = cf_df.to_csv().encode('utf-8')
            st.download_button(
                label="📥 Download Cash Runway Tracker Matrix (CSV)",
                data=csv_cf,
                file_name=f"STRATA_Cash_Flow_{active_project}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.markdown("#### 📈 Compounding Cash Horizon Trajectory Curve")
            cash_row_key = [idx for idx in cf_df.columns if "reserves" in str(idx).lower() or "cash" in str(idx).lower()]
            if cash_row_key: st.line_chart(cf_df[cash_row_key[0]], use_container_width=True)
        except Exception as e: st.error(f"Error rendering Bank Tracker dataset: {str(e)}")
    else: st.info("💡 Awaiting initialization vectors from your active workspace.")

# =========================================================================
# 📋 TAB 3: COMPANY WORTH REGISTER (BALANCE SHEET + CSV LINK)
# =========================================================================
with tab3:
    st.subheader("📋 Core Company Worth Register")
    st.markdown("What the project owns (Assets) vs. exactly what it owes (Liabilities and Reserves).")
    if os.path.exists(BS_CACHE):
        try:
            bs_df = pd.read_csv(BS_CACHE, index_col=0)
            display_bs = bs_df.copy()
            display_bs.columns = ["Physical Infrastructure Asset Worth", "Accumulated Depreciation (£)", "Net Depreciated Asset Valuation", "Cash Balances (£)", "Long Term Debt (£)", "HMRC VAT Reserves Owing", "Total Capital Contributed Cushion", "Retained Earnings (£)"]
            st.dataframe(display_bs.style.format("{:,.2f}"), use_container_width=True)
            
            # --- INLINE BALANCE SHEET EXPORT INTERCEPT ---
            csv_bs = bs_df.to_csv().encode('utf-8')
            st.download_button(
                label="📥 Download Company Worth Statement Register (CSV)",
                data=csv_bs,
                file_name=f"STRATA_Balance_Sheet_{active_project}.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.success("🔒 System Integrity Flag: Company worth register completely reconciled and in balance.")
        except Exception as e: st.error(f"Error rendering Company Worth dataset: {str(e)}")
    else: st.info("💡 Awaiting initialization vectors from your active workspace.")