# engine/ledger.py

class MasterLedger:
    """
    Centralised computational ledger matrix. Accumulates individual asset, 
    financing, income, and expenditure vectors into a unified 60-month 
    integrated three-way financial forecast model.
    """
    def __init__(self, total_timeline_months: int = 60):
        self.total_months = total_timeline_months
        self.income_streams = []
        self.expense_streams = []
        self.hp_streams = []
        self.loan_streams = []
        
    def add_income(self, income_obj, invoice_finance_eligible: bool = False, invoice_finance_advance_rate: float = 0.85):
        """Registers a revenue stream with active invoice discounting attributes."""
        self.income_streams.append({
            "obj": income_obj,
            "if_eligible": invoice_finance_eligible,
            "if_advance": float(invoice_finance_advance_rate)
        })
        
    def add_expenditure(self, expense_obj):
        """Registers an operational cost overhead line."""
        self.expense_streams.append(expense_obj)
        
    def add_hire_purchase(self, hp_obj):
        """Registers a financed asset arrangement."""
        self.hp_streams.append(hp_obj)
        
    def add_loan(self, loan_obj):
        """Registers a corporate term debt facility."""
        self.loan_streams.append(loan_obj)

    def compile_forecast_matrix(self) -> dict:
        """
        Compiles all standalone child streams, executing invoice discounting cash 
        acceleration loops and netting quarterly VAT balances with an ironclad 40-day 
        HMRC Direct Debit settlement delay hitting squarely in Month 5 (2 months post-quarter close).
        """
        # --- 1. Initialize Master Structural Arrays ---
        pl_revenue = [0.0] * self.total_months
        pl_expenses = [0.0] * self.total_months
        pl_interest = [0.0] * self.total_months
        pl_depreciation = [0.0] * self.total_months
        
        cf_inflows = [0.0] * self.total_months
        cf_outflows = [0.0] * self.total_months
        
        bs_debtors = [0.0] * self.total_months
        bs_creditors = [0.0] * self.total_months
        bs_hp_liability = [0.0] * self.total_months
        bs_loan_liability = [0.0] * self.total_months
        bs_asset_nbv = [0.0] * self.total_months
        bs_hmrc_vat_balance = [0.0] * self.total_months
        
        output_vat_register = [0.0] * self.total_months
        input_vat_register = [0.0] * self.total_months

        # --- 2. Process Revenue Layer & Invoice Finance Overrides ---
        for entry in self.income_streams:
            inc = entry["obj"]
            vec = inc.get_monthly_vectors(self.total_months)
            for m in range(self.total_months):
                pl_revenue[m] += vec["net_revenue"][m]
                output_vat_register[m] += vec["vat_collected"][m]
                
                if entry["if_eligible"]:
                    gross_invoiced_this_month = vec["net_revenue"][m] + vec["vat_collected"][m]
                    advance_cash = gross_invoiced_this_month * entry["if_advance"]
                    cf_inflows[m] += advance_cash
                    
                    regular_cash_collected = vec["gross_debtor_inflow"][m]
                    margin_collected = max(regular_cash_collected - advance_cash, 0.0)
                    cf_inflows[m] += margin_collected
                    bs_debtors[m] += max(vec["closing_debtors_balance"][m] - advance_cash, 0.0)
                else:
                    cf_inflows[m] += vec["gross_debtor_inflow"][m]
                    bs_debtors[m] += vec["closing_debtors_balance"][m]

        # --- 3. Process Operational Expenditures Line-by-Line ---
        for exp in self.expense_streams:
            vec = exp.get_monthly_vectors(self.total_months)
            for m in range(self.total_months):
                pl_expenses[m] += vec["net_expense"][m]
                input_vat_register[m] += vec["vat_paid"][m]
                cf_outflows[m] += vec["gross_cash_outflow"][m]
                bs_creditors[m] += vec["closing_creditors_balance"][m]

        # --- 4. Process Hire Purchase Asset Tranches ---
        for hp in self.hp_streams:
            vec = hp.get_monthly_vectors(self.total_months)
            for m in range(self.total_months):
                pl_interest[m] += vec["interest_expense"][m]
                pl_depreciation[m] += vec["depr_expense"][m]
                cf_outflows[m] += vec["cash_outflow"][m]
                bs_hp_liability[m] += vec["hp_creditor_balance"][m]
                bs_asset_nbv[m] += vec["asset_nbv"][m]

        # --- 5. Process Corporate Term Loans ---
        for loan in self.loan_streams:
            vec = loan.get_monthly_vectors(self.total_months)
            for m in range(self.total_months):
                pl_interest[m] += vec["interest_expense"][m]
                if vec["cash_flow_impact"][m] > 0:
                    cf_inflows[m] += vec["cash_flow_impact"][m]
                else:
                    cf_outflows[m] += abs(vec["cash_flow_impact"][m])
                bs_loan_liability[m] += vec["loan_liability_balance"][m]

        # --- 6. Continuous Cumulative VAT Ledger with 40-Day Direct Debit Clearance ---
        rolling_balance = 0.0
        vat_cash_settlements = [0.0] * self.total_months
        
        # Intermediate arrays to track individual quarter historical blocks
        q_accumulator = 0.0
        
        for m in range(self.total_months):
            current_month_index = m + 1
            
            # Net transaction change for this specific month
            month_net_vat = output_vat_register[m] - input_vat_register[m]
            
            # 1. Feed the active quarter block accumulator
            q_accumulator += month_net_vat
            
            # 2. Feed the master continuous balance register
            rolling_balance += month_net_vat
            
            # Every 3rd month represent a quarter freeze lock point
            if current_month_index % 3 == 0:
                # Lock the exact cumulative total owed for the 3-month block
                locked_quarter_debt = q_accumulator
                
                # Direct Debit cash outflow hits exactly 2 months down the road (Month m + 2)
                payment_month_target = m + 2
                if payment_month_target < self.total_months:
                    vat_cash_settlements[payment_month_target] = locked_quarter_debt
                
                # Reset only the block counter, leaving the master rolling balance fully intact
                q_accumulator = 0.0
                
            # 3. Apply physical Direct Debit clearance hits to the master continuous balance
            cash_clearance = vat_cash_settlements[m]
            if cash_clearance != 0.0:
                cf_outflows[m] += cash_clearance
                rolling_balance -= cash_clearance
                
            # The Balance Sheet row now natively represents the accurate rolling position
            bs_hmrc_vat_balance[m] = rolling_balance

        return {
            "pl_revenue": pl_revenue,
            "pl_expenses": pl_expenses,
            "pl_interest": pl_interest,
            "pl_depreciation": pl_depreciation,
            "cf_inflows": cf_inflows,
            "cf_outflows": cf_outflows,
            "bs_debtors": bs_debtors,
            "bs_creditors": bs_creditors,
            "bs_hp_liability": bs_hp_liability,
            "bs_loan_liability": bs_loan_liability,
            "bs_asset_nbv": bs_asset_nbv,
            "bs_hmrc_vat_balance": bs_hmrc_vat_balance
        }