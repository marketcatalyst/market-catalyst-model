import pytest
from utils.depreciation import calculate_monthly_depreciation


def test_straight_line_depreciation():
    asset = {
        "depreciation_basis": "straight_line",
        "amount": 12000.0,
        "residual_value": 2000.0,
        "term_months": 60,  # 5 years
    }
    # Monthly depreciation should be (12000 - 2000) / 60 = 166.67
    dep = calculate_monthly_depreciation(asset, current_month=1)
    assert dep == 166.67


def test_reducing_balance_depreciation():
    asset = {
        "depreciation_basis": "reducing_balance",
        "amount": 10000.0,
        "residual_value": 1000.0,
        "depreciation_rate": 0.20,
    }
    dep = calculate_monthly_depreciation(asset, current_month=1)
    assert dep > 0.0


def test_units_of_production_depreciation():
    asset = {
        "depreciation_basis": "units_of_production",
        "amount": 10000.0,
        "residual_value": 0.0,
        "lifetime_units": 10000.0,
    }
    # 500 units produced out of 10,000 lifetime units on a 10,000 base = 500.0
    dep = calculate_monthly_depreciation(
        asset, current_month=1, cumulative_units_produced=500.0
    )
    assert dep == 500.0


def test_zero_depreciable_base():
    asset = {
        "depreciation_basis": "straight_line",
        "amount": 5000.0,
        "residual_value": 5000.0,
        "term_months": 12,
    }
    dep = calculate_monthly_depreciation(asset, current_month=1)
    assert dep == 0.0


def test_unknown_basis_fallback():
    asset = {
        "depreciation_basis": "unknown_method",
        "amount": 5000.0,
        "residual_value": 1000.0,
    }
    dep = calculate_monthly_depreciation(asset, current_month=1)
    assert dep == 0.0
