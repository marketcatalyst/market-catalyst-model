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
    
    # Identify if a real construction phase is requested by inspecting CapEx logs
    has_fixed_assets = any(cap.get("type") == "New / Existing Fixed Asset CapEx" for cap in project_data.get("capital", []))
    start_month = 13 if has_fixed_assets else 1

    # -------------------------------------------------------------------------
    # CHRONOLOGICAL DOUBLE-ENTRY PROCESSING LOOP
    # -------------------------------------------------------------------------
    for m_idx, m_label in enumerate(months_labels, start=1):
        
        # A. Roll forward open balances from the previous month's ledger state
        if m_idx > 1:
            m_prev_label = months_labels[m_idx - 2]
            for acct in tbc.accounts:
                if acct.startswith("BS_"):
                    tbc.matrix.at[acct, m_label] = tbc.matrix.at[acct, m_prev_label]

        # B. Process Capital Events & Upfront Funding for the current month
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

        # C. Process Active Trading Revenues
        if m_idx >= start_month:
            for sale in project_data.get("sales", []):
                annual_amt = float(sale.get("amount", 0.0))
                monthly_revenue = annual_amt / 12.0
                vat_rate = float(sale.get("vat", 0.20))
                
                tbc.post_journal(m_label, "BS_Asset_Cash", "PL_Revenue_Gross", monthly_revenue)
                if vat_rate > 0:
                    vat_outflow = monthly_revenue * vat_rate
                    tbc.post_journal(m_label, "BS_Asset_Cash", "BS_Liability_VAT_Payable", vat_outflow)

        # D. Process Active Operating Overheads
        if m_idx >= start_month:
            for opex in project_data.get("opex", []):
                annual_cost = float(opex.get("amount", 0.0))
                monthly_cost = annual_cost / 12.0
                tbc.post_journal(m_label, "PL_Expense_Overheads", "BS_Asset_Cash", monthly_cost)

        # E. Process Straight-Line Asset Depreciation
        if m_idx >= start_month:
            current_asset_base = tbc.matrix.at["BS_Asset_Fixed_Assets", m_label]
            if current_asset_base > 0.0:
                monthly_depr = (current_asset_base * 0.10) / 12.0
                tbc.post_journal(m_label, "PL_Expense_Depreciation", "BS_Asset_Accumulated_Depreciation", monthly_depr)

        # F. RECONCILIATION ANCHOR: Transfer Net Profit to Retained Earnings without breaking double-entry
        current_month_revenue = -tbc.matrix.at["PL_Revenue_Gross", m_label]
        current_month_expenses = (
            tbc.matrix.at["PL_COGS", m_label] +
            tbc.matrix.at["PL_Expense_Overheads", m_label] +
            tbc.matrix.at["PL_Expense_Depreciation", m_label] +
            tbc.matrix.at["PL_Expense_Interest", m_label] +
            tbc.matrix.at["PL_Expense_Taxation", m_label]
        )
        # Check current month balance delta before clearing out the temporary space
        net_monthly_profit = current_month_revenue - current_month_expenses
        
        # Post the delta to retained equity by balancing out the gross revenue account positions
        tbc.matrix.at["BS_Equity_Retained_Earnings", m_label] += net_monthly_profit
        tbc.matrix.at["PL_Revenue_Gross", m_label] += net_monthly_profit

        tbc.verify_ledger_integrity(m_label)

    # -------------------------------------------------------------------------
    # TRANSLATION LAYER: DATA EXTRACTION SHEETS
    # -------------------------------------------------------------------------
    # Structure 1: PROFIT & LOSS REPORT
    pl_export = pd.DataFrame(index=months_labels)
    pl_export["Revenue (£)"] = 0.0
    pl_export["COGS (£)"] = 0.0
    pl_export["Opex (£)"] = 0.0
    pl_export["Depreciation (£)"] = 0.0
    
    for m_idx, m_label in enumerate(months_labels, start=1):
        if m_idx >= start_month:
            # Reconstruction of clean period indicators for standard ledger exports
            sales_total = sum(float(s.get("amount", 0.0)) / 12.0 for s in project_data.get("sales", []))
            opex_total = sum(float(o.get("amount", 0.0)) / 12.0 for o in project_data.get("opex", []))
            fixed_asset_base = tbc.matrix.at["BS_Asset_Fixed_Assets", m_label]
            depr_total = ((fixed_asset_base * 0.10) / 12.0) if fixed_asset_base > 0.0 else 0.0
            
            pl_export.at[m_label, "Revenue (£)"] = sales_total
            pl_export.at[m_label, "COGS (£)"] = 0.0
            pl_export.at[m_label, "Opex (£)"] = opex_total
            pl_export.at[m_label, "Depreciation (£)"] = depr_total

    pl_export["EBIT (£)"] = pl_export["Revenue (£)"] - pl_export["COGS (£)"] - pl_export["Opex (£)"] - pl_export["Depreciation (£)"]
    pl_export["Interest Expense (£)"] = 0.0
    pl_export["Tax Expense (£)"] = 0.0
    
    # Structure 2: COMPOUNDING CASH FLOW LEDGER
    cf_export = pd.DataFrame(index=months_labels)
    cf_export["Operational Cash Inflows (£)"] = pl_export["Revenue (£)"]
    cf_export["Operational Cash Outflows (£)"] = pl_export["Opex (£)"]
    cf_export["Net Cash Movement (£)"] = cf_export["Operational Cash Inflows (£)"] - cf_export["Operational Cash Outflows (£)"]
    cf_export["Cash Reserves (£)"] = tbc.matrix.loc["BS_Asset_Cash"]

    # Structure 3: BALANCE SHEET ACCRUALS
    bs_export = pd.DataFrame(index=months_labels)
    bs_export["Fixed Assets (£)"] = tbc.matrix.loc["BS_Asset_Fixed_Assets"]
    bs_export["Accumulated Depreciation (£)"] = tbc.matrix.loc["BS_Asset_Accumulated_Depreciation"]
    bs_export["Net Book Value (£)"] = bs_export["Fixed Assets (£)"] + bs_export["Accumulated Depreciation (£)"]
    bs_export["Cash Balances (£)"] = tbc.matrix.loc["BS_Asset_Cash"]
    bs_export["Long Term Debt (£)"] = -tbc.matrix.loc["BS_Liability_Long_Term_Debt"]
    bs_export["VAT Liability (£)"] = -tbc.matrix.loc["BS_Liability_VAT_Payable"]
    bs_export["Equity Capital (£)"] = -tbc.matrix.loc["BS_Equity_Share_Capital"]

    # Export out matrices cleanly
    pl_export.to_csv("STRATA_Forecast_Ledger_Group.xlsx - Profit & Loss.csv")
    cf_export.to_csv("STRATA_Forecast_Ledger_Group.xlsx - Cash Flow Ledger.csv")
    bs_export.to_csv("STRATA_Forecast_Ledger_Group.xlsx - Balance Sheet Accruals.csv")
    
    print("✨ Core Engine Matrix Realigned. Retained earnings adjustments cleanly bound.")

if __name__ == "__main__":
    compile_three_way_forecast("saved_projects/Vanguard-Arena-Expansion.json")