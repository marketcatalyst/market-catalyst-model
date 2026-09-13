# utils/consolidation.py
# STRATA SUITE // MULTI-ENTITY CONSOLIDATION & INTER-COMPANY ELIMINATION ENGINE

import pandas as pd

def consolidate_group_entities(subsidiary_ledgers: list, ownership_percentages: dict = None) -> dict:
    """
    Consolidates multiple subsidiary trial balances or financial statements 
    into a single master group balance sheet, applying elimination entries.
    """
    if not subsidiary_ledgers:
        return {}

    consolidated_bs = {}
    eliminations = {
        "intercompany_debtors_creditors": 0.0,
        "intercompany_revenue_costs": 0.0
    }

    # Base accumulation across all entities
    for sub in subsidiary_ledgers:
        bs = sub.get("balance_sheet", {})
        for line_item, val in bs.items():
            consolidated_bs[line_item] = consolidated_bs.get(line_item, 0.0) + float(val)

    # Apply standard consolidation adjustments / eliminations if intercompany data is present
    for sub in subsidiary_ledgers:
        ic_balances = sub.get("intercompany_balances", {})
        ic_amount = float(ic_balances.get("amount", 0.0))
        
        # Eliminate intercompany trade debtors against trade creditors
        if ic_amount > 0:
            consolidated_bs["Trade Debtors Balance (£)"] = max(0.0, consolidated_bs.get("Trade Debtors Balance (£)", 0.0) - ic_amount)
            consolidated_bs["Trade Creditors Balance (£)"] = max(0.0, consolidated_bs.get("Trade Creditors Balance (£)", 0.0) - ic_amount)
            eliminations["intercompany_debtors_creditors"] += ic_amount

    # Trial balance integrity check
    total_assets = consolidated_bs.get("Total Assets (£)", 0.0)
    total_liabs_equity = consolidated_bs.get("Total Liabilities & Equity Reserves (£)", 0.0)
    checksum = round(total_assets - total_liabs_equity, 2)
    consolidated_bs["Trial Balance Checksum Balance"] = checksum

    return {
        "consolidated_balance_sheet": consolidated_bs,
        "eliminations_summary": eliminations,
        "is_balanced": abs(checksum) < 1.0
    }