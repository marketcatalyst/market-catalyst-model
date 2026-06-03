# ui_skin/pages/2_🔮_sandbox.py
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Stewardship Sandbox")

st.title("🔮 Capital Stewardship Sandbox")
st.caption("Path B: Tactical Optimization Challenges & Cost-of-Inaction Simulators")
st.markdown("---")

# --- 1. SESSION STATE FALLBACK CHECK ---
# Ensure the sandbox doesn't crash if a user navigates here before clicking submit on page 1
if "baseline_inputs" not in st.session_state:
    st.warning("⚠️ No active ingestion data detected. Seeding sandbox with baseline AHOTG corporate data.")
    st.session_state["baseline_inputs"] = {
        "nominal_seasonal_sales_base": 120000.0,
        "nominal_cogs_base": 48000.0,
        "opening_cash_balance": 69488.0,
        "opening_long_term_debt": 147110.0
    }

base = st.session_state["baseline_inputs"]
raw_sales = base.get("nominal_seasonal_sales_base", 120000.0) * 2

# --- 2. LAYOUT: TWO-COLUMN STRATEGIC ARENA ---
col_controls, col_charts = st.columns([1, 1.2])

with col_controls:
    st.subheader("🏆 Strategic Stewardship Levers")
    st.markdown("Toggle these advanced corporate maneuvers to observe their compounding impact on cash runway and tax optimization.")
    
    # --- LEVER 1: INVOICE DISCOUNTING ---
    with st.expander("🔗 Asset-Backed Lending (Invoice Discounting)", expanded=True):
        id_enabled = st.checkbox("Enable Invoice Discounting Facility", value=False)
        if id_enabled:
            id_mode = st.radio(
                "Drawdown Strategy Strategy",
                options=["Defensive Minimum (Just-in-Time)", "Maximum Extraction"],
                help="Minimum draws only what is required to meet monthly obligations, preserving headroom."
            )
            
            # Parametric adjustments
            advance_rate = st.slider("Invoice Advance Rate (%)", min_value=50, max_value=95, value=80)
            dilution_haircut = st.slider("Expected Credit Note/Dilution Haircut (%)", min_value=0, max_value=15, value=3)
            
            # Early Settlement Arbitrage Switch
            supplier_discount = st.checkbox("Utilize Headroom for 2% Early Supplier Settlement Discounts", value=False)
        else:
            id_mode = "None"
            advance_rate = 0
            supplier_discount = False

    # --- LEVER 2: EV HP TAX SHIELD ---
    with st.expander("⚡ Green Fleet CapEx (Tax Shielding)", expanded=False):
        ev_enabled = st.checkbox("Execute £50,000 Electric Vehicle Fleet Rollout", value=False)
        if ev_enabled:
            st.info("💡 Structure: 5% Deposit (£2,500) via HP. Triggers 100% First-Year Capital Allowances (FYA).")
            deposit_source = st.selectbox("Fund Deposit Via:", ["Clearing Bank Cash", "Invoice Discounting Headroom"] if id_enabled else ["Clearing Bank Cash"])

    # --- LEVER 3: VAT SCHEME OPTIMIZATION ---
    with st.expander("📊 HMRC VAT Scheme Selection", expanded=False):
        vat_scheme = st.radio(
            "Select VAT Accounting Framework",
            options=["Standard Invoice Accounting", "HMRC Cash Accounting Scheme"],
            help="Cash accounting allows you to delay output VAT liability until the customer physically settles their invoice."
        )

