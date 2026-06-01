# ui_skin/core_engine/forecast_formulas.py
import pandas as pd
import numpy as np

def run_three_way_forecast(
    months: int = 24,
    starting_cash: float = 500000.00,
    starting_retained_earnings: float = 500000.00,
    monthly_sales: float = 100000.00,
    gross_profit_percent: float = 65.0,
    monthly_wages: float = 8672.57,
    debtor_days: int = 30,
    creditor_days: int = 30
) -> pd.DataFrame:
    
    records = []
    
    # Track rolling balances across the entire horizon timeline
    current_cash = starting_cash
    current_retained_earnings = starting_retained_earnings
    
    # Static statutory rules
    paye_ni_rate = 0.25      # 25% HMRC burden
    pension_rate = 0.05      # 5% Pension workplace allocation
    vat_rate = 0.20          # 20% Standard UK VAT
    
    for m in range(1, months + 1):
        # --- 1. PROFIT & LOSS LAYER ---
        turnover = monthly_sales
        cogs = turnover * (1 - (gross_profit_percent / 100.0))
        gross_profit = turnover - cogs
        
        # Payroll breakdown details
        wages_expense = monthly_wages
        paye_ni_expense = wages_expense * paye_ni_rate
        pension_expense = wages_expense * pension_rate
        total_payroll_costs = wages_expense + paye_ni_expense + pension_expense
        
        # Calculate final net operational profit
        net_profit = gross_profit - total_payroll_costs
        current_retained_earnings += net_profit
        
        # --- 2. BALANCE SHEET WORKING CAPITAL LAYER ---
        gross_sales_with_vat = turnover * (1 + vat_rate)
        debtors_balance = gross_sales_with_vat * (debtor_days / 30.0)
        
        gross_cogs_with_vat = cogs * (1 + vat_rate)
        trade_creditors = gross_cogs_with_vat * (creditor_days / 30.0)
        
        hmrc_paye_ni_owed = paye_ni_expense
        pension_owed = pension_expense
        vat_owed = (turnover * vat_rate) - (cogs * vat_rate)
        
        total_creditors_under_1yr = trade_creditors + hmrc_paye_ni_owed + pension_owed + vat_owed
        
        # --- 3. CASH FLOW LAYER ---
        current_cash = current_retained_earnings + total_creditors_under_1yr - debtors_balance
        
        # --- 4. DOUBLE-ENTRY INTEGRITY CHECK ---
        total_assets = current_cash + debtors_balance
        total_liabilities_and_equity = total_creditors_under_1yr + current_retained_earnings
        variance = total_assets - total_liabilities_and_equity
        
        records.append({
            "Month": f"Month {m}",
            "Turnover (£)": turnover,
            "Payroll Costs (£)": total_payroll_costs,
            "Net Profit (£)": net_profit,
            "Bank Cash Position (£)": current_cash,
            "Debtors Asset (£)": debtors_balance,
            "HMRC PAYE/NI Owed (£)": hmrc_paye_ni_owed,
            "Pension Owed (£)": pension_owed,
            "VAT Owed (£)": vat_owed,
            "Retained Earnings Balance (£)": current_retained_earnings,
            "Creditors Under 1 Yr (£)": total_creditors_under_1yr,
            "Variance (£)": variance
        })
        
    return pd.DataFrame(records)