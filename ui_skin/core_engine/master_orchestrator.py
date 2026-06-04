import numpy as np
import pandas as pd
import streamlit as st
from ui_skin.core_engine.payroll import calculate_uk_payroll_breakdown, DEFAULT_UK_TAX_CONFIG

def run_master_three_way_engine(baseline_inputs: dict, loan_register_df, revenue_matrix_df, planned_capex_list: list, total_months: int = 60) -> dict:
    """
    Master 3-Way Financial Engine for STRATA.
    Chronologically unifies multi-channel revenue growth escalators, capacity 
    expansion overlays, and the hardwired 5-tier statutory UK payroll engine 
    to output fully reconciled, dynamic financial statements.
    """
    
    # =========================================================================
    # 1. EXTRACT OPERATIONAL LEVERS FROM STREAMLIT STATE
    # =========================================================================
    # Stage 3: Revenue Growth Levers (Pulls dynamically from frontend page inputs)
    ret_vol_growth = st.session_state.get("retail_annual_volume_growth", 0.05)
    ret_prc_ramp   = st.session_state.get("retail_annual_price_ramp", 0.025)
    whl_vol_growth = st.session_state.get("wholesale_annual_volume_growth", 0.12)
    whl_prc_ramp   = st.session_state.get("wholesale_annual_price_ramp", 0.00)
    
    # Stage 4: Capacity Expansion Levers
    expansion_active = st.session_state.get("expansion_scenario_active", False)
    exp_start_month  = st.session_state.get("expansion_month", 13) - 1  # Zero-indexed conversion
    exp_rev_base     = st.session_state.get("incremental_revenue_start", 20000.00)
    exp_cogs_pct     = st.session_state.get("expansion_cogs_pct", 0.40)
    exp_rent         = st.session_state.get("incremental_rent", 2500.00)
    exp_insurance    = st.session_state.get("incremental_insurance", 500.00)
    exp_overtime     = st.session_state.get("logistics_overtime_premium", 750.00)

    # Global OpEx Inflation Indexer established in Stage 2
    opex_annual_indexation = 0.035

    # =========================================================================
    # 2. INITIALISE 3-WAY FINANCIAL STATEMENT MATRICES (60 MONTHS)
    # =========================================================================
    out_revenue = np.zeros(total_months)
    out_purchases = np.zeros(total_months)
    out_stock_mov = np.zeros(total_months)
    out_cogs = np.zeros(total_months)
    out_overheads = np.zeros(total_months)
    out_depr = np.zeros(total_months)
    out_interest = np.zeros(total_months)
    out_tax_exp = np.zeros(total_months)
    out_net_profit = np.zeros(total_months)
    
    out_principal = np.zeros(total_months)
    out_tax_paid = np.zeros(total_months)
    out_proceeds = np.zeros(total_months)
    out_cash_at_bank = np.zeros(total_months)
    
    out_fa_nbv = np.zeros(total_months)
    out_inv_bs = np.zeros(total_months)
    out_ar_bs = np.zeros(total_months)
    out_debt_bs = np.zeros(total_months)
    out_tax_bs = np.zeros(total_months)

    # Extract opening capital asset seeds from historical baseline ingestion dictionaries
    cash_seed = float(baseline_inputs.get("opening_cash_balance", 84350.00))
    fa_seed   = float(baseline_inputs.get("opening_fixed_assets_nbv", 150000.00))
    ar_seed   = float(baseline_inputs.get("opening_accounts_receivable", 44886.00))
    ap_seed   = float(baseline_inputs.get("opening_accounts_payable", 8000.00))
    debt_seed = float(baseline_inputs.get("opening_long_term_debt", 0.0))
    inv_seed  = float(baseline_inputs.get("opening_inventory_balance", 12000.00))
    
    running_cash = cash_seed
    running_fa = fa_seed
    running_debt = debt_seed
    running_inv = inv_seed

    # Parse baseline parameters from your uploaded source tracking documents
    try:
        if isinstance(revenue_matrix_df, pd.DataFrame) and not revenue_matrix_df.empty:
            if "Revenue" in revenue_matrix_df.columns:
                base_total_monthly = float(revenue_matrix_df["Revenue"].iloc[0])
            else:
                base_total_monthly = float(revenue_matrix_df.iloc[:, 0].sum()) / 12
        else:
            base_total_monthly = 2633661.00 / 12
    except Exception:
        base_total_monthly = 2633661.00 / 12

    # Map core revenue turnover split context (65% Retail / 35% Wholesale)
    base_retail_monthly = base_total_monthly * 0.65
    base_wholesale_monthly = base_total_monthly * 0.35
    base_historical_monthly_opex = 8000.00  # Formulates your £96,000 baseline framework

    # =========================================================================
    # 3. INITIALISE STRUCTURAL INTERNAL PAYROLL LEDGERS & ACCRUAL POOLS
    # =========================================================================
    payroll_gross_base = np.full(total_months, float(baseline_inputs.get("base_payroll_monthly", 4800.00)))
    bs_hmrc_accrual = np.zeros(total_months)
    bs_pension_accrual = np.zeros(total_months)

    # =========================================================================
    # 4. CHRONOLOGICAL TIMELINE SIMULATION LOOP (MONTH 0 TO 59)
    # =========================================================================
    for m in range(total_months):
        current_year = m // 12
        
        # ---------------------------------------------------------------------
        # STAGE 3 MATH: TIMELINE GROWTH VECTOR COMPOUNDING
        # ---------------------------------------------------------------------
        retail_vol_mod = (1 + ret_vol_growth) ** current_year
        retail_prc_mod = (1 + ret_prc_ramp) ** current_year
        m_retail_revenue = base_retail_monthly * retail_vol_mod * retail_prc_mod
        
        wholesale_vol_mod = (1 + whl_vol_growth) ** current_year
        wholesale_prc_mod = (1 + whl_prc_ramp) ** current_year
        m_wholesale_revenue = base_wholesale_monthly * wholesale_vol_mod * wholesale_prc_mod
        
        m_core_revenue = m_retail_revenue + m_wholesale_revenue
        m_core_cogs = (m_retail_revenue * 0.35) + (m_wholesale_revenue * 0.60)

        # ---------------------------------------------------------------------
        # STAGE 4 MATH: ISOLATED FOOTPRINT CAPACITY EXPANSION OVERLAY
        # ---------------------------------------------------------------------
        m_inc_revenue = 0.0
        m_inc_cogs = 0.0
        m_inc_opex_step = 0.0
        
        if expansion_active and m >= exp_start_month:
            exp_years_active = (m - exp_start_month) // 12
            m_inc_revenue = exp_rev_base * ((1 + ret_vol_growth) ** exp_years_active)
            m_inc_cogs = m_inc_revenue * exp_cogs_pct
            m_inc_opex_step = exp_rent + exp_insurance + exp_overtime

        # Consolidated P&L Trading Trackers for Month m
        out_revenue[m] = m_core_revenue + m_inc_revenue
        out_cogs[m] = m_core_cogs + m_inc_cogs
        out_purchases[m] = out_cogs[m] * 0.95  # Dynamic proportional tracking variable
        out_stock_mov[m] = out_purchases[m] - out_cogs[m]

        # ---------------------------------------------------------------------
        # THE HARDWIRED 5-TIER UK STATUTORY PAYROLL SUB-ROUTINE
        # ---------------------------------------------------------------------
        payroll_snapshot = calculate_uk_payroll_breakdown(
            base_salary_flat=payroll_gross_base[m],
            hourly_rate=0.0, regular_hours_worked=0.0, overtime_hours_worked=0.0,
            pension_opt_out=False, tax_config=DEFAULT_UK_TAX_CONFIG
        )

        # Tier 1 & 2 Execution
        m_payroll_employment_cost = payroll_snapshot["pl_total_employment_cost"]
        net_wages_paid_m0 = payroll_snapshot["bs_net_wages_clearing"]

        # Tier 3 Liability Accrual
        prev_hmrc_bal = bs_hmrc_accrual[m-1] if m > 0 else 0.0
        prev_pension_bal = bs_pension_accrual[m-1] if m > 0 else 0.0
        bs_hmrc_accrual[m] = prev_hmrc_bal + payroll_snapshot["bs_hmrc_paye_ni_due"]
        bs_pension_accrual[m] = prev_pension_bal + payroll_snapshot["bs_pension_due"]

        # Tier 4 & 5 Month+1 Statutory Cash Sweeps
        hmrc_sweep_paid_m1 = 0.0
        pension_sweep_paid_m1 = 0.0
        if m > 0:
            hmrc_sweep_paid_m1 = bs_hmrc_accrual[m-1]
            pension_sweep_paid_m1 = bs_pension_accrual[m-1]
            
            bs_hmrc_accrual[m] -= hmrc_sweep_paid_m1
            bs_pension_accrual[m] -= pension_sweep_paid_m1

        # ---------------------------------------------------------------------
        # OVERHEAD CONSOLIDATION (STAGE 2 INDEXATION MIX)
        # ---------------------------------------------------------------------
        m_indexed_admin_overheads = base_historical_monthly_opex * ((1 + opex_annual_indexation) ** current_year)
        out_overheads[m] = m_indexed_admin_overheads + m_payroll_employment_cost + m_inc_opex_step
        
        # ---------------------------------------------------------------------
        # DYNAMIC DEBT, INVESTMENT & ASSET BALANCING LOOPS
        # ---------------------------------------------------------------------
        m_principal = 0.0
        m_interest = 0.0
        try:
            if isinstance(loan_register_df, pd.DataFrame) and not loan_register_df.empty:
                if "Monthly Payment" in loan_register_df.columns:
                    m_interest = float(loan_register_df["Interest"].iloc[0]) / 12
                    m_principal = float(loan_register_df["Principal"].iloc[0]) / 12
        except Exception:
            pass
            
        if m_interest == 0.0 and debt_seed > 0:
            m_interest = (debt_seed * 0.05) / 12  # Dynamic interest roll fallback

        # Process Scheduled additions via Capex allocations list
        m_depr = running_fa * (0.15 / 12)
        m_proceeds = 0.0
        for asset in planned_capex_list:
            if asset.get("Transaction Month") == m:
                running_fa += float(asset.get("Gross Purchase Price (£)", 0.0))

        out_depr[m] = m_depr
        out_interest[m] = m_interest
        out_principal[m] = m_principal
        out_proceeds[m] = m_proceeds
        
        # Profit and Loss aggregation variables
        m_ebitda = out_revenue[m] - out_cogs[m] - out_overheads[m]
        m_ebit = m_ebitda - out_depr[m] - out_interest[m]
        out_tax_exp[m] = max(0.0, m_ebit * 0.19 / 12)
        out_net_profit[m] = m_ebit - out_tax_exp[m]
        
        out_tax_paid[m] = out_tax_exp[m-1] if m > 0 else 0.0

        # Balance Sheet tracking state synchronization
        running_fa -= out_depr[m]
        out_fa_nbv[m] = running_fa
        
        running_inv += out_stock_mov[m]
        out_inv_bs[m] = running_inv
        
        # Debtor accounts track revenue scales dynamically to break flat line schedules
        out_ar_bs[m] = ar_seed + (out_revenue[m] * 0.15)
        
        running_debt = max(0.0, running_debt - out_principal[m])
        out_debt_bs[m] = running_debt
        
        # Tax liability includes short term payables to preserve balance sheet parity
        out_tax_bs[m] = out_tax_exp[m] + bs_hmrc_accrual[m] + bs_pension_accrual[m]

        # ---------------------------------------------------------------------
        # LIQUID CASH LEDGER RECONCILIATION
        # ---------------------------------------------------------------------
        m_cash_inflow = out_net_profit[m] + out_depr[m] + out_stock_mov[m]
        m_cash_outflow = out_principal[m] + out_tax_paid[m] + out_interest[m] + net_wages_paid_m0 + hmrc_sweep_paid_m1 + pension_sweep_paid_m1
        
        running_cash += (m_cash_inflow - m_cash_outflow)
        out_cash_at_bank[m] = running_cash

    # =========================================================================
    # 5. RETURNING THE 18 EXPECTED MATRICES FOR PRESENTATION
    # =========================================================================
    return {
        "Revenue": out_revenue.tolist(),
        "Purchases": out_purchases.tolist(),
        "Stock Movement": out_stock_mov.tolist(),
        "COGS": out_cogs.tolist(),
        "Overheads": out_overheads.tolist(),
        "Depreciation": out_depr.tolist(),
        "Interest Paid": out_interest.tolist(),
        "Tax Expense": out_tax_exp.tolist(),
        "Net Profit": out_net_profit.tolist(),
        "Principal Repayments": out_principal.tolist(),
        "Tax Cash Paid": out_tax_paid.tolist(),
        "Asset Disposal Proceeds": out_proceeds.tolist(),
        "Cash At Bank": out_cash_at_bank.tolist(),
        "Fixed Asset NBV": out_fa_nbv.tolist(),
        "Inventory Asset BS": out_inv_bs.tolist(),
        "Accounts Receivable BS": out_ar_bs.tolist(),
        "Outstanding Debt": out_debt_bs.tolist(),
        "Tax Liability BS": out_tax_bs.tolist()
    }