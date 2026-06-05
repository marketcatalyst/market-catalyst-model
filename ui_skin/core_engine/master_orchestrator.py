import numpy as np
import pandas as pd

def run_master_three_way_engine(baseline_inputs, loan_register_df, revenue_matrix_df, planned_capex_list, total_months=60, overrides=None):
    """
    STRATA Purified Three-Way Engine.
    Operates via functional parameters to guarantee absolute mathematical 
    independence between baseline visualization and sandbox scenario tracking.
    """
    if overrides is None:
        overrides = {}

    # 1. Parse operational rates and adjust with dynamic scenario overrides
    annual_revenue_baseline = float(revenue_matrix_df["Revenue"].iloc[0])
    monthly_revenue_baseline = annual_revenue_baseline / 12.0
    
    retail_vol_growth = overrides.get("retail_annual_volume_growth", 0.05)
    retail_price_ramp = overrides.get("retail_annual_price_ramp", 0.025)
    wholesale_vol_growth = overrides.get("wholesale_annual_volume_growth", 0.10)
    wholesale_price_ramp = overrides.get("wholesale_annual_price_ramp", 0.065)
    
    # Capacity Overlay settings (Stage 4)
    stage4_active = overrides.get("expansion_scenario_active", False)
    expansion_m = overrides.get("expansion_month", 13)
    node_rev_mo = overrides.get("incremental_revenue_start", 20000.00)
    node_cogs_pct = overrides.get("expansion_cogs_pct", 0.40)
    node_rent = overrides.get("incremental_rent", 2500.00)
    node_insurance = overrides.get("incremental_insurance", 500.00)
    node_overtime = overrides.get("logistics_overtime_premium", 750.00)
    
    # Working Capital adjustments (Stage 5)
    std_lag_m = int(overrides.get("wc_lag_standard_months", 1))
    corp_lag_m = int(overrides.get("wc_lag_corporate_months", 2))
    corp_split = overrides.get("wc_split_corporate", 0.70)
    std_split = 1.0 - corp_split
    
    # Initialize the synchronized tracking ledger structure
    outputs = {
        "Revenue": np.zeros(total_months),
        "Purchases": np.zeros(total_months),
        "Stock Movement": np.zeros(total_months),
        "COGS": np.zeros(total_months),
        "Overheads": np.zeros(total_months),
        "Depreciation": np.zeros(total_months),
        "Interest Paid": np.zeros(total_months),
        "Tax Expense": np.zeros(total_months),
        "Net Profit": np.zeros(total_months),
        "Working Capital CF": np.zeros(total_months),
        "Tax Cash Paid": np.zeros(total_months),
        "Principal Repayments": np.zeros(total_months),
        "Asset Disposal Proceeds": np.zeros(total_months),
        "Cash At Bank": np.zeros(total_months),
        "Fixed Asset NBV": np.zeros(total_months),
        "Inventory Asset BS": np.zeros(total_months),
        "Accounts Receivable BS": np.zeros(total_months),
        "Outstanding Debt": np.zeros(total_months),
        "Tax Liability BS": np.zeros(total_months),
        "Equity Retained BS": np.zeros(total_months)
    }
    
    # Seed ledger opening states
    current_cash = float(baseline_inputs.get("opening_cash_balance", 84350.00))
    current_fa_nbv = float(baseline_inputs.get("opening_fixed_assets_nbv", 150000.00))
    current_ar = float(baseline_inputs.get("opening_accounts_receivable", 44886.00))
    current_inventory = float(baseline_inputs.get("opening_inventory_balance", 12000.00))
    current_tax_liability = 0.0
    current_debt = float(baseline_inputs.get("opening_long_term_debt", 0.0))
    
    current_equity = current_cash + current_fa_nbv + current_inventory + current_ar - current_debt - current_tax_liability
    
    wholesale_billing_history = [current_ar * std_split] * 12
    corporate_billing_history = [current_ar * corp_split] * 12

    # Chronological Execution Grid
    for m in range(total_months):
        year_interval = m // 12
        
        m_retail_rev = (monthly_revenue_baseline * 0.65) * ((1.0 + retail_vol_growth) ** year_interval) * ((1.0 + retail_price_ramp) ** year_interval)
        m_wholesale_rev = (monthly_revenue_baseline * 0.35) * ((1.0 + wholesale_vol_growth) ** year_interval) * ((1.0 + wholesale_price_ramp) ** year_interval)
        
        m_node_rev, m_node_cogs, m_node_fixed = 0.0, 0.0, 0.0
        if stage4_active and (m >= (expansion_m - 1)):
            m_node_rev = node_rev_mo
            m_node_cogs = node_rev_mo * node_cogs_pct
            m_node_fixed = node_rent + node_insurance + node_overtime
            
        total_m_rev = m_retail_rev + m_wholesale_rev + m_node_rev
        total_m_cogs = ((m_retail_rev + m_wholesale_rev) * 0.42) + m_node_cogs
        total_m_overheads = 8000.00 + m_node_fixed
        
        m_depreciation, m_interest = 1250.00, 0.00
        m_ebit = total_m_rev - total_m_cogs - total_m_overheads - m_depreciation - m_interest
        m_tax_provision = max(0.0, m_ebit * 0.19)
        m_net_profit = m_ebit - m_tax_provision
        
        # Working capital delays mapping
        m_std_billed = total_m_rev * std_split
        m_corp_billed = total_m_rev * corp_split
        
        wholesale_billing_history.append(m_std_billed)
        corporate_billing_history.append(m_corp_billed)
        
        cash_rec_wholesale = wholesale_billing_history[-1 - std_lag_m] + corporate_billing_history[-1 - corp_lag_m]
        cash_received = m_retail_rev + cash_rec_wholesale
        
        m_tax_cash_outflow = current_tax_liability if (m > 0 and m % 3 == 0) else 0.0
        if m_tax_cash_outflow > 0: current_tax_liability = 0.0
        current_tax_liability += m_tax_provision
        
        cash_paid = total_m_cogs + total_m_overheads + m_tax_cash_outflow
        m_cash_variance = cash_received - cash_paid
        
        current_cash += m_cash_variance
        current_ar = current_ar + (m_std_billed + m_corp_billed) - cash_rec_wholesale
        current_fa_nbv -= m_depreciation
        current_equity += m_net_profit
        
        # Store to dataset fields using pristine shared naming strings
        outputs["Revenue"][m] = total_m_rev
        outputs["Purchases"][m] = total_m_cogs
        outputs["Stock Movement"][m] = 0.0
        outputs["COGS"][m] = total_m_cogs
        outputs["Overheads"][m] = total_m_overheads
        outputs["Depreciation"][m] = m_depreciation
        outputs["Interest Paid"][m] = m_interest
        outputs["Tax Expense"][m] = m_tax_provision
        outputs["Net Profit"][m] = m_net_profit
        outputs["Working Capital CF"][m] = cash_rec_wholesale - (m_std_billed + m_corp_billed)
        outputs["Tax Cash Paid"][m] = m_tax_cash_outflow
        outputs["Principal Repayments"][m] = 0.0
        outputs["Asset Disposal Proceeds"][m] = 0.0
        outputs["Cash At Bank"][m] = current_cash
        outputs["Fixed Asset NBV"][m] = current_fa_nbv
        outputs["Inventory Asset BS"][m] = current_inventory
        outputs["Accounts Receivable BS"][m] = max(0.0, current_ar)
        outputs["Outstanding Debt"][m] = current_debt
        outputs["Tax Liability BS"][m] = max(0.0, current_tax_liability)
        outputs["Equity Retained BS"][m] = current_equity

    return outputs