# core_engine/master_model.py
import pandas as pd
from core_engine.payroll import calculate_uk_payroll_breakdown

def generate_integrated_3way_forecast(inputs: dict) -> pd.DataFrame:
    """
    The Master Coordination Engine for market-catalyst-model.
    Processes user-defined scenario variables and loops month-by-month
    to build structurally aligned, integrated financial statement records.
    """
    months_timeline = [f"Month {i+1}" for i in range(60)]
    
    columns_to_track = [
        "Revenue", "Gross_Wages", "Employer_NI", "Employer_Pension",
        "Total_Employment_Overhead", "Net_Profit", "Bank_Cash_Asset",
        "HMRC_PAYE_NI_Liability", "Pension_Liability", "Total_Current_Liabilities",
        "Retained_Earnings", "Double_Entry_Check"
    ]
    
    forecast_matrix = pd.DataFrame(index=months_timeline, columns=columns_to_track)
    
    # Process static variables from the inputs package
    monthly_sales_target = inputs.get("target_monthly_sales", 50000.0)
    base_gross_wages = inputs.get("base_monthly_gross_wages", 0.0)
    pension_opt_out = inputs.get("pension_opt_out", False)
    
    running_bank_cash = inputs.get("opening_cash_balance", 0.0)
    running_retained_earnings = inputs.get("opening_retained_earnings", 0.0)
    
    # Execute our underlying UK payroll breakdown core module pass
    payroll_packet = calculate_uk_payroll_breakdown(base_gross_wages, pension_opt_out)
    
    # --- Chronological Monthly Financial Balancing Loop ---
    for i in range(60):
        current_m = f"Month {i+1}"
        
        # 1. Populate the Profit & Loss Entries
        forecast_matrix.loc[current_m, "Revenue"] = monthly_sales_target
        forecast_matrix.loc[current_m, "Gross_Wages"] = payroll_packet["pl_gross_salary"]
        forecast_matrix.loc[current_m, "Employer_NI"] = payroll_packet["pl_employer_ni"]
        forecast_matrix.loc[current_m, "Employer_Pension"] = payroll_packet["pl_employer_pension"]
        
        total_payroll_burden = payroll_packet["pl_total_employment_cost"]
        forecast_matrix.loc[current_m, "Total_Employment_Overhead"] = total_payroll_burden
        
        # Calculate monthly net profit line
        monthly_net_profit = monthly_sales_target - total_payroll_burden
        forecast_matrix.loc[current_m, "Net_Profit"] = monthly_net_profit
        
        # 2. Process Cash Flow Account Entries (Assuming cash collection baseline)
        monthly_cash_collected = monthly_sales_target
        monthly_cash_paid_out = total_payroll_burden
        
        running_bank_cash += (monthly_cash_collected - monthly_cash_paid_out)
        running_retained_earnings += monthly_net_profit
        
        # 3. Populate the Balance Sheet Entries
        forecast_matrix.loc[current_m, "Bank_Cash_Asset"] = running_bank_cash
        forecast_matrix.loc[current_m, "HMRC_PAYE_NI_Liability"] = payroll_packet["bs_hmrc_paye_ni_due"]
        forecast_matrix.loc[current_m, "Pension_Liability"] = payroll_packet["bs_pension_due"]
        
        total_liabilities = payroll_packet["bs_hmrc_paye_ni_due"] + payroll_packet["bs_pension_due"]
        forecast_matrix.loc[current_m, "Total_Current_Liabilities"] = total_liabilities
        forecast_matrix.loc[current_m, "Retained_Earnings"] = running_retained_earnings
        
        # 4. Integrated Accounting Balance Verification Check
        # Equation: Total Assets - (Total Liabilities + Total Equity) == 0.00
        total_assets = running_bank_cash
        total_liabilities_equity = total_liabilities + running_retained_earnings
        
        variance_check = round(total_assets - total_liabilities_equity, 2)
        forecast_matrix.loc[current_m, "Double_Entry_Check"] = variance_check
        
    return forecast_matrix