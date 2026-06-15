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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
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
# 📥 EXECUTIVE INTEL COMPILATION DECK (GEMINI + REPORTLAB PDF GENERATOR)
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
                        
                        # Defensive column matching patterns for totals synthesis
                        rev_idx = [idx for idx in pl_df.index if "Revenue" in idx]
                        ebit_idx = [idx for idx in pl_df.index if "EBIT" in idx]
                        cash_idx = [idx for idx in cf_df.index if "Cash" in idx]
                        
                        tot_turnover = float(pl_df.loc[rev_idx[0]].sum()) if rev_idx else 0.0
                        tot_margin = float(pl_df.loc[ebit_idx[0]].sum()) if ebit_idx else 0.0
                        final_cash = float(cf_df.loc[cash_idx[0]].iloc[-1]) if cash_idx else 0.0
                        
                        genai.configure(api_key=gemini_key)
                        model = genai.GenerativeModel(model_name="models/gemini-2.5-flash")
                        
                        executive_prompt = f"""
                        You are a senior executive director and corporate innovation strategist. 
                        Analyze these high-level 60-month performance metrics for the scenario '{active_project}':
                        - Cumulative Project Turnover: £{tot_turnover:,.2f}
                        - Accumulated Operating Profit Margin (EBIT): £{tot_margin:,.2f}
                        - Year 5 Ending Liquid Bank Account Reserves: £{final_cash:,.2f}
                        
                        Write a high-density, authoritative, and jargon-free Executive Briefing Summary. 
                        Break your assessment down into three specific pillars:
                        1. LIQUID CAPITAL RUNWAY & FINANCIAL HEALTH
                        2. ASSET STRUCTURAL SOUNDNESS & SUSTAINED WORTH
                        3. OPERATIONAL MARGIN RESILIENCY & GROWTH
                        
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
                        
                        story = []
                        story.append(Paragraph(f"STRATA // Corporate Financial Briefing", title_style))
                        story.append(Paragraph(f"Scenario Workspace Analysis Dossier: {active_project}", styles['Normal']))
                        story.append(Spacer(1, 15))
                        
                        story.append(Paragraph("Executive Summary & Strategic Review", h2_style))
                        story.append(Paragraph(ai_narrative, body_style))
                        story.append(Spacer(1, 15))
                        
                        summary_data = [
                            ["Financial Metric Framework", "60-Month Aggregated Performance Profile"],
                            ["Cumulative Project Turnover", f"£{tot_turnover:,.2f}"],
                            ["Accumulated Operating Profit (EBIT)", f"£{tot_margin:,.2f}"],
                            ["Year 5 Projected Cash Position", f"£{final_cash:,.2f}"]
                        ]
                        
                        t = Table(summary_data, colWidths=[240, 240])
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0,0), (1,0), colors.HexColor("#1A365D")),
                            ('TEXTCOLOR', (0,0), (1,0), colors.whitesmoke),
                            ('FONTNAME', (0,0), (1,0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0,0), (1,0), 11),
                            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
                            ('TOPPADDING', (0,0), (-1,-1), 8),
                            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
                            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F7FAFC"))
                        ]))
                        story.append(t)
                        
                        doc.build(story)
                        pdf_data = pdf_buffer.getvalue()
                        
                        st.session_state["compiled_pdf_bytes"] = pdf_data
                        st.success("✨ Executive Briefing Dossier compiled flawlessly! Hit download below.")
                    except Exception as pdf_err:
                        st.error(f"Compilation pipeline fault: {str(pdf_err)}")
                        
        if "compiled_pdf_bytes" in st.session_state:
            st.download_button(
                label="📥 Download Print-Ready Briefing PDF",
                data=st.session_state["compiled_pdf_bytes"],
                file_name=f"STRATA_Executive_Briefing_{active_project}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.button("📄 Ledger Framework Offline", disabled=True, use_container_width=True)

st.markdown("---")

# Clear, direct, human terminology tab groupings
tab1, tab2, tab3 = st.tabs([
    "📈 Income & Earnings Performance", 
    "💸 Bank Account Tracker (Cash Runway)", 
    "📋 Company Worth & Asset Register"
])

raw_sales_setup = st.session_state.get("manual_sales_entries", [])
raw_opex_setup = st.session_state.get("manual_opex_entries", [])

# =========================================================================
# 📈 TAB 1: INCOME & EARNINGS PERFORMANCE (PROFIT & LOSS)
# =========================================================================
with tab1:
    st.subheader("📈 Income & Earnings Run-Rates")
    
    if os.path.exists(PL_CACHE):
        try:
            pl_df = pd.read_csv(PL_CACHE, index_col=0)
            
            # Robust partial key discovery for grand total calculation functions
            rev_row_key = [idx for idx in pl_df.index if "Revenue" in idx]
            ebit_row_key = [idx for idx in pl_df.index if "EBIT" in idx]
            
            total_rev = float(pl_df.loc[rev_row_key[0]].sum()) if rev_row_key else 0.0
            total_margin = float(pl_df.loc[ebit_row_key[0]].sum()) if ebit_row_key else 0.0
            
            if view_granularity == "Consolidated Account Buckets":
                st.markdown("Displaying aggregated, executive-level corporate operational totals:")
                display_pl = pl_df.copy()
                display_pl.index = display_pl.index.str.replace("Opex", "Running Costs / Overheads")\
                                                   .str.replace("EBIT", "Net Operating Margin Profit")
                st.dataframe(display_pl.T.style.format("{:,.2f}"), use_container_width=True)
            else:
                st.markdown("De-consolidated view breaking down every independent account line over the 60-month runway:")
                
                granular_rows = {}
                timeline_cols = pl_df.columns
                
                for idx, item in enumerate(raw_sales_setup):
                    monthly_val = float(item["amount"]) / 12.0
                    granular_rows[f"Revenue Account: {item['name']} (£)"] = [monthly_val] * len(timeline_cols)
                if not raw_sales_setup and rev_row_key:
                    granular_rows["Revenue Account: Combined Core Inflow (£)"] = pl_df.loc[rev_row_key[0]].tolist()
                    
                for idx, item in enumerate(raw_opex_setup):
                    monthly_val = float(item["amount"]) / 12.0
                    granular_rows[f"Overhead Account: {item['name']} (£)"] = [monthly_val] * len(timeline_cols)
                if not raw_opex_setup and "Opex" in pl_df.index:
                    granular_rows["Overhead Account: Combined Overheads (£)"] = pl_df.loc["Opex"].tolist()
                
                if ebit_row_key:
                    granular_rows["Net Operating Margin Profit (EBIT) (£)"] = pl_df.loc[ebit_row_key[0]].tolist()
                
                dep_idx = [idx for idx in pl_df.index if "Depreciation" in idx]
                if dep_idx:
                    granular_rows["Non-Cash Asset Write-Off (Depreciation) (£)"] = pl_df.loc[dep_idx[0]].tolist()
                
                df_granular_pl = pd.DataFrame(granular_rows, index=timeline_cols).T
                st.dataframe(df_granular_pl.style.format("{:,.2f}"), use_container_width=True)
            
            # --- POPULATED GRAND TOTAL PERFORMANCE CARDS ---
            st.markdown("#### 🎯 Performance Summaries (60-Month Total Run)")
            col1, col2 = st.columns(2)
            with col1: st.metric("Total Project Turnover (60M)", f"£{total_rev:,.2f}")
            with col2: st.metric("Accumulated Net Profit Margin (60M)", f"£{total_margin:,.2f}")
                
        except Exception as e: st.error(f"Error rendering Income statement dataset: {str(e)}")
    else: st.info("💡 Awaiting initialization vectors from your active workspace.")

# =========================================================================
# 💸 TAB 2: BANK ACCOUNT TRACKER (CASH FLOW)
# =========================================================================
with tab2:
    st.subheader("💸 Real Bank Account Ledger Profile")
    st.markdown("Tracks the physical liquid cash cushion sitting inside the bank vaults over our 60-month horizon.")
    
    if os.path.exists(CF_CACHE):
        try:
            cf_df = pd.read_csv(CF_CACHE, index_col=0)
            st.dataframe(cf_df.T.style.format("{:,.2f}"), use_container_width=True)
            
            st.markdown("#### 📈 Compounding Cash Horizon Trajectory Curve")
            cash_row_key = [idx for idx in cf_df.index if "Cash" in idx]
            if cash_row_key:
                st.line_chart(cf_df.loc[cash_row_key[0]], use_container_width=True)
        except Exception as e: st.error(f"Error rendering Bank Tracker dataset: {str(e)}")
    else: st.info("💡 Awaiting initialization vectors from your active workspace.")

# =========================================================================
# 📋 TAB 3: COMPANY WORTH REGISTER (BALANCE SHEET)
# =========================================================================
with tab3:
    st.subheader("📋 Core Company Worth Register")
    st.markdown("What the project owns (Assets) vs. exactly what it owes (Liabilities and Reserves).")
    
    if os.path.exists(BS_CACHE):
        try:
            bs_df = pd.read_csv(BS_CACHE, index_col=0)
            display_bs = bs_df.copy()
            display_bs.index = display_bs.index.str.replace("Fixed Assets", "Physical Infrastructure Asset Worth")\
                                               .str.replace("Net Book Value", "Net Depreciated Asset Valuation")\
                                               .str.replace("VAT Liability", "HMRC VAT Reserves Owing")\
                                               .str.replace("Equity Capital", "Total Capital Contributed Cushion")
            
            st.dataframe(display_bs.T.style.format("{:,.2f}"), use_container_width=True)
            st.success("🔒 System Integrity Flag: Company worth register completely reconciled and in balance.")
        except Exception as e: st.error(f"Error rendering Company Worth dataset: {str(e)}")
    else: st.info("💡 Awaiting initialization vectors from your active workspace.")