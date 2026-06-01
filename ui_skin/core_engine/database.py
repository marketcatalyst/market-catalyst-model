# core_engine/database.py
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """
    Establishes a secure connection to your Neon Serverless Postgres instance
    using the credentials stored inside your hidden .streamlit/secrets.toml file.
    """
    connection_string = st.secrets["postgres"]["url"]
    conn = psycopg2.connect(connection_string)
    return conn

def initialize_database_tables():
    """
    Creates our statutory UK SIC Sector benchmarking table and our scenario
    storage tables inside Neon if they do not already exist.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Build the Sector Benchmarks Reference Table
    create_benchmarks_table = """
    CREATE TABLE IF NOT EXISTS uk_sic_benchmarks (
        sic_code VARCHAR(10) PRIMARY KEY,
        sector_name VARCHAR(100) NOT NULL,
        sub_sector_detail TEXT,
        target_gross_profit_percent NUMERIC(5,2) NOT NULL,
        typical_debtor_days INT NOT NULL,
        typical_creditor_days INT NOT NULL
    );
    """
    
    # 2. Build the Scenario Permanent Storage Table
    create_scenarios_table = """
    CREATE TABLE IF NOT EXISTS saved_scenarios (
        id SERIAL PRIMARY KEY,
        scenario_name VARCHAR(50) UNIQUE NOT NULL,
        target_sales NUMERIC(12,2),
        gross_wages NUMERIC(12,2),
        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    cursor.execute(create_benchmarks_table)
    cursor.execute(create_scenarios_table)
    conn.commit() 
    cursor.close()
    conn.close()

def seed_initial_benchmarks():
    """
    Populates our Neon table with standard UK fallback operational baselines.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    benchmarks_data = [
        ('56101', 'Hospitality', 'Licensed Restaurants', 68.00, 0, 30),
        ('62012', 'Technology', 'Business Software (SaaS)', 80.00, 30, 30),
        ('41202', 'Construction', 'Residential Housebuilding', 25.00, 45, 60),
        ('47110', 'Retail', 'Grocery Stores', 30.00, 0, 30)
    ]
    
    insert_query = """
    INSERT INTO uk_sic_benchmarks 
    (sic_code, sector_name, sub_sector_detail, target_gross_profit_percent, typical_debtor_days, typical_creditor_days)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (sic_code) DO NOTHING;
    """
    
    cursor.executemany(insert_query, benchmarks_data)
    conn.commit()
    cursor.close()
    conn.close()

def save_forecast_scenario_to_neon(scenario_name: str, sales: float, wages: float):
    """
    Takes data variables captured from the Streamlit user interface 
    and writes them permanently into your Neon serverless database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    upsert_query = """
        INSERT INTO saved_scenarios (scenario_name, target_sales, gross_wages)
        VALUES (%s, %s, %s)
        ON CONFLICT (scenario_name) 
        DO UPDATE SET target_sales = EXCLUDED.target_sales, gross_wages = EXCLUDED.gross_wages;
    """
    
    cursor.execute(upsert_query, (scenario_name, sales, wages))
    conn.commit()
    cursor.close()
    conn.close()

def load_scenario_names_from_neon() -> list:
    """
    Fetches a simple list of all saved scenario names from Neon 
    to populate a dropdown selection menu on the frontend UI.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT scenario_name FROM saved_scenarios ORDER BY saved_at DESC;")
        records = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return [row[0] for row in records]
    except Exception:
        return []

def fetch_single_scenario_data(scenario_name: str) -> dict:
    """
    Pulls the exact sales and wage variables for a specific named 
    scenario out of Neon so the frontend can override its current state.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT target_sales, gross_wages FROM saved_scenarios WHERE scenario_name = %s;",
        (scenario_name,)
    )
    record = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if record:
        return {
            "target_sales": float(record[0]),
            "gross_wages": float(record[1])
        }
    return None