# --- 3. THE LIVE CALCULATION MATRIX (COL 2) ---
with col_charts:
    st.subheader("📊 Dynamic Impact Metrics")
    
    # A. PREDICTIVE VAT THRESHOLD MONITOR
    st.markdown("### **1. Compliance Ceiling Monitor**")
    rolling_turnover_projection = raw_sales * 1.10 # Assuming standard scaling growth
    
    if vat_scheme == "HMRC Cash Accounting Scheme":
        if rolling_turnover_projection > 1600000.0:
            st.error(f"""
            **⚠️ CRITICAL THRESHOLD BREACH DETECTED**  
            Your projected rolling 12-month taxable turnover of **£{rolling_turnover_projection:,.2f}** exceeds the statutory HMRC Cash Accounting ceiling of **£1,600,000**.  
            *Action Matrix:* The simulation forces a structural transition back to Standard Invoice VAT in Month 25, creating a one-time working capital cash contraction.
            """)
        elif rolling_turnover_projection > 1350000.0:
            st.warning(f"**⚠️ Entry Boundary Warning:** Rolling sales (£{rolling_turnover_projection:,.2f}) are past the initial £1.35m entry limit. New enrollment is blocked, but existing coverage is active until £1.6m.")
        else:
            st.success(f"✅ **Cash Accounting Compliant:** Projected rolling sales (£{rolling_turnover_projection:,.2f}) sit comfortably inside safe statutory limits.")
    else:
        st.caption("Standard Invoice Accounting selected. No turnover ceiling restrictions apply.")

    st.markdown("---")

    # B. ARBITRAGE AND HEADROOM CARD PRESENTATIONS
    st.markdown("### **2. Liquidity Runway & Headroom Indicators**")
    
    # Calculate simulated available debtor pool from AR entries
    simulated_ar = base.get("opening_accounts_receivable", 44886.0)
    eligible_pool = simulated_ar * (1 - (dilution_haircut / 100 if id_enabled else 0))
    max_facility_limit = eligible_pool * (advance_rate / 100)
    
    metric_col1, metric_col2 = st.columns(2)
    
    with metric_col1:
        if id_enabled:
            if id_mode == "Defensive Minimum (Just-in-Time)":
                simulated_draw = 15000.0  # Simulated defensive requirement
                headroom = max_facility_limit - simulated_draw
                st.metric(label="Active Facility Headroom (Phantom Liquidity)", value=f"£{headroom:,.2f}", delta="Protected Buffer")
            else:
                st.metric(label="Active Facility Headroom", value="£0.00", delta="-100% Fully Extracted", delta_color="inverse")
        else:
            st.metric(label="Active Facility Headroom", value="£0.00", help="Enable Invoice Discounting to unlock credit facility tracking.")

    with metric_col2:
        if supplier_discount and id_enabled:
            net_arbitrage_savings = (base.get("nominal_cogs_base", 48000.0) * 0.02) - (max_facility_limit * 0.0075)
            st.metric(label="Net Supplier Arbitrage Yield", value=f"+£{net_arbitrage_savings:,.2f}", delta="Net Capital Saved")
        else:
            st.metric(label="Net Supplier Arbitrage Yield", value="£0.00", help="Activate early payment discount toggle to simulate gross profit margin preservation.")

    st.markdown("---")

    # C. THE TAX SHIELD CHRONOLOGY
    st.markdown("### **3. Delayed Corporation Tax Chronology**")
    if ev_enabled:
        st.success("🏆 **EV Stewardship Challenge Activated!**")
        st.markdown(f"""
        *   **Month of Purchase:** Cash Account reflects a **-£2,500** initial layout for the {deposit_source.lower()}.
        *   **Month 12 (Year End):** 100% First-Year Allowance completely shields £50,000 from taxable accounting profit.
        *   **Month 21 (9 Months & 1 Day Post Year-End):** Your statutory Corporation Tax payment to HMRC drops cleanly by **£12,500**.
        *   **Net Capital Stewardship Bonus:** **+£10,000 liquid cash advantage** realized at the exact moment tax falls due compared to your baseline timeline.
        """)
    else:
        st.info("Challenge Opportunity: Enable the Green Fleet lever to observe how matching low-deposit HP contracts with accelerated allowances creates delayed liquid cash windfalls.")