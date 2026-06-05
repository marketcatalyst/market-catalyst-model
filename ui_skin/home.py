import streamlit as st

st.set_page_config(page_title="STRATA - Financial Intelligence Platform", page_icon="🏢", layout="wide")

st.title("🏢 STRATA Financial Intelligence Platform")
st.caption("Enterprise three-way financial forecasting model environment modeled on Sage WinForecast parameters.")

# =============================================================================
# 🛡️ FLOW STATE TRACKING INITIALIZATION
# =============================================================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "project_initialized" not in st.session_state:
    st.session_state["project_initialized"] = False

# =============================================================================
# 🔑 STAGE 1: THE WELCOME & ACCESS CONTROL ROOM
# =============================================================================
if not st.session_state["authenticated"]:
    st.subheader("🔒 Platform Authentication")
    st.caption("Please access or provision your secure corporate modeling workspace environment.")
    
    auth_col1, auth_col2 = st.columns(2)
    with auth_col1:
        username = st.text_input("User ID / Email Address", placeholder="e.g., manager@company.com")
        password = st.text_input("Secure Password", type="password", placeholder="••••••••")
    with auth_col2:
        business_name = st.text_input("Registered Corporate/Trading Name", placeholder="e.g., AHOGT Group Ltd")
        entity_type = st.selectbox("Operating Structure Framework", ["Limited Company (UK)", "Partnership", "Sole Trader", "LLC / Corp (US)"])

    if st.button("🚀 Access Modeling Terminal", type="primary"):
        if username and password and business_name:
            st.session_state["authenticated"] = True
            st.session_state["user_profile"] = {"username": username, "business_name": business_name, "entity": entity_type}
            st.rerun()
        else:
            st.error("Access Denied: Please provide valid credentials and a registered business entity name.")

# =============================================================================
# ⚙️ STAGE 2: THE WINFORECAST CONFIGURATION WIZARD
# =============================================================================
elif st.session_state["authenticated"] and not st.session_state["project_initialized"]:
    st.subheader(f"🛠️ Project Configuration Wizard: {st.session_state['user_profile']['business_name']}")
    st.caption("Replicating standard Sage WinForecast ledger constraints to structure your three-way relational database.")

    with st.form("winforecast_setup_wizard"):
        config_col1, config_col2 = st.columns(2)
        
        with config_col1:
            project_title = st.text_input("Forecast Project Model Name", value="Core Strategy Expansion Plan")
            forecast_extent_years = st.slider("Forecast Extent Framework Horizon (Years)", min_value=1, max_value=5, value=5)
            reporting_currency = st.selectbox("Reporting Base Currency Unit", ["GBP (£)", "EUR (€)", "USD ($)", "CAD ($)"])
            
        with config_col2:
            financial_year_end_month = st.selectbox(
                "Financial Year End Target Month",
                ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
                index=11
            )
            tax_regime = st.selectbox("Statutory Corporate Tax Framework", ["UK Corporation Tax (19%)", "US Federal Scale", "Exempt / Sovereign Margin"])
            gross_margin_baseline = st.slider("Target Base Production Gross Profit Coefficient (%)", min_value=10, max_value=90, value=30)

        # Base Financial Opening Seeds Form Row
        st.markdown("##### ⚖️ Statement Opening Balance Seeds")
        seed_col1, seed_col2, seed_col3 = st.columns(3)
        with seed_col1:
            opening_cash = st.number_input("Liquid Cash held at Bank (£)", value=69488.00, step=1000.00)
        with seed_col2:
            opening_ar = st.number_input("Outstanding Trade Debtors / Accounts Receivable (£)", value=44886.00, step=1000.00)
        with seed_col3:
            opening_fa = st.number_input("Fixed Asset Carrying Book Value (NBV) (£)", value=531385.00, step=5000.00)

        submit_setup = st.form_submit_button("🏁 Compile Relational Three-Way Database Structure", type="primary")
        
        if submit_setup:
            # Seed our production targets dynamically right into the system session state arrays
            st.session_state["baseline_inputs"] = {
                "opening_cash_balance": opening_cash,
                "opening_fixed_assets_nbv": opening_fa,
                "opening_accounts_receivable": opening_ar,
                "opening_accounts_payable": 8000.00,
                "opening_long_term_debt": 341001.00,
                "opening_inventory_balance": 12000.00,
                
                "y1_revenue_target": 6528886.00,
                "y2_revenue_target": 10805679.00,
                "y3_revenue_target": 12126469.00,
                "monthly_overhead_baseline": 18575.00,
                "base_production_cogs_pct": 0.696,
                
                "y1_monthly_revenue_curve": [
                    249310.00, 356310.00, 385200.00, 404460.00, 447260.00, 470800.00,
                    508785.00, 707525.00, 763067.00, 750127.00, 750025.00, 736017.00
                ],
                "historical_cash_flow_vector": [
                    30534.00, 55816.00, 57184.00, 107551.00, 112372.00, 313144.00, 
                    133467.00, 210615.00, 232118.00, 373846.00, 335510.00, 313760.00,
                    543297.00, 614240.00, 718038.00, 920317.00, 1044788.00, 1165807.00,
                    1382623.00, 1491213.00, 1617929.00, 1808973.00, 1887158.00, 1946084.00,
                    2176989.00, 2265357.00, 2390615.00, 2623144.00, 2772046.00, 2917012.00,
                    3166164.00, 3296896.00, 3448372.00, 3668049.00, 3763998.00, 3837934.00,
                    4068140.00, 4156980.00, 4295761.00, 4567153.00, 4732985.00, 4894313.00,
                    5184725.00, 5329768.00, 5498544.00, 5755233.00, 5860489.00, 5940553.00,
                    6150000.00, 6340000.00, 6520000.00, 6710000.00, 6920000.00, 7120000.00,
                    7320000.00, 7540000.00, 7750000.00, 7940000.00, 8120000.00, 8244000.00
                ],
                "historical_fa_nbv_vector": [755746.00, 661095.00, 477464.00, 302254.00, 150000.00],
                "historical_debt_vector": [341001.00, 237330.00, 11001.00, 0.0, 0.0],
                "historical_ar_vector": [320000.00, 352000.00, 387200.00, 442957.00, 480000.00],
                "historical_inventory_vector": [12000.00, 12000.00, 12000.00, 12000.00, 12000.00],
                "meta_project_name": project_title,
                "meta_horizon_years": forecast_extent_years,
                "meta_year_end": financial_year_end_month
            }
            st.session_state["project_initialized"] = True
            st.success("Relational three-way accounting database constructed cleanly!")
            st.rerun()

# =============================================================================
# 📊 STAGE 3: THE MAIN TERMINAL OVERVIEW
# =============================================================================
else:
    st.sidebar.markdown(f"**🏢 Workspace:** {st.session_state['user_profile']['business_name']}")
    st.sidebar.markdown(f"**📂 Model:** {st.session_state['baseline_inputs']['meta_project_name']}")
    st.sidebar.markdown(f"**📅 Horizon:** {st.session_state['baseline_inputs']['meta_horizon_years']} Years ({st.session_state['baseline_inputs']['meta_year_end']} YE)")
    
    if st.sidebar.button("🔄 Reset / Load Alternative Project"):
        st.session_state["project_initialized"] = False
        st.session_state["authenticated"] = False
        st.rerun()
        
    st.success("✨ **STRATA Engine Core Active:** Navigation terminal initialized successfully.")
    st.info("👈 Use the left sidebar menu to navigate to the **Financial Forecast** tab to view your three-way ledger reports.")