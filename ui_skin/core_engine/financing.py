# core_engine/financing.py

def calculate_debt_amortization_and_split(
    principal_amount: float,
    annual_interest_rate: float,
    term_months: int,
    start_month_index: int,
    forecast_horizon_months: int = 60
) -> dict:
    """
    Calculates a monthly commercial loan or HP amortization schedule.
    Automatically splits the remaining debt profile into current (<12m)
    and non-current (>12m) liabilities across the 60-month timeline.
    """
    monthly_interest_rate = (annual_interest_rate / 100.0) / 12.0
    
    # 1. Calculate the Fixed Monthly Payment using the standard financial PMT formula
    if monthly_interest_rate > 0:
        fixed_monthly_payment = (
            principal_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** term_months) / 
            ((1 + monthly_interest_rate) ** term_months - 1)
        )
    else:
        fixed_monthly_payment = principal_amount / term_months

    # Initialize empty arrays for our 60-month master projection timeline
    pl_interest_expense = [0.0] * forecast_horizon_months
    cf_net_cash_flow = [0.0] * forecast_horizon_months
    bs_creditors_under_1yr = [0.0] * forecast_horizon_months
    bs_creditors_over_1yr = [0.0] * forecast_horizon_months
    
    # Create a tracking array for the principal balance, padded by 12 months 
    # to allow the look-ahead logic to scan ahead without crashing at Month 60.
    padded_balance_track = [0.0] * (forecast_horizon_months + 13)
    
    running_balance = principal_amount
    months_paid = 0
    
    # 2. Chronological Payment Loop to map principal changes
    for m in range(len(padded_balance_track)):
        if m < start_month_index:
            padded_balance_track[m] = 0.0
            continue
            
        if months_paid < term_months and running_balance > 0:
            # Capture initial loan/HP capital injection in the setup month
            if m == start_month_index and m < forecast_horizon_months:
                cf_net_cash_flow[m] = principal_amount
                
            # Split the payment into interest and principal reduction components
            interest_charge = running_balance * monthly_interest_rate
            principal_reduction = fixed_monthly_payment - interest_charge
            
            if m < forecast_horizon_months:
                pl_interest_expense[m] = round(interest_charge, 2)
                # Cash shifts out of bank (or nets against initial injection in Month 0)
                cf_net_cash_flow[m] -= round(fixed_monthly_payment, 2)
                
            running_balance -= principal_reduction
            padded_balance_track[m] = max(0.0, running_balance)
            months_paid += 1
        else:
            padded_balance_track[m] = 0.0

    # 3. Dynamic Rolling 12-Month Look-Ahead Balance Sheet Split
    for m in range(forecast_horizon_months):
        if m < start_month_index:
            continue
            
        total_outstanding_debt = padded_balance_track[m]
        # Look exactly 12 months into the future array to see what the debt balance drops to
        future_balance_12m = padded_balance_track[m + 12]
        
        # The current element is what will be paid off over the coming year
        current_liability_portion = total_outstanding_debt - future_balance_12m
        long_term_liability_portion = future_balance_12m
        
        bs_creditors_under_1yr[m] = round(current_liability_portion, 2)
        bs_creditors_over_1yr[m] = round(long_term_liability_portion, 2)

    return {
        "timeline_pl_interest": pl_interest_expense,
        "timeline_cf_cash_movement": cf_net_cash_flow,
        "timeline_bs_current_debt": bs_creditors_under_1yr,
        "timeline_bs_long_term_debt": bs_creditors_over_1yr
    }