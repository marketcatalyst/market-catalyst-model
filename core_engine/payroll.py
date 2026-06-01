# core_engine/payroll.py

def calculate_uk_payroll_breakdown(gross_pay_monthly: float, pension_opt_out: bool = False) -> dict:
    """
    Calculates a full monthly payroll allocation using UK statutory tax parameters for 2026/27.
    Assumes standard personal allowance (Tax Code 1257L) as sole source of income.
    """
    # --- Statutory Monthly Thresholds ---
    MONTHLY_PERSONAL_ALLOWANCE = 1047.50   # £12,570 annual personal allowance / 12
    NI_PRIMARY_THRESHOLD = 1048.00         # Employee NI start point / 12
    NI_SECONDARY_THRESHOLD = 416.67        # Employer NI secondary threshold / 12
    
    PENSION_AUTO_ENROL_TRIGGER = 833.33   # Auto-enrolment trigger (£10,000 / 12)
    PENSION_LOWER_LIMIT = 520.00           # Lower qualifying earnings limit / 12
    PENSION_UPPER_LIMIT = 4189.17          # Upper qualifying earnings limit / 12

    # 1. Income Tax (PAYE) Calculation - Basic & Higher Rate Bands
    taxable_income = max(0.00, gross_pay_monthly - MONTHLY_PERSONAL_ALLOWANCE)
    
    # Standard monthly basic rate band cap: £37,700 / 12 = £3,141.67
    if taxable_income <= 3141.67:
        paye_tax = taxable_income * 0.20
    else:
        basic_slice_tax = 3141.67 * 0.20
        higher_slice_tax = (taxable_income - 3141.67) * 0.40
        paye_tax = basic_slice_tax + higher_slice_tax

    # 2. National Insurance (NI) Calculations
    # Employee Class 1 NI: 8% between primary threshold and upper limit
    if gross_pay_monthly <= NI_PRIMARY_THRESHOLD:
        employee_ni = 0.00
    elif gross_pay_monthly <= PENSION_UPPER_LIMIT:
        employee_ni = (gross_pay_monthly - NI_PRIMARY_THRESHOLD) * 0.08
    else:
        employee_ni = ((PENSION_UPPER_LIMIT - NI_PRIMARY_THRESHOLD) * 0.08) + ((gross_pay_monthly - PENSION_UPPER_LIMIT) * 0.02)

    # Employer Class 1 NI: 15% on all earnings above the secondary threshold (2026 Rules)
    if gross_pay_monthly > NI_SECONDARY_THRESHOLD:
        employer_ni = (gross_pay_monthly - NI_SECONDARY_THRESHOLD) * 0.15
    else:
        employer_ni = 0.00

    # 3. Workplace Auto-Enrolment Pension (Standard 5% Employee / 3% Employer)
    if not pension_opt_out and gross_pay_monthly >= PENSION_AUTO_ENROL_TRIGGER:
        pensionable_pay = min(gross_pay_monthly, PENSION_UPPER_LIMIT) - PENSION_LOWER_LIMIT
        pensionable_pay = max(0.00, pensionable_pay)
        
        employee_pension = pensionable_pay * 0.05
        employer_pension = pensionable_pay * 0.03
    else:
        employee_pension = 0.00
        employer_pension = 0.00

    # 4. Net Take-Home Pay (The Net Cash out to Employee)
    net_wages = gross_pay_monthly - paye_tax - employee_ni - employee_pension
    total_employment_cost = gross_pay_monthly + employer_ni + employer_pension

    return {
        "pl_gross_salary": round(gross_pay_monthly, 2),
        "pl_employer_ni": round(employer_ni, 2),
        "pl_employer_pension": round(employer_pension, 2),
        "pl_total_employment_cost": round(total_employment_cost, 2),
        "bs_net_wages_clearing": round(net_wages, 2),
        "bs_hmrc_paye_ni_due": round(paye_tax + employee_ni + employer_ni, 2),
        "bs_pension_due": round(employee_pension + employer_pension, 2)
    }