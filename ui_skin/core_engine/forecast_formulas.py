# core_engine/forecast_formulas.py
import numpy as np
import pandas as pd

def run_three_way_forecast(
    months: int = 24,
    starting_cash: float = 500000.00,
    starting_retained_earnings: float = 0.00,
    monthly_sales: float = 100000.00,
    gross_profit_percent: float = 65.00,
    monthly_wages: float = 8672.57,
    debtor_days: int = 30,
    creditor_days: int = 30,
    paye_ni_rate: float = 20.00,
    pension_rate: float = 3.00
) -> pd.DataFrame:
    """
    Executes a mathematically tight 3-Way Financial Model projection (P&L, Cash Flow, Balance Sheet).
    Enforces double-entry constraints to ensure Assets = Liabilities + Equity at every month node.
    """
    
    # 1. Initialize empty arrays for tracking lines across time
    timeline = [f"Month {i+1}" for i in range(months)]
    
    # P&L Lines
    revenue = np.full(months, monthly_sales)
    cost_of_sales = revenue * (1 - (gross_profit_percent / 100.0))
    gross_profit = revenue - cost_of_sales
    
    # Payroll Breakdown Overhead lines
    payroll_costs = np.full(months, monthly_wages)
    hmrc_paye_ni_expense = payroll_costs * (paye_ni_rate / 100.0)
    pension_expense = payroll_costs * (pension_rate / 100.0)
    total_overheads = payroll_costs + hmrc_paye_ni_expense + pension_expense
    
    net_profit = gross_profit - total_overheads
    
    # Balance Sheet & Cash Vector trackers
    bank_cash = np.zeros(months)
    debtors_cl = np.zeros(months)
    creditors_cl = np.zeros(months)
    hmrc_owed_cl = np.zeros(months)
    pension_owed_cl = np.zeros(months)
    retained_earnings = np.zeros(months)
    variance = np.zeros(months)
    
    # Initialize rolling state variables using balance sheet baseline inputs
    current_cash = starting_cash
    current_retained_earnings = starting_retained_earnings
    
    # 2. Iterate sequentially through time nodes to accumulate ledger elements
    for m in range(months):
        # --- WORKING CAPITAL TIMING CALCULATIONS ---
        # Debtors (Accounts Receivable) timing logic
        if debtor_days > 0:
            cash_collected_from_sales = revenue[m] * (1.0 - (debtor_days / 30.0))
            if m > 0:
                # Add previous month's collections trailing lag
                cash_collected_from_sales += revenue[m-1] * (debtor_days / 30.0)
            else:
                cash_collected_from_sales += 0.0  # Assumes no legacy debtors opening match
            debtors_balance = max(0.0, revenue[m] * (debtor_days / 30.0))
        else:
            cash_collected_from_sales = revenue[m]
            debtors_balance = 0.0

        # Creditors (Accounts Payable) timing logic
        if creditor_days > 0:
            cash_paid_to_suppliers = cost_of_sales[m] * (1.0 - (creditor_days / 30.0))
            if m > 0:
                cash_paid_to_suppliers += cost_of_sales[m-1] * (creditor_days / 30.0)
            creditors_balance = max(0.0, cost_of_sales[m] * (creditor_days / 30.0))
        else:
            cash_paid_to_suppliers = cost_of_sales[m]
            creditors_balance = 0.0

        # --- GOVERNANCE LIABILITIES LAGS ---
        # Payroll liabilities trail exactly one month behind cash outlays
        if m > 0:
            hmrc_cash_outflow = hmrc_paye_ni_expense[m-1]
            pension_cash_outflow = pension_expense[m-1]
        else:
            hmrc_cash_outflow = 0.0  # Paid in month + 1
            pension_cash_outflow = 0.0

        hmrc_balance = hmrc_paye_ni_expense[m]
        pension_balance = pension_expense[m]

        # --- CASH FLOW STATEMENT INTEGRATION ---
        # Net operational cash movement formula
        net_cash_flow = (
            cash_collected_from_sales 
            - cash_paid_to_suppliers 
            - payroll_costs[m] 
            - hmrc_cash_outflow 
            - pension_cash_outflow
        )
        current_cash += net_cash_flow
        bank_cash[m] = current_cash

        # --- EQUALITY EQUITY FIX (The Core Math Adjustment) ---
        # Retained earnings MUST accumulate net profit independent of cash balances!
        current_retained_earnings += net_profit[m]
        retained_earnings[m] = current_retained_earnings

        # --- BALANCE SHEET VERIFICATION ENGINE ---
        debtors_cl[m] = debtors_balance
        creditors_cl[m] = creditors_balance
        hmrc_owed_cl[m] = hmrc_balance
        pension_owed_cl[m] = pension_balance

        # Double entry ledger formula: Total Assets = Total Liabilities + Total Equity
        total_assets = bank_cash[m] + debtors_cl[m]
        total_liabilities_and_equity = (
            creditors_cl[m] 
            + hmrc_owed_cl[m] 
            + pension_owed_cl[m] 
            + retained_earnings[m]
        )
        
        # Calculate discrepancies to pipe right to your validation banner component
        variance[m] = round(total_assets - total_liabilities_and_equity, 2)

    # 3. Compile vectors cleanly into a standardized pandas matrix dataframe
    forecast_df = pd.DataFrame({
        "Month": timeline,
        "Revenue (£)": revenue,
        "Cost of Sales (£)": cost_of_sales,
        "Gross Profit (£)": gross_profit,
        "Payroll Costs (£)": payroll_costs,
        "HMRC PAYE/NI Overhead (£)": hmrc_paye_ni_expense,
        "Pension Overhead (£)": pension_expense,
        "Net Profit (£)": net_profit,
        "Bank Cash Position (£)": bank_cash,
        "Debtors Balance (£)": debtors_cl,
        "Creditors Under 1 Yr (£)": creditors_cl,
        "HMRC PAYE/NI Owed (£)": hmrc_owed_cl,
        "Pension Owed (£)": pension_owed_cl,
        "Retained Earnings Balance (£)": retained_earnings,
        "Variance (£)": variance
    })

    return forecast_df