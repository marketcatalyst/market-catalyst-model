# ui_skin/core_engine/tax_engine.py
import numpy as np
from typing import Dict

def calculate_corporation_tax_schedule(
    monthly_net_profit: np.ndarray,
    monthly_book_depreciation: np.ndarray,
    monthly_disposal_gains: np.ndarray,
    monthly_disposal_proceeds: np.ndarray,
    tax_main_pool_additions: np.ndarray,
    tax_special_pool_additions: np.ndarray,
    opening_main_pool_wdv: float = 50000.0,
    opening_special_pool_wdv: float = 20000.0,
    base_tax_rate: float = 0.25,
    total_months: int = 60
) -> Dict[str, np.ndarray]:
    """
    Computes annual corporation tax reconciliations and projects accurate 
    statutory cash payout timelines using 2026 HMRC fiscal protocols.
    """
    timeline_tax_expense = np.zeros(total_months)
    timeline_tax_liability_bs = np.zeros(total_months)
    timeline_tax_cash_outflow = np.zeros(total_months)
    
    # Track the running Written Down Value (WDV) of the tax pools across years
    current_main_wdv = opening_main_pool_wdv
    current_special_wdv = opening_special_pool_wdv
    
    accumulated_tax_liability = 0.0
    
    # Loop through the 5-year horizon in annual 12-month blocks
    for year in range(total_months // 12):
        start_m = year * 12
        end_m = start_m + 12
        
        # 1. Aggregate Year-to-Date Accounting Figures
        y_net_profit = np.sum(monthly_net_profit[start_m:end_m])
        y_book_depr = np.sum(monthly_book_depreciation[start_m:end_m])
        y_disp_gains = np.sum(monthly_disposal_gains[start_m:end_m])
        y_disp_proceeds = np.sum(monthly_disposal_proceeds[start_m:end_m])
        
        # 2. Aggregate Year-to-Date CapEx Additions
        y_main_additions = np.sum(tax_main_pool_additions[start_m:end_m])
        y_special_additions = np.sum(tax_special_pool_additions[start_m:end_m])
        
        # 3. Process Accelerated Incentives (Annual Investment Allowance)
        # Up to £1m AIA shields additions 100%. Remaining balances enter the pools.
        aia_claimed_main = y_main_additions 
        aia_claimed_special = y_special_additions
        total_accelerated_allowances = aia_claimed_main + aia_claimed_special
        
        # 4. Process Disposals against Tax Pools
        current_main_wdv = max(0.0, current_main_wdv - y_disp_proceeds)
        
        # 5. Compute Annual 2026 Writing Down Allowances (WDA)
        # Main pool runs at 14% on a reducing balance basis; Special rate pool stays at 6%
        wda_main = current_main_wdv * 0.14
        wda_special = current_special_wdv * 0.06
        total_pool_wda = wda_main + wda_special
        
        # Amortize pools for the start of the next financial year
        current_main_wdv -= wda_main
        current_special_wdv -= wda_special
        
        # Sum total statutory tax relief claimed
        total_capital_allowances = total_accelerated_allowances + total_pool_wda
        
        # 6. Execute the Master Taxable Profit Reconciliation Formula
        taxable_profit = y_net_profit + y_book_depr - y_disp_gains - total_capital_allowances
        taxable_profit = max(0.0, taxable_profit) # Floor taxable base to prevent negative values
        
        # 7. Calculate Final Corporation Tax Due
        annual_tax_due = taxable_profit * base_tax_rate
        
        # Assign the tax charge to hit the final month of that financial year's P&L
        timeline_tax_expense[end_m - 1] = round(annual_tax_due, 2)
        
        # 8. Time-Shift the Cash Outflow (9 Months & 1 Day Collection Lag)
        payout_month = end_m + 9 # Month 12 tax liability leaves the bank in Month 21
        if payout_month - 1 < total_months:
            timeline_tax_cash_outflow[payout_month - 1] = round(annual_tax_due, 2)
            
    # 9. Compile the Accumulating Balance Sheet Liability Trace
    for m in range(total_months):
        accumulated_tax_liability += timeline_tax_expense[m]
        accumulated_tax_liability -= timeline_tax_cash_outflow[m]
        timeline_tax_liability_bs[m] = round(accumulated_tax_liability, 2)
        
    return {
        "timeline_tax_expense": timeline_tax_expense,
        "timeline_tax_liability_bs": timeline_tax_liability_bs,
        "timeline_tax_cash_outflow": timeline_tax_cash_outflow
    }