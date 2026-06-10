# ui_skin/core_engine/pdf_generator.py
import sys
from pathlib import Path

# Force tracking safety to isolate root modules cleanly
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from ui_skin.core_engine.master_model import generate_integrated_3way_forecast

# Defensive type-checker mitigation wrapper
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    # This prevents your local VS Code environment from throwing typing faults
    HTML = None
    WEASYPRINT_AVAILABLE = False

def generate_pdf_executive_summary(inputs: dict, overrides: dict = None) -> bytes:
    """
    Generates an enterprise-grade corporate PDF Executive Summary report
    using HTML-to-PDF conversion via WeasyPrint. Handles local environment 
    type-checking limits gracefully.
    """
    if not WEASYPRINT_AVAILABLE:
        raise RuntimeError(
            "WeasyPrint system C-libraries (Pango/Cairo) are missing from your local OS. "
            "Deploy to Streamlit Cloud to run this output builder seamlessly."
        )

    # 1. Compute 3-Way projections via core engine
    df = generate_integrated_3way_forecast(inputs, overrides)
    
    # 2. Extract high-level metrics for executive summaries
    total_revenue = df["Revenue (£)"].sum()
    total_ebit = df["EBIT (£)"].sum()
    peak_cash = df["Cash Reserves (£)"].max()
    ending_cash = df["Cash Reserves (£)"].iloc[-1]
    avg_margin = (df["EBIT (£)"].sum() / df["Revenue (£)"].sum()) * 100
    
    # Extract structural names defensively
    trading_name = "Corporate Group Matrix"
    if "sales_locations" in inputs and inputs["sales_locations"]:
        trading_name = inputs["sales_locations"][0].get("Trading Location Name", "Corporate Group Matrix")
    elif "sales_locations_clean" in inputs and inputs["sales_locations_clean"]:
        trading_name = inputs["sales_locations_clean"][0].get("site_name", "Corporate Group Matrix")

    # 3. Compile highly structured HTML with integrated CSS layout structures
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 20mm 15mm;
                background-color: #ffffff;
                @bottom-right {{
                    content: "Page " counter(page);
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 8pt;
                    color: #718096;
                }}
                @bottom-left {{
                    content: "STRATA Financial Intelligence Confidential";
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                    font-size: 8pt;
                    color: #718096;
                }}
            }}
            
            body {{
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #2d3748;
                margin: 0;
                padding: 0;
                font-size: 10pt;
                line-height: 1.6;
            }}
            
            .header-banner {{
                margin: -20mm -15mm 25px -15mm;
                padding: 30px 15mm;
                background-color: #1a365d;
                color: #ffffff;
            }}
            
            .header-banner h1 {{
                margin: 0;
                font-size: 20pt;
                font-weight: 700;
                letter-spacing: -0.5px;
            }}
            
            .header-banner p {{
                margin: 5px 0 0 0;
                font-size: 10pt;
                color: #90cdf4;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            
            h2 {{
                font-size: 14pt;
                color: #1a365d;
                border-left: 4px solid #2b6cb0;
                padding-left: 10px;
                margin-top: 25px;
                margin-bottom: 12px;
                page-break-inside: avoid;
                page-break-after: avoid;
            }}
            
            .metric-table {{
                display: table;
                width: 100%;
                margin-bottom: 25px;
                border-collapse: collapse;
            }}
            
            .metric-row {{
                display: table-row;
            }}
            
            .metric-card {{
                display: table-cell;
                width: 33.33%;
                padding: 15px;
                background-color: #f7fafc;
                border: 1px solid #e2e8f0;
                text-align: center;
            }}
            
            .metric-value {{
                font-size: 16pt;
                font-weight: bold;
                color: #2b6cb0;
                margin-bottom: 2px;
            }}
            
            .metric-label {{
                font-size: 8pt;
                text-transform: uppercase;
                color: #718096;
                letter-spacing: 0.5px;
            }}
            
            table.data-matrix {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                page-break-inside: avoid;
            }}
            
            table.data-matrix th {{
                background-color: #2d3748;
                color: #ffffff;
                text-align: center;
                padding: 8px 10px;
                font-size: 9pt;
                font-weight: 600;
            }}
            
            table.data-matrix td {{
                padding: 7px 10px;
                border-bottom: 1px solid #e2e8f0;
                font-size: 9pt;
                text-align: right;
            }}
            
            table.data-matrix td.month-col {{
                text-align: left;
                font-weight: bold;
                color: #4a5568;
            }}
            
            .zebra-row:nth-child(even) {{
                background-color: #f7fafc;
            }}
            
            .memo-block {{
                background-color: #ebf8ff;
                border-left: 4px solid #3182ce;
                padding: 15px;
                margin-bottom: 25px;
                border-radius: 0 4px 4px 0;
            }}
            
            .memo-block p {{
                margin: 0;
                font-style: italic;
                color: #2c5282;
            }}
        </style>
    </head>
    <body>

        <div class="header-banner">
            <h1>STRATA Executive Summary Report</h1>
            <p>Environment Scenario Registry Workspace: {trading_name}</p>
        </div>

        <div class="memo-block">
            <p><strong>Strategic Briefing Memorandum:</strong> This quantitative position assessment outlines the modeled 60-month horizon performance trajectory for {trading_name}. Data arrays are compiled directly from secure client data registries and fully synchronized with authorized corporate tax, debt scheduling, and overhead models.</p>
        </div>

        <h2>Core Key Performance Benchmarks</h2>
        <div class="metric-table">
            <div class="metric-row">
                <div class="metric-card">
                    <div class="metric-value">£{total_revenue:,.0f}</div>
                    <div class="metric-label">Cumulative Gross Revenue</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">£{total_ebit:,.0f}</div>
                    <div class="metric-label">Aggregate Operating EBIT</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{avg_margin:.2f}%</div>
                    <div class="metric-label">Average Operating Margin</div>
                </div>
            </div>
        </div>

        <div class="metric-table">
            <div class="metric-row">
                <div class="metric-card">
                    <div class="metric-value">£{peak_cash:,.0f}</div>
                    <div class="metric-label">Peak Liquidity Point</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">£{ending_cash:,.0f}</div>
                    <div class="metric-label">Month-60 Cash Position</div>
                </div>
                <div class="metric-card" style="background-color: #edf2f7;">
                    <div class="metric-value" style="color: #4a5568;">60 Months</div>
                    <div class="metric-label">Projection Run Window</div>
                </div>
            </div>
        </div>

        <h2>Year-1 Monthly Runway Matrix</h2>
        <p style="margin-bottom: 10px; color: #4a5568;">Granular monthly position tracking spanning the initial 12-month initialization runway loop:</p>
        
        <table class="data-matrix">
            <thead>
                <tr>
                    <th style="text-align: left;">Timeline</th>
                    <th>Revenue</th>
                    <th>COGS</th>
                    <th>Opex</th>
                    <th>Operating EBIT</th>
                    <th>Cash Reserves</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Build out first 12 months rows dynamically
    for idx in range(12):
        row = df.iloc[idx]
        html_content += f"""
                <tr class="zebra-row">
                    <td class="month-col">{df.index[idx]}</td>
                    <td>£{row['Revenue (£)']:,.0f}</td>
                    <td>£{row['COGS (£)']:,.0f}</td>
                    <td>£{row['Opex (£)']:,.0f}</td>
                    <td>£{row['EBIT (£)']:,.0f}</td>
                    <td style="font-weight: bold; color: #2b6cb0;">£{row['Cash Reserves (£)']:,.0f}</td>
                </tr>"""
                
    html_content += """
            </tbody>
        </table>

        <h2 style="page-break-before: always;">Long-Range Annual Financial Position</h2>
        <p style="margin-bottom: 10px; color: #4a5568;">Aggregated twelve-month chronological blocks illustrating structured macro trends:</p>
        
        <table class="data-matrix">
            <thead>
                <tr>
                    <th style="text-align: left;">Annualized Block</th>
                    <th>Gross Revenue</th>
                    <th>Operating EBIT</th>
                    <th>Year-End Cash Position</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Aggregate to annual rows
    for yr in range(1, 6):
        start_m = (yr - 1) * 12
        end_m = yr * 12
        annual_slice = df.iloc[start_m:end_m]
        
        rev_ann = annual_slice["Revenue (£)"].sum()
        ebit_ann = annual_slice["EBIT (£)"].sum()
        cash_ann = annual_slice["Cash Reserves (£)"].iloc[-1]
        
        html_content += f"""
                <tr class="zebra-row">
                    <td class="month-col">Year {yr} Summary Matrix</td>
                    <td>£{rev_ann:,.0f}</td>
                    <td>£{ebit_ann:,.0f}</td>
                    <td style="font-weight: bold; color: #2b6cb0;">£{cash_ann:,.0f}</td>
                </tr>"""

    html_content += """
            </tbody>
        </table>

        <h2>Regulatory Compliance & Governance Sign-off</h2>
        <p>This document constitutes a compiled quantitative forecast and does not substitute formal audited regulatory reports. Calculations align explicitly with parameters tracked inside the secure corporate core engine workspace registries.</p>
        
        <div style="margin-top: 40px; border-top: 1px solid #cbd5e0; padding-top: 15px; font-size: 8pt; color: #a0aec0; text-align: center;">
            Report generated via STRATA Core Intelligence Pipeline Engine on 2026-06-10.
        </div>
    </body>
    </html>
    """
    
    # Explicitly pass html_content as a named keyword parameter to bypass instantiation mismatch
    html_object = HTML(string=html_content)
    return html_object.write_pdf()