"""Read-only test script for Supabase PostgreSQL connection using pg8000.

Validates connectivity, displays database metadata, and inspects existing table row counts.
Strictly read-only; never logs plain text credentials or raw exception messages.
"""

import sys
from pathlib import Path
from sqlalchemy import text

SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db import get_engine, get_masked_connection_url


def test_connection():
    print("=" * 65)
    print("Supabase PostgreSQL Read-Only Connection Test (pg8000 Driver)")
    print("=" * 65)

    try:
        masked_url = get_masked_connection_url()
        print(f"Target Connection: {masked_url}")
    except ValueError as e:
        print("[ERROR] Configuration Missing: Database credentials not found in environment.")
        print("Please configure DB_HOST, DB_USER, and DB_PASSWORD (or DATABASE_URL) in your .env file.")
        sys.exit(1)

    print("\nAttempting connection to Supabase...")
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Query server version and context
            version_row = conn.execute(text("SELECT version();")).fetchone()
            ctx_row = conn.execute(
                text("SELECT current_database(), current_user, current_schema();")
            ).fetchone()

            db_version = version_row[0] if version_row else "Unknown"
            current_db, current_user, current_schema = ctx_row if ctx_row else ("?", "?", "?")

            print("[SUCCESS] Connected to Supabase PostgreSQL!")
            print(f"  - Database:       {current_db}")
            print(f"  - Current User:   {current_user}")
            print(f"  - Current Schema: {current_schema}")
            print(f"  - Server Engine:  {db_version.split(',')[0]}")

            # Query existing tables in public schema
            tables_query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in conn.execute(tables_query).fetchall()]

            print("\n" + "=" * 65)
            print(f"Existing Tables in 'public' Schema ({len(tables)} found):")
            print("=" * 65)

            if not tables:
                print("No tables currently found in the 'public' schema.")
            else:
                print(f"{'Table Name':<45} | {'Row Count':>14}")
                print("-" * 62)
                for tbl in tables:
                    count_query = text(f'SELECT COUNT(*) FROM public."{tbl}";')
                    try:
                        count = conn.execute(count_query).scalar()
                        print(f"{tbl:<45} | {count:>14,}")
                    except Exception as cnt_err:
                        print(f"{tbl:<45} | [ERR: {type(cnt_err).__name__}]")

            print("=" * 65)
            print("Read-only verification completed successfully.")
            return True

    except Exception as e:
        print("\n[FAILED] Unable to connect to Supabase PostgreSQL.")
        # Security: Print only the exception type, never raw messages or tracebacks
        print(f"Error Type: {type(e).__name__}")
        print("\nSafe Troubleshooting Guidance:")
        print("1. Credentials: Verify DB_HOST, DB_USER, and DB_PASSWORD in your .env file.")
        print("2. Network & Port: Verify that outbound TCP traffic on port 5432 (or pooler port 6543) is allowed.")
        print("3. SSL Requirement: Supabase requires SSL encryption (DB_SSLMODE=require).")
        print("4. Project Status: Check the Supabase dashboard to ensure the project instance is active and not paused.")
        sys.exit(1)


if __name__ == "__main__":
    test_connection()
