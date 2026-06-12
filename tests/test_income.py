# tests/test_income.py
from engine.income import IncomeObject

# Scenario parameters: Commercial contract generating £10,000 net per month.
# Standard 20% UK VAT applies (Gross invoiced = £12,000/mo).
# Client cash delay payment term profile:
# - 20% paid immediately in the invoice month (Month 0 Lag)
# - 50% paid 30 days later (Month 1 Lag)
# - 30% paid 60 days later (Month 2 Lag)
commercial_stream = IncomeObject(
    stream_name="Commercial Contract Sales",
    baseline_monthly_net_sales=10000.0,
    vat_rate=0.20,
    cash_delay_profile={0: 0.20, 1: 0.50, 2: 0.30}
)

vectors = commercial_stream.get_monthly_vectors()

print("--- 📈 DEBTOR CASH-DELAY MATRIX MODULE VERIFICATION ---")
print(f"✔️ Month 1 Net P&L Revenue (Ex VAT):        £{vectors['net_revenue'][0]:,.2f}")
print(f"✔️ Month 1 Gross Cash Realized Inflow:      £{vectors['gross_debtor_inflow'][0]:,.2f}")
print(f"✔️ Month 1 Closing Balance Sheet Debtors:   £{vectors['closing_debtors_balance'][0]:,.2f}")
print(f"\n✔️ Month 2 Gross Cash Realized Inflow:      £{vectors['gross_debtor_inflow'][1]:,.2f}")
print(f"✔️ Month 2 Closing Balance Sheet Debtors:   £{vectors['closing_debtors_balance'][1]:,.2f}")
print(f"\n✔️ Month 3 Gross Cash Realized Inflow:      £{vectors['gross_debtor_inflow'][2]:,.2f}")
print(f"✔️ Month 3 Closing Balance Sheet Debtors:   £{vectors['closing_debtors_balance'][2]:,.2f}")