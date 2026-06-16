# ui_skin/core_engine/double_entry_matrix.py

import os
import json
import pandas as pd
import numpy as np

class TrialBalanceCuboid:
    """
    Maintains a balanced ledger matrix across a 60-month forecasting horizon.
    Enforces that at any single month, Sum(Debits) + Sum(Credits) = 0.
    """
    def __init__(self):
        self.accounts = [
            # --- BALANCE SHEET ASSETS ---
            "BS_Asset_Cash",
            "BS_Asset_Debtors",
            "BS_Asset_Fixed_Assets",
            "BS_Asset_Accumulated_Depreciation",
            
            # --- BALANCE SHEET LIABILITIES & EQUITY ---
            "BS_Liability_Creditors",
            "BS_Liability_VAT_Payable",
            "BS_Liability_Tax_Payable",
            "BS_Liability_Long_Term_Debt",
            "BS_Equity_Share_Capital",
            "BS_Equity_Retained_Earnings",
            
            # --- PROFIT & LOSS ACCOUNTS ---
            "PL_Revenue_Gross",
            "PL_COGS",
            "PL_Expense_Overheads",
            "PL_Expense_Interest",
            "PL_Expense_Depreciation",
            "PL_Expense_Taxation"
        ]
        self.matrix = pd.DataFrame(
            0.0, 
            index=self.accounts, 
            columns=[f"M{str(i).zfill(2)}" for i in range(1, 61)]
        )

    def post_journal(self, month_label, debit_acct, credit_acct, amount):
        if amount == 0.0:
            return
        if debit_acct not in self.accounts or credit_acct not in self.accounts:
            raise KeyError(f"Ledger Post Defect: Account identifier mismatch.")
        self.matrix.at[debit_acct, month_label] += amount
        self.matrix.at[credit_acct, month_label] -= amount

    def verify_ledger_integrity(self, month_label):
        checksum = self.matrix[month_label].sum()
        if abs(checksum) > 1e-4:
            raise ValueError(f"CRITICAL BREAKDOWN: Trial balance imbalance of £{checksum:.2f} at {month_label}")
        return True


def compile_three_way_forecast(project_json_path):
    """
    Engine master routine. Reads project parameters and processes them chronologically
    into fully compounding, synchronized three-way financial statements.
    """
    tbc = TrialBalanceCuboid()
    
    if not os.path.exists(project_json_path):
        raise FileNotFoundError(f"Missing active workspace dataset file: {project_json_path}")
        
    with open(project_json_path, "r") as pf:
        project_data = json.load(pf)

    months_labels = [f"M{str(i).zfill(2)}" for i in range(1, 61)]
    
    # Identify if a construction phase is required
    has_fixed_assets = any(cap.get("type") == "New / Existing Fixed Asset CapEx" for cap in project_data.get("capital", []))
    start_month = 13 if has_fixed_assets else 1

    # -------------------------------------------------------------------------
    # CHRONOLOGICAL TRANSACTION LOOP (PURE MONOTONIC POSTINGS)
    # -------------------------------------------------------------------------
    for m_idx, m_label in enumerate(months_labels, start=1):
        
        # 1. Process Capital Events & Upfront Funding
        for cap in project_data.get("capital", []):
            target_month = int(cap.get("month", 1))
            if target_month == m_idx:
                val = float(cap.get("value", 0.0))
                t_type = cap.get("type", "")
                
                if t_type == "Equity Capital / Share Premium Injection":
                    tbc.post_journal(m_label, "BS_Asset_Cash", "BS_Equity_Share_Capital", val)
                elif t_type == "Commercial Debt / Facility Drawdown":
                    tbc.post_journal(m_label, "BS_Asset_Cash", "BS_Liability_Long_Term_Debt", val)
                elif t_type == "New / Existing Fixed Asset CapEx":
                    tbc.post_journal(m_label, "BS_Asset_Fixed_Assets", "BS_Asset_Cash", val)

        # 2. Process Active Trading Revenues (With Balanced Net/VAT Flows)
        if m_idx >= start_month:
            for sale in project_data.get("sales", []):
                annual_amt = float(sale.get("amount", 0.0))
                monthly_revenue = annual_amt / 12.0
                vat_rate = float(sale.get("vat", 0.20))
                
                # Credit Revenue P&L, Debit Cash with the clean Net baseline
                tbc.post_journal(m_label, "BS_Asset_Cash", "PL_Revenue_Gross", monthly_revenue)
                if vat_rate > 0:
                    vat_outflow = monthly_revenue * vat_rate
                    # Collect VAT cash immediately into the bank, balancing the liability ledger
                    tbc.post_journal(m_label, "BS_Asset_Cash", "BS_Liability_VAT_Payable", vat_outflow)

        # 3. Process Active Operating Overheads
        if m_idx >= start_month:
            for opex in project_data.get("opex", []):
                annual_cost = float(opex.get("amount", 0.0))
                monthly_cost = annual_cost / 12.0
                tbc.post_journal(m_label, "PL_Expense_Overheads", "BS_Asset_Cash", monthly_cost)

        # 4. Process Straight-Line Asset Depreciation
        if m_idx >= start_month:
            current_asset_base = tbc.matrix.loc["BS_Asset_Fixed_Assets", :m_label].sum()
            if current_asset_base > 0.0:
                monthly_depr = (current_asset_base * 0.10) / 12.0
                tbc.post_journal(m_label, "PL_Expense_Depreciation", "BS_Asset_Accumulated_Depreciation", monthly_depr)

        tbc.verify_ledger_integrity(m_label)

    # -------------------------------------------------------------------------
    # TRANSLATION LAYER: PROGRESSIVE CHRONOLOGICAL CUMULATIVE ACCUMULATOR
    # -------------------------------------------------------------------------
    cumulative_matrix = pd.DataFrame(0.0, index=tbc.accounts, columns=months_labels)
    running_balances = {acct: 0.0 for acct in tbc.accounts if acct.startswith("BS_")}
    
    for m_label in months_labels:
        for acct in running_balances.keys():
            running_balances[acct] += tbc.matrix.at[acct, m_label]
            cumulative_matrix.at[acct, m_label] = running_balances[acct]

    # Calculate and compound Retained Earnings chronologically from P&L histories
    running_retained_earnings = 0.0
    for m_label in months_labels:
        monthly_rev = -tbc.matrix.at["PL_Revenue_Gross", m_label]
        monthly_exp = (
            tbc.matrix.at["PL_COGS", m_label] +
            tbc.matrix.at["PL_Expense_Overheads", m_label] +
            tbc.matrix.at["PL_Expense_Depreciation", m_label] +
            tbc.matrix.at["PL_Expense_Interest", m_label] +
            tbc.matrix.at["PL_Expense_Taxation", m_label]
        )
        net_profit_period = monthly_rev - monthly_exp
        running_retained_earnings += net_profit_period
        cumulative_matrix.at["BS_Equity_Retained_Earnings", m_label] = running_retained_earnings

    # Structure 1: PROFIT & LOSS REPORT
    pl_export = pd.DataFrame(index=months_labels)
    pl_export["Revenue (£)"] = -tbc.matrix.loc["PL_Revenue_Gross"]
    pl_export["COGS (£)"] = tbc.matrix.loc["PL_COGS"]
    pl_export["Opex (£)"] = tbc.matrix.loc["PL_Expense_Overheads"]
    pl_export["Depreciation (£)"] = tbc.matrix.loc["PL_Expense_Depreciation"]
    pl_export["EBIT (£)"] = pl_export["Revenue (£)"] - pl_export["COGS (£)"] - pl_export["Opex (£)"] - pl_export["Depreciation (£)"]
    pl_export["Interest Expense (£)"] = tbc.matrix.loc["PL_Expense_Interest"]
    pl_export["Tax Expense (£)"] = tbc.matrix.loc["PL_Expense_Taxation"]
    
    # Structure 2: REAL COMPOUNDING CASH FLOW LEDGER (FIXED LOGIC LINKS)
    cf_export = pd.DataFrame(index=months_labels)
    
    # Inflows track total cash entering the bank (Net Revenue + Collected VAT)
    cf_export["Operational Cash Inflows (£)"] = pl_export["Revenue (£)"] + tbc.matrix.loc["BS_Liability_VAT_Payable"]
    cf_export["Operational Cash Outflows (£)"] = pl_export["Opex (£)"]
    
    # Extract the true net transaction movement from the physical cash account delta
    cf_export["Net Cash Movement (£)"] = tbc.matrix.loc["BS_Asset_Cash"]
    cf_export["Cash Reserves (£)"] = cumulative_matrix.loc["BS_Asset_Cash"]

    # Structure 3: BALANCE SHEET ACCRUALS
    bs_export = pd.DataFrame(index=months_labels)
    bs_export["Fixed Assets (£)"] = cumulative_matrix.loc["BS_Asset_Fixed_Assets"]
    bs_export["Accumulated Depreciation (£)"] = cumulative_matrix.loc["BS_Asset_Accumulated_Depreciation"]
    bs_export["Net Book Value (£)"] = bs_export["Fixed Assets (£)"] + bs_export["Accumulated Depreciation (£)"]
    bs_export["Cash Balances (£)"] = cumulative_matrix.loc["BS_Asset_Cash"]
    bs_export["Long Term Debt (£)"] = -cumulative_matrix.loc["BS_Liability_Long_Term_Debt"]
    bs_export["VAT Liability (£)"] = -cumulative_matrix.loc["BS_Liability_VAT_Payable"]
    bs_export["Equity Capital (£)"] = -cumulative_matrix.loc["BS_Equity_Share_Capital"]
    bs_export["Retained Earnings (£)"] = cumulative_matrix.loc["BS_Equity_Retained_Earnings"]

    # Export metrics cleanly
    pl_export.to_csv("STRATA_Forecast_Ledger_Group.xlsx - Profit & Loss.csv")
    cf_export.to_csv("STRATA_Forecast_Ledger_Group.xlsx - Cash Flow Ledger.csv")
    bs_export.to_csv("STRATA_Forecast_Ledger_Group.xlsx - Balance Sheet Accruals.csv")
    
    print("✨ Core Engine Matrix Realigned. True cash and gross receipts fully locked.")

if __name__ == "__main__":
    compile_three_way_forecast("saved_projects/Vanguard-Arena-Expansion.json")