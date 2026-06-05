import numpy as np
import pandas as pd
import streamlit as st

def run_master_three_way_engine(baseline_inputs, loan_register_df, revenue_matrix_df, planned_capex_list, total_months=60):
    """
    STRATA Core Three-Way Forecasting Engine.
    Employs an independent direct cash tracking matrix to completely eliminate
    cross-key variable data collisions between the P&L and Cash Flow ledgers.
    """
    
    # Extract baseline metrics and normalise annual turnover into a monthly trading base
    annual_revenue_baseline = float(revenue_matrix_df["Revenue"].iloc[0])
    monthly_revenue_baseline = annual_revenue_baseline / 12.0
    
    # Load Stage 3 configuration inputs
    retail_vol_growth = st.session_state.get("retail_annual_volume_growth", 0.05)
    retail_price_ramp = st.session_state.get("retail_annual_price_ramp", 0.025)
    wholesale_vol_growth = st.session_state.get("wholesale_annual_volume_growth", 0.10)
    wholesale_price_ramp = st.session_state.get("wholesale_annual_price_ramp", 0.065)
    
    # Load Stage 4 footprint expansion inputs
    stage4_active = st.session_state.get("expansion_scenario_active", False)
    expansion_m = st.session_state.get("expansion_month", 13)
    node_rev_mo = st.session_state.get("incremental_revenue_start", 20000.00)
    node_cogs_pct = st.session_state.get("expansion_cogs_pct", 0.40)
    node_rent = st.session_state.get("incremental_rent", 2500.00)
    node_insurance = st.session_state.get("incremental_insurance", 500.00)
    node_overtime = st.session_state.get("logistics_overtime_premium", 750.00)
    
    # Load Stage 5 Credit & Working Capital allocations
    wc_advanced = st.session_state.get("wc_advanced_active", False)
    std_split = st.session_state.get("wc_split_standard", 0.30)
    corp_split = st.session_state.get("wc_split_corporate", 0.70)
    std_lag_m = int(st.session_state.get("wc_lag_standard_months", 1))
    corp_lag_m = int(st.session_state.get("wc_lag_corporate_months", 2))
    
    stress_delay_active = st.session_state.get("stress_simulate_delay", False)
    stress_default_active = st.session_state.get("stress_simulate_default", False)
    
    if stress_delay_active:
        corp_lag_m += 1  # Add +30 days lookback collection friction
        
    # Build cleanly separated data keys for tracking arrays
    outputs = {
        "Revenue": np.zeros(total_months),
        "Purchases": np.zeros(total_months),
        "Stock Movement P&L": np.zeros(total_months),
        "COGS": np.zeros(total_months),
        "Overheads": np.zeros(total_months),
        "Depreciation": np.zeros(total_months),
        "Interest Paid": np.zeros(total_months),
        "Tax Expense": np.zeros(total_months),
        "Net Profit": np.zeros(total_months),
        "Working Capital CF": np.zeros(total_months),  # ◄── NEW UNIQUE KEY TO PREVENT KEY COLLISION
        "Tax Cash Paid": np.zeros(total_months),
        "Principal Repayments": np.zeros(total_months),
        "Asset Disposal Proceeds": np.zeros(total_months),
        "Cash At Bank": np.zeros(total_months),
        "Fixed Asset NBV": np.zeros(total_months),
        "Inventory Asset BS": np.zeros(total_months),
        "Accounts Receivable BS": np.zeros(total_months),
        "Outstanding Debt": np.zeros(total_months),
        "Tax Liability BS": np.zeros(total_months),
        "Equity Retained BS": np.zeros(total_months)   # ◄── NEW KEY FOR EXPLICIT BALANCE SHEET AUDITING
    }
    
    # Seed ledger balances carried forward from opening ground-truths
    current_cash = float(baseline_inputs.get("opening_cash_balance", 84350.00))
    current_fa_nbv = float(baseline_inputs.get("opening_fixed_assets_nbv", 150000.00))
    current_ar = float(baseline_inputs.get("opening_accounts_receivable", 44886.00))
    current_inventory = float(baseline_inputs.get("opening_inventory_balance", 12000.00))
    current_tax_liability = 0.0
    current_debt = float(baseline_inputs.get("opening_long_term_debt", 0.0))
    
    # Calculate initial opening equity position to lock down structural balance parameters
    current_equity = current_cash + current_fa_nbv + current_inventory + current_ar - current_debt - current_tax_liability
    
    # Setup invoice lag lookback queues
    wholesale_billing_history = []
    corporate_billing_history = []
    
    # Pre-seed lookback buffers with safe baseline counts
    for _ in range(12):
        wholesale_billing_history.append((current_ar * 0.30))
        corporate_billing_history.append((current_ar * 0.70))

    # Run timeline execution loop
    for m in range(total_months):
        current_year_interval = m // 12
        
        # Split revenue by channel lines (65% Retail / 35% Wholesale)
        base_m_retail = monthly_revenue_baseline * 0.65
        base_m_wholesale = monthly_revenue_baseline * 0.35
        
        # Apply annual anniversary compounding logic
        retail_volume_mult = (1.0 + retail_vol_growth) ** current_year_interval
        retail_price_mult = (1.0 + retail_price_ramp) ** current_year_interval
        wholesale_volume_mult = (1.0 + wholesale_vol_growth) ** current_year_interval
        wholesale_price_mult = (1.0 + wholesale_price_ramp) ** current_year_interval
        
        m_retail_rev = base_m_retail * retail_volume_mult * retail_price_mult
        m_wholesale_rev = base_m_wholesale * wholesale_volume_mult * wholesale_price_mult
        
        # Layer on Stage 4 satellite expansion nodes if active
        m_node_rev = 0.0
        m_node_cogs = 0.0
        m_node_fixed_costs = 0.0
        
        if stage4_active and (m >= (expansion_m - 1)):
            m_node_rev = node_rev_mo
            m_node_cogs = node_rev_mo * node_cogs_pct
            m_node_fixed_costs = node_rent + node_insurance + node_overtime
            
        total_m_rev = m_retail_rev + m_wholesale_rev + m_node_rev
        
        # Standard corporate production COGS modeling parameter anchored at 42% base
        base_production_cogs = (m_retail_rev + m_wholesale_rev) * 0.42
        total_m_cogs = base_production_cogs + m_node_cogs
        
        total_m_purchases = total_m_cogs
        m_stock_movement_pl = 0.0
        
        base_admin_overheads = 8000.00  # Legacy monthly administrative overhead baseline
        total_m_overheads = base_admin_overheads + m_node_fixed_costs
        
        m_depreciation_expense = 1250.00  
        m_finance_interest = 0.00
        
        # P&L Net Earnings Summary Block
        m_ebitda = total_m_rev - total_m_cogs - total_m_overheads
        m_ebit = m_ebitda - m_depreciation_expense - m_finance_interest
        m_tax_provision = max(0.0, m_ebit * 0.19)
        m_net_profit = m_ebit - m_tax_provision
        
        # =============================================================================
        # 💸 WORKING CAPITAL TIMING TIMELINE LOGIC
        # =============================================================================
        cash_collections_retail = m_retail_rev
        cash_collections_wholesale = 0.0
        
        if not wc_advanced:
            wholesale_billing_history.append(m_wholesale_rev + m_node_rev)
            corporate_billing_history.append(0.0)
            
            lookback_idx = len(wholesale_billing_history) - 1 - std_lag_m
            cash_collections_wholesale = wholesale_billing_history[lookback_idx]
            m_total_wholesale_billed = m_wholesale_rev + m_node_rev
        else:
            m_std_wholesale_billed = (m_wholesale_rev + m_node_rev) * std_split
            m_corp_wholesale_billed = (m_wholesale_rev + m_node_rev) * corp_split
            
            if stress_default_active:
                m_corp_wholesale_billed = 0.0  # Key corporate account defaults completely
                
            wholesale_billing_history.append(m_std_wholesale_billed)
            corporate_billing_history.append(m_corp_wholesale_billed)
            
            std_lookback_idx = len(wholesale_billing_history) - 1 - std_lag_m
            corp_lookback_idx = len(corporate_billing_history) - 1 - corp_lag_m
            
            cash_collections_wholesale = (
                wholesale_billing_history[std_lookback_idx] + 
                corporate_billing_history[corp_lookback_idx]
            )
            m_total_wholesale_billed = m_std_wholesale_billed + m_corp_wholesale_billed

        # Settle monthly tax cash outlays quarterly to HMRC
        m_tax_cash_outflow = 0.0
        if m > 0 and m % 3 == 0:
            m_tax_cash_outflow = current_tax_liability
            current_tax_liability = 0.0
        current_tax_liability += m_tax_provision
        
        m_principal_paid = 0.0
        m_asset_liquidation = 0.0
        
        # DIRECT CASH FLOW CONGRUENCE CHECK (Calculates strict physical capital changes)
        cash_received = cash_collections_retail + cash_collections_wholesale
        cash_paid = total_m_purchases + total_m_overheads + m_tax_cash_outflow + m_principal_paid + m_finance_interest
        m_cash_variance = cash_received - cash_paid
        
        # Synchronise ledger asset layers safely
        current_cash += m_cash_variance
        current_ar = current_ar + m_total_wholesale_billed - cash_collections_wholesale
        current_fa_nbv -= m_depreciation_expense
        current_equity += m_net_profit  # Track rolling retained capital position
        
        # Calculate the working capital mismatch plugging value required to balance the indirect row report matrix
        wc_report_plug = cash_collections_wholesale - m_total_wholesale_billed + m_tax_provision
        
        # Save array metrics cleanly across tracking fields
        outputs["Revenue"][m] = total_m_rev
        outputs["Purchases"][m] = total_m_purchases
        outputs["Stock Movement P&L"][m] = m_stock_movement_pl
        outputs["COGS"][m] = total_m_cogs
        outputs["Overheads"][m] = total_m_overheads
        outputs["Depreciation"][m] = m_depreciation_expense
        outputs["Interest Paid"][m] = m_finance_interest
        outputs["Tax Expense"][m] = m_tax_provision
        outputs["Net Profit"][m] = m_net_profit
        
        outputs["Working Capital CF"][m] = wc_report_plug
        outputs["Tax Cash Paid"][m] = m_tax_cash_outflow
        outputs["Principal Repayments"][m] = m_principal_paid
        outputs["Asset Disposal Proceeds"][m] = m_asset_liquidation
        
        outputs["Cash At Bank"][m] = current_cash
        outputs["Fixed Asset NBV"][m] = current_fa_nbv
        outputs["Inventory Asset BS"][m] = current_inventory
        outputs["Accounts Receivable BS"][m] = max(0.0, current_ar)
        outputs["Outstanding Debt"][m] = current_debt
        outputs["Tax Liability BS"][m] = max(0.0, current_tax_liability)
        outputs["Equity Retained BS"][m] = current_equity

    return outputs