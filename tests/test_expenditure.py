# tests/test_expenditure.py
from engine.expenditure import ExpenditureObject

# Scenario parameters: Core overhead costing £5,000 net per month.
# Standard 20% UK VAT applies (Gross supplier invoice = £6,000/mo).
# Corporate payment terms profile: 
# - 100% paid on standard 30-day terms (Month 1 Lag: {1: 1.0})
supplier_stream = ExpenditureObject(
    expense_name="Raw Material Supply",
    baseline_monthly_net_cost=5000.0,
    vat_rate=0.20,
    creditor_payment_profile={1: 1.0}
)

vectors = supplier_stream.get_monthly_vectors()

print("--- 📉 CREDITOR CASH-LAG MATRIX MODULE VERIFICATION ---")
print(f"✔️ Month 1 Net P&L Expense (Ex VAT):       £{vectors['net_expense'][0]:,.2f}")
print(f"✔️ Month 1 Physical Cash Paid Out:         £{vectors['gross_cash_outflow'][0]:,.2f}")
print(f"✔️ Month 1 Closing Balance Sheet Creditors: £{vectors['closing_creditors_balance'][0]:,.2f}")
print(f"\n✔️ Month 2 Net P&L Expense (Ex VAT):       £{vectors['net_expense'][1]:,.2f}")
print(f"✔️ Month 2 Physical Cash Paid Out:         £{vectors['gross_cash_outflow'][1]:,.2f}")
print(f"✔️ Month 2 Closing Balance Sheet Creditors: £{vectors['closing_creditors_balance'][1]:,.2f}")