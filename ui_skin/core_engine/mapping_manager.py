# ui_skin/core_engine/mapping_manager.py
import pandas as pd
from typing import List, Dict, Any

# Hardcoded platform-wide target slots
PLATFORM_TARGET_SLOTS = [
    "Liquid Bank Cash Base",
    "Trade Accounts Receivable (AR)",
    "Fixed Assets Gross Cost",
    "Trade Accounts Payable (AP)",
    "Outstanding Debt Obligations",
    "Retained Earnings Reserve"
]

# The Semantic Keyword Lexicon
LEXICON = {
    "Liquid Bank Cash Base": ["bank", "cash", "current account", "barclays", "lloyds", "clearing", "current acc"],
    "Trade Accounts Receivable (AR)": ["debtors", "receivable", "trade allocations", "customer ledger"],
    "Fixed Assets Gross Cost": ["fixed assets", "plant", "machinery", "vehicles", "equipment", "leasehold"],
    "Trade Accounts Payable (AP)": ["creditors", "payable", "supplier ledger", "trade payables"],
    "Outstanding Debt Obligations": ["term loan", "dbw", "funding circle", "iwoca", "credit facility", "borrowings"],
    "Retained Earnings Reserve": ["retained", "earnings", "brought forward", "p&l reserve", "equity surplus"]
}

def analyze_and_map_ledger(raw_ledger_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Scans every row of an extracted trial balance, runs keyword semantic checks,
    assigns a mapping status, and provides the UI layer with pre-selected options.
    """
    mapped_records = []
    
    for _, row in raw_ledger_df.iterrows():
        code = str(row.get("Account Code", "")).strip()
        name = str(row.get("Account Name", "")).strip()
        balance = float(row.get("Balance", 0.0))
        
        name_lower = name.lower()
        best_slot = ""
        highest_score = 0.0
        
        # Scan through the lexicon to determine match scoring parameters
        for slot, keywords in LEXICON.items():
            score = 0.0
            for kw in keywords:
                if kw in name_lower:
                    score += 0.5  # Keyword match found
                    
            if score > highest_score:
                highest_score = score
                best_slot = slot
                
        # Determine UI routing threshold classification
        if highest_score >= 1.0:
            status = "🟢 AUTO-MAPPED"
        elif highest_score > 0.0:
            status = "🟡 REVIEW SUGGESTION"
        else:
            status = "🔴 UNRESOLVED"
            best_slot = PLATFORM_TARGET_SLOTS[0] # Default fallback placement for picker dropdowns
            
        mapped_records.append({
            "Account Code": code,
            "Account Name": name,
            "Net Balance (£)": balance,
            "Assigned Platform Destination": best_slot,
            "System Action Status": status
        })
        
    return mapped_records