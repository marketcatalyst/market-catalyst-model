# ui_skin/core_engine/master_model.py
import pandas as pd
import numpy as np
from ui_skin.core_engine.fixed_assets import calculate_multi_asset_depreciation_matrix
from ui_skin.core_engine.payroll import calculate_uk_payroll_breakdown
from ui_skin.core_engine.tax_engine import calculate_corporation_tax_schedule

def generate_integrated_3way_forecast(inputs: dict, overrides: dict = None) -> pd.DataFrame:
    """
    The Single Source of Truth Orchestration Engine for STRATA.
    Integrates operational sandbox inputs, baseline financial actuals, 
    and advanced statutory sub-engines into a 60-month double-entry balanced ledger
    designed for direct mathematical benchmarking against WinForecast.
    """
    if overrides is None:
        overrides = {}
        
    total_months = 60
    months_axis = [f"Month {m+1}" for m in range(total_months)]
    
    # ─── 1. EXTRACT SCENARIO OVERRIDES (THE SANDBOX LEVERS) ──────────────────
    vol_growth = float(overrides.get("retail_annual_volume_growth", 0.0))
    price_ramp = float(overrides.get("retail_annual_price_ramp", 0.0))
    
    # ─── 2. EXTRACT VECTORIZED INGESTION VARIABLES ───────────────────────────
    y1_curve = inputs.get("y1_monthly_revenue_curve", [0.0] * 12)
    y2_target = float(inputs.get("y2_revenue_target", 10805679.00))
    y3_target = float(inputs.get("y3_revenue_target", 12126469.00))
    
    admin_overheads = float(inputs.get("admin_overheads_monthly", 18575.00))
    directors_salaries = float(inputs.get("directors_salaries_monthly", 5150.00))
    base_gross_wages = float(inputs.get("base_monthly_gross_wages", 12000.00))
    pension_opt_out = bool(inputs.get("pension_opt_out", False))
    
    # Opening Balance Sheet Snapshots
    opening_cash = float(inputs.get("opening_cash_balance", 69488.0))
    opening_fa_nbv = float(inputs.get("opening_fixed_assets_nbv", 531385.0))
    opening_ar = float(inputs.get("opening_accounts_receivable", 44886.0))
    opening_ap = float(inputs.get("opening_accounts_payable", 8000.0))
    opening_debt = float(inputs.get("opening_long_term_debt", 341001.0))
    opening_re = float(inputs.get("opening_retained_earnings", -82005.0))
    
    planned_capex = inputs.get("planned_capex_list", [])

    # ─── 3. PRE-EXECUTE ASSET DEPRECIATION MATRIX ────────────────────────────
    asset_schedules = calculate_multi_asset_depreciation_matrix(
        opening_nbv=opening_fa_nbv,
        planned_capex_list=planned_capex,
        total_months=total_months
    )

    # ─── 4. INITIALIZE TIME-SERIES CHRONOLOGICAL LEDGER FIELDS ───────────────
    outputs = {
        "Revenue": np.zeros(total_months), "COGS": np.zeros(total_months),
        "Overheads": np.zeros(total_months), "Payroll Burden": np.zeros(total_months),
        "Depreciation": asset_schedules["timeline_depreciation_expense"],
        "Interest Paid": np.zeros(total_months), "Net Profit Before Tax": np.zeros(total_months),
        "Tax Expense": np.zeros(total_months), "Net Profit": np.zeros(total_months),
        "Cash At Bank": np.zeros(total_months), "Fixed Asset NBV": asset_schedules["timeline_nbv"],
        "Accounts Receivable BS": np.zeros(total_months), "Accounts Payable & Debt": np.zeros(total_months),
        "Tax Liability BS": np.zeros(total_months), "Equity Retained BS": np.zeros(total_months),
        "Working Capital CF": np.zeros(total_months), "Tax Cash Paid": np.zeros(total_months),
        "Ops_FTE_Strain": np.zeros(total_months), "Double_Entry_Check": np.zeros(total_months)
    }

    running_cash = opening_cash
    running_re = opening_re
    running_liabilities_pool = opening_ap + opening_debt

    # ─── 5. CHRONOLOGICAL MONTHLY FINANCIAL ITERATION LOOP ───────────────────
    for m in range(total_months):
        year_idx = m // 12
        month_in_year = m % 12
        
        # A. Vectorized Revenue Parsing
        if year_idx == 0:
            base_turnover = y1_curve[month_in_year] if month_in_year < len(y1_curve) else 0.0
        elif year_idx == 1:
            base_turnover = y2_target / 12.0
        elif year_idx == 2:
            base_turnover = y3_target / 12.0
        else:
            base_turnover = (y3_target / 12.0) * ((1.05) ** (year_idx - 2))
            
        turnover = base_turnover * (1.0 + vol_growth + price_ramp)
        direct_costs = turnover * 0.696
        
        # B. Connected Costs: Real-Time Payroll Burden Pass
        simulated_overtime_hours = max(0.0, (vol_growth * 40.0))
        payroll_data = calculate_uk_payroll_breakdown(
            base_salary_flat=base_gross_wages,
            overtime_hours_worked=simulated_overtime_hours,
            pension_opt_out=pension_opt_out
        )
        wages_expense = payroll_data.get("pl_total_employment_cost", base_gross_wages * 1.12)
        fte_strain = payroll_data.get("ops_fte_utilization", 1.0)
        
        # C. Profitability Accrual
        m_depreciation = outputs["Depreciation"][m]
        m_interest = 1250.00 if m < 12 else 0.00
        
        m_overheads_total = admin_overheads + directors_salaries
        ebit = turnover - direct_costs - m_overheads_total - wages_expense - m_depreciation
        pbt = ebit - m_interest
        
        outputs["Revenue"][m] = turnover
        outputs["COGS"][m] = direct_costs
        outputs["Overheads"][m] = m_overheads_total
        outputs["Payroll Burden"][m] = wages_expense
        outputs["Interest Paid"][m] = m_interest
        outputs["Net Profit Before Tax"][m] = pbt
        outputs["Ops_FTE_Strain"][m] = fte_strain

    # ─── 6. ROUTE ACCRUED TIMELINES INTO STATUTORY TAX ENGINE ────────────────
    tax_schedules = calculate_corporation_tax_schedule(
        monthly_net_profit=outputs["Net Profit Before Tax"],
        monthly_book_depreciation=outputs["Depreciation"],
        monthly_disposal_gains=asset_schedules["timeline_disposal_gains"],
        monthly_disposal_proceeds=asset_schedules["timeline_disposal_proceeds"],
        tax_main_pool_additions=asset_schedules["tax_main_pool_additions"],
        tax_special_pool_additions=asset_schedules["tax_special_pool_additions"]
    )
    
    outputs["Tax Expense"] = tax_schedules["timeline_tax_expense"]
    outputs["Tax Cash Paid"] = tax_schedules["timeline_tax_cash_outflow"]
    outputs["Tax Liability BS"] = tax_schedules["timeline_tax_liability_bs"]

    # ─── 7. FINAL BALANCE SHEET & LIQUIDITY RECONCILIATION RUN ───────────────
    for m in range(total_months):
        month_1based = m + 1
        net_profit_after_tax = outputs["Net Profit Before Tax"][m] - outputs["Tax Expense"][m]
        outputs["Net Profit"][m] = net_profit_after_tax
        running_re += net_profit_after_tax
        
        # Capital Expenditure Outflows Tracking
        cash_capex_outflow = 0.0
        for asset in planned_capex:
            if int(asset.get("Transaction Month", -1)) == month_1based:
                if asset.get("Funding Mechanism") == "Upfront Cash":
                    cash_capex_outflow += float(asset.get("Gross Purchase Price (£)", 0.0))

        # Financing Event Slicing
        debt_injection = 400000.0 if month_1based == 6 else 0.0
        debt_repayment = 72890.0 if month_1based == 6 else (8499.0 if month_1based > 6 else 0.0)
        
        # Indirect Cash Flow formulation (Re-anchored around PBT to remove double-tax counting)
        m_tax_cash = outputs["Tax Cash Paid"][m]
        m_depr = outputs["Depreciation"][m]
        
        net_cash_movement = outputs["Net Profit Before Tax"][m] + m_depr - cash_capex_outflow + debt_injection - debt_repayment - m_tax_cash
        running_cash += net_cash_movement
        
        running_liabilities_pool = running_liabilities_pool + debt_injection - debt_repayment
        
        # Double Entry Identity Verification
        current_asset_nbv = outputs["Fixed Asset NBV"][m]
        total_assets = current_asset_nbv + running_cash + opening_ar
        total_equities_liabilities = running_re + running_liabilities_pool + outputs["Tax Liability BS"][m]
        variance = total_assets - total_equities_liabilities
        
        outputs["Cash At Bank"][m] = running_cash
        outputs["Accounts Receivable BS"][m] = opening_ar
        outputs["Accounts Payable & Debt"][m] = running_liabilities_pool
        outputs["Equity Retained BS"][m] = running_re
        outputs["Working Capital CF"][m] = net_cash_movement
        outputs["Double_Entry_Check"][m] = variance

    # ─── 8. TRANSLATE TO PRECISE UNIFORM STREAMLIT MATRIX ────────────────────
    forecast_matrix = pd.DataFrame(index=months_axis)
    forecast_matrix["Month"] = months_axis
    
    translations = {
        "Turnover (£)": "Revenue", "Direct Costs (£)": "COGS",
        "Admin Overheads (£)": "Overheads", "Depreciation Expense (£)": "Depreciation",
        "Interest Paid (£)": "Interest Paid", "Tax Expense (£)": "Tax Expense",
        "Net Profit (£)": "Net Profit", "Fixed Asset NBV (£)": "Fixed Asset NBV",
        "Bank Cash Position (£)": "Cash At Bank", "Accounts Receivable BS (£)": "Accounts Receivable BS",
        "Accounts Payable & Debt (£)": "Accounts Payable & Debt", "Retained Earnings (£)": "Equity Retained BS", 
        "Tax Liability BS (£)": "Tax Liability BS", "Bridge: Net Profit": "Net Profit", 
        "Bridge: Depreciation": "Depreciation", "Bridge: Operating CF": "Net Profit", 
        "Bridge: Investing CF": "Net Profit", "Bridge: Financing CF": "Net Profit", 
        "Bridge: Net Movement": "Working Capital CF", "Ops_FTE_Strain": "Ops_FTE_Strain", 
        "Double_Entry_Check": "Double_Entry_Check"
    }
    
    for ui_label, internal_key in translations.items():
        forecast_matrix[ui_label] = np.round(outputs[internal_key], 2)
        
    return forecast_matrix