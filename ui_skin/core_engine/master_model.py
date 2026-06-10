# ui_skin/core_engine/master_model.py
import pandas as pd
import numpy as np

def generate_integrated_3way_forecast(inputs: dict, overrides: dict = None) -> pd.DataFrame:
    """
    Core 60-Month Integrated Three-Way Calculation Engine.
    Processes baseline ingestion datasets and outputs unified rows 
    for P&L, Balance Sheet, and statutory HMRC tax/payroll schedules.
    """
    if overrides is None:
        overrides = {}
        
    # Extract scenario multipliers or default to zero structural change
    volume_delta = overrides.get("volume_delta", 0.0)
    opex_delta = overrides.get("opex_delta", 0.0)
    
    # 1. Timeline Setup (60 Months)
    months = [f"M{i:02d}" for i in range(1, 61)]
    
    # 2. Revenue & Expense Vectors
    base_revenue_curve = inputs.get("y1_monthly_revenue_curve", [0.0] * 12)
    # Stretch out the 12-month pattern across a full 5-year timeline
    extended_revenue = (base_revenue_curve * 5)[:60]
    
    simulated_revenue = [float(r * (1.0 + volume_delta)) for r in extended_revenue]
    simulated_cogs = [r * 0.40 for r in simulated_revenue] # 40% Target Cost of Goods Sold
    
    # Extract structural fixed overhead run-rates
    admin_overheads = float(inputs.get("admin_overheads_monthly", 0.0))
    gross_wages = float(inputs.get("base_monthly_gross_wages", 0.0))
    directors_salaries = float(inputs.get("directors_salaries_monthly", 0.0))
    pension_opt_out = inputs.get("pension_opt_out", False)
    
    # Calculate employment tax overheads
    employer_ni = max(0.0, (gross_wages - 758.0) * 0.138) if gross_wages > 758.0 else 0.0
    pension_burden = 0.0 if pension_opt_out else (gross_wages * 0.03)
    
    total_monthly_opex_base = admin_overheads + gross_wages + directors_salaries + employer_ni + pension_burden
    simulated_opex = [total_monthly_opex_base * (1.0 + opex_delta)] * 60
    
    # 3. Monthly Operating Profit & Dynamic Tax Provisioning
    simulated_ebit = []
    tax_expense_timeline = []
    
    for m in range(60):
        ebit = simulated_revenue[m] - simulated_cogs[m] - simulated_opex[m]
        simulated_ebit.append(ebit)
        
        # Approximate 19% Corporation Tax accrual on positive operating cycles
        tax_accrual = max(0.0, ebit * 0.19)
        tax_expense_timeline.append(tax_accrual)
        
    # 4. Cash Flow & Statutory Accrual Balances
    simulated_cash = []
    tax_balance_sheet_timeline = []
    
    current_cash = float(inputs.get("opening_cash_balance", 0.0))
    current_tax_accrual_balance = 0.0
    
    # Matrix engine tracking loops
    for m in range(60):
        # Accumulate the current month's provision onto the Balance Sheet liability line
        current_tax_accrual_balance += tax_expense_timeline[m]
        
        # Calculate standard trading cash conversion (85% net cash collection assumption)
        net_monthly_profit = simulated_ebit[m]
        monthly_cash_flow = net_monthly_profit * 0.85
        
        # Apply the explicit 9-month annual lump-sum Corporation Tax payment lag rule
        # Check if the current month represents payment for an explicit year-end
        # Months 21 (Y1 payment), 33 (Y2 payment), 45 (Y3 payment), 57 (Y4 payment)
        if m in [20, 32, 44, 56]:
            target_year = (m + 4) // 12  # Identifies completed year index (1, 2, 3, or 4)
            start_idx = (target_year - 1) * 12
            end_idx = target_year * 12
            
            # Sum up the historical 12-month provision bundle for that exact year block
            annual_lump_sum_exit = sum(tax_expense_timeline[start_idx:end_idx])
            
            # Deduct the payment from both cash reserves and the ongoing liability line
            monthly_cash_flow -= annual_lump_sum_exit
            current_tax_accrual_balance -= annual_lump_sum_exit
            
        current_cash += monthly_cash_flow
        simulated_cash.append(current_cash)
        tax_balance_sheet_timeline.append(max(0.0, current_tax_accrual_balance))
        
    # 5. Compile into structured Pandas Frame matching our UI hooks
    output_df = pd.DataFrame({
        "Revenue (£)": simulated_revenue,
        "COGS (£)": simulated_cogs,
        "Opex (£)": simulated_opex,
        "EBIT (£)": simulated_ebit,
        "Cash Reserves (£)": simulated_cash,
        "Tax Expense (£)": tax_expense_timeline,
        "Tax Liability BS (£)": tax_balance_sheet_timeline
    }, index=months)
    
    return output_df