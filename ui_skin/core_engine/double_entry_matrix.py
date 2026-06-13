# core_engine/double_entry_matrix.py

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
        # Establish structural multi-statement chart of accounts
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
        # Initialize 60-month zero matrix (Rows = Accounts, Columns = 60 Months)
        self.matrix = pd.DataFrame(
            0.0, 
            index=self.accounts, 
            columns=[f"M{str(i).zfill(2)}" for i in range(1, 61)]
        )

    def post_journal(self, month_label, debit_acct, credit_acct, amount):
        """
        Executes a strict double-entry balancing handshake.
        Debits increase asset/expense accounts (Positive values).
        Credits increase liability/equity/revenue accounts (Negative values).
        """
        if amount == 0.0:
            return
            
        if debit_acct not in self.accounts or credit_acct not in self.accounts:
            raise KeyError(f"Ledger Post Defect: Account identifier mismatch.")

        # Atomic double-sided posting
        self.matrix.at[debit_acct, month_label] += amount
        self.matrix.at[credit_acct, month_label] -= amount # Stored as negative representation

    def verify_ledger_integrity(self, month_label):
        """Mathematical safeguard enforcing total balancing rules."""
        checksum = self.matrix[month_label].sum()
        if abs(checksum) > 1e-4:
            raise ValueError(f"CRITICAL BREAKDOWN: Trial balance imbalance of £{checksum:.2f} at {month_label}")
        return True


