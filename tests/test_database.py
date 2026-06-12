# tests/test_database.py
import os
from database.connection import NeonDatabaseManager

# To run this test locally, ensure your database connection string is active in terminal memory:
# $env:DATABASE_URL="postgresql://user:password@endpoint-pool.neon.tech/dbname?sslmode=require"

print("--- ☁️ NEON POSTGRESQL CONNECTION HANDSHAKE VERIFICATION ---")

# Check if environment variable is accessible
db_uri = os.environ.get("DATABASE_URL")
if not db_uri:
    print("❌ Critical Error: 'DATABASE_URL' variable is missing from your environment block.")
    print("👉 Set it via PowerShell using: $env:DATABASE_URL='your_neon_connection_string'")
else:
    print("✔️ 'DATABASE_URL' environment string detected in local memory.")
    try:
        # Attempt to initialize pool and fetch a test connection line
        NeonDatabaseManager.initialize_pool()
        
        with NeonDatabaseManager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                db_version = cursor.fetchone()
                print(f"🚀 Live Handshake Successful! Connected to:")
                print(f"   {db_version[0]}")
                
        NeonDatabaseManager.close_all_connections()
        print("\n✔️ Connection pool teardown completed cleanly.")
    except Exception as e:
        print(f"❌ Handshake failed: {str(e)}")