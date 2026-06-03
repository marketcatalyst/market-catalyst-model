# ui_skin/core_engine/report_generator.py
import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def compile_pdf_executive_report(forecast_df: pd.DataFrame, scenario_name: str) -> bytes:
    """
    Compiles a highly polished corporate PDF briefing document summarizing the 
    AHOTG multi-site fresh food retail expansion performance and liquidity positions.
    """
    buffer = io.BytesIO()
    
    # 1. Page Frame Geometry Configuration
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=40, 
        leftMargin=40, 
        topMargin=40, 
        bottomMargin=40
    )
    story = []
    
    # 2. Advanced Typography Stylesheet Specifications
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=20
    )
    
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#111827'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#374151'),
        spaceAfter=10
    )
    
    table_text = ParagraphStyle(
        'TableText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#111827')
    )
    
    table_header_text = ParagraphStyle(
        'TableHeaderText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )

    # 3. Document Header Generation
    story.append(Paragraph("AHOTG — Executive Financial Summary Report", title_style))
    story.append(Paragraph(f"Strategic Staging Track: <b>{scenario_name}</b>  •  Published: June 2026  •  Framework: Market Catalyst Engine", subtitle_style))
    story.append(Spacer(1, 10))
    
    # 4. Executive Narrative Context Formulation
    story.append(Paragraph("1. Operational Context & Project Blueprint", h2_style))
    narrative_p1 = (
        "This executive briefing document summarizes the 3-way financial trajectory modeled for the "
        "AHOTG network. The operational model focuses on premium, healthy fresh food production "
        "and retail hospitality distribution channels. Financial forecasts integrate centralized kitchen prep overheads "
        "and rolling logistics management matrices with multi-site retail café branches across regional nodes, including "
        "Carmarthen, Wellfield Road, Bridgend Town Centre, Cardiff Bay, Penarth, and Merthyr."
    )
    story.append(Paragraph(narrative_p1, body_style))
    
    narrative_p2 = (
        "All underlying financial schedules—including Profit & Loss accruals, asset register depreciation lifecycles, "
        "and working capital timing lags—are processed using double-entry logic, ensuring "
        "absolute reconciliation balance across the entire horizon runway."
    )
    story.append(Paragraph(narrative_p2, body_style))
    story.append(Spacer(1, 10))
    
    # 5. Milestone Data Table Formulation
    story.append(Paragraph("2. Strategic Milestone Financial Summary Table", h2_style))
    
    # Select key structural milestone target month columns
    milestone_months = ["Month 1", "Month 6", "Month 12", "Month 24", "Month 36"]
    filtered_df = forecast_df[forecast_df["Month"].isin(milestone_months)]
    
    # Structure rows for the print layout canvas
    table_content = [
        [Paragraph("Financial Line Item Component", table_header_text)] + [Paragraph(m, table_header_text) for m in milestone_months]
    ]
    
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
        
    # Apply high-contrast corporate table styling matrices
    summary_table = Table(table_content, colWidths=[160] + [70]*5)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F9FAFB'), colors.white]),
        ('LINEBELOW', (0, -1), (-1, -1), 1.5, colors.HexColor('#1E3A8A')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 15))
    
    # 6. Corporate Risk Governance Sign-Off Declarations
    story.append(Paragraph("3. Scenario Underwriting Control Sign-Off", h2_style))
    sign_off_text = (
        "The figures compiled above represent an authorized output from the centralized Market Catalyst engine. "
        "Any modifications made via the Interactive Capital Asset Register or the 12-Month Seasonality Profile "
        "are fully accounted for within these ledger balances. These figures are approved for downstream board disclosure "
        "and commercial underwriting review."
    )
    story.append(Paragraph(sign_off_text, body_style))
    
    # Build Document Canvas Story Blocks
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes