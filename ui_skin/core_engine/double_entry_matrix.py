# ui_skin/core_engine/double_entry_matrix.py

import os
import json
import pandas as pd
import numpy as np

class JournalToken:
    """
    Atomic double-entry transaction voucher. 
    Enforces that every financial event has an equal and opposite reaction.
    """
    def __init__(self, month_label, debit_acct, credit_acct, amount, narrative=""):
        self.month_label = month_label
        self.debit_acct = debit_acct
        self.credit_acct = credit_acct
        self.amount = float(amount)
        self.narrative = narrative

class CommercialTrialBalanceCuboid:
    """
    Hardened multi-period ledger matrix tracking 60 months of financial space.
    Compiles conventional P&L, Cash Flow, and Balance Sheet reports purely from 
    balanced transaction tokens.
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
            "BS_Liability_PAYE_NIC_Payable",
            "BS_Liability_Long_Term_Debt",
            "BS_Equity_Share_Capital",
            "BS_Equity_Retained_Earnings",
            
            # --- PROFIT & LOSS HEADINGS ---
            "PL_Revenue_Gross",
            "PL_COGS",
            "PL_Expense_Overheads",
            "PL_Expense_Payroll",
            "PL_Expense_Depreciation",
            "PL_Expense_Interest"
        ]
        self.months = [f"M{str(i).zfill(2)}" for i in range(1, 61)]
        
        # Seasonality Profiles Matrix (Sum of weights across 12 months must equal 1.0)
        self.seasonality_profiles = {
            "Flat_Linear": [1/12] * 12,
            "Winter_Peak": [0.12, 0.12, 0.10, 0.07, 0.05, 0.05, 0.05, 0.06, 0.08, 0.09, 0.10, 0.11],
            "Summer_Peak": [0.05, 0.05, 0.07, 0.10, 0.12, 0.12, 0.12, 0.11, 0.09, 0.07, 0.05, 0.05]
        }
        self.token_pool = []

    def inject_token(self, month_idx, debit_acct, credit_acct, amount, narrative=""):
        if amount == 0.0:
            return
        if month_idx < 1 or month_idx > 60:
            return  # Prevents out-of-bounds timeline overflows
        
        month_label = f"M{str(month_idx).zfill(2)}"
        if debit_acct not in self.accounts or credit_acct not in self.accounts:
            raise KeyError(f"Bookkeeping Mismatch Fault: Account '{debit_acct}' or '{credit_acct}' does not exist.")
        
        token = JournalToken(month_label, debit_acct, credit_acct, amount, narrative)
        self.token_pool.append(token)

    def extract_monthly_weight(self, profile_name, month_idx):
        profile = self.seasonality_profiles.get(profile_name, self.seasonality_profiles["Flat_Linear"])
        calendar_month_idx = (month_idx - 1) % 12
        return profile[calendar_month_idx]

    def process_simulation(self, runtime_payload):
        self.token_pool = []  # Clear memory vector cache cleanly
        
        # --- 1. PROCESS INITIAL FUNDING RUNWAY & ASSET INJECTIONS ---
        for cap in runtime_payload.get("capital", []):
            m_start = int(cap.get("month", 1))
            val = float(cap.get("value", 0.0))
            c_type = cap.get("type", "")
            
            if c_type == "Equity Capital / Share Premium Injection":
                self.inject_token(m_start, "BS_Asset_Cash", "BS_Equity_Share_Capital", val, "Founder Capital Injection")
            elif c_type == "Commercial Debt / Facility Drawdown":
                self.inject_token(m_start, "BS_Asset_Cash", "BS_Liability_Long_Term_Debt", val, "Debt Drawdown Event")
            elif c_type == "New / Existing Fixed Asset CapEx":
                self.inject_token(m_start, "BS_Asset_Fixed_Assets", "BS_Asset_Cash", val, "Infrastructure Buildout")

        # --- 2. CHRONOLOGICAL TRANSACTIONS PIPELINE HORIZON ---
        for m in range(1, 61):
            
            # A. REVENUE ENGINE: Seasonality & Debtor Credit Terms Realisation
            for sale in runtime_payload.get("sales", []):
                ann_net = float(sale.get("amount", 0.0))
                profile = sale.get("seasonality", "Flat_Linear")
                debtor_days = int(sale.get("debtor_days", 0))
                vat_applicable = sale.get("vat_applicable", True)
                
                monthly_net_revenue = ann_net * self.extract_monthly_weight(profile, m)
                monthly_vat = (monthly_net_revenue * 0.20) if vat_applicable else 0.0
                monthly_gross_revenue = monthly_net_revenue + monthly_vat
                
                self.inject_token(m, "BS_Asset_Debtors", "PL_Revenue_Gross", monthly_net_revenue, "Recognized P&L Revenue")
                if monthly_vat > 0:
                    self.inject_token(m, "BS_Asset_Debtors", "BS_Liability_VAT_Payable", monthly_vat, "Accrued Output VAT")
                
                cash_shift_months = debtor_days // 30
                self.inject_token(m + cash_shift_months, "BS_Asset_Cash", "BS_Asset_Debtors", monthly_gross_revenue, "Debtor Receipt Settled")

            # B. OVERHEADS ENGINE: Creditor Credit Terms Payment Terms
            for opex in runtime_payload.get("opex", []):
                ann_net_cost = float(opex.get("amount", 0.0))
                profile = opex.get("seasonality", "Flat_Linear")
                creditor_days = int(opex.get("creditor_days", 0))
                vat_recoverable = opex.get("vat_applicable", True)
                
                monthly_net_cost = ann_net_cost * self.extract_monthly_weight(profile, m)
                monthly_input_vat = (monthly_net_cost * 0.20) if vat_recoverable else 0.0
                monthly_gross_cost = monthly_net_cost + monthly_input_vat
                
                self.inject_token(m, "PL_Expense_Overheads", "BS_Liability_Creditors", monthly_net_cost, "Recognized Opex Expense")
                if monthly_input_vat > 0:
                    self.inject_token(m, "BS_Liability_VAT_Payable", "BS_Liability_Creditors", monthly_input_vat, "Recoverable Input VAT")
                
                creditor_shift_months = creditor_days // 30
                self.inject_token(m + creditor_shift_months, "BS_Liability_Creditors", "BS_Asset_Cash", monthly_gross_cost, "Supplier Invoice Settled")

            # C. HUMAN CAPITAL PAYROLL ENGINE: Multi-Stage Scheduled Taxes
            for pay in runtime_payload.get("payroll", []):
                ann_gross = float(pay.get("amount", 0.0))
                monthly_gross = ann_gross / 12.0
                
                employer_nic = monthly_gross * 0.138
                paye_employee_nic_deduction = monthly_gross * 0.25
                net_salary_outflow = monthly_gross - paye_employee_nic_deduction
                total_hmrc_liability = paye_employee_nic_deduction + employer_nic
                
                self.inject_token(m, "PL_Expense_Payroll", "BS_Asset_Cash", net_salary_outflow, "Net Monthly Salaries Paid")
                self.inject_token(m, "PL_Expense_Payroll", "BS_Liability_PAYE_NIC_Payable", total_hmrc_liability, "Accrued HMRC Payroll Tax")
                self.inject_token(m + 1, "BS_Liability_PAYE_NIC_Payable", "BS_Asset_Cash", total_hmrc_liability, "HMRC PAYE/NIC Settlement Wave")

            # D. DEPRECIATION MODULE
            current_fa_base = self.compute_running_balance_to_month("BS_Asset_Fixed_Assets", m)
            if current_fa_base > 0.0:
                monthly_depr_charge = (current_fa_base * 0.10) / 12.0
                self.inject_token(m, "PL_Expense_Depreciation", "BS_Asset_Accumulated_Depreciation", monthly_depr_charge, "Asset Depreciation Write-off")

            # E. SCHEDULED HMRC QUARTERLY VAT FLUSH
            if m in [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60]:
                vat_accumulation = self.compute_running_balance_to_month("BS_Liability_VAT_Payable", m)
                if vat_accumulation != 0.0:
                    self.inject_token(m, "BS_Liability_VAT_Payable", "BS_Asset_Cash", vat_accumulation, "Quarterly Consolidated HMRC VAT Settlement")

        return self.compile_financial_statements()

    def compute_running_balance_to_month(self, account_name, month_limit):
        balance = 0.0
        for token in self.token_pool:
            t_m = int(token.month_label.replace("M", ""))
            if t_m <= month_limit:
                if token.debit_acct == account_name: balance += token.amount
                if token.credit_acct == account_name: balance -= token.amount
        return balance

    def compile_financial_statements(self):
        df_pl = pd.DataFrame(0.0, index=["Revenue (£)", "COGS (£)", "Operational Overheads (£)", "Staff Payroll Overhead (£)", "Depreciation (£)", "Net Operating Profit (EBIT)"], columns=self.months)
        df_cf = pd.DataFrame(0.0, index=["Operational Cash Inflows (£)", "Operational Cash Outflows (£)", "Net Cash Movement (£)", "Cash Reserves (£)"], columns=self.months)
        df_bs = pd.DataFrame(0.0, index=["Fixed Infrastructure Assets (£)", "Accumulated Depreciation (£)", "Net Book Value Asset Worth (£)", "Accounts Receivable (Debtors) (£)", "Accounts Payable (Creditors) (£)", "HMRC VAT Reserves Owing (£)", "HMRC PAYE Obligations (£)", "Long Term Facility Debt (£)", "Shareholder Invested Equity (£)", "Retained Earnings Accumulation (£)", "Ledger Verification Checksum Balance"], columns=self.months)

        for m_idx, m_label in enumerate(self.months, start=1):
            for t in self.token_pool:
                if t.month_label == m_label:
                    if t.credit_acct == "PL_Revenue_Gross": df_pl.at["Revenue (£)", m_label] += t.amount
                    if t.debit_acct == "PL_COGS": df_pl.at["COGS (£)", m_label] += t.amount
                    if t.debit_acct == "PL_Expense_Overheads": df_pl.at["Operational Overheads (£)", m_label] += t.amount
                    if t.debit_acct == "PL_Expense_Payroll": df_pl.at["Staff Payroll Overhead (£)", m_label] += t.amount
                    if t.debit_acct == "PL_Expense_Depreciation": df_pl.at["Depreciation (£)", m_label] += t.amount

            df_pl.at["Net Operating Profit (EBIT)", m_label] = (
                df_pl.at["Revenue (£)", m_label] - df_pl.at["COGS (£)", m_label] - 
                df_pl.at["Operational Overheads (£)", m_label] - df_pl.at["Staff Payroll Overhead (£)", m_label] - 
                df_pl.at["Depreciation (£)", m_label]
            )

            for t in self.token_pool:
                if t.month_label == m_label:
                    if t.debit_acct == "BS_Asset_Cash" and t.credit_acct in ["BS_Asset_Debtors", "BS_Equity_Share_Capital", "BS_Liability_Long_Term_Debt"]:
                        df_cf.at["Operational Cash Inflows (£)", m_label] += t.amount
                    if t.credit_acct == "BS_Asset_Cash" and t.debit_acct in ["BS_Liability_Creditors", "BS_Asset_Fixed_Assets", "BS_Liability_PAYE_NIC_Payable", "BS_Expense_Payroll", "BS_Liability_VAT_Payable"]:
                        df_cf.at["Operational Cash Outflows (£)", m_label] += t.amount

            df_cf.at["Net Cash Movement (£)", m_label] = df_cf.at["Operational Cash Inflows (£)", m_label] - df_cf.at["Operational Cash Outflows (£)", m_label]
            df_cf.at["Cash Reserves (£)", m_label] = self.compute_running_balance_to_month("BS_Asset_Cash", m_idx)

            df_bs.at["Fixed Infrastructure Assets (£)", m_label] = self.compute_running_balance_to_month("BS_Asset_Fixed_Assets", m_idx)
            df_bs.at["Accumulated Depreciation (£)", m_label] = -self.compute_running_balance_to_month("BS_Asset_Accumulated_Depreciation", m_idx)
            df_bs.at["Net Book Value Asset Worth (£)", m_label] = df_bs.at["Fixed Infrastructure Assets (£)", m_label] - df_bs.at["Accumulated Depreciation (£)", m_label]
            
            df_bs.at["Accounts Receivable (Debtors) (£)", m_label] = self.compute_running_balance_to_month("BS_Asset_Debtors", m_idx)
            df_bs.at["Accounts Payable (Creditors) (£)", m_label] = -self.compute_running_balance_to_month("BS_Liability_Creditors", m_idx)
            df_bs.at["HMRC VAT Reserves Owing (£)", m_label] = -self.compute_running_balance_to_month("BS_Liability_VAT_Payable", m_idx)
            df_bs.at["HMRC PAYE Obligations (£)", m_label] = -self.compute_running_balance_to_month("BS_Liability_PAYE_NIC_Payable", m_idx)
            df_bs.at["Long Term Facility Debt (£)", m_label] = -self.compute_running_balance_to_month("BS_Liability_Long_Term_Debt", m_idx)
            df_bs.at["Shareholder Invested Equity (£)", m_label] = -self.compute_running_balance_to_month("BS_Equity_Share_Capital", m_idx)
            
            hist_sum = 0.0
            for past_m in self.months[:m_idx]:
                hist_sum += (df_pl.at["Revenue (£)", past_m] - df_pl.at["COGS (£)", past_m] - df_pl.at["Operational Overheads (£)", past_m] - df_pl.at["Staff Payroll Overhead (£)", past_m] - df_pl.at["Depreciation (£)", past_m])
            df_bs.at["Retained Earnings Accumulation (£)", m_label] = hist_sum

            t_as = df_bs.at["Net Book Value Asset Worth (£)", m_label] + df_bs.at["Accounts Receivable (Debtors) (£)", m_label] + df_cf.at["Cash Reserves (£)", m_label]
            t_li = df_bs.at["Accounts Payable (Creditors) (£)", m_label] + df_bs.at["HMRC VAT Reserves Owing (£)", m_label] + df_bs.at["HMRC PAYE Obligations (£)", m_label] + df_bs.at["Long Term Facility Debt (£)", m_label] + df_bs.at["Shareholder Invested Equity (£)", m_label] + df_bs.at["Retained Earnings Accumulation (£)", m_label]
            df_bs.at["Ledger Verification Checksum Balance", m_label] = t_as - t_li

        df_pl.to_csv("STRATA_Clean_Sheet_PL.csv")
        df_cf.to_csv("STRATA_Clean_Sheet_CF.csv")
        df_bs.to_csv("STRATA_Clean_Sheet_BS.csv")
        return True