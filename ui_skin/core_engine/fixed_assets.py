# ui_skin/core_engine/fixed_assets.py
import numpy as np
from typing import List, Dict, Any

def calculate_multi_asset_depreciation_matrix(
    opening_nbv: float,
    planned_capex_list: List[Dict[str, Any]],
    total_months: int = 60
) -> Dict[str, Any]:
    """
    Orchestrates the corporate asset lifecycle across a multi-year horizon.
    Calculates monthly reducing-balance depreciation, maps capital additions 
    into strategic tax pools, and handles contract disposal valuations.
    """
    # Initialize timeline arrays to store vectorized records
    timeline_depreciation_expense = np.zeros(total_months)
    timeline_disposal_gains = np.zeros(total_months)
    timeline_disposal_proceeds = np.zeros(total_months)
    tax_main_pool_additions = np.zeros(total_months)
    tax_special_pool_additions = np.zeros(total_months)
    timeline_nbv = np.zeros(total_months)
    
    # Track the core legacy opening pool book value
    running_opening_nbv = opening_nbv
    # Standard monthly depreciation rate for legacy pool (15% per annum reducing balance)
    monthly_legacy_rate = 0.15 / 12.0
    
    # Store active individual capex objects for localized monitoring
    active_capex_items: List[Dict[str, Any]] = []
    
    for m in range(total_months):
        # Convert 0-indexed loop timeline variable 'm' into a 1-based calendar month
        current_calendar_month = m + 1
        
        # 1. Evaluate incoming additions (Capex Deployment) for Month m
        for capex in planned_capex_list:
            # Check against the 1-based calendar month provided by the ingestion layer
            if capex.get("Transaction Month") == current_calendar_month:
                cost = float(capex.get("Gross Purchase Price (£)", 0.0))
                category = str(capex.get("Category", "Main Pool")).lower()
                
                # Segregate into HMRC compliance pools
                if "special" in category or "integral" in category or "vehicle" in category:
                    tax_special_pool_additions[m] += cost
                else:
                    tax_main_pool_additions[m] += cost
                    
                # Append to active tracking matrices
                active_capex_items.append({
                    "cost": cost,
                    "nbv": cost,
                    "rate": 0.15 / 12.0,  # Standardized 15% monthly allocation rate
                    "disposal_month": capex.get("Disposal Month", -1),
                    "disposal_proceeds": float(capex.get("Disposal Proceeds (£)", 0.0))
                })
        
        # 2. Run Monthly Amortization Calculations
        # Legacies pool calculation
        legacy_dep_charge = running_opening_nbv * monthly_legacy_rate
        running_opening_nbv -= legacy_dep_charge
        monthly_depreciation_accumulator = legacy_dep_charge
        
        # Iterate over new equipment profiles and process unexpected liquidations
        remaining_active_assets = []
        for item in active_capex_items:
            if item["disposal_month"] == current_calendar_month:
                # Process structural asset retirement
                proceeds = item["disposal_proceeds"]
                timeline_disposal_proceeds[m] += proceeds
                
                # Gain/Loss = Net Sales Proceeds minus carrying Net Book Value
                capital_gain_or_loss = proceeds - item["nbv"]
                timeline_disposal_gains[m] += capital_gain_or_loss
            else:
                # Regular depreciation run
                item_dep_charge = item["nbv"] * item["rate"]
                item["nbv"] -= item_dep_charge
                monthly_depreciation_accumulator += item_dep_charge
                remaining_active_assets.append(item)
                
        active_capex_items = remaining_active_assets
        
        # 3. Synchronize Month End Calculations
        timeline_depreciation_expense[m] = monthly_depreciation_accumulator
        
        # Total combined net book value remaining on the Balance Sheet
        total_current_capex_nbv = sum(asset["nbv"] for asset in active_capex_items)
        timeline_nbv[m] = running_opening_nbv + total_current_capex_nbv

    # Return elements protected by vectorized numpy round rules to eliminate scalar TypeErrors
    return {
        "timeline_depreciation_expense": np.round(timeline_depreciation_expense, 2),
        "timeline_disposal_gains": np.round(timeline_disposal_gains, 2),
        "timeline_disposal_proceeds": np.round(timeline_disposal_proceeds, 2),
        "tax_main_pool_additions": np.round(tax_main_pool_additions, 2),
        "tax_special_pool_additions": np.round(tax_special_pool_additions, 2),
        "timeline_nbv": np.round(timeline_nbv, 2)
    }