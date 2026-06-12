# engine/expenditure.py

class ExpenditureObject:
    """
    Pure Python model for corporate operational expenses (OpEx) and overheads.
    Dynamically maps net cost curves against dynamic creditor payment profiles
    and UK VAT regimes to output synchronized 3-way forecasting arrays.
    """
    def __init__(self, expense_name: str, baseline_monthly_net_cost: float, 
                 vat_rate: float = 0.20, creditor_payment_profile: dict = None):
        """
        Args:
            expense_name: Identifier for the expense row (e.g., 'Rent', 'Raw Materials').
            baseline_monthly_net_cost: Flat net cost run-rate across the timeline.
            vat_rate: Decimal tax rate (e.g., 0.20 for standard UK VAT, 0.0 for zero-rated/exempt).
            creditor_payment_profile: Dict mapping month lags to percentages.
                                      Default is 100% immediate cash payment: {0: 1.0}
        """
        self.expense_name = expense_name
        self.baseline_cost = float(baseline_monthly_net_cost)
        self.vat_rate = float(vat_rate)
        
        # Default to 100% cash payment within the active invoice month if unspecified
        if creditor_payment_profile is None:
            self.profile = {0: 1.0}
        else:
            self.profile = {int(k): float(v) for k, v in creditor_payment_profile.items()}
            
        # Enforce ironclad accounting validation: Profile allocation sum must equal 100%
        if not abs(sum(self.profile.values()) - 1.0) < 1e-4:
            raise ValueError(f"Creditor payment profile for '{expense_name}' must sum exactly to 1.0 (100%)")

    def get_monthly_vectors(self, total_timeline_months: int = 60) -> dict:
        """
        Compiles synchronized 60-month array vectors for 3-way integration mapping.
        
        Outputs:
            net_expense: Clear P&L cost row (Excludes input VAT)
            vat_paid: Row tracking input tax paid to suppliers, offsetting HMRC liability
            gross_cash_outflow: Realized physical cash exiting the Cash Flow Statement
            closing_creditors_balance: Balance Sheet Liability row tracking outstanding supplier debt
        """
        net_expense = [self.baseline_cost] * total_timeline_months
        vat_paid = [self.baseline_cost * self.vat_rate] * total_timeline_months
        
        # Calculate gross invoiced totals (Net + VAT) hitting accounts payable each period
        gross_invoiced = [n + v for n, v in zip(net_expense, vat_paid)]
        
        gross_cash_outflow = [0.0] * total_timeline_months
        closing_creditors_balance = [0.0] * total_timeline_months
        
        # --- Compute Cash Outflow Loops & Aging Creditors Balance Sheet Adjustments ---
        for m in range(total_timeline_months):
            # 1. Calculate cash paid out in the current month across historical invoices
            allocated_cash_run = 0.0
            for lag, weight in self.profile.items():
                invoice_month_target = m - lag
                if invoice_month_target >= 0:
                    allocated_cash_run += gross_invoiced[invoice_month_target] * weight
                    
            gross_cash_outflow[m] = allocated_cash_run
            
            # 2. Calculate cumulative opening creditors balance up to this point
            cumulative_invoiced = sum(gross_invoiced[:m+1])
            cumulative_paid = sum(gross_cash_outflow[:m+1])
            
            # Balance Sheet outstanding Accounts Payable value
            closing_creditors_balance[m] = max(cumulative_invoiced - cumulative_paid, 0.0)
            
        return {
            "net_expense": net_expense,
            "vat_paid": vat_paid,
            "gross_cash_outflow": gross_cash_outflow,
            "closing_creditors_balance": closing_creditors_balance
        }