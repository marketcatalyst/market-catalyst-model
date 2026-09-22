# utils/depreciation.py
# STRATA SUITE // MULTI-BASIS DEPRECIATION CALCULATOR


def calculate_monthly_depreciation(
    asset: dict, current_month: int, cumulative_units_produced: float = 0.0
) -> float:
    basis = asset.get("depreciation_basis", "straight_line")
    cost = float(asset.get("amount", 0.0))
    residual_value = float(asset.get("residual_value", 0.0))
    depreciable_base = max(0.0, cost - residual_value)

    if basis == "straight_line":
        term_months = max(1, int(asset.get("term_months", 36)))
        return round(depreciable_base / term_months, 2)

    elif basis == "reducing_balance":
        annual_rate = float(asset.get("depreciation_rate", 0.20))
        monthly_rate = 1.0 - ((1.0 - annual_rate) ** (1 / 12))
        # Net book value approximation for the current period
        return round((depreciable_base * monthly_rate), 2)

    elif basis == "units_of_production":
        total_lifetime_units = float(asset.get("lifetime_units", 100000.0))
        per_unit_rate = depreciable_base / max(1.0, total_lifetime_units)
        return round(cumulative_units_produced * per_unit_rate, 2)

    return 0.0