def compile_three_way_forecast(project_json_path):
    """
    Engine master routine. Reads generic project parameters and processes them 
    chronologically into synchronized financial statements using transactional logic.
    """
    # Initialize the balancing cuboid
    tbc = TrialBalanceCuboid()
    
    # Load raw data baseline arrays
    if not os.path.exists(project_json_path):
        raise FileNotFoundError(f"Missing active workspace dataset file: {project_json_path}")
        
    with open(project_json_path, "r") as pf:
        project_data = json.load(pf)

    # -------------------------------------------------------------------------
    # VECTOR A: CAPITAL INFLOW MATRIX DEPLOYMENT
    # -------------------------------------------------------------------------
    # Post opening corporate funding cushion on day one
    for cap in project_data.get("capital", []):
        val = float(cap.get("value", 0.0))
        m_idx = int(cap.get("month", 1))
        m_label = f"M{str(m_idx).zfill(2)}"
        t_type = cap.get("type", "")
        
        if t_type == "Director / Equity Inflow" or t_type == "New Bank Loan Injection":
            # Debit Current Asset Cash, Credit Share Capital or Debt Liabilities
            credit_target = "BS_Equity_Share_Capital" if "Equity" in t_type else "BS_Liability_Long_Term_Debt"
            tbc.post_journal(m_label, "BS_Asset_Cash", credit_target, val)
        
        elif t_type == "Fixed Asset Purchase":
            # Capitalize asset infrastructure instantly without impacting the P&L overhead line
            tbc.post_journal(m_label, "BS_Asset_Fixed_Assets", "BS_Asset_Cash", val)

    # -------------------------------------------------------------------------
    # VECTOR B: CHRONOLOGICAL TIME-SERIES TRANSACTIONS
    # -------------------------------------------------------------------------
    months_labels = [f"M{str(i).zfill(2)}" for i in range(1, 61)]
    
    # Assume 12-month pre-launch setup phase. Commercial operations launch cleanly on Month 13 (M13).
    for m_idx, m_label in enumerate(months_labels, start=1):
        
        # 1. Map Time-Indexed Revenues (From M13 onwards)
        if m_idx >= 13:
            for sale in project_data.get("sales", []):
                annual_amt = float(sale.get("amount", 0.0))
                monthly_revenue = annual_amt / 12.0
                vat_rate = float(sale.get("vat", 0.20)) # Standard UK VAT defaults to 20%
                
                # Double-entry allocation loop for operational turnover
                tbc.post_journal(m_label, "BS_Asset_Cash", "PL_Revenue_Gross", monthly_revenue)
                
                # Capture rolling VAT liabilities automatically during transactions
                vat_outflow = monthly_revenue * vat_rate
                tbc.post_journal(m_label, "BS_Asset_Cash", "BS_Liability_VAT_Payable", vat_outflow)

        # 2. Map Time-Indexed Expenditures (From M13 onwards)
        if m_idx >= 13:
            for opex in project_data.get("opex", []):
                annual_cost = float(opex.get("amount", 0.0))
                monthly_cost = annual_cost / 12.0
                
                # Double-entry transaction pair for operating overheads
                tbc.post_journal(m_label, "PL_Expense_Overheads", "BS_Asset_Cash", monthly_cost)

        # 3. Dynamic Non-Cash Balance Sheet Adjustments (Depreciation & Taxes)
        # Straight-line depreciation routine for long-term fixed assets
        fixed_assets_pool = tbc.matrix.loc["BS_Asset_Fixed_Assets", :m_label].sum()
        if fixed_assets_pool > 0.0:
            monthly_depr = (fixed_assets_pool * 0.10) / 12.0 # 10% annual straight-line metric
            tbc.post_journal(m_label, "PL_Expense_Depreciation", "BS_Asset_Accumulated_Depreciation", monthly_depr)

        # Enforce chronological ledger verification check at every milestone step
        tbc.verify_ledger_integrity(m_label)

    # -------------------------------------------------------------------------
    # TRANSLATION LAYER: HYDRATE THE THREE FORECAST OUTPUT MATRIX PAPERS
    # -------------------------------------------------------------------------
    # Generate cumulative rolling tracking sheets
    rolling_matrix = tbc.matrix.copy()
    for col_idx in range(1, 60):
        prev_col = months_labels[col_idx - 1]
        curr_col = months_labels[col_idx]
        
        # Accumulate balance sheet asset and liability balances across columns
        for acct in tbc.accounts:
            if acct.startswith("BS_"):
                rolling_matrix.at[acct, curr_col] += rolling_matrix.at[acct, prev_col]

    # Structure 1: PROFIT & LOSS STATEMENT EXPORT
    pl_export = pd.DataFrame(index=months_labels)
    pl_export["Revenue (£)"] = -tbc.matrix.loc["PL_Revenue_Gross"] # Reverse credit representation
    pl_export["COGS (£)"] = tbc.matrix.loc["PL_COGS"]
    pl_export["Opex (£)"] = tbc.matrix.loc["PL_Expense_Overheads"]
    pl_export["Depreciation (£)"] = tbc.matrix.loc["PL_Expense_Depreciation"]
    pl_export["EBIT (£)"] = pl_export["Revenue (£)"] - pl_export["COGS (£)"] - pl_export["Opex (£)"] - pl_export["Depreciation (£)"]
    pl_export["Interest Expense (£)"] = tbc.matrix.loc["PL_Expense_Interest"]
    pl_export["Tax Expense (£)"] = tbc.matrix.loc["PL_Expense_Taxation"]
    
    # Structure 2: CASH FLOW LEDGER EXPORT
    cf_export = pd.DataFrame(index=months_labels)
    cf_export["Operational Cash Inflows (£)"] = -tbc.matrix.loc["PL_Revenue_Gross"]
    cf_export["Operational Cash Outflows (£)"] = tbc.matrix.loc["PL_Expense_Overheads"]
    cf_export["Net Cash Movement (£)"] = cf_export["Operational Cash Inflows (£)"] - cf_export["Operational Cash Outflows (£)"]
    cf_export["Cash Reserves (£)"] = rolling_matrix.loc["BS_Asset_Cash"]

    # Structure 3: BALANCE SHEET ACCRUALS EXPORT
    bs_export = pd.DataFrame(index=months_labels)
    bs_export["Fixed Assets (£)"] = rolling_matrix.loc["BS_Asset_Fixed_Assets"]
    bs_export["Accumulated Depreciation (£)"] = rolling_matrix.loc["BS_Asset_Accumulated_Depreciation"]
    bs_export["Net Book Value (£)"] = bs_export["Fixed Assets (£)"] + bs_export["Accumulated Depreciation (£)"]
    bs_export["Cash Balances (£)"] = rolling_matrix.loc["BS_Asset_Cash"]
    bs_export["Long Term Debt (£)"] = -rolling_matrix.loc["BS_Liability_Long_Term_Debt"]
    bs_export["VAT Liability (£)"] = -rolling_matrix.loc["BS_Liability_VAT_Payable"]
    bs_export["Equity Capital (£)"] = -rolling_matrix.loc["BS_Equity_Share_Capital"]

    # Commit output sheets cleanly to disk caches
    pl_export.to_csv("STRATA_Forecast_Ledger_Group.xlsx - Profit & Loss.csv")
    cf_export.to_csv("STRATA_Forecast_Ledger_Group.xlsx - Cash Flow Ledger.csv")
    bs_export.to_csv("STRATA_Forecast_Ledger_Group.xlsx - Balance Sheet Accruals.csv")
    
    print("✨ Dynamic Three-Way Double-Entry Run Successful. Output repository files hydrated.")

if __name__ == "__main__":
    # Internal validation harness test
    compile_three_way_forecast("saved_projects/Indoor-Padel-Pure-PDF-Baseline.json")