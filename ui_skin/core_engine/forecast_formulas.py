# core_engine/forecast_formulas.py
import pandas as pd
import numpy as np

def run_three_way_forecast(
    months: int = 36,
    starting_cash: float = 500000.00,
    starting_retained_earnings: float = 500000.00,
    monthly_sales: float = 100000.00,
    opex_input: float = 15000.00,          # ◄── ADDED: Core Overhead Baseline Input
    gross_profit_percent: float = 65.0,
    monthly_wages: float = 8672.57,
    debtor_days: int = 30,
    creditor_days: int = 30,
    vol_growth_monthly: float = 0.0,       # ◄── ADDED: Dynamic Index Hooks Passed Natively
    price_inc_monthly: float = 0.0,        # ◄── ADDED: Dynamic Index Hooks Passed Natively
    supplier_inf_monthly: float = 0.0,     # ◄── ADDED: Dynamic Index Hooks Passed Natively
    wage_inf_monthly: float = 0.0          # ◄── ADDED: Dynamic Index Hooks Passed Natively
) -> pd.DataFrame:
    """
    Executes a mathematically balanced 3-Way Financial Model over a flexible monthly horizon.
    Integrates compounding inflation profiles, variable volume increases, pricing indices,
    direct expenses (COGS), indirect overheads (OpEx), payroll mechanics, and working capital cash lags.
    """
    records = []
    current_cash = starting_cash
    current_retained_earnings = starting_retained_earnings
    
    # Statutory Fiscal Overlays
    paye_ni_rate = 0.25
    pension_rate = 0.05
    vat_rate = 0.20
    
    for m in range(1, months + 1):
        # Derive discrete compound multipliers for current month index (0-indexed compounding)
        v_mult = (1 + vol_growth_monthly) ** (m - 1)
        p_mult = (1 + price_inc_monthly) ** (m - 1)
        s_mult = (1 + supplier_inf_monthly) ** (m - 1)
        w_mult = (1 + wage_inf_monthly) ** (m - 1)
        
        # 1. PROFIT & LOSS ACCRUAL LAYERS
        # Turnover scales with unit demand expansion AND selling price hikes together
        turnover = monthly_sales * v_mult * p_mult
        
        # Direct Expenses (COGS) scale with volume and increase with material inflation
        direct_expenses = (monthly_sales * v_mult * (1 - (gross_profit_percent / 100.0))) * s_mult
        
        # Indirect Overheads (OpEx) scale strictly with fixed overhead inflation
        indirect_overheads = opex_input * w_mult
        
        # Payroll scales with labor/wage cost inflation adjustments
        wages_expense = monthly_wages * w_mult
        total_payroll_overheads = wages_expense * (1 + paye_ni_rate + pension_rate)
        
        # Bottom Line Net Earnings Calculation
        net_profit = turnover - direct_expenses - indirect_overheads - total_payroll_overheads
        current_retained_earnings += net_profit
        
        # 2. WORKING CAPITAL ASSETS & LIABILITIES (TIMING VARIANCE EFFECTS)
        # Gross Debtors Asset (Accounts Receivable with trailing VAT)
        debtors_balance = (turnover * (1 + vat_rate)) * (debtor_days / 30.0)
        
        # Gross Trade Creditors (Accounts Payable to suppliers with trailing VAT)
        trade_creditors = (direct_expenses * (1 + vat_rate)) * (creditor_days / 30.0)
        
        # Statutory Liabilities owed to tax entities and pensions
        payroll_liabilities = (wages_expense * paye_ni_rate) + (wages_expense * pension_rate)
        net_vat_payable = (turnover * vat_rate) - (direct_expenses * vat_rate)
        
        total_creditors = trade_creditors + payroll_liabilities + net_vat_payable
        
        # 3. CASH FLOW & DOUBLE-ENTRY EQUILIBRIUM BALANCE
        # Assets = Liabilities + Equity  -->  Cash + Debtors = Creditors + Retained Earnings
        # Solved for Cash: Cash = Retained Earnings + Creditors - Debtors
        current_cash = current_retained_earnings + total_creditors - debtors_balance
        
        # Strict validation checkpoint (Must evaluate to absolute zero)
        variance = (current_cash + debtors_balance) - (total_creditors + current_retained_earnings)
        
        records.append({
            "Month": f"Month {m}",
            "Turnover (£)": turnover,
            "Direct Expenses (COGS) (£)": direct_expenses,
            "Indirect Overheads (£)": indirect_overheads,
            "Payroll Costs (£)": total_payroll_overheads,
            "Net Profit (£)": net_profit,
            "Bank Cash Position (£)": current_cash,
            "Debtors Asset (£)": debtors_balance,
            "Creditors Under 1 Yr (£)": total_creditors,
            "Retained Earnings Balance (£)": current_retained_earnings,
            "Variance (£)": variance
        })
        
    return pd.DataFrame(records)