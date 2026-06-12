# engine/income.py

class IncomeObject:
    """
    Pure Python model for corporate revenue streams.
    Dynamically maps gross sales curves against dynamic debtor cash-delay matrices
    and UK VAT regimes to produce accurate 3-way forecasting arrays.
    """
    def __init__(self, stream_name: str, baseline_monthly_net_sales: float, 
                 vat_rate: float = 0.20, cash_delay_profile: dict = None):
        """
        Args:
            stream_name: Identifier for the revenue stream.
            baseline_monthly_net_sales: Flat net revenue run-rate across the timeline.
            vat_rate: Decimal tax rate (e.g., 0.20 for standard 20% UK VAT, 0.0 for exempt).
            cash_delay_profile: Dict mapping month lags to percentages. 
                                Default is 100% immediate cash realization: {0: 1.0}
        """
        self.stream_name = stream_name
        self.baseline_sales = float(baseline_monthly_net_sales)
        self.vat_rate = float(vat_rate)
        
        # Default to 100% cash collections within the active invoice month if unspecified
        if cash_delay_profile is None:
            self.profile = {0: 1.0}
        else:
            self.profile = {int(k): float(v) for k, v in cash_delay_profile.items()}
            
        # Enforce ironclad accounting validation: Profile allocation sum must equal 100%
        if not abs(sum(self.profile.values()) - 1.0) < 1e-4:
            raise ValueError(f"Debtor cash-delay profile for '{stream_name}' must sum exactly to 1.0 (100%)")

    def get_monthly_vectors(self, total_timeline_months: int = 60) -> dict:
        """
        Compiles synchronized 60-month array vectors for 3-way integration mapping.
        
        Outputs:
            net_revenue: Clear P&L revenue row (Excludes VAT)
            vat_collected: Liability row tracking outstanding tax collections due to HMRC
            gross_debtor_inflow: Realized physical cash entering the Cash Flow Statement
            closing_debtors_balance: Balance Sheet Asset row tracking outstanding client debt
        """
        net_revenue = [self.baseline_sales] * total_timeline_months
        vat_collected = [self.baseline_sales * self.vat_rate] * total_timeline_months
        
        # Calculate gross invoiced totals (Net + VAT) hitting accounts receivable each period
        gross_invoiced = [n + v for n, v in zip(net_revenue, vat_collected)]
        
        gross_debtor_inflow = [0.0] * total_timeline_months
        closing_debtors_balance = [0.0] * total_timeline_months
        
        # --- Compute Cash Collection Loops & Aging Debtors Balance Sheet Adjustments ---
        for m in range(total_timeline_months):
            # 1. Calculate cash collected in the current month from all historical invoices
            allocated_cash_run = 0.0
            for lag, weight in self.profile.items():
                invoice_month_target = m - lag
                if invoice_month_target >= 0:
                    allocated_cash_run += gross_invoiced[invoice_month_target] * weight
                    
            gross_debtor_inflow[m] = allocated_cash_run
            
            # 2. Calculate cumulative opening debtors balance up to this point
            cumulative_invoiced = sum(gross_invoiced[:m+1])
            cumulative_collected = sum(gross_debtor_inflow[:m+1])
            
            # Balance Sheet outstanding Accounts Receivable value
            closing_debtors_balance[m] = max(cumulative_invoiced - cumulative_collected, 0.0)
            
        return {
            "net_revenue": net_revenue,
            "vat_collected": vat_collected,
            "gross_debtor_inflow": gross_debtor_inflow,
            "closing_debtors_balance": closing_debtors_balance
        }