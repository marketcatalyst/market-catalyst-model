# utils/database.py
# STRATA SUITE DATABASE ABSTRACTION LAYER // POSTGRESQL & JSON DUAL-WRITE
import os
import json
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

DATABASE_URL = os.environ.get("DATABASE_URL", "postgres://postgres:postgres@localhost:5432/strata_prod")

# Initialize a thread-safe connection pool
try:
    db_pool = pool.ThreadedConnectionPool(1, 20, DATABASE_URL)
    DB_AVAILABLE = True
except Exception as e:
    db_pool = None
    DB_AVAILABLE = False

@contextmanager
def get_db_cursor(tenant_id: str = "default_tenant"):
    if not DB_AVAILABLE or not db_pool:
        yield None
        return
    
    conn = db_pool.getconn()
    try:
        cursor = conn.cursor()
        # Enforce Row-Level Security (RLS) tenant context session variable
        cursor.execute("SET LOCAL app.current_tenant_id = %s;", (tenant_id,))
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        db_pool.putconn(conn)