# tests/test_ledger.py
from engine.income import IncomeObject
from engine.expenditure import ExpenditureObject
from engine.finance import LoanObject
from engine.ledger import MasterLedger

# Initialize the master ledger container for a full horizon check
ledger = MasterLedger(total_timeline_months=12)

# Add Revenue Stream: £20,000 net/mo, Standard 20% VAT, 30-day term debtor delay.
# Explicitly flag this stream as ENABLED for Invoice Discounting (85% advance rate).
sales = IncomeObject("Energy Tech Invoicing", 20000.0, vat_rate=0.20, cash_delay_profile={1: 1.0})
ledger.add_income(sales, invoice_finance_eligible=True, invoice_finance_advance_rate=0.85)

# Add Operational Expenditure Overheads: £8,000 net/mo, Standard 20% VAT, 100% paid instantly.
overheads = ExpenditureObject("Operational Opex", 8000.0, vat_rate=0.20, creditor_payment_profile={0: 1.0})
ledger.add_expenditure(overheads)

# Execute compilation calculation matrix
matrix = ledger.compile_forecast_matrix()

print("--- ⚖️ HMRC 40-DAY VAT DIRECT DEBIT TIMING VERIFICATION ---")
print(f"✔️ Month 2 Cumulative VAT Liability:       £{matrix['bs_hmrc_vat_balance'][1]:,.2f}")
print(f"✔️ Month 3 Quarter Ends (Liability Held):  £{matrix['bs_hmrc_vat_balance'][2]:,.2f}")
print(f"✔️ Month 4 Preparing Return (Cash Intact): £{matrix['bs_hmrc_vat_balance'][3]:,.2f}")
print(f"✔️ Month 5 Direct Debit Clears (Settled):  £{matrix['bs_hmrc_vat_balance'][4]:,.2f}")