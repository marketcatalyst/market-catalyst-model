# ui_skin/core_engine/master_model.py
import pandas as pd
import numpy as np

def generate_integrated_3way_forecast(inputs: dict, overrides: dict = None) -> pd.DataFrame:
    """
    Core 60-Month Integrated Three-Way Calculation Engine.
    Processes baseline ingestion datasets and outputs unified rows 
    for P&L, Balance Sheet, statutory taxes, and generic debt amortization.
    """
    if overrides is None:
        overrides = {}
        
    volume_delta = overrides.get("volume_delta", 0.0)
    opex_delta = overrides.get("opex_delta", 0.0)
    
    # 1. Timeline Setup (60 Months)
    months = [f"M{i:02d}" for i in range(1, 61)]
    
    # 2. Revenue & Expense Vectors
    base_revenue_curve = inputs.get("y1_monthly_revenue_curve", [0.0] * 12)
    extended_revenue = (base_revenue_curve * 5)[:60]
    
    simulated_revenue = [float(r * (1.0 + volume_delta)) for r in extended_revenue]
    simulated_cogs = [r * 0.40 for r in simulated_revenue]
    
    admin_overheads = float(inputs.get("admin_overheads_monthly", 0.0))
    gross_wages = float(inputs.get("base_monthly_gross_wages", 0.0))
    directors_salaries = float(inputs.get("directors_salaries_monthly", 0.0))
    pension_opt_out = inputs.get("pension_opt_out", False)
    
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
        tax_accrual = max(0.0, ebit * 0.19)
        tax_expense_timeline.append(tax_accrual)
        
    # 4. GENERIC DEBT AMORTIZATION RECONCILIATION LAYER
    # Ingest dynamic debt facility dictionaries if available, fallback to baseline totals if empty
    debt_facilities = inputs.get("debt_facilities", [
        {"facility_name": "Consolidated Corporate Debt", "opening_balance": float(inputs.get("opening_long_term_debt", 130176.0)), "interest_rate_annual": 0.08, "term_months": 60}
    ])
    
    monthly_total_debt_service_cash = np.zeros(60)
    monthly_interest_expense_p_and_l = np.zeros(60)
    debt_balance_sheet_timeline = np.zeros(60)
    
    # Process each liability tranche independently using a generic amortization math loop
    for facility in debt_facilities:
        bal = float(facility["opening_balance"])
        rate_monthly = float(facility["interest_rate_annual"]) / 12.0
        term = int(facility["term_months"])
        
        # Calculate standard monthly regularized payment using the classic PMT annuity formula
        if rate_monthly > 0 and term > 0:
            pmt = bal * (rate_monthly * (1 + rate_monthly)**term) / ((1 + rate_monthly)**term - 1)
        else:
            pmt = bal / max(1, term)
            
        current_facility_bal = bal
        for m in range(60):
            if current_facility_bal > 0:
                interest_payment = current_facility_bal * rate_monthly
                principal_payment = min(current_facility_bal, pmt - interest_payment)
                
                monthly_interest_expense_p_and_l[m] += interest_payment
                monthly_total_debt_service_cash[m] += (interest_payment + principal_payment)
                
                current_facility_bal -= principal_payment
            debt_balance_sheet_timeline[m] += current_facility_bal

    # 5. Cash Flow & Statutory Accrual Balances
    simulated_cash = []
    tax_balance_sheet_timeline = []
    
    current_cash = float(inputs.get("opening_cash_balance", 0.0))
    current_tax_accrual_balance = 0.0
    
    for m in range(60):
        current_tax_accrual_balance += tax_expense_timeline[m]
        
        # Deduct both standard trading adjustments and our active debt service overheads
        net_monthly_profit = simulated_ebit[m] - monthly_interest_expense_p_and_l[m]
        monthly_cash_flow = (net_monthly_profit * 0.85) - monthly_total_debt_service_cash[m]
        
        # Apply the explicit 9-month annual lump-sum Corporation Tax payment lag rule
        if m in [20, 32, 44, 56]:
            target_year = (m + 4) // 12
            start_idx = (target_year - 1) * 12
            end_idx = target_year * 12
            annual_lump_sum_exit = sum(tax_expense_timeline[start_idx:end_idx])
            
            monthly_cash_flow -= annual_lump_sum_exit
            current_tax_accrual_balance -= annual_lump_sum_exit
            
        current_cash += monthly_cash_flow
        simulated_cash.append(current_cash)
        tax_balance_sheet_timeline.append(max(0.0, current_tax_accrual_balance))
        
    # 6. Compile into structured Pandas Frame matching our UI hooks
    output_df = pd.DataFrame({
        "Revenue (£)": simulated_revenue,
        "COGS (£)": simulated_cogs,
        "Opex (£)": simulated_opex,
        "EBIT (£)": simulated_ebit,
        "Interest Expense (£)": monthly_interest_expense_p_and_l,
        "Debt Service Cash Outflow (£)": monthly_total_debt_service_cash,
        "Cash Reserves (£)": simulated_cash,
        "Tax Expense (£)": tax_expense_timeline,
        "Tax Liability BS (£)": tax_balance_sheet_timeline,
        "Outstanding Debt Balance (£)": debt_balance_sheet_timeline
    }, index=months)
    
    return output_df