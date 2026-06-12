# engine/assets.py

class AssetObject:
    """
    Pure Python computational model for Corporate Fixed Asset Lifecycles.
    Handles capital expenditure shocks, accounting depreciation runs, and 
    Net Book Value (NBV) tracking independently of visual frameworks.
    """
    def __init__(self, asset_name: str, cost: float, purchase_month: int, useful_life_months: int, residual_value: float = 0.0):
        self.asset_name = asset_name
        self.cost = float(cost)
        self.purchase_month = int(purchase_month)  # Month index, e.g., 1 to 60
        self.useful_life = int(useful_life_months)
        self.residual_value = float(residual_value)
        
    def get_monthly_vectors(self, total_timeline_months: int = 60) -> dict:
        """
        Compiles synchronized 60-month array vectors for 3-way integration mapping.
        
        Outputs:
            capex_cash: Outflow vector for the Cash Flow Statement (Investing Activities)
            depreciation_expense: Monthly P&L charge vector reducing EBIT
            accumulated_depreciation: Cumulative balance sheet offset vector
            net_book_value: Active asset carrying balance sheet value
        """
        capex_cash = [0.0] * total_timeline_months
        depreciation_expense = [0.0] * total_timeline_months
        accumulated_depreciation = [0.0] * total_timeline_months
        net_book_value = [0.0] * total_timeline_months
        
        # Prevent zero division errors defensively
        if self.useful_life <= 0:
            monthly_depr_rate = 0.0
        else:
            monthly_depr_rate = (self.cost - self.residual_value) / self.useful_life
            
        # 1. Map the Capital Expenditure Cash Outflow shock point
        if 1 <= self.purchase_month <= total_timeline_months:
            capex_cash[self.purchase_month - 1] = self.cost
            
        running_accum_depr = 0.0
        
        # 2. Compute 60-Month Relational Balances
        for m in range(total_timeline_months):
            current_month_index = m + 1
            
            # Asset is active if current month falls within its operational lifepan window
            is_active = (current_month_index >= self.purchase_month) and \
                        (current_month_index < (self.purchase_month + self.useful_life))
            
            if is_active:
                depreciation_expense[m] = monthly_depr_rate
                running_accum_depr += monthly_depr_rate
                
            # If asset lifespan completes fully, clamp values to permanent residual value
            if current_month_index >= (self.purchase_month + self.useful_life):
                running_accum_depr = self.cost - self.residual_value
                
            # Keep balances anchored to zero prior to asset acquisition month
            if current_month_index < self.purchase_month:
                current_nbv = 0.0
                current_accum = 0.0
            else:
                current_nbv = max(self.cost - running_accum_depr, self.residual_value)
                current_accum = running_accum_depr
                
            accumulated_depreciation[m] = current_accum
            net_book_value[m] = current_nbv
            
        return {
            "capex_cash": capex_cash,
            "depreciation_expense": depreciation_expense,
            "accumulated_depreciation": accumulated_depreciation,
            "net_book_value": net_book_value
        }