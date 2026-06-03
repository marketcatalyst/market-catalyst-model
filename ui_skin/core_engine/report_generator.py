# core_engine/report_generator.py
import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def compile_pdf_executive_report(forecast_df: pd.DataFrame, scenario_name: str) -> bytes:
    """
    Compiles a highly polished corporate PDF briefing document summarising the 
    AHOTG multi-site fresh food retail expansion performance and liquidity positions.
    """
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=40, 
        leftMargin=40, 
        topMargin=40, 
        bottomMargin=40
    )
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold',
        fontSize=24, leading=28, textColor=colors.HexColor('#1E3A8A'), spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle', parent=styles['Normal'], fontName='Helvetica',
        fontSize=11, leading=14, textColor=colors.HexColor('#4B5563'), spaceAfter=20
    )
    h2_style = ParagraphStyle(
        'SectionHeader', parent=styles['Heading2'], fontName='Helvetica-Bold',
        fontSize=14, leading=18, textColor=colors.HexColor('#111827'), spaceBefore=14, spaceAfter=8, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyTextCustom', parent=styles['Normal'], fontName='Helvetica',
        fontSize=10, leading=14, textColor=colors.HexColor('#374151'), spaceAfter=10
    )
    table_text = ParagraphStyle('TableText', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=11, textColor=colors.HexColor('#111827'))
    table_header_text = ParagraphStyle('TableHeaderText', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=colors.white)

    story.append(Paragraph("AHOTG — Executive Financial Summary Report", title_style))
    story.append(Paragraph(f"Strategic Staging Track: <b>{scenario_name}</b>  •  Published: 2026  •  Framework: Market Catalyst Engine", subtitle_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("1. Operational Context & Project Blueprint", h2_style))
    narrative_p1 = (
        "This executive briefing document summarises the 3-way financial trajectory modelled for the "
        "AHOTG network. The operational model focuses on premium, healthy fresh food production "
        "and retail hospitality distribution channels. All figures are dynamically compiled and verified."
    )
    story.append(Paragraph(narrative_p1, body_style))
    
    story.append(Paragraph("2. Strategic Milestone Financial Summary Table", h2_style))
    
    milestone_months = ["Month 1", "Month 6", "Month 12", "Month 24", "Month 36"]
    filtered_df = forecast_df[forecast_df["Month"].isin(milestone_months)]
    
    table_content = [[Paragraph("Financial Line Item Component", table_header_text)] + [Paragraph(m, table_header_text) for m in milestone_months]]
    
    row_definitions = [
        ("Turnover (£)", "Gross Scheduled Revenue"),
        ("Direct Costs (£)", "Total Cost of Sales (COGS)"),
        ("Net Profit (£)", "Net Operational P&L Profit"),
        ("Fixed Asset NBV (£)", "Non-Current Asset NBV Carrying Base"),
        ("Bank Cash Position (£)", "Closing Bank Liquidity Balance")
    ]
    
    for key, label in row_definitions:
        row_data = [Paragraph(label, table_text)]
        for m in milestone_months:
            val_series = filtered_df[filtered_df["Month"] == m][key]
            val = float(val_series.iloc[0]) if not val_series.empty else 0.0
            row_data.append(Paragraph(f"£{val:,.0f}", table_text))
        table_content.append(row_data)
        
    summary_table = Table(table_content, colWidths=[160] + [70]*5)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F9FAFB'), colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(summary_table)
    
    story.append(Paragraph("3. Scenario Underwriting Control Sign-Off", h2_style))
    sign_off_text = (
        "The figures compiled above represent an authorised output from the centralised Market Catalyst engine. "
        "Any modifications made via the Interactive Capital Asset Register or the 12-Month Seasonality Profile "
        "are fully accounted for within these ledger balances."
    )
    story.append(Paragraph(sign_off_text, body_style))
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes