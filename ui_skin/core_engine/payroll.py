# core_engine/payroll.py
from typing import Optional, dict

# Default configuration registry calibrated for UK Statutory Tax Rules (2026/27)
# Moving this to a dictionary ensures the code remains generic and multi-year compatible
DEFAULT_UK_TAX_CONFIG = {
    "monthly_personal_allowance": 1047.50,   # £12,570 annual / 12
    "ni_primary_threshold": 1048.00,         # Employee NI threshold / 12
    "ni_secondary_threshold": 416.67,        # Employer NI threshold / 12
    "pension_auto_enrol_trigger": 833.33,    # Auto-enrolment trigger (£10,000 / 12)
    "pension_lower_limit": 520.00,           # Lower qualifying earnings limit / 12
    "pension_upper_limit": 4189.17,          # Upper qualifying earnings limit / 12
    "basic_rate_band_cap": 3141.67,          # £37,700 / 12
    "income_tax_basic_rate": 0.20,
    "income_tax_higher_rate": 0.40,
    "employee_ni_standard_rate": 0.08,
    "employee_ni_higher_rate": 0.02,
    "employer_ni_rate": 0.15,                 # Calibrated to modern 15% legislation
    "employee_pension_rate": 0.05,
    "employer_pension_rate": 0.03,
    "standard_fte_hours_monthly": 160.0       # 40 hours/week * 4 weeks baseline
}

def calculate_uk_payroll_breakdown(
    base_salary_flat: Optional[float] = None,
    hourly_rate: float = 0.0,
    regular_hours_worked: float = 0.0,
    overtime_hours_worked: float = 0.0,
    overtime_multiplier: float = 1.5,
    pension_opt_out: bool = False,
    tax_config: dict = DEFAULT_UK_TAX_CONFIG
) -> dict:
    """
    Decoupled SaaS Payroll Engine: Processes variable hourly rotas or salaried headcount.
    Calculates full monthly PAYE, National Insurance, and Workplace Pension allocations 
    using configurable tax structures while returning operational workforce strain metrics.
    """
    
    # --- 1. Dynamic Gross Pay Assembly Line ---
    if base_salary_flat is not None and base_salary_flat > 0:
        gross_pay_monthly = base_salary_flat
        total_hours_worked = tax_config["standard_fte_hours_monthly"]
    else:
        # Calculate dynamic gross wages based on production kitchen shift fulfillment
        regular_wages = regular_hours_worked * hourly_rate
        overtime_wages = overtime_hours_worked * (hourly_rate * overtime_multiplier)
        gross_pay_monthly = regular_wages + overtime_wages
        total_hours_worked = regular_hours_worked + overtime_hours_worked

    # --- 2. Income Tax (PAYE) Calculation ---
    taxable_income = max(0.00, gross_pay_monthly - tax_config["monthly_personal_allowance"])
    
    if taxable_income <= tax_config["basic_rate_band_cap"]:
        paye_tax = taxable_income * tax_config["income_tax_basic_rate"]
    else:
        basic_slice_tax = tax_config["basic_rate_band_cap"] * tax_config["income_tax_basic_rate"]
        higher_slice_tax = (taxable_income - tax_config["basic_rate_band_cap"]) * tax_config["income_tax_higher_rate"]
        paye_tax = basic_slice_tax + higher_slice_tax

    # --- 3. National Insurance (NI) Calculations ---
    # Employee Class 1 NI
    if gross_pay_monthly <= tax_config["ni_primary_threshold"]:
        employee_ni = 0.00
    elif gross_pay_monthly <= tax_config["pension_upper_limit"]:
        employee_ni = (gross_pay_monthly - tax_config["ni_primary_threshold"]) * tax_config["employee_ni_standard_rate"]
    else:
        main_slice = (tax_config["pension_upper_limit"] - tax_config["ni_primary_threshold"]) * tax_config["employee_ni_standard_rate"]
        upper_slice = (gross_pay_monthly - tax_config["pension_upper_limit"]) * tax_config["employee_ni_higher_rate"]
        employee_ni = main_slice + upper_slice

    # Employer Class 1 NI
    if gross_pay_monthly > tax_config["ni_secondary_threshold"]:
        employer_ni = (gross_pay_monthly - tax_config["ni_secondary_threshold"]) * tax_config["employer_ni_rate"]
    else:
        employer_ni = 0.00

    # --- 4. Workplace Auto-Enrolment Pension ---
    if not pension_opt_out and gross_pay_monthly >= tax_config["pension_auto_enrol_trigger"]:
        pensionable_pay = min(gross_pay_monthly, tax_config["pension_upper_limit"]) - tax_config["pension_lower_limit"]
        pensionable_pay = max(0.00, pensionable_pay)
        
        employee_pension = pensionable_pay * tax_config["employee_pension_rate"]
        employer_pension = pensionable_pay * tax_config["employer_pension_rate"]
    else:
        employee_pension = 0.00
        employer_pension = 0.00

    # --- 5. Financial Reconciliation Blending ---
    net_wages = gross_pay_monthly - paye_tax - employee_ni - employee_pension
    total_employment_cost = gross_pay_monthly + employer_ni + employer_pension

    # --- 6. Systems-Thinking Operational Metrics ---
    # Computes operational strain or capacity scaling indicators for the master model
    fte_utilization = total_hours_worked / tax_config["standard_fte_hours_monthly"]

    return {
        # Timelines for P&L and Balance Sheet integration
        "pl_gross_salary": round(gross_pay_monthly, 2),
        "pl_employer_ni": round(employer_ni, 2),
        "pl_employer_pension": round(employer_pension, 2),
        "pl_total_employment_cost": round(total_employment_cost, 2),
        "bs_net_wages_clearing": round(net_wages, 2),
        "bs_hmrc_paye_ni_due": round(paye_tax + employee_ni + employer_ni, 2),
        "bs_pension_due": round(employee_pension + employer_pension, 2),
        
        # Operational feedback parameters
        "ops_fte_utilization": round(fte_utilization, 2),
        "ops_overtime_hours_triggered": round(overtime_hours_worked, 2)
    }