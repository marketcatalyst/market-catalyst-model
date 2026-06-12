# database/connection.py

import os
import logging
from contextlib import contextmanager
import psycopg2
from psycopg2 import pool

# Configure explicit engineering logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("STRATA_DATABASE")

class NeonDatabaseManager:
    """
    Manages secure cloud connectivity and thread-safe connection pooling
    for the STRATA relational database engine on Neon PostgreSQL.
    """
    _pool = None

    @classmethod
    def initialize_pool(cls):
        """
        Initialises a centralized thread-safe connection pool using connection
        string attributes securely injected from the environment block.
        """
        if cls._pool is None:
            # Extract secure database URI string from system environment variables
            database_url = os.environ.get("DATABASE_URL")
            
            if not database_url:
                logger.error("Database connection string missing. Ensure 'DATABASE_URL' environment variable is set.")
                raise ConnectionError("DATABASE_URL environment variable is unassigned.")
            
            try:
                logger.info("Initializing secure thread-safe Neon connection pool...")
                # Establish pool setting baseline: min 1 connection, max 10 concurrent channels
                cls._pool = pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dsn=database_url
                )
                logger.info("Neon PostgreSQL connection pool active and provisioned.")
            except Exception as e:
                logger.error(f"Failed to initialize Neon connection channel: {str(e)}")
                raise

    @classmethod
    @contextmanager
    def get_connection(cls):
        """
        Context manager that yields a pristine, managed connection from the pool.
        Automatically handles transaction commits, rollbacks, and channel cleanup.
        """
        if cls._pool is None:
            cls.initialize_pool()
            
        connection = cls._pool.getconn()
        try:
            # Set isolation level to automatically commit clean structural writes
            connection.autocommit = False
            yield connection
            # If the code inside the 'with' block executes without exception, commit the transaction
            connection.commit()
        except Exception as e:
            # If any failure triggers down the execution line, roll back to prevent ledger corruption
            connection.rollback()
            logger.error(f"Transaction exception encountered. Rollback executed: {str(e)}")
            raise
        finally:
            # Return the connection back to the active pool reservoir safely
            cls._pool.putconn(connection)

    @classmethod
    def close_all_connections(cls):
        """Gracefully tears down the connection pool reservoir during system shutdown operations."""
        if cls._pool:
            logger.info("Closing all active database pool connections...")
            cls._pool.closeall()
            cls._pool = None
            logger.info("Database pool offline.")