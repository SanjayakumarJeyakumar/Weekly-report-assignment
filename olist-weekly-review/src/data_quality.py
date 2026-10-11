"""Data Quality Checks Suite for Olist E-Commerce Pipeline (Part B).

Executes data quality SQL checks against Supabase PostgreSQL.
- Critical checks that fail raise an exception to halt the pipeline and trigger rollback.
- Warning checks report flagged discrepancies (e.g. payment reconciliation variances)
  and explicitly preserve records without modifying or deleting data.
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
from sqlalchemy import text, Engine, Connection

# Ensure project modules are importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db import get_engine, get_masked_connection_url

logger = logging.getLogger("olist_pipeline.data_quality")
if not logger.handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

SQL_DIR = PROJECT_ROOT / "sql"


def run_data_quality_checks(conn: Optional[Connection] = None) -> List[Dict]:
    """Execute the data quality checks suite and evaluate results.
    
    Accepts an existing active transaction Connection or connects via get_engine().
    Raises RuntimeError if any CRITICAL check fails.
    """
    logger.info("=" * 76)
    logger.info("Executing Data Quality Checks Suite (Part B)")
    logger.info("=" * 76)

    sql_file = SQL_DIR / "03_data_quality_checks.sql"
    if not sql_file.exists():
        raise FileNotFoundError(f"DQ checks SQL file not found: {sql_file}")

    query_sql = sql_file.read_text(encoding="utf-8")

    def _execute(c: Connection) -> List[Dict]:
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

    # Display formatted CLI report table
    header = f"{'ID':<3} | {'Check Name':<40} | {'Failed':>8} | {'Status':>6} | {'Severity':>8}"
    logger.info(header)
    logger.info("-" * len(header))

    critical_failures = []
    warnings_found = []

    for item in results:
        cid = item["check_id"]
        cname = item["check_name"]
        failed = item["failed_count"]
        status = item["status"]
        severity = item["severity"]
        explanation = item["explanation"]

        logger.info(f"{cid:<3} | {cname:<40} | {failed:>8,} | {status:>6} | {severity:>8}")
        logger.info(f"     -> Explanation: {explanation}")

        if severity == "CRITICAL" and status == "FAIL":
            critical_failures.append((cname, failed))
        elif severity == "WARNING" and status == "WARN":
            warnings_found.append((cname, failed))

    logger.info("=" * 76)

    # Handle Warning-level checks
    if warnings_found:
        for w_name, w_count in warnings_found:
            logger.warning(
                "[WARN] Data Quality Warning on '%s': %d records flagged.",
                w_name,
                w_count,
            )
            logger.warning(
                "       Action: Records are flagged for analysis; NO records were deleted or modified."
            )
            logger.warning(
                "       Root Cause: Financing interest on installments or platform voucher discounts."
            )

    # Handle Critical-level checks
    if critical_failures:
        err_details = "\n".join([f"  - {name}: {count:,} failed rows" for name, count in critical_failures])
        err_msg = (
            f"DATA QUALITY CRITICAL FAILURE:\n{err_details}\n"
            f"Halting pipeline and initiating transaction rollback."
        )
        logger.error(err_msg)
        raise RuntimeError(err_msg)

    logger.info("Data Quality Suite: ALL CRITICAL CHECKS PASSED.")
    logger.info("=" * 76)
    return results


if __name__ == "__main__":
    try:
        run_data_quality_checks()
    except Exception as err:
        logger.error("Data Quality check halted: %s", type(err).__name__)
        sys.exit(1)
