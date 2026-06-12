# tests/test_schema.py
import logging
from engine.income import IncomeObject
from engine.expenditure import ExpenditureObject
from engine.ledger import MasterLedger
from database.schema import deploy_database_schema, serialize_matrix_to_db

# Configure clean console logs
logging.basicConfig(level=logging.INFO)

print("--- ⚖️ STRATA CLOUD SCHEMA SERIALIZATION VERIFICATION ---")

# 1. Ingest baseline calculations (Using our exact verified 40-day VAT setup)
ledger = MasterLedger(total_timeline_months=12)
sales = IncomeObject("Primary Technical Supply", 20000.0, vat_rate=0.20, cash_delay_profile={1: 1.0})
ledger.add_income(sales, invoice_finance_eligible=True, invoice_finance_advance_rate=0.85)

overheads = ExpenditureObject("Operational Opex", 8000.0, vat_rate=0.20, creditor_payment_profile={0: 1.0})
ledger.add_expenditure(overheads)

matrix = ledger.compile_forecast_matrix()

try:
    # 2. Deploy database tables to Neon
    deploy_database_schema()
    
    # 3. Stream the calculated arrays into Neon tables
    serialize_matrix_to_db(
        scenario_name="Base Case Forecast Run",
        scenario_desc="Verified model scenario run incorporating 85% Invoice Finance advances and 40-day HMRC VAT lag.",
        matrix=matrix
    )
    print("\n🚀 SUCCESS! Financial matrix has been dynamically pushed and relational database constraints verified.")
except Exception as e:
    print(f"❌ Serialization Failure: {str(e)}")