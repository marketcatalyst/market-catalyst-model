# utils/invoice_finance.py
# STRATA SUITE // INVOICE FINANCE & TRUST ACCOUNT CLEARING

def process_invoice_finance_drawdown(invoice_amount: float, advance_rate: float = 0.80, discount_fee_rate: float = 0.02) -> dict:
    gross_invoice = float(invoice_amount)
    advance_cash = gross_invoice * float(advance_rate)
    discount_fee = gross_invoice * float(discount_fee_rate)
    retention_reserve = gross_invoice - advance_cash - discount_fee
    
    return {
        "trust_bank_deposit": round(advance_cash, 2),
        "financing_fee_expense": round(discount_fee, 2),
        "retention_reserve_asset": round(retention_reserve, 2),
        "ledger_memo": "Invoice factoring advance routed via trust clearing account"
    }