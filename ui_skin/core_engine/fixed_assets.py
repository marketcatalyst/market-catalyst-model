# core_engine/fixed_assets.py

def calculate_fixed_asset_lifecycle(
    asset_cost: float,
    purchase_month_index: int,
    useful_life_months: int,
    residual_value: float = 0.0,
    tax_allowance_code: str = "WDA_MAIN",  # "AIA_100", "FYA_100", "WDA_MAIN", "WDA_SPECIAL"
    systemic_multiplier: float = 1.0,      # Abstract modifier for core engine capacity modeling
    systemic_note: str = "Standard asset deployment.",
    uk_corp_tax_rate: float = 0.25,        # Calibrated for current UK corporate tax baselines
    forecast_horizon_months: int = 60
) -> dict:
    """
    Decoupled SaaS Engine: Processes any capital expenditure asset from purchase to disposal.
    Accepts standardized tax configuration codes and abstract physical multipliers, 
    ensuring the engine remains entirely agnostic to the subscriber's specific industry.
    """
    # Initialize empty timeline arrays for the global 3-Way master orchestrator
    capex_cash_outflow = [0.0] * forecast_horizon_months
    pl_depreciation_expense = [0.0] * forecast_horizon_months
    bs_net_book_value = [0.0] * forecast_horizon_months
    
    # Trigger the equipment invoice cash impact in the designated purchase month
    if 0 <= purchase_month_index < forecast_horizon_months:
        capex_cash_outflow[purchase_month_index] = asset_cost

    # --- 1. Pure Accounting Depreciation Loop (Straight-Line with Salvage Protection) ---
    depreciable_base = asset_cost - residual_value
    monthly_depreciation_charge = depreciable_base / useful_life_months if useful_life_months > 0 else 0.0
    running_nbv = asset_cost

    for m in range(forecast_horizon_months):
        if m < purchase_month_index:
            bs_net_book_value[m] = 0.0
            continue
            
        # Guarantee the asset never depreciates past its designated residual market value
        if running_nbv > residual_value:
            actual_charge = min(monthly_depreciation_charge, running_nbv - residual_value)
            pl_depreciation_expense[m] = round(actual_charge, 2)
            running_nbv -= actual_charge
        else:
            pl_depreciation_expense[m] = 0.0
            
        bs_net_book_value[m] = round(running_nbv, 2)

    # --- 2. Abstractized UK HMRC Tax Planning Router ---
    fya_tax_shield_saved = 0.0
    tax_treatment_applied = "Standard Main Pool WDA (18%)"
    
    if tax_allowance_code == "AIA_100":
        # Annual Investment Allowance / Full Expensing (100% upfront relief)
        fya_tax_shield_saved = asset_cost * uk_corp_tax_rate
        tax_treatment_applied = "100% Upfront Capital Allowance (AIA / Full Expensing)"
        
    elif tax_allowance_code == "FYA_100":
        # First-Year Allowance (100% upfront relief for specialized/green assets)
        fya_tax_shield_saved = asset_cost * uk_corp_tax_rate
        tax_treatment_applied = "100% First-Year Allowance (FYA)"
        
    elif tax_allowance_code == "WDA_SPECIAL":
        # Special Rate Pool (6% writing down allowance on integral features/structures)
        year_1_wda = asset_cost * 0.06
        fya_tax_shield_saved = year_1_wda * uk_corp_tax_rate
        tax_treatment_applied = "Special Rate Pool WDA (6%)"
        
    else:
        # Default standard main pool writing down allowance (18% reducing balance)
        year_1_wda = asset_cost * 0.18
        fya_tax_shield_saved = year_1_wda * uk_corp_tax_rate
        tax_treatment_applied = "Standard Main Pool WDA (18%)"

    return {
        # Timelines for the 3-Way output schedules
        "timeline_cash_outflow": capex_cash_outflow,
        "timeline_pl_depreciation": pl_depreciation_expense,
        "timeline_bs_asset_nbv": bs_net_book_value,
        
        # Regulatory/Tax Planning metadata
        "tax_treatment_applied": tax_treatment_applied,
        "immediate_tax_cash_saving": round(fya_tax_shield_saved, 2),
        
        # Causal Systems-Thinking Metadata
        "systemic_multiplier": systemic_multiplier,
        "systemic_note": systemic_note
    }