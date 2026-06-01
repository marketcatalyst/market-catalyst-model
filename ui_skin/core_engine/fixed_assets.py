# core_engine/fixed_assets.py

def calculate_fixed_asset_lifecycle(
    asset_cost: float,
    purchase_month_index: int,
    useful_life_months: int,
    asset_type: str, # "EV_Brand_New", "Standard_Machinery", "General_Office_Asset"
    forecast_horizon_months: int = 60
) -> dict:
    """
    Processes a capital expenditure asset from purchase to disposal.
    Generates monthly timelines for accounting depreciation, cash requirements,
    and returns immediate UK HMRC tax-planning data.
    """
    # Initialize empty 60-month arrays to map our data to the master orchestrator
    capex_cash_outflow = [0.0] * forecast_horizon_months
    pl_depreciation_expense = [0.0] * forecast_horizon_months
    bs_net_book_value = [0.0] * forecast_horizon_months
    
    # Trigger the full equipment invoice cash drop in the month it is bought
    if 0 <= purchase_month_index < forecast_horizon_months:
        capex_cash_outflow[purchase_month_index] = asset_cost

    # --- 1. Accounting Depreciation Loop (Straight-Line) ---
    monthly_depreciation_charge = asset_cost / useful_life_months if useful_life_months > 0 else 0.0
    running_nbv = asset_cost

    for m in range(forecast_horizon_months):
        if m < purchase_month_index:
            bs_net_book_value[m] = 0.0
            continue
            
        if running_nbv > 0.0:
            # Ensure we don't accidentally depreciate below zero
            actual_charge = min(monthly_depreciation_charge, running_nbv)
            pl_depreciation_expense[m] = round(actual_charge, 2)
            running_nbv -= actual_charge
            
        bs_net_book_value[m] = round(running_nbv, 2)

    # --- 2. Proactive UK HMRC Tax Planning Logic ---
    # Determine if the asset qualifies for immediate 100% upfront tax shields
    fya_tax_shield_saved = 0.0
    tax_treatment_applied = "Standard Main Pool WDA (18%)"
    
    # Using 25% standard UK Corporation Tax main rate for calculations
    UK_CORP_TAX_RATE = 0.25 
    
    if asset_type == "EV_Brand_New":
        # 100% First-Year Allowance completely clears the asset cost against tax in Year 1
        fya_tax_shield_saved = asset_cost * UK_CORP_TAX_RATE
        tax_treatment_applied = "100% First-Year Allowance (FYA)"
    elif asset_type == "Standard_Machinery":
        # Annual Investment Allowance offers 100% upfront relief on standard plant up to £1m
        fya_tax_shield_saved = asset_cost * UK_CORP_TAX_RATE
        tax_treatment_applied = "100% Annual Investment Allowance (AIA)"
    else:
        # Standard cars or used office assets write down slowly at 18% in Year 1
        year_1_wda_deduction = asset_cost * 0.18
        fya_tax_shield_saved = year_1_wda_deduction * UK_CORP_TAX_RATE

    return {
        # Timelines for the 3-Way layout loop
        "timeline_cash_outflow": capex_cash_outflow,
        "timeline_pl_depreciation": pl_depreciation_expense,
        "timeline_bs_asset_nbv": bs_net_book_value,
        
        # Static advisory tax flags
        "tax_treatment_applied": tax_treatment_applied,
        "immediate_tax_cash_saving": round(fya_tax_shield_saved, 2)
    }