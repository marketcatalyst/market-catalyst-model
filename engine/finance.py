# engine/finance.py

from engine.assets import AssetObject

class HirePurchaseObject:
    """
    Pure Python model mirroring the WinForecast Financed Asset paradigm.
    Combines a fixed asset depreciation engine with a standard reducing-balance
    loan amortization schedule under a single synchronized object.
    """
    def __init__(self, asset_name: str, total_asset_value: float, deposit: float, 
                 term_months: int, annual_interest_rate: float, purchase_month: int):
        
        self.asset_name = asset_name
        self.total_asset_value = float(total_asset_value)
        self.deposit = float(deposit)
        self.term = int(term_months)
        self.annual_rate = float(annual_interest_rate) # e.g., 0.085 for 8.5%
        self.purchase_month = int(purchase_month)
        
        # Instantiate the internal background asset engine twin
        # Assuming standard economic useful life of 60 months for capitalized equipment
        self.asset_engine = AssetObject(
            asset_name=asset_name,
            cost=self.total_asset_value,
            purchase_month=self.purchase_month,
            useful_life_months=60
        )
        
        # Calculate opening credit facility baseline
        self.financed_principal = self.total_asset_value - self.deposit

    def get_monthly_vectors(self, total_timeline_months: int = 60) -> dict:
        """
        Compiles synchronized 60-month array vectors for 3-way integration mapping.
        
        Outputs:
            cash_outflow: Total cash paid (Deposit in M0, monthly instalments subsequently)
            interest_expense: P&L finance cost charge vector reducing Net Profit
            hp_creditor_balance: Balance Sheet liability vector (HP Creditors)
            asset_nbv: Balance Sheet Net Book Value vector handled by asset engine
            depr_expense: P&L depreciation charge vector handled by asset engine
        """
        # 1. Gather baseline asset tracking vectors from the twin engine
        asset_data = self.asset_engine.get_monthly_vectors(total_timeline_months)
        
        # 2. Initialize fresh finance array tracks
        cash_outflow = [0.0] * total_timeline_months
        interest_expense = [0.0] * total_timeline_months
        hp_creditor_balance = [0.0] * total_timeline_months
        
        # Compute standard fixed monthly installment using standard loan amortization formula
        # PMT = P * (r * (1 + r)^n) / ((1 + r)^n - 1)
        monthly_rate = self.annual_rate / 12.0
        if monthly_rate > 0 and self.term > 0:
            fixed_monthly_payment = self.financed_principal * (monthly_rate * (1 + monthly_rate) ** self.term) / ((1 + monthly_rate) ** self.term - 1)
        else:
            fixed_monthly_payment = self.financed_principal / max(self.term, 1)

        current_loan_balance = 0.0
        months_paid = 0
        
        for m in range(total_timeline_months):
            current_month_index = m + 1
            
            # --- Month 0 / Point of Purchase Event ---
            if current_month_index == self.purchase_month:
                cash_outflow[m] += self.deposit
                current_loan_balance = self.financed_principal
                hp_creditor_balance[m] = current_loan_balance
                continue
                
            # --- Pre-purchase Dead Zone ---
            if current_month_index < self.purchase_month:
                hp_creditor_balance[m] = 0.0
                continue
                
            # --- Monthly Payment Active Window Run ---
            if current_month_index > self.purchase_month and months_paid < self.term:
                # Calculate monthly interest portion based on opening balance for the period
                current_month_interest = current_loan_balance * monthly_rate
                # Principal reduction is total payment minus the interest cost drag
                current_month_principal = fixed_monthly_payment - current_month_interest
                
                # Defensive check for terminal payment over-repayment
                if current_month_principal > current_loan_balance or (months_paid == self.term - 1):
                    current_month_principal = current_loan_balance
                    fixed_monthly_payment = current_month_principal + current_month_interest
                
                cash_outflow[m] = fixed_monthly_payment
                interest_expense[m] = current_month_interest
                current_loan_balance -= current_month_principal
                months_paid += 1
                
            hp_creditor_balance[m] = max(current_loan_balance, 0.0)
            
        return {
            "cash_outflow": cash_outflow,
            "interest_expense": interest_expense,
            "hp_creditor_balance": hp_creditor_balance,
            "asset_nbv": asset_data["net_book_value"],
            "depr_expense": asset_data["depreciation_expense"]
        }


class LoanObject:
    """
    Pure Python model for standard corporate term debt.
    Unlike Hire Purchase, a standard term loan injects gross liquidity
    directly into cash reserves at Month X and amortizes principal over time.
    """
    def __init__(self, facility_name: str, principal: float, term_months: int, 
                 annual_interest_rate: float, draw_down_month: int):
        self.facility_name = facility_name
        self.principal = float(principal)
        self.term = int(term_months)
        self.annual_rate = float(annual_interest_rate) # e.g., 0.075 for 7.5%
        self.draw_down_month = int(draw_down_month)    # Month index, 1 to 60

    def get_monthly_vectors(self, total_timeline_months: int = 60) -> dict:
        """
        Compiles synchronized 60-month loan vectors for 3-way modeling.
        
        Outputs:
            cash_flow_impact: Cash injection (+ Principal) or outflow (- Installment)
            interest_expense: P&L finance cost charge vector
            loan_liability_balance: Balance Sheet debt liability row
        """
        cash_flow_impact = [0.0] * total_timeline_months
        interest_expense = [0.0] * total_timeline_months
        loan_liability_balance = [0.0] * total_timeline_months
        
        # Calculate monthly interest factor and fixed payment baseline
        monthly_rate = self.annual_rate / 12.0
        if monthly_rate > 0 and self.term > 0:
            fixed_monthly_payment = self.principal * (monthly_rate * (1 + monthly_rate) ** self.term) / ((1 + monthly_rate) ** self.term - 1)
        else:
            fixed_monthly_payment = self.principal / max(self.term, 1)

        current_loan_balance = 0.0
        months_paid = 0
        
        for m in range(total_timeline_months):
            current_month_index = m + 1
            
            # --- Drawdown Event: Inject Gross Liquidity ---
            if current_month_index == self.draw_down_month:
                cash_flow_impact[m] += self.principal
                current_loan_balance = self.principal
                loan_liability_balance[m] = current_loan_balance
                continue
                
            # --- Pre-drawdown Dormant Window ---
            if current_month_index < self.draw_down_month:
                loan_liability_balance[m] = 0.0
                continue
                
            # --- Active Servicing Repayment Loop ---
            if current_month_index > self.draw_down_month and months_paid < self.term:
                current_month_interest = current_loan_balance * monthly_rate
                current_month_principal = fixed_monthly_payment - current_month_interest
                
                # Check for final over-repayment truncation points
                if current_month_principal > current_loan_balance or (months_paid == self.term - 1):
                    current_month_principal = current_loan_balance
                    fixed_monthly_payment = current_month_principal + current_month_interest
                    
                cash_flow_impact[m] = -fixed_monthly_payment # Negative sign represents cash outflow
                interest_expense[m] = current_month_interest
                current_loan_balance -= current_month_principal
                months_paid += 1
                
            loan_liability_balance[m] = max(current_loan_balance, 0.0)
            
        return {
            "cash_flow_impact": cash_flow_impact,
            "interest_expense": interest_expense,
            "loan_liability_balance": loan_liability_balance
        }