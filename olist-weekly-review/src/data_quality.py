import sys
from pathlib import Path
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db import get_engine

SQL_DIR = PROJECT_ROOT / "sql"


def run_data_quality_checks(conn=None):
    print("Running Data Quality Checks...")

    sql_file = SQL_DIR / "03_data_quality_checks.sql"
    query_sql = sql_file.read_text(encoding="utf-8")

    def _execute(c):
        rows = c.execute(text(query_sql)).fetchall()
        results = []
        for r in rows:
            results.append({
                "check_id": r[0],
                "check_name": r[1],
                "severity": r[2],
                "failed_count": r[3],
                "status": r[4],
                "explanation": r[5],
            })
        return results

    if conn is not None:
        results = _execute(conn)
    else:
        engine = get_engine()
        with engine.connect() as standalone_conn:
            results = _execute(standalone_conn)

    print(f"\n{'ID':<3} | {'Check Name':<38} | {'Failed':>8} | {'Status':>6}")
    print("-" * 62)

    critical_failures = []
    for item in results:
        cid = item["check_id"]
        cname = item["check_name"]
        failed = item["failed_count"]
        status = item["status"]
        severity = item["severity"]

        print(f"{cid:<3} | {cname:<38} | {failed:>8,} | {status:>6}")

        if severity == "CRITICAL" and status == "FAIL":
            critical_failures.append((cname, failed))

    if critical_failures:
        print("\nCritical data quality checks failed:")
        for name, count in critical_failures:
            print(f" - {name}: {count:,} failed rows")
        raise RuntimeError("Data quality check failed")

    print("\nAll critical data quality checks passed successfully.\n")
    return results


if __name__ == "__main__":
    try:
        run_data_quality_checks()
    except Exception as err:
        print(f"Error: {err}")
        sys.exit(1)
