# ui_skin/core_engine/project_registry.py

def get_user_projects(username: str) -> dict:
    """
    Fetches all scenarios and project entries linked to a verified user profile.
    """
    ahotg_y2_baseline = {
        "opening_cash_balance": 69488.00,
        "opening_fixed_assets_nbv": 531385.00,
        "admin_overheads_monthly": 18575.00,
        "base_monthly_gross_wages": 12000.00,
        "directors_salaries_monthly": 5150.00,
        "pension_opt_out": False,
        "y1_monthly_revenue_curve": [249310.0, 356310.0, 385200.0, 404460.0, 447260.0, 470800.0, 508785.0, 707525.0, 763067.0, 750127.0, 750025.0, 736017.0],
        "debt_facilities": [
            {"Facility Name Description": "DBW Tranche 1", "Opening Principal Balance (£)": 50000.0, "Annual Interest Rate (%)": 7.5, "Contractual Amortization Term (Months)": 60},
            {"Facility Name Description": "Funding Circle Line", "Opening Principal Balance (£)": 45000.0, "Annual Interest Rate (%)": 9.2, "Contractual Amortization Term (Months)": 48},
            {"Facility Name Description": "IWOCA Short-Term", "Opening Principal Balance (£)": 35176.0, "Annual Interest Rate (%)": 12.0, "Contractual Amortization Term (Months)": 24}
        ],
        "sales_locations": [
            {"Trading Location Name": "Bridgend Hub", "Corporate Revenue Share (%)": 40.0, "Zero-Rated / Exempt Mix (%)": 65.0},
            {"Trading Location Name": "Cardiff Bay Center", "Corporate Revenue Share (%)": 35.0, "Zero-Rated / Exempt Mix (%)": 0.0},
            {"Trading Location Name": "Penarth Acquisition", "Corporate Revenue Share (%)": 25.0, "Zero-Rated / Exempt Mix (%)": 100.0}
        ]
    }
    
    clean_slate_venture = {
        "opening_cash_balance": 250000.00,
        "opening_fixed_assets_nbv": 0.00,
        "admin_overheads_monthly": 5000.00,
        "base_monthly_gross_wages": 8000.00,
        "directors_salaries_monthly": 3000.00,
        "pension_opt_out": True,
        "y1_monthly_revenue_curve": [50000.0] * 12,
        "debt_facilities": [],
        "sales_locations": [
            {"Trading Location Name": "New Online Channel", "Corporate Revenue Share (%)": 100.0, "Zero-Rated / Exempt Mix (%)": 0.0}
        ]
    }

    # Added 'marketcatalyst' explicitly to the secure workspace map
    registry = {
        "admin": {
            "AHOTG Multi-Shop Baseline (Scenario 2)": ahotg_y2_baseline,
            "Greenfield Project Alpha (Scenario 1)": clean_slate_venture
        },
        "marketcatalyst": {
            "AHOTG Multi-Shop Baseline (Scenario 2)": ahotg_y2_baseline,
            "Greenfield Project Alpha (Scenario 1)": clean_slate_venture
        },
        "user2": {
            "Greenfield Project Alpha (Scenario 1)": clean_slate_venture
        }
    }
    
    return registry.get(username, {})