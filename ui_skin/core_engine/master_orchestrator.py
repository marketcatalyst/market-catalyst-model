# core_engine/orchestrator.py
import numpy as np
from core_engine.payroll import calculate_uk_payroll_breakdown, DEFAULT_UK_TAX_CONFIG

def run_3way_payroll_orchestrator(ui_workforce_inputs: dict, total_months: int = 60) -> dict:
    """
    Orchestrates the 60-month financial simulation loop for payroll.
    Binds operational workforce rotas to the 3-Way Ledger Matrix,
    handling real-time expense routing and Month+1 statutory cash sweeps.
    """
    # 1. Initialize empty financial ledger arrays for the 5-year timeline
    pl_expenses = {
        "gross_salaries": np.zeros(total_months),
        "employer_ni": np.zeros(total_months),
        "employer_pension": np.zeros(total_months),
        "total_employment_cost": np.zeros(total_months)
    }
    
    bs_liabilities = {
        "hmrc_paye_ni_accrual": np.zeros(total_months),
        "pension_pot_accrual": np.zeros(total_months)
    }
    
    cf_outflows = {
        "net_wages_paid_m0": np.zeros(total_months),
        "hmrc_sweep_paid_m1": np.zeros(total_months),
        "pension_sweep_paid_m1": np.zeros(total_months),
        "total_payroll_cash_drain": np.zeros(total_months)
    }

    # 2. Step through the 60-month timeline chronologically
    for m in range(total_months):
        
        # Pull this month's operational rota signals from the UI configuration arrays
        month_salary_flat = ui_workforce_inputs["base_salary_flat"][m]
        month_hourly_rate = ui_workforce_inputs["hourly_rate"][m]
        month_reg_hours   = ui_workforce_inputs["regular_hours_worked"][m]
        month_ot_hours    = ui_workforce_inputs["overtime_hours_worked"][m]
        month_ot_mult     = ui_workforce_inputs.get("overtime_multiplier", 1.5)
        is_pension_opt_out = ui_workforce_inputs["pension_opt_out"][m]

        # Execute your decoupled SaaS payroll engine function
        payroll_snapshot = calculate_uk_payroll_breakdown(
            base_salary_flat=month_salary_flat if month_salary_flat > 0 else None,
            hourly_rate=month_hourly_rate,
            regular_hours_worked=month_reg_hours,
            overtime_hours_worked=month_ot_hours,
            overtime_multiplier=month_ot_mult,
            pension_opt_out=is_pension_opt_out,
            tax_config=DEFAULT_UK_TAX_CONFIG
        )

        # --- TIER 1: PROFIT & LOSS POPULATION ---
        pl_expenses["gross_salaries"][m] = payroll_snapshot["pl_gross_salary"]
        pl_expenses["employer_ni"][m]    = payroll_snapshot["pl_employer_ni"]
        pl_expenses["employer_pension"][m] = payroll_snapshot["pl_employer_pension"]
        pl_expenses["total_employment_cost"][m] = payroll_snapshot["pl_total_employment_cost"]

        # --- TIER 2: IMMEDIATE CASH OUT (MONTH m) ---
        # Net take-home wages leave the corporate bank account instantly to clear the staff line
        cf_outflows["net_wages_paid_m0"][m] = payroll_snapshot["bs_net_wages_clearing"]

        # --- TIER 3: BALANCE SHEET LIABILITY ACCRUALS ---
        # Compound tax and pension pots pile up on the balance sheet as current obligations
        current_hmrc_accrual = payroll_snapshot["bs_hmrc_paye_ni_due"]
        current_pension_accrual = payroll_snapshot["bs_pension_due"]
        
        # Accumulate the ledger balance by carrying forward the previous month's remaining balance
        prev_hmrc_bal = bs_liabilities["hmrc_paye_ni_accrual"][m-1] if m > 0 else 0.0
        prev_pension_bal = bs_liabilities["pension_pot_accrual"][m-1] if m > 0 else 0.0
        
        bs_liabilities["hmrc_paye_ni_accrual"][m] = prev_hmrc_bal + current_hmrc_accrual
        bs_liabilities["pension_pot_accrual"][m] = prev_pension_bal + current_pension_accrual

        # --- TIER 4: THE HARDWIRED STATUTORY CASH SWEEPS (MONTH m) ---
        # If we are in Month 1 or beyond, we must execute the lagged cash sweep to clear Month m-1 liabilities
        if m > 0:
            # Determine what was left owing on the balance sheet from the previous month's calculations
            hmrc_sweep_amount = payroll_snapshot_prev_month_hmrc_due = ui_workforce_inputs.get("_last_hmrc_due", 0.0) if m==0 else bs_liabilities["hmrc_paye_ni_accrual"][m-1]
            pension_sweep_amount = ui_workforce_inputs.get("_last_pension_due", 0.0) if m==0 else bs_liabilities["pension_pot_accrual"][m-1]
            
            # Record the physical cash leaving the bank account under Month m
            cf_outflows["hmrc_sweep_paid_m1"][m] = hmrc_sweep_amount
            cf_outflows["pension_sweep_paid_m1"][m] = pension_sweep_amount
            
            # Debit the Balance Sheet tracking pools retroactively to reflect the cash settlement
            bs_liabilities["hmrc_paye_ni_accrual"][m] -= hmrc_sweep_amount
            bs_liabilities["pension_pot_accrual"][m] -= pension_sweep_amount

        # --- TIER 5: CONSOLIDATED TOTAL CASH OUTFLOW ---
        cf_outflows["total_payroll_cash_drain"][m] = (
            cf_outflows["net_wages_paid_m0"][m] + 
            cf_outflows["hmrc_sweep_paid_m1"][m] + 
            cf_outflows["pension_sweep_paid_m1"][m]
        )

    return {
        "P&L_Expenses": pl_expenses,
        "Balance_Sheet_Liabilities": bs_liabilities,
        "Cash_Flow_Outflows": cf_outflows
    }