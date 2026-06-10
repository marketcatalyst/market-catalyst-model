# ui_skin/core_engine/report_generator.py
import pandas as pd
import io
from ui_skin.core_engine.master_model import generate_integrated_3way_forecast

def export_forecast_to_excel(inputs: dict, overrides: dict = None) -> bytes:
    """
    Generates a multi-tab, highly formatted corporate Excel workbook 
    from the current active 60-month model dataset.
    Returns raw bytes suitable for Streamlit download buttons.
    """
    # 1. Compute the underlying data matrices
    df = generate_integrated_3way_forecast(inputs, overrides)
    
    # Isolate independent blocks for specialized sheets
    pl_cols = ["Revenue (£)", "COGS (£)", "Opex (£)", "EBIT (£)", "Tax Expense (£)"]
    cf_cols = ["EBIT (£)", "Interest Expense (£)", "Debt Service Cash Outflow (£)", "VAT Cash Outflow (£)", "Cash Reserves (£)"]
    bs_cols = ["Cash Reserves (£)", "VAT Liability BS (£)", "Tax Liability BS (£)", "Outstanding Debt Balance (£)"]
    
    output = io.BytesIO()
    
    # 2. Compile using xlsxwriter for professional presentation auto-styling
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df[pl_cols].to_excel(writer, sheet_name='Profit & Loss')
        df[cf_cols].to_excel(writer, sheet_name='Cash Flow Ledger')
        df[bs_cols].to_excel(writer, sheet_name='Balance Sheet Accruals')
        
        # Access the workbook to apply enterprise-grade styling wrappers
        workbook  = writer.book
        
        # Define uniform formats
        header_format = workbook.add_format({
            'bold': True, 'text_wrap': True, 'fg_color': '#1a365d', 'font_color': '#ffffff', 'border': 1
        })
        currency_format = workbook.add_format({'num_format': '£#,##0', 'align': 'right'})
        total_format = workbook.add_format({'bold': True, 'top': 1, 'bottom': 6, 'num_format': '£#,##0'})
        
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            worksheet.set_zoom(100)
            
            # Format column metrics cleanly
            worksheet.set_column('A:A', 12) # Month tags column
            worksheet.set_column('B:Z', 18, currency_format) # Financial numeric ranges
            
            # Re-apply bold headers with custom navy color palette
            for col_num, value in enumerate(df.columns):
                worksheet.write(0, col_num + 1, value, header_format)
                
    return output.getvalue()