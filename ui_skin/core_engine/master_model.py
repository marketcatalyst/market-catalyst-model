# core_engine/master_model.py
import pandas as pd
from core_engine.payroll import calculate_uk_payroll_breakdown
from core_engine.fixed_assets import calculate_fixed_asset_lifecycle

def generate_integrated_3way_forecast(inputs: dict) -> pd.DataFrame:
    """
    The Master Coordination Engine for market-catalyst-model.
    Processes user-defined scenario variables, integrates asset and payroll modules,
    and loops month-by-month to build structurally aligned, integrated 3-way financial records.
    """
    months_timeline = [f"Month {i+1}" for i in range(60)]
    
    # Schema aligned with report_generator.py to ensure zero deployment errors
    columns_to_track = [
        "Month", "Turnover (£)", "Direct Costs (£)", "Admin Overheads (£)",
        "Directors Salaries (£)", "Depreciation Expense (£)", "Net Profit (£)",
        "Fixed Asset NBV (£)", "Bank Cash Position (£)", "Accounts Payable & Debt (£)",
        "Retained Earnings (£)", "Bridge: Net Profit", "Bridge: Depreciation",
        "Bridge: Operating CF", "Bridge: Investing CF", "Bridge: Financing CF",
        "Bridge: Net Movement", "Double_Entry_Check", "Ops_FTE_Strain"
    ]
    
    forecast_matrix = pd.DataFrame(index=months_timeline, columns=columns_to_track)
    
    # --- 1. Extract Dynamic User Inputs & SaaS Overrides ---
    monthly_sales_target = inputs.get("target_monthly_sales", 50000.0)
    base_gross_wages = inputs.get("base_monthly_gross_wages", 0.0)
    pension_opt_out = inputs.get("pension_opt_out", False)
    
    # Sub-ledger structural variables
    direct_costs_baseline = inputs.get("direct_costs_monthly", 0.0)
    admin_overheads_baseline = inputs.get("admin_overheads_monthly", 0.0)
    directors_salaries_baseline = inputs.get("directors_salaries_monthly", 0.0)
    
    opening_cash = inputs.get("opening_cash_balance", 0.0)
    opening_retained_earnings = inputs.get("opening_retained_earnings", 0.0)
    
    # --- 2. Process Capital Expenditures Sub-Ledger ---
    # Ingesting optional planned capital events from the application layer
    asset_cost = inputs.get("planned_asset_cost", 0.0)
    asset_purchase_month = inputs.get("planned_asset_purchase_month_index", -1)
    asset_uel = inputs.get("planned_asset_uel_months", 36)
    asset_residual = inputs.get("planned_asset_residual_value", 0.0)
    asset_tax_code = inputs.get("planned_asset_tax_code", "WDA_MAIN")
    asset_multiplier = inputs.get("planned_asset_systemic_multiplier", 1.0)
    
    # Execute the generic asset submodule pass to obtain full 60-month schedules
    asset_schedules = calculate_fixed_asset_lifecycle(
        asset_cost=asset_cost,
        purchase_month_index=asset_purchase_month,
        useful_life_months=asset_uel,
        residual_value=asset_residual,
        tax_allowance_code=asset_tax_code,
        systemic_multiplier=asset_multiplier,
        forecast_horizon_months=60
    )
    
    # --- 3. Process Labor Cost Sub-Ledger ---
    # Execute our underlying UK payroll breakdown core module pass
    payroll_packet = calculate_uk_payroll_breakdown(
        base_salary_flat=base_gross_wages, 
        pension_opt_out=pension_opt_out
    )
    
    running_bank_cash = opening_cash
    running_retained_earnings = opening_retained_earnings
    
    # --- 4. Chronological Monthly Financial Balancing Loop ---
    for i in range(60):
        current_m = f"Month {i+1}"
        forecast_matrix.loc[current_m, "Month"] = current_m
        
        # Pull asset values for the current iteration month
        m_capex_outflow = asset_schedules["timeline_cash_outflow"][i]
        m_depreciation = asset_schedules["timeline_pl_depreciation"][i]
        m_asset_nbv = asset_schedules["timeline_bs_asset_nbv"][i]
        
        # Systems-thinking application: Adjust efficiency parameters based on assets
        # If an operational efficiency multiplier is active, it modifies direct variable costs
        effective_direct_costs = direct_costs_baseline
        if m_asset_nbv > 0.0 and asset_multiplier != 1.0:
            # Multiplier scales down unit friction or process costs
            effective_direct_costs = direct_costs_baseline * (2.0 - asset_multiplier)
            
        # A. Populate Schedule 1: Profit & Loss Entries
        forecast_matrix.loc[current_m, "Turnover (£)"] = monthly_sales_target
        forecast_matrix.loc[current_m, "Direct Costs (£)"] = effective_direct_costs
        forecast_matrix.loc[current_m, "Admin Overheads (£)"] = admin_overheads_baseline
        forecast_matrix.loc[current_m, "Directors Salaries (£)"] = directors_salaries_baseline
        forecast_matrix.loc[current_m, "Depreciation Expense (£)"] = m_depreciation
        
        # Net Operating Profit / Loss calculation
        total_payroll_burden = payroll_packet["pl_total_employment_cost"]
        total_operating_expenses = (
            effective_direct_costs + 
            admin_overheads_baseline + 
            directors_salaries_baseline + 
            total_payroll_burden + 
            m_depreciation
        )
        monthly_net_profit = monthly_sales_target - total_operating_expenses
        forecast_matrix.loc[current_m, "Net_Profit"] = monthly_net_profit  # Internal tracker
        forecast_matrix.loc[current_m, "Net Profit (£)"] = monthly_net_profit
        
        # B. Process Schedule 3: Cash Flow Reconciliation Bridge
        monthly_cash_collected = monthly_sales_target
        # Operating cash outflows include immediate clearance of complete payroll overheads
        monthly_operating_cash_out = total_operating_expenses - m_depreciation  # Strip out non-cash
        
        m_operating_cf = monthly_cash_collected - monthly_operating_cash_out
        m_investing_cf = -m_capex_outflow
        m_financing_cf = 0.0  # Open slot for future debt drawdown logic
        m_net_movement = m_operating_cf + m_investing_cf + m_financing_cf
        
        running_bank_cash += m_net_movement
        running_retained_earnings += monthly_net_profit
        
        # Map Cash Flow items to the matrix
        forecast_matrix.loc[current_m, "Bridge: Net Profit"] = monthly_net_profit
        forecast_matrix.loc[current_m, "Bridge: Depreciation"] = m_depreciation
        forecast_matrix.loc[current_m, "Bridge: Operating CF"] = m_operating_cf
        forecast_matrix.loc[current_m, "Bridge: Investing CF"] = m_investing_cf
        forecast_matrix.loc[current_m, "Bridge: Financing CF"] = m_financing_cf
        forecast_matrix.loc[current_m, "Bridge: Net Movement"] = m_net_movement
        
        # C. Populate Schedule 2: Balance Sheet Entries
        forecast_matrix.loc[current_m, "Fixed Asset NBV (£)"] = m_asset_nbv
        forecast_matrix.loc[current_m, "Bank Cash Position (£)"] = running_bank_cash
        forecast_matrix.loc[current_m, "Accounts Payable & Debt (£)"] = 0.0  # Current liabilities spot
        forecast_matrix.loc[current_m, "Retained Earnings (£)"] = running_retained_earnings
        
        # Back-end legacy validation slots
        forecast_matrix.loc[current_m, "Gross_Wages"] = payroll_packet["pl_gross_salary"]
        forecast_matrix.loc[current_m, "Employer_NI"] = payroll_packet["pl_employer_ni"]
        forecast_matrix.loc[current_m, "Employer_Pension"] = payroll_packet["pl_employer_pension"]
        forecast_matrix.loc[current_m, "Total_Employment_Overhead"] = total_payroll_burden
        forecast_matrix.loc[current_m, "Bank_Cash_Asset"] = running_bank_cash
        forecast_matrix.loc[current_m, "HMRC_PAYE_NI_Liability"] = 0.0
        forecast_matrix.loc[current_m, "Pension_Liability"] = 0.0
        forecast_matrix.loc[current_m, "Total_Current_Liabilities"] = 0.0
        forecast_matrix.loc[current_m, "Retained_Earnings"] = running_retained_earnings
        
        # D. Integrated Accounting Balance Verification Check
        # Equation: (Fixed Asset NBV + Bank Cash) - (Liabilities + Retained Earnings)
        total_assets = m_asset_nbv + running_bank_cash
        total_liabilities_equity = 0.0 + running_retained_earnings
        
        variance_check = round(total_assets - total_liabilities_equity, 2)
        forecast_matrix.loc[current_m, "Double_Entry_Check"] = variance_check
        
        # Operational Strain Feedback Metrics
        forecast_matrix.loc[current_m, "Ops_FTE_Strain"] = payroll_packet["ops_fte_utilization"]
        
    return forecast_matrix