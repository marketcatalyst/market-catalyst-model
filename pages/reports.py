# pages/reports.py
# STRATA SUITE PRODUCTION ENGINE // THREE-WAY REPORTING CANVAS v6.8.1-PRODUCTION

import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

# Enforce secure routing context backup check
if not st.session_state.get("authenticated") or not st.session_state.get(
    "onboarding_complete"
):
    st.warning("⚠️ **Security Intercept:** Route session token context not cleared.")
    st.page_link("home.py", label="↩️ Return to Access Gateway Portal")
    st.stop()

# Import the trial balance simulation block dynamically from app file context
from pages.app import CommercialTrialBalanceCuboid

st.title("📊 STRATA // Performance & Reporting Tab")
st.page_link("pages/app.py", label="✍️ Return to Parameter Input Workspace")
st.markdown("---")

# Execute background trial balance processing cube to refresh active states
cuboid_engine = CommercialTrialBalanceCuboid()
cuboid_engine.run_simulation_engine(
    st.session_state.get(
        "active_data",
        {
            "sales": [],
            "opex": [],
            "payroll": [],
            "financed_assets": [],
            "outright_capex": [],
            "equity_funding": [],
        },
    )
)

# 🚀 RESOLVED PYLANCE BLOCK: Corrected to standard FileNotFoundError catch-all
try:
    df_pl = pd.read_csv("STRATA_v5_PL.csv", index_col=0)
    df_cf = pd.read_csv("STRATA_v5_CF.csv", index_col=0)
    df_bs = pd.read_csv("STRATA_v5_BS.csv", index_col=0)
except FileNotFoundError:
    st.error(
        "🎰 **Ledger Processing Exception:** Simulation engine failed to export operational streams. Please ensure baseline data is mapped."
    )
    st.stop()

# =========================================================================
# 👑 EXECUTIVE KPIs
# =========================================================================
closing_cash_array = df_cf.loc["Closing Bank Cash Reserves (£)"].astype(float).values
peak_cash = closing_cash_array.max()
lowest_cash = closing_cash_array.min()
y5_worth = df_bs.loc["Retained Earnings Accumulation (£)", "M60"]

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Peak Cash Runway Worth", f"£{peak_cash:,.2f}")
kpi2.metric(
    "Max Venture Risk Valley",
    f"£{lowest_cash:,.2f}",
    delta="LIQUID BUFFER" if lowest_cash > 0 else "OVERDRAWN INVERSION",
    delta_color="normal" if lowest_cash > 0 else "inverse",
)
kpi3.metric("Year 5 Horizon Value", f"£{y5_worth:,.2f}")

st.markdown("---")

# =========================================================================
# 📥 EXPORT MATRIX TRIGGERS (CSV & SELF-CONTAINED PRINT EXPEDITION)
# =========================================================================
st.subheader("📥 Export Financial Report Summary Pack")
exp1, exp2, exp3, exp4 = st.columns(4)
with exp1:
    st.download_button(
        "Export P&L (CSV)",
        df_pl.to_csv().encode("utf-8"),
        "STRATA_PL.csv",
        "text/csv",
        use_container_width=True,
    )
with exp2:
    st.download_button(
        "Export Cash Flow (CSV)",
        df_cf.to_csv().encode("utf-8"),
        "STRATA_CF.csv",
        "text/csv",
        use_container_width=True,
    )
with exp3:
    st.download_button(
        "Export Balance Sheet (CSV)",
        df_bs.to_csv().encode("utf-8"),
        "STRATA_BS.csv",
        "text/csv",
        use_container_width=True,
    )
with exp4:
    html_pack = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
            h1 {{ color: #1e3a8a; border-bottom: 2px solid #1e3a8a; }}
            .card {{ background: #f1f5f9; padding: 20px; border-radius: 6px; margin: 20px 0; }}
        </style>
    </head>
    <body onload="window.print()">
        <h1>🏛️ STRATA Corporate Presentation Pack</h1>
        <p><strong>Scenario Instance Reference Trace:</strong> {st.session_state.get('active_project_name', 'Unsaved_Draft_Scenario')}</p>
        <div class="card">
            <h2>📈 Forecast Horizon Milestones</h2>
            <p><strong>Maximum Liquid Cash Run Peak:</strong> £{peak_cash:,.2f}</p>
            <p><strong>Maximum Capital Exposure Valley:</strong> £{lowest_cash:,.2f}</p>
            <p><strong>Year 5 Retained Asset Worth Capitalization:</strong> £{y5_worth:,.2f}</p>
        </div>
    </body>
    </html>
    """
    st.download_button(
        "🏆 Download HTML Print Pack",
        html_pack.encode("utf-8"),
        "STRATA_Executive_Pack.html",
        "text/html",
        use_container_width=True,
    )

st.markdown("---")

# Horizon display accounting window window slicing filters
horiz = st.selectbox(
    "Analytical Accounting Window Filter:",
    [
        "Year 1 Horizon View (M00 - M12)",
        "Year 2 Horizon View (M13 - M24)",
        "Year 3 Horizon View (M25 - M36)",
        "Full 5-Year Comprehensive Asset Track (M00 - M60)",
    ],
)
if "Year 1" in horiz:
    targets = [f"M{str(i).zfill(2)}" for i in range(0, 13)]
elif "Year 2" in horiz:
    targets = [f"M{str(i).zfill(2)}" for i in range(13, 25)]
elif "Year 3" in horiz:
    targets = [f"M{str(i).zfill(2)}" for i in range(25, 37)]
else:
    targets = [f"M{str(i).zfill(2)}" for i in range(0, 61)]

t1, t2, t3 = st.tabs(
    [
        "📈 Master Ledgers",
        "🚜 WinForecast Asset Depreciation Ledger",
        "🏦 Loan Amortisation Schedule",
    ]
)

with t1:
    st.markdown("#### Profit & Loss Statement")
    st.dataframe(df_pl[targets].style.format("{:,.2f}"), use_container_width=True)
    st.markdown("#### Cash Flow Statement")
    st.dataframe(df_cf[targets].style.format("{:,.2f}"), use_container_width=True)
    st.markdown("#### Balance Sheet Statement")
    st.dataframe(df_bs[targets].style.format("{:,.2f}"), use_container_width=True)

with t2:
    st.markdown("### 🚜 Time-Phased Fixed Asset Value Track")
    active_sic = st.session_state.get(
        "sic_profile", {"macro_depreciation_baseline": 0.10}
    )
    fa_rows = []
    for outright in st.session_state.get("active_data", {}).get("outright_capex", []):
        fa_rows.append(
            {
                "Asset Item": outright["name"],
                "Type": "Direct Purchase",
                "Value": outright["amount"],
                "Month": int(outright["month"]),
            }
        )
    for fin in st.session_state.get("active_data", {}).get("financed_assets", []):
        fa_rows.append(
            {
                "Asset Item": fin["name"],
                "Type": "Financed HP",
                "Value": fin["amount"],
                "Month": int(fin["month"]),
            }
        )

    if fa_rows:
        ledger_rows = []
        for item in fa_rows:
            v_rec = {
                "Asset Item": item["Asset Item"],
                "Metric Category": "Net Book Value (£)",
            }
            running_val = 0.0
            for m in range(0, 61):
                m_lbl = f"M{str(m).zfill(2)}"
                if m == item["Month"]:
                    running_val = item["Value"]
                if m >= item["Month"] and running_val > 0:
                    running_val = max(
                        0.0,
                        running_val
                        - (
                            (item["Value"] * active_sic["macro_depreciation_baseline"])
                            / 12.0
                        ),
                    )
                v_rec[m_lbl] = running_val
            ledger_rows.append(v_rec)
        st.dataframe(
            pd.DataFrame(ledger_rows)
            .set_index(["Asset Item", "Metric Category"])[targets]
            .style.format("{:,.2f}"),
            use_container_width=True,
        )
    else:
        st.info("No fixed assets mapped inside active parameter arrays.")

with t3:
    st.markdown("### 🏦 Chronological Liability Allocation Ledger")
    if st.session_state.get("active_data", {}).get("financed_assets"):
        loan_rows = []
        for fin in st.session_state["active_data"]["financed_assets"]:
            m_start = int(fin["month"])
            fin_bal = float(fin["amount"]) * (
                1.0 - (float(fin.get("deposit_pct", 10.0)) / 100.0)
            )
            term = int(fin["term_months"])
            monthly_principal = fin_bal / term

            bal_rec = {"Facility": fin["name"], "Metric": "Total Outstanding (£)"}
            st_rec = {
                "Facility": fin["name"],
                "Metric": "Current Liabilities (<12m) (£)",
            }
            lt_rec = {"Facility": fin["name"], "Metric": "Non-Current Debt (>1yr) (£)"}

            running_debt = 0.0
            for m in range(0, 61):
                m_lbl = f"M{str(m).zfill(2)}"
                if m == m_start:
                    running_debt = fin_bal
                if m >= m_start and running_debt > 0:
                    elapsed = m - m_start
                    st_debt = (
                        min(running_debt, monthly_principal * 12)
                        if elapsed < term
                        else 0.0
                    )
                    bal_rec[m_lbl] = running_debt
                    st_rec[m_lbl] = st_debt
                    lt_rec[m_lbl] = max(0.0, running_debt - st_debt)
                    running_debt = max(0.0, running_debt - monthly_principal)
                else:
                    bal_rec[m_lbl] = running_debt
                    st_rec[m_lbl] = 0.0
                    lt_rec[m_lbl] = 0.0
            loan_rows.extend([bal_rec, st_rec, lt_rec])
        st.dataframe(
            pd.DataFrame(loan_rows)
            .set_index(["Facility", "Metric"])[targets]
            .style.format("{:,.2f}"),
            use_container_width=True,
        )
    else:
        st.info("No active liabilities found.")
