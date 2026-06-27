# database/schema.py
# STRATA RELATIONAL PERSISTENCE CONTROLLER // NEON SCHEMA ENGINE

import logging
from database.connection import NeonDatabaseManager

logger = logging.getLogger("STRATA_SCHEMA")


def deploy_database_schema():
    """
    Executes DDL statements to construct the relational forecasting schema
    inside Neon PostgreSQL, ensuring strict data types and foreign key integrity.
    """
    sql_create_scenarios_table = """
    CREATE TABLE IF NOT EXISTS forecast_scenarios (
        scenario_id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    sql_create_ledger_table = """
    CREATE TABLE IF NOT EXISTS forecast_monthly_ledger (
        ledger_entry_id SERIAL PRIMARY KEY,
        scenario_id INTEGER REFERENCES forecast_scenarios(scenario_id) ON DELETE CASCADE,
        month_index INTEGER NOT NULL,
        pl_revenue NUMERIC(15, 2) DEFAULT 0.00,
        pl_expenses NUMERIC(15, 2) DEFAULT 0.00,
        pl_interest NUMERIC(15, 2) DEFAULT 0.00,
        pl_depreciation NUMERIC(15, 2) DEFAULT 0.00,
        cf_inflows NUMERIC(15, 2) DEFAULT 0.00,
        cf_outflows NUMERIC(15, 2) DEFAULT 0.00,
        bs_debtors NUMERIC(15, 2) DEFAULT 0.00,
        bs_creditors NUMERIC(15, 2) DEFAULT 0.00,
        bs_hp_liability NUMERIC(15, 2) DEFAULT 0.00,
        bs_loan_liability NUMERIC(15, 2) DEFAULT 0.00,
        bs_asset_nbv NUMERIC(15, 2) DEFAULT 0.00,
        bs_hmrc_vat_balance NUMERIC(15, 2) DEFAULT 0.00,
        CONSTRAINT unique_scenario_month UNIQUE (scenario_id, month_index)
    );
    """

    with NeonDatabaseManager.get_connection() as conn:
        with conn.cursor() as cursor:
            logger.info("Deploying STRATA relational database tables to Neon Cloud...")
            cursor.execute(sql_create_scenarios_table)
            cursor.execute(sql_create_ledger_table)
            logger.info("DDL Schema deployment completed successfully.")


def serialize_matrix_to_db(scenario_name: str, scenario_desc: str, matrix: dict):
    """
    Serialises calculated 60-month master ledger vectors directly into the Neon tables.
    Utilises standard UPSERT logic to overwrite data if the scenario run already exists.
    """
    sql_upsert_scenario = """
    INSERT INTO forecast_scenarios (name, description) 
    VALUES (%s, %s)
    ON CONFLICT (name) DO UPDATE 
    SET description = EXCLUDED.description
    RETURNING scenario_id;
    """

    sql_upsert_ledger_row = """
    INSERT INTO forecast_monthly_ledger (
        scenario_id, month_index, pl_revenue, pl_expenses, pl_interest, pl_depreciation,
        cf_inflows, cf_outflows, bs_debtors, bs_creditors, bs_hp_liability, bs_loan_liability,
        bs_asset_nbv, bs_hmrc_vat_balance
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (scenario_id, month_index) DO UPDATE SET
        pl_revenue = EXCLUDED.pl_revenue,
        pl_expenses = EXCLUDED.pl_expenses,
        pl_interest = EXCLUDED.pl_interest,
        pl_depreciation = EXCLUDED.pl_depreciation,
        cf_inflows = EXCLUDED.cf_inflows,
        cf_outflows = EXCLUDED.cf_outflows,
        bs_debtors = EXCLUDED.bs_debtors,
        bs_creditors = EXCLUDED.bs_creditors,
        bs_hp_liability = EXCLUDED.bs_hp_liability,
        bs_loan_liability = EXCLUDED.bs_loan_liability,
        bs_asset_nbv = EXCLUDED.bs_asset_nbv,
        bs_hmrc_vat_balance = EXCLUDED.bs_hmrc_vat_balance;
    """

    # 🚀 ROBUST VALUE CONSTRAINT PROTECTION LAYER
    required_keys = [
        "pl_revenue",
        "pl_expenses",
        "pl_interest",
        "pl_depreciation",
        "cf_inflows",
        "cf_outflows",
        "bs_debtors",
        "bs_creditors",
        "bs_hp_liability",
        "bs_loan_liability",
        "bs_asset_nbv",
        "bs_hmrc_vat_balance",
    ]
    for key in required_keys:
        if key not in matrix:
            logger.error(
                f"Serialization failed: Missing matrix baseline parameter key '{key}'"
            )
            raise KeyError(f"Input forecasting matrix is missing data track: {key}")

    with NeonDatabaseManager.get_connection() as conn:
        with conn.cursor() as cursor:
            # 1. Insert or update the parent scenario entry and grab its relational ID
            cursor.execute(sql_upsert_scenario, (scenario_name, scenario_desc))
            scenario_id = cursor.fetchone()[0]

            # 2. Extract array total length from the compiled dictionary matrix
            total_run_months = len(matrix["pl_revenue"])

            # 3. Stream data points vertically month-by-month using a high-performance batch loop
            logger.info(
                f"Streaming {total_run_months}-month financial matrix run to cloud table for scenario '{scenario_name}'..."
            )
            for m in range(total_run_months):
                month_index = m + 1
                cursor.execute(
                    sql_upsert_ledger_row,
                    (
                        scenario_id,
                        month_index,
                        float(matrix["pl_revenue"][m]),
                        float(matrix["pl_expenses"][m]),
                        float(matrix["pl_interest"][m]),
                        float(matrix["pl_depreciation"][m]),
                        float(matrix["cf_inflows"][m]),
                        float(matrix["cf_outflows"][m]),
                        float(matrix["bs_debtors"][m]),
                        float(matrix["bs_creditors"][m]),
                        float(matrix["bs_hp_liability"][m]),
                        float(matrix["bs_loan_liability"][m]),
                        float(matrix["bs_asset_nbv"][m]),
                        float(matrix["bs_hmrc_vat_balance"][m]),
                    ),
                )
            logger.info(f"Database sync complete for scenario ID: {scenario_id}")
