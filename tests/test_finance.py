# test_run.py
from engine.finance import HirePurchaseObject, LoanObject

# 1. Instantiate Hire Purchase Deal (From step 2)
hp = HirePurchaseObject("Van HP", 100000, 20000, 24, 0.085, 1)
hp_vectors = hp.get_monthly_vectors()

# 2. Instantiate a Standard Bank Loan Facility
# £100,000 cash injected directly into reserves at Month 2
# Repaid over 24 months at a 7.5% annual interest rate
bank_loan = LoanObject(
    facility_name="Development Loan",
    principal=100000,
    term_months=24,
    annual_interest_rate=0.075,
    draw_down_month=2
)
loan_vectors = bank_loan.get_monthly_vectors()

print("--- 💸 HYBRID HIRE PURCHASE OBJECT (Month 2 Check) ---")
print(f"Liability Balance:         £{hp_vectors['hp_creditor_balance'][1]:,.2f}")
print(f"Interest Expense:          £{hp_vectors['interest_expense'][1]:,.2f}")

print("\n--- 🏦 STANDARD TERM DEBT OBJECT (Month 2 Check) ---")
print(f"Cash Flow Injected (M2):   £{loan_vectors['cash_flow_impact'][1]:,.2f}")
print(f"Closing Liability Balance: £{loan_vectors['loan_liability_balance'][1]:,.2f}")

print("\n--- 🏦 STANDARD TERM DEBT OBJECT (Month 3 Check) ---")
print(f"Monthly Repayment Cash (M3): £{loan_vectors['cash_flow_impact'][2]:,.2f}")
print(f"Interest Expense (M3):       £{loan_vectors['interest_expense'][2]:,.2f}")
print(f"Remaining Liability (M3):     £{loan_vectors['loan_liability_balance'][2]:,.2f}")