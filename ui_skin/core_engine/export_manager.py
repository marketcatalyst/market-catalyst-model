# ui_skin/core_engine/export_manager.py
import io
import pandas as pd
import numpy as np
from typing import Dict, Any

def generate_three_way_excel_bundle(engine_output: Dict[str, Any], baseline_inputs: Dict[str, Any]) -> bytes:
    """
    Converts raw 3-way numerical arrays into a stylized, institutional-grade 
    multi-tab Excel Workbook stream. All records are rounded to the nearest integer £1.
    """
    buffer = io.BytesIO()
    total_months = len(engine_output["Revenue"])
    timeline_columns = [f"Month {i}" for i in range(1, total_months + 1)]
    
    # --- 1. EXTRACT DATA FOR TAB 1: PROFIT & LOSS ---
    rev = engine_output["Revenue"]
    cogs = engine_output["COGS"]
    overheads = engine_output["Overheads"]
    ebitda = rev - cogs - overheads
    operating_profit = ebitda - engine_output["Depreciation"] - engine_output["Interest Paid"]
    
    pl_dict = {
        "Gross Revenue Turnover (£)": rev,
        "Direct Raw Material Purchases (£)": -engine_output["Purchases"],
        "Add/Less: Capitalized Stock Movement (£)": engine_output["Stock Movement"],
        "TOTAL COST OF GOODS SOLD (COGS) (£)": -cogs,
        "Administrative Overheads (£)": -overheads,
        "OPERATIONAL EBITDA (£)": ebitda,
        "Book Depreciation Expense (£)": -engine_output["Depreciation"],
        "Finance Costs / Interest Expense (£)": -engine_output["Interest Paid"],
        "OPERATING PROFIT (EBIT) (£)": operating_profit,
        "Statutory Corporation Tax Provision (£)": -engine_output["Tax Expense"],
        "NET PROFIT AFTER TAX (EAT) (£)": engine_output["Net Profit"]
    }
    pl_df = pd.DataFrame(pl_dict, index=timeline_columns).T

    # --- 2. EXTRACT DATA FOR TAB 2: CASH FLOW ---
    net_operating_cash_flow = engine_output["Net Profit"] + engine_output["Depreciation"] + engine_output["Stock Movement"]
    net_movement = (net_operating_cash_flow - engine_output["Principal Repayments"] - engine_output["Tax Cash Paid"] - engine_output["Interest Paid"] + engine_output["Asset Disposal Proceeds"])
    
    cf_dict = {
        "Net Profit Allocation (£)": engine_output["Net Profit"],
        "Add: Non-Cash Depreciation (£)": engine_output["Depreciation"],
        "Add/Less: Stock Movement Non-Cash Delta (£)": engine_output["Stock Movement"],
        "Less: Debt Principal Repayments (£)": -engine_output["Principal Repayments"],
        "Less: Corporation Tax Payouts (£)": -engine_output["Tax Cash Paid"],
        "Less: Interest Payments (£)": -engine_output["Interest Paid"],
        "Add: Asset Disposal Proceeds Windfalls (£)": engine_output["Asset Disposal Proceeds"],
        "Net Monthly Cash Flow Movement (£)": net_movement,
        "CLOSING BANK CASH POSITION (£)": engine_output["Cash At Bank"]
    }
    cf_df = pd.DataFrame(cf_dict, index=timeline_columns).T

    # --- 3. EXTRACT DATA FOR TAB 3: BALANCE SHEET ---
    cash_seed = float(baseline_inputs.get("opening_cash_balance", 69488.0))
    fa_seed = float(baseline_inputs.get("opening_fixed_assets_nbv", 150000.0))
    ar_seed = float(baseline_inputs.get("opening_accounts_receivable", 44886.0))
    ap_seed = float(baseline_inputs.get("opening_accounts_payable", 8000.0))
    debt_seed = float(baseline_inputs.get("opening_long_term_debt", 0.0))
    inv_seed = engine_output["Inventory Asset BS"][0]
    re_seed = (cash_seed + fa_seed + ar_seed + inv_seed) - (debt_seed + ap_seed)
    
    timeline_ap = np.full(total_months, ap_seed)
    timeline_re = np.zeros(total_months)
    running_re = re_seed
    for m in range(total_months):
        running_re += engine_output["Net Profit"][m]
        timeline_re[m] = running_re
        
    total_assets = engine_output["Fixed Asset NBV"] + engine_output["Cash At Bank"] + engine_output["Inventory Asset BS"] + engine_output["Accounts Receivable BS"]
    total_liabilities = engine_output["Outstanding Debt"] + engine_output["Tax Liability BS"] + timeline_ap
    net_assets = total_assets - total_liabilities
    
    bs_dict = {
        "Non-Current Assets: Fixed Assets NBV (£)": engine_output["Fixed Asset NBV"],
        "Current Assets: Warehouse Inventory Pool (£)": engine_output["Inventory Asset BS"],
        "Current Assets: Accounts Receivable (AR) (£)": engine_output["Accounts Receivable BS"],
        "Current Assets: Liquid Cash Base (£)": engine_output["Cash At Bank"],
        "TOTAL STRUCTURAL ASSETS (£)": total_assets,
        "Non-Current Liabilities: Outstanding Debt (£)": -engine_output["Outstanding Debt"],
        "Current Liabilities: Deferred Tax Reserve (£)": -engine_output["Tax Liability BS"],
        "Current Liabilities: Accounts Payable (AP) (£)": -timeline_ap,
        "TOTAL STRUCTURAL LIABILITIES (£)": -total_liabilities,
        "NET NET ASSETS CAPITAL (£)": net_assets,
        "Equity: Accumulated Retained Reserves (£)": timeline_re,
        "TOTAL CAPITAL AND RESERVES MATCH (£)": timeline_re
    }
    bs_df = pd.DataFrame(bs_dict, index=timeline_columns).T

    # BOARDROOM RESOLUTION: Round all output datasets cleanly to integers before Excel compilation
    pl_df = pl_df.round(0).astype(int)
    cf_df = cf_df.round(0).astype(int)
    bs_df = bs_df.round(0).astype(int)

    # --- 4. STREAM COMPILED TABLES TO EXCEL TABS ---
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        pl_df.to_excel(writer, sheet_name="Income Statement (P&L)")
        cf_df.to_excel(writer, sheet_name="Cash Flow Statement")
        bs_df.to_excel(writer, sheet_name="Balance Sheet Position")
        
    return buffer.getvalue()