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
    operational margins, proactive inventory procurement, rolling channel-by-channel AR collections,
    debt amortization, asset lifecycles, and corporate tax schedules.
    """
    # --- 1. OPERATIONAL BASELINES & POLICY MODIFIERS ---
    monthly_revenue = float(revenue_matrix_df["Monthly Base Volume (£)"].sum())
    monthly_base_cogs = float(revenue_matrix_df["Associated COGS Pool (£)"].sum())
    monthly_overheads = float(baseline_inputs.get("admin_overheads_monthly", 8000.0))
    days_cover = float(baseline_inputs.get("inventory_days_cover", 30.0))
    
    rev_array = np.full(total_months, monthly_revenue)
    base_cogs_demand = np.full(total_months, monthly_base_cogs)
    
    # --- 2. PROACTIVE INVENTORY ROLL-FORWARD ENGINE ---
    timeline_inventory_asset_bs = np.zeros(total_months)
    timeline_purchases_cash_outflow = np.zeros(total_months)
    timeline_p_l_stock_movement = np.zeros(total_months)
    
    for m in range(total_months):
        next_month_demand = base_cogs_demand[m + 1] if (m + 1) < total_months else monthly_base_cogs
        timeline_inventory_asset_bs[m] = next_month_demand * (days_cover / 30.0)
        
    opening_inventory_seed = monthly_base_cogs * (days_cover / 30.0)
    for m in range(total_months):
        current_target_stock = timeline_inventory_asset_bs[m]
        previous_target_stock = timeline_inventory_asset_bs[m - 1] if m > 0 else opening_inventory_seed
        
        stock_delta = current_target_stock - previous_target_stock
        timeline_purchases_cash_outflow[m] = base_cogs_demand[m] + stock_delta
        timeline_p_l_stock_movement[m] = -stock_delta
        
    final_p_l_cogs_line = timeline_purchases_cash_outflow + timeline_p_l_stock_movement
    overhead_array = np.full(total_months, monthly_overheads)
    ebitda_array = rev_array - final_p_l_cogs_line - overhead_array
    
    # --- 3. DYNAMIC GRANULAR CHANNEL CASH COLLECTION ENGINE ---
    timeline_cash_collected_from_sales = np.zeros(total_months)
    timeline_ar_balance_bs = np.zeros(total_months)
    
    opening_ar_seed = float(baseline_inputs.get("opening_accounts_receivable", 44886.0))
    running_ar_balance = opening_ar_seed
    
    # Process cash collections channel-by-channel
    for m in range(total_months):
        total_month_inflow = 0.0
        
        for _, row in revenue_matrix_df.iterrows():
            vol = float(row["Monthly Base Volume (£)"])
            p_curr = float(row["Cash % (Immediate)"]) / 100.0
            p_m1 = float(row["30-Day % (Terms)"]) / 100.0
            p_m2 = float(row["60-Day % (Terms)"]) / 100.0
            
            # Channel volume histories
            vol_m = vol
            vol_m_1 = vol # Assuming flat baseline baseline initialization vectors
            vol_m_2 = vol
            
            total_month_inflow += (vol_m * p_curr)
            if m > 0:
                total_month_inflow += (vol_m_1 * p_m1)
            else:
                total_month_inflow += (opening_ar_seed * 0.5 * p_m1) # Safe opening recovery heuristic
                
            if m > 1:
                total_month_inflow += (vol_m_2 * p_m2)
            else:
                total_month_inflow += (opening_ar_seed * 0.3 * p_m2)
                
        if m < 2 and running_ar_balance > 0:
            legacy_burn = min(running_ar_balance * 0.5, total_month_inflow)
            total_month_inflow = max(total_month_inflow, legacy_burn)
            
        timeline_cash_collected_from_sales[m] = total_month_inflow
        running_ar_balance = running_ar_balance + monthly_revenue - total_month_inflow
        timeline_ar_balance_bs[m] = max(running_ar_balance, 0.0)

    # --- 4. DEBT AMORTIZATION WHEEL (APR-DRIVEN) ---
    timeline_interest_expense = np.zeros(total_months)
    timeline_principal_repayments = np.zeros(total_months)
    timeline_debt_balance_bs = np.zeros(total_months)
    running_debt_pool = float(loan_register_df["Current Balance (£)"].sum())
    
    for m in range(total_months):
        month_1based = m + 1
        monthly_interest_accumulator = 0.0
        monthly_principal_accumulator = 0.0
        
        for _, loan in loan_register_df.iterrows():
            if int(loan["Remaining Term (Months)"]) >= month_1based:
                approx_monthly_interest = (float(loan["Current Balance (£)"]) * (float(loan["Interest Rate (%)"]) / 100.0)) / 12.0
                monthly_interest_accumulator += approx_monthly_interest
                monthly_principal_accumulator += min(float(loan["Monthly Payment (£)"]) - approx_monthly_interest, float(loan["Current Balance (£)"]))
                
        timeline_interest_expense[m] = round(monthly_interest_accumulator, 2)
        timeline_principal_repayments[m] = round(monthly_principal_accumulator, 2)
        running_debt_pool -= monthly_principal_accumulator
        timeline_debt_balance_bs[m] = round(max(running_debt_pool, 0.0), 2)

    # --- 5. FIXED ASSETS & DISPOSALS PIPELINE ---
    asset_results = calculate_multi_asset_depreciation_matrix(
        opening_nbv=float(baseline_inputs.get("opening_fixed_assets_nbv", 150000.0)),
        planned_capex_list=planned_capex_list,
        total_months=total_months
    )
    
    # --- 6. CORPORATION TAX ENGINE LOOKBACK ---
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
    
    # --- 7. THE COMBINED THREE-WAY CONSOLIDATION RUNTIME ---
    final_net_profit = pre_tax_operating_profit + asset_results["timeline_disposal_gains"] - tax_results["timeline_tax_expense"]
    
    timeline_cash_at_bank = np.zeros(total_months)
    running_cash = float(baseline_inputs.get("opening_cash_balance", 69488.0))
    
    for m in range(total_months):
        net_monthly_cash_flow = (
            timeline_cash_collected_from_sales[m]
            - timeline_purchases_cash_outflow[m]
            - overhead_array[m]
            + asset_results["timeline_disposal_proceeds"][m]
            - timeline_principal_repayments[m]
            - tax_results["timeline_tax_cash_outflow"][m]
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
        "Inventory Asset BS": np.round(timeline_inventory_asset_bs, 2),
        "Accounts Receivable BS": np.round(timeline_ar_balance_bs, 2)
    }