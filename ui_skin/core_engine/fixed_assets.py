# ui_skin/core_engine/fixed_assets.py
import pandas as pd
import numpy as np
from typing import List, Dict, Any

def calculate_multi_asset_depreciation_matrix(
    opening_nbv: float,
    planned_capex_list: List[Dict[str, Any]],
    total_months: int = 60,
    estimated_existing_residual_months: int = 48
) -> Dict[str, np.ndarray]:
    """
    Computes a synchronized 60-month time-series array tracking gross capital costs, 
    monthly straight-line depreciation expenses, accumulated depreciation, and Net Book Value (NBV).
    
    Handles a point-in-time opening asset base alongside a dynamic stream of staggered future capex events.
    """
    # Initialize zero-filled tracking vectors for the entire horizon
    timeline_gross_cost = np.zeros(total_months)
    timeline_depreciation_expense = np.zeros(total_months)
    timeline_accumulated_depreciation = np.zeros(total_months)
    timeline_nbv = np.zeros(total_months)
    
    # --- PHASE 1: Existing Legacy Asset Base Run-Rate ---
    # Safely unwind the opening balance sheet book value over its remaining lifecycle
    if opening_nbv > 0 and estimated_existing_residual_months > 0:
        monthly_legacy_depr = opening_nbv / estimated_existing_residual_months
        current_legacy_nbv = opening_nbv
        
        for m in range(total_months):
            if current_legacy_nbv > 0:
                # Depreciate until carrying value hits zero floor
                depr_charge = min(monthly_legacy_depr, current_legacy_nbv)
                timeline_depreciation_expense[m] += depr_charge
                current_legacy_nbv -= depr_charge
    
    # Set the initial seeding net book value for Month 0 context
    running_opening_nbv = opening_nbv

    # --- PHASE 2: Dynamic Staggered Future Capital Rollouts ---
    # Track the cumulative cost additions over the time series vector
    cumulative_additions_cost = 0.0
    
    for m in range(total_months):
        month_index_1based = m + 1
        
        # Scan the planned asset list for items matching the active calendar month index
        for asset in planned_capex_list:
            purchase_month = int(asset.get("Transaction Month", -1))
            cost = float(asset.get("Gross Purchase Price (£)", 0.0))
            useful_life_years = float(asset.get("Useful Life (Years)", 5))
            useful_life_months = max(useful_life_years * 12, 1.0)
            
            # If the item execution month hits our active index, activate its cost basis
            if purchase_month == month_index_1based:
                cumulative_additions_cost += cost
        
        # Capture current running asset base gross cost
        timeline_gross_cost[m] = cumulative_additions_cost
        
        # Calculate active runtime depreciation for all executed assets up to this month
        for asset in planned_capex_list:
            purchase_month = int(asset.get("Transaction Month", -1))
            cost = float(asset.get("Gross Purchase Price (£)", 0.0))
            useful_life_years = float(asset.get("Useful Life (Years)", 5))
            useful_life_months = max(useful_life_years * 12, 1.0)
            
            # An asset only depreciates if we are chronologically past its purchase date
            if month_index_1based >= purchase_month and purchase_month > 0:
                months_held = (month_index_1based - purchase_month) + 1
                # Ensure the asset has not already exceeded its economic useful life span
                if months_held <= useful_life_months:
                    monthly_charge = cost / useful_life_months
                    timeline_depreciation_expense[m] += monthly_charge
                elif months_held == useful_life_months + 1:
                    # Capture fractional remainder on expiration boundary if any
                    pass

    # --- PHASE 3: Consolidated Accounting Reconciliation ---
    # Traverse the arrays to compound monthly accumulated totals and absolute net values
    current_acc_depr = 0.0
    current_calculated_nbv = running_opening_nbv
    
    for m in range(total_months):
        monthly_expense = timeline_depreciation_expense[m]
        current_acc_depr += monthly_expense
        
        # New NBV = Previous NBV + New Additions Added in Month - Monthly Depreciation Expense
        # Determine additions explicitly occurring in this exact step
        if m == 0:
            additions_this_month = timeline_gross_cost[m]
        else:
            additions_this_month = timeline_gross_cost[m] - timeline_gross_cost[m - 1]
            
        current_calculated_nbv = current_calculated_nbv + additions_this_month - monthly_expense
        
        # Commit computed values safely into vector stores
        timeline_accumulated_depreciation[m] = round(current_acc_depr, 2)
        timeline_nbv[m] = round(max(current_calculated_nbv, 0.0), 2)
        timeline_depreciation_expense[m] = round(monthly_expense, 2)
        timeline_gross_cost[m] = round(timeline_gross_cost[m], 2)

    return {
        "timeline_gross_cost": timeline_gross_cost,
        "timeline_depreciation_expense": timeline_depreciation_expense,
        "timeline_accumulated_depreciation": timeline_accumulated_depreciation,
        "timeline_nbv": timeline_nbv
    }