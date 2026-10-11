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
    print("Testing connection to database...")
    try:
        masked_url = get_masked_connection_url()
        print(f"Target: {masked_url}")
    except ValueError as e:
        print("Missing credentials in .env file.")
        sys.exit(1)

    try:
        engine = get_engine()
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
            print("Connected successfully!")
            print(f"PostgreSQL version: {version.split(',')[0]}")

            tables_query = text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in conn.execute(tables_query).fetchall()]

            print(f"\nTables in public schema ({len(tables)} found):")
            for tbl in tables:
                count_query = text(f'SELECT COUNT(*) FROM public."{tbl}";')
                try:
                    count = conn.execute(count_query).scalar()
                    print(f" - {tbl}: {count:,} rows")
                except Exception:
                    print(f" - {tbl}: [error reading count]")

            print("\nCheck completed.")
            return True

    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_connection()
