# ui_skin/core_engine/fixed_assets.py
import pandas as pd
import numpy as np
from typing import List, Dict, Any

# Statutory Rules for 2026 Financial Year (HMRC Main Pool adjusted to 14% as of April 2026)
CATEGORY_RULES = {
    "Office Tech & Software": {"book_life_years": 3, "book_method": "SL", "hmrc_pool": "Main"},
    "Catering & Plant Machinery": {"book_life_years": 7, "book_method": "SL", "hmrc_pool": "Main"},
    "Standard Delivery Vehicles": {"book_life_years": 5, "book_method": "SL", "hmrc_pool": "Main"},
    "Electric Vehicles (EV)": {"book_life_years": 5, "book_method": "SL", "hmrc_pool": "Main"},
    "Building Fit-Outs & Electrics": {"book_life_years": 10, "book_method": "RB", "hmrc_pool": "Special"}
}

def calculate_multi_asset_depreciation_matrix(
    opening_nbv: float,
    planned_capex_list: List[Dict[str, Any]],
    total_months: int = 60,
    estimated_existing_residual_months: int = 48
) -> Dict[str, np.ndarray]:
    """
    Advanced 3-way platform asset engine. Computes a synchronized time-series array 
    tracking gross capital costs, monthly book depreciation, accumulated pools, and NBV.
    
    Upgraded to handle asset category mapping, mid-horizon disposal events (P&L gains/losses),
    and isolated tax capital allowance pool additions in a single linear pass.
    """
    # 1. Initialize empty tracking arrays for the entire 60-month window
    timeline_gross_cost = np.zeros(total_months)
    timeline_depreciation_expense = np.zeros(total_months)
    timeline_accumulated_depreciation = np.zeros(total_months)
    timeline_nbv = np.zeros(total_months)
    
    # New structural outputs required for downstream Cash Flow and P&L Tax reconciliation
    timeline_disposal_gains = np.zeros(total_months)
    timeline_disposal_proceeds = np.zeros(total_months)
    tax_main_pool_additions = np.zeros(total_months)
    tax_special_pool_additions = np.zeros(total_months)
    
    # --- PHASE 1: Legacy Asset Base Setup ---
    # We maintain your safe floor logic for the legacy unwinding base
    legacy_monthly_depr = opening_nbv / max(estimated_existing_residual_months, 1)
    current_legacy_nbv = opening_nbv
    
    # --- PHASE 2: Consolidated Single-Pass Matrix Construction ---
    # By un-nesting the asset arrays, we eliminate the O(M x N) calculation bottleneck
    for m in range(total_months):
        month_index_1based = m + 1
        
        # A. Process Legacy Unwind for the active month step
        if current_legacy_nbv > 0:
            depr_charge = min(legacy_monthly_depr, current_legacy_nbv)
            timeline_depreciation_expense[m] += depr_charge
            current_legacy_nbv -= depr_charge
            
        # B. Scan and calculate individual forward asset lifecycles dynamically
        for asset in planned_capex_list:
            category = asset.get("Category", "Catering & Plant Machinery")
            rules = CATEGORY_RULES.get(category, CATEGORY_RULES["Catering & Plant Machinery"])
            
            cost = float(asset.get("Gross Purchase Price (£)", 0.0))
            purchase_month = int(asset.get("Transaction Month", -1))
            disposal_month = int(asset.get("Disposal Month", -1))
            proceeds = float(asset.get("Disposal Proceeds (£)", 0.0))
            
            life_months = max(int(asset.get("Useful Life (Years)", rules["book_life_years"]) * 12), 1)
            
            # Identify if the asset has been purchased yet, and ensure it isn't disposed of yet
            is_active_this_month = (purchase_month <= month_index_1based) if purchase_month > 0 else False
            if disposal_month > -1 and month_index_1based >= disposal_month:
                is_active_this_month = False
                
            # Track tax allowance pool additions at the exact moment of execution
            if purchase_month == month_index_1based:
                if rules["hmrc_pool"] == "Main":
                    tax_main_pool_additions[m] += cost
                else:
                    tax_special_pool_additions[m] += cost
                    
            # Process Live Book Depreciation Run-rates
            if is_active_this_month:
                months_held = (month_index_1based - purchase_month) + 1
                
                # Check if asset is still inside its useful book lifecycle
                if months_held <= life_months:
                    if rules["book_method"] == "SL":
                        monthly_charge = cost / life_months
                    else:
                        # Reducing Balance implementation: 25% annual split down to monthly
                        # Calculates depreciation based on the remaining balance at the start of the year
                        elapsed_years = (months_held - 1) // 12
                        remaining_cost_base = cost * ((1 - 0.25) ** elapsed_years)
                        monthly_charge = (remaining_cost_base * 0.25) / 12
                        
                    timeline_depreciation_expense[m] += monthly_charge
                    
            # C. Process Active Cost Tracking
            if is_active_this_month:
                timeline_gross_cost[m] += cost
                
            # D. Handle Interactive Asset Disposal Events (The Realism Trigger)
            if month_index_1based == disposal_month:
                timeline_disposal_proceeds[m] += proceeds
                
                # Reconstruct NBV at the exact point of disposal to deduce gain/loss
                months_held_pre_sale = (disposal_month - purchase_month)
                total_depr_claimed = min((cost / life_months) * months_held_pre_sale, cost)
                nbv_at_sale = max(cost - total_depr_claimed, 0.0)
                
                # Dynamic P&L Gain/Loss statement settlement
                gain_loss = proceeds - nbv_at_sale
                timeline_disposal_gains[m] += gain_loss

    # --- PHASE 3: Balancing and Rounding Sweep ---
    running_accumulated_depr = 0.0
    running_net_additions_nbv = opening_nbv
    
    for m in range(total_months):
        monthly_expense = timeline_depreciation_expense[m]
        running_accumulated_depr += monthly_expense
        
        # Determine gross changes occurring in this specific month step
        if m == 0:
            additions_this_month = timeline_gross_cost[m]
        else:
            additions_this_month = timeline_gross_cost[m] - timeline_gross_cost[m - 1]
            
        # If an asset was disposed of, adjust the running NBV base
        if timeline_disposal_proceeds[m] > 0:
            # Drop the carrying cost out of the balance sheet pool
            running_net_additions_nbv -= (timeline_disposal_proceeds[m] - timeline_disposal_gains[m])
            
        running_net_additions_nbv = running_net_additions_nbv + additions_this_month - monthly_expense
        
        # Commit clean, rounded integers to vectors to preserve system scannability
        timeline_accumulated_depreciation[m] = round(running_accumulated_depr, 2)
        timeline_nbv[m] = round(max(running_net_additions_nbv, 0.0), 2)
        timeline_depreciation_expense[m] = round(monthly_expense, 2)
        timeline_gross_cost[m] = round(timeline_gross_cost[m], 2)

    return {
        "timeline_gross_cost": timeline_gross_cost,
        "timeline_depreciation_expense": timeline_depreciation_expense,
        "timeline_accumulated_depreciation": timeline_accumulated_depreciation,
        "timeline_nbv": timeline_nbv,
        "timeline_disposal_gains": round(timeline_disposal_gains, 2),
        "timeline_disposal_proceeds": round(timeline_disposal_proceeds, 2),
        "tax_main_pool_additions": tax_main_pool_additions,
        "tax_special_pool_additions": tax_special_pool_additions
    }