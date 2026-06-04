# ui_skin/core_engine/master_orchestrator.py
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from core_engine.fixed_assets import calculate_multi_asset_depreciation_matrix
from core_engine.tax_engine import calculate_corporation_tax_schedule

def run_master_three_way_engine(
    baseline_inputs: Dict[str, Any],
    loan_register_df: pd.DataFrame,
    revenue_matrix_df: pd.DataFrame,
    planned_capex_list: List[Dict[str, Any]],
    total_months: int = 60
) -> Dict[str, Any]:
    """
    The master control hub for the STRATA financial engine. Sequentially orchestrates 
    operational margins, proactive inventory procurement, debt amortization, asset 
    lifecycles, and corporate tax schedules to output a balanced 3-way data ledger.
    """
    # --- 1. OPERATIONAL BASELINES & POLICY MODIFIERS ---
    monthly_revenue = float(revenue_matrix_df["Monthly Base Volume (£)"].sum())
    monthly_base_cogs = float(revenue_matrix_df["Associated COGS Pool (£)"].sum())
    monthly_overheads = float(baseline_inputs.get("admin_overheads_monthly", 8000.0))
    days_cover = float(baseline_inputs.get("inventory_days_cover", 30.0))
    
    # Initialize basic demand arrays across the 60-month timeline
    rev_array = np.full(total_months, monthly_revenue)
    base_cogs_demand = np.full(total_months, monthly_base_cogs)
    
    # --- 2. PROACTIVE INVENTORY ROLL-FORWARD ENGINE ---
    timeline_inventory_asset_bs = np.zeros(total_months)
    timeline_purchases_cash_outflow = np.zeros(total_months)
    timeline_p_l_stock_movement = np.zeros(total_months)
    
    # Calculate target stock requirements by scanning next month's sales activity level
    for m in range(total_months):
        next_month_demand = base_cogs_demand[m + 1] if (m + 1) < total_months else monthly_base_cogs
        # Target Stock Asset Base = Future Month Cost Base * (Days Cover Buffer / 30)
        timeline_inventory_asset_bs[m] = next_month_demand * (days_cover / 30.0)
        
    # Reconcile purchases vs internal stock delta tracking
    opening_inventory_seed = monthly_base_cogs * (days_cover / 30.0)
    
    for m in range(total_months):
        current_target_stock = timeline_inventory_asset_bs[m]
        previous_target_stock = timeline_inventory_asset_bs[m - 1] if m > 0 else opening_inventory_seed
        
        # Production Equation: Purchases = Demand Match + Stock Holding Incremental Change
        stock_delta = current_target_stock - previous_target_stock
        timeline_purchases_cash_outflow[m] = base_cogs_demand[m] + stock_delta
        
        # Double-entry rebalancing line: Positive delta pulls raw costs out of active month P&L
        timeline_p_l_stock_movement[m] = -stock_delta
        
    # Combined Cost of Goods Sold Line = Total Purchases + Stock Movement Adjustment
    final_p_l_cogs_line = timeline_purchases_cash_outflow + timeline_p_l_stock_movement
    overhead_array = np.full(total_months, monthly_overheads)
    
    # Core EBITDA calculation reflecting true matched production boundaries
    ebitda_array = rev_array - final_p_l_cogs_line - overhead_array
    
    # --- 3. DEBT AMORTIZATION WHEEL (APR-DRIVEN) ---
    timeline_interest_expense = np.zeros(total_months)
    timeline_principal_repayments = np.zeros(total_months)
    timeline_debt_balance_bs = np.zeros(total_months)
    running_debt_pool = float(loan_register_df["Current Balance (£)"].sum())
    
    for m in range(total_months):
        month_1based = m + 1
        monthly_interest_accumulator = 0.0
        monthly_principal_accumulator = 0.0
        
        for _, loan in loan_register_df.iterrows():
            rem_term = int(loan["Remaining Term (Months)"])
            pmt = float(loan["Monthly Payment (£)"])
            bal = float(loan["Current Balance (£)"])
            rate = float(loan["Interest Rate (%)"]) / 100.0
            
            if rem_term >= month_1based:
                approx_monthly_interest = (bal * rate) / 12.0
                principal_portion = min(pmt - approx_monthly_interest, bal)
                
                monthly_interest_accumulator += approx_monthly_interest
                monthly_principal_accumulator += principal_portion
                
        timeline_interest_expense[m] = round(monthly_interest_accumulator, 2)
        timeline_principal_repayments[m] = round(monthly_principal_accumulator, 2)
        
        running_debt_pool -= monthly_principal_accumulator
        timeline_debt_balance_bs[m] = round(max(running_debt_pool, 0.0), 2)

    # --- 4. FIXED ASSETS & DISPOSALS PIPELINE ---
    asset_results = calculate_multi_asset_depreciation_matrix(
        opening_nbv=float(baseline_inputs.get("opening_fixed_assets_nbv", 150000.0)),
        planned_capex_list=planned_capex_list,
        total_months=total_months
    )
    
    # --- 5. CORPORATION TAX ENGINE LOOKBACK ---
    pre_tax_operating_profit = ebitda_array - asset_results["timeline_depreciation_expense"] - timeline_interest_expense
    
    tax_results = calculate_corporation_tax_schedule(
        monthly_net_profit=pre_tax_operating_profit,
        monthly_book_depreciation=asset_results["timeline_depreciation_expense"],
        monthly_disposal_gains=asset_results["timeline_disposal_gains"],
        monthly_disposal_proceeds=asset_results["timeline_disposal_proceeds"],
        tax_main_pool_additions=asset_results["tax_main_pool_additions"],
        tax_special_pool_additions=asset_results["tax_special_pool_additions"],
        opening_main_pool_wdv=float(baseline_inputs.get("opening_fixed_assets_nbv", 150000.0)) * 0.70,
        opening_special_pool_wdv=float(baseline_inputs.get("opening_fixed_assets_nbv", 150000.0)) * 0.30,
        total_months=total_months
    )
    
    # --- 6. THE COMBINED THREE-WAY CONSOLIDATION RUNTIME ---
    final_net_profit = pre_tax_operating_profit + asset_results["timeline_disposal_gains"] - tax_results["timeline_tax_expense"]
    
    timeline_cash_at_bank = np.zeros(total_months)
    running_cash = float(baseline_inputs.get("opening_cash_balance", 69488.0))
    
    for m in range(total_months):
        # Master Flow Formula updated to inject the P&L Stock Movement working capital delta
        net_monthly_cash_flow = (
            final_net_profit[m]
            + asset_results["timeline_depreciation_expense"][m]
            - asset_results["timeline_disposal_gains"][m]
            + asset_results["timeline_disposal_proceeds"][m]
            - timeline_principal_repayments[m]
            - tax_results["timeline_tax_cash_outflow"][m]
            + timeline_p_l_stock_movement[m]
        )
        running_cash += net_monthly_cash_flow
        timeline_cash_at_bank[m] = round(running_cash, 2)
        
    return {
        "Revenue": rev_array,
        "Purchases": np.round(timeline_purchases_cash_outflow, 2),
        "Stock Movement": np.round(timeline_p_l_stock_movement, 2),
        "COGS": np.round(final_p_l_cogs_line, 2),
        "Overheads": overhead_array,
        "Depreciation": asset_results["timeline_depreciation_expense"],
        "Interest Paid": timeline_interest_expense,
        "Tax Expense": tax_results["timeline_tax_expense"],
        "Net Profit": np.round(final_net_profit, 2),
        "Principal Repayments": timeline_principal_repayments,
        "Tax Cash Paid": tax_results["timeline_tax_cash_outflow"],
        "Asset Disposal Proceeds": asset_results["timeline_disposal_proceeds"],
        "Cash At Bank": timeline_cash_at_bank,
        "Fixed Asset NBV": asset_results["timeline_nbv"],
        "Outstanding Debt": timeline_debt_balance_bs,
        "Tax Liability BS": tax_results["timeline_tax_liability_bs"],
        "Inventory Asset BS": np.round(timeline_inventory_asset_bs, 2)
    }