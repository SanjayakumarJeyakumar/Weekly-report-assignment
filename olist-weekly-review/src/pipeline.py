import sys
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
from sqlalchemy import text, Engine, Connection

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db import get_engine, get_masked_connection_url
from src.data_quality import run_data_quality_checks

DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
SQL_DIR = PROJECT_ROOT / "sql"

EXPECTED_DATASETS: Dict[str, Dict] = {
    "olist_customers_dataset.csv": {
        "table_name": "olist_customers_dataset",
        "required_columns": [
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ],
    },
    "olist_geolocation_dataset.csv": {
        "table_name": "olist_geolocation_dataset",
        "required_columns": [
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state",
        ],
    },
    "olist_order_items_dataset.csv": {
        "table_name": "olist_order_items_dataset",
        "required_columns": [
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ],
    },
    "olist_order_payments_dataset.csv": {
        "table_name": "olist_order_payments_dataset",
        "required_columns": [
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
        ],
    },
    "olist_order_reviews_dataset.csv": {
        "table_name": "olist_order_reviews_dataset",
        "required_columns": [
            "review_id",
            "order_id",
            "review_score",
            "review_creation_date",
            "review_answer_timestamp",
        ],
    },
    "olist_orders_dataset.csv": {
        "table_name": "olist_orders_dataset",
        "required_columns": [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    },
    "olist_products_dataset.csv": {
        "table_name": "olist_products_dataset",
        "required_columns": [
            "product_id",
            "product_category_name",
        ],
    },
    "olist_sellers_dataset.csv": {
        "table_name": "olist_sellers_dataset",
        "required_columns": [
            "seller_id",
            "seller_zip_code_prefix",
            "seller_city",
            "seller_state",
        ],
    },
    "product_category_name_translation.csv": {
        "table_name": "product_category_name_translation",
        "required_columns": [
            "product_category_name",
            "product_category_name_english",
        ],
    },
}

EXPECTED_MART_SCHEMA: Dict[str, List[str]] = {
    "order_id": ["text", "character varying"],
    "customer_unique_id": ["text", "character varying"],
    "customer_state": ["text", "character varying"],
    "order_status": ["text", "character varying"],
    "purchase_timestamp": ["timestamp without time zone", "timestamp"],
    "delivered_date": ["timestamp without time zone", "timestamp"],
    "estimated_delivery_date": ["timestamp without time zone", "timestamp"],
    "total_item_value": ["numeric"],
    "total_freight": ["numeric"],
    "total_payment": ["numeric"],
    "average_review_score": ["numeric"],
    "delivery_days": ["integer"],
    "delivery_delay_days": ["integer"],
}


def parse_sql_statements(sql_text: str) -> List[str]:
    statements: List[str] = []
    current_chars: List[str] = []
    in_single_quote = False
    in_dollar_quote = False
    dollar_tag = ""
    in_line_comment = False
    in_block_comment = False

    i = 0
    n = len(sql_text)
    while i < n:
        c = sql_text[i]
        nxt = sql_text[i + 1] if i + 1 < n else ""

        if in_line_comment:
            if c == "\n":
                in_line_comment = False
            i += 1
            continue

        if in_block_comment:
            if c == "*" and nxt == "/":
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue

        if not in_single_quote and not in_dollar_quote:
            if c == "-" and nxt == "-":
                in_line_comment = True
                i += 2
                continue
            if c == "/" and nxt == "*":
                in_block_comment = True
                i += 2
                continue

        if c == "$" and not in_single_quote:
            if not in_dollar_quote:
                end_dollar = sql_text.find("$", i + 1)
                if end_dollar != -1 and (end_dollar - i) < 32:
                    tag = sql_text[i : end_dollar + 1]
                    inner = tag[1:-1]
                    if inner == "" or inner.isidentifier():
                        in_dollar_quote = True
                        dollar_tag = tag
                        current_chars.append(tag)
                        i = end_dollar + 1
                        continue
            else:
                if sql_text[i:].startswith(dollar_tag):
                    in_dollar_quote = False
                    current_chars.append(dollar_tag)
                    i += len(dollar_tag)
                    continue

        if c == "'" and not in_dollar_quote:
            if in_single_quote and nxt == "'":
                current_chars.append("''")
                i += 2
                continue
            in_single_quote = not in_single_quote
            current_chars.append(c)
            i += 1
            continue

        if c == ";" and not in_single_quote and not in_dollar_quote:
            stmt = "".join(current_chars).strip()
            if stmt:
                statements.append(stmt)
            current_chars = []
            i += 1
            continue

        current_chars.append(c)
        i += 1

    tail = "".join(current_chars).strip()
    if tail:
        statements.append(tail)

    return statements


def get_table_row_count(conn: Connection, schema: str, table: str) -> int:
    if schema:
        query = text(f'SELECT COUNT(1) FROM "{schema}"."{table}";')
    else:
        query = text(f'SELECT COUNT(1) FROM "{table}";')
    return conn.execute(query).scalar() or 0


def check_table_dependencies(conn: Connection, schema: str, table: str) -> None:
    view_dep_query = text("""
        SELECT dependent_view.relname AS dep_name
        FROM pg_depend
        JOIN pg_rewrite ON pg_depend.objid = pg_rewrite.oid
        JOIN pg_class AS dependent_view ON pg_rewrite.ev_class = dependent_view.oid
        JOIN pg_class AS source_table ON pg_depend.refobjid = source_table.oid
        JOIN pg_namespace AS nsp ON source_table.relnamespace = nsp.oid
        WHERE nsp.nspname = :schema_name
          AND source_table.relname = :table_name
          AND dependent_view.relname != source_table.relname
          AND dependent_view.relkind IN ('v', 'm');
    """)
    dependent_views = [
        r[0] for r in conn.execute(view_dep_query, {"schema_name": schema, "table_name": table}).fetchall()
    ]

    fk_dep_query = text("""
        SELECT conname, conrelid::regclass::text AS referencing_table
        FROM pg_constraint
        WHERE confrelid = (
            SELECT c.oid
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = :schema_name AND c.relname = :table_name
        );
    """)
    referencing_fks = [
        f"{r[0]} on {r[1]}"
        for r in conn.execute(fk_dep_query, {"schema_name": schema, "table_name": table}).fetchall()
    ]

    if dependent_views or referencing_fks:
        raise RuntimeError(f"Dependency error on {schema}.{table}: views={dependent_views}, fks={referencing_fks}")


def check_mart_schema_compatibility(conn: Connection) -> None:
    col_query = text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'mart_order_summary';
    """)
    existing_cols = {row[0]: row[1].lower() for row in conn.execute(col_query).fetchall()}

    if not existing_cols:
        return

    mismatches = []
    for expected_col, allowed_types in EXPECTED_MART_SCHEMA.items():
        if expected_col not in existing_cols:
            mismatches.append(f"Missing column: '{expected_col}'")
        else:
            actual_type = existing_cols[expected_col]
            if actual_type not in allowed_types:
                mismatches.append(f"Type mismatch on '{expected_col}': expected {allowed_types}, found '{actual_type}'")

    if mismatches:
        raise ValueError("Schema mismatch in public.mart_order_summary:\n" + "\n".join(mismatches))


def validate_csvs_and_compare_db(engine: Engine, raw_dir: Path) -> Dict[str, Tuple[int, int]]:
    print("Checking CSV datasets and database tables...")
    results: Dict[str, Tuple[int, int]] = {}
    validation_failures = []

    with engine.connect() as conn:
        for filename, meta in EXPECTED_DATASETS.items():
            file_path = raw_dir / filename
            table_name = meta["table_name"]

            if not file_path.exists():
                validation_failures.append(f"{filename}: File not found.")
                continue
            if file_path.stat().st_size == 0:
                validation_failures.append(f"{filename}: File is empty.")
                continue

            try:
                sample_df = pd.read_csv(file_path, nrows=1)
                missing_cols = set(meta["required_columns"]) - set(sample_df.columns)
                if missing_cols:
                    validation_failures.append(f"{filename}: Missing columns {sorted(missing_cols)}")
                    continue
            except Exception as e:
                validation_failures.append(f"{filename}: Failed reading header: {e}")
                continue

            try:
                full_df = pd.read_csv(file_path)
                csv_count = len(full_df)
            except Exception as e:
                validation_failures.append(f"{filename}: Failed reading CSV: {e}")
                continue

            try:
                db_count = get_table_row_count(conn, "public", table_name)
            except Exception:
                db_count = -1

            status = "MATCH" if csv_count == db_count else "MISMATCH"
            results[table_name] = (csv_count, db_count)
            print(f" - {table_name}: CSV={csv_count:,}, DB={db_count:,} ({status})")

            if status == "MISMATCH":
                validation_failures.append(
                    f"{table_name}: CSV count ({csv_count}) does not match DB count ({db_count})"
                )

    if validation_failures:
        raise ValueError("Validation failed:\n" + "\n".join(validation_failures))

    print("All datasets validated successfully.\n")
    return results


def refresh_staging(conn: Connection) -> None:
    print("Refreshing staging tables...")
    sql_file = SQL_DIR / "01_create_staging.sql"
    statements = parse_sql_statements(sql_file.read_text(encoding="utf-8"))

    for stmt in statements:
        conn.execute(text(stmt))

    expected_temp_counts = {
        "tmp_stg_orders": 99441,
        "tmp_stg_customers": 99441,
        "tmp_stg_order_items": 112650,
        "tmp_stg_payments": 103886,
        "tmp_stg_reviews": 99224,
    }

    for tmp_tbl, expected_count in expected_temp_counts.items():
        actual_count = conn.execute(text(f"SELECT COUNT(1) FROM {tmp_tbl};")).scalar()
        if actual_count != expected_count:
            raise ValueError(f"Validation error for {tmp_tbl}: expected {expected_count}, got {actual_count}")

    null_orders = conn.execute(text("SELECT COUNT(1) FROM tmp_stg_orders WHERE order_id IS NULL;")).scalar()
    if null_orders > 0:
        raise ValueError("NULL order_id found in tmp_stg_orders")

    staging_tables = ["stg_orders", "stg_customers", "stg_order_items", "stg_payments", "stg_reviews"]
    for tbl in staging_tables:
        check_table_dependencies(conn, "staging", tbl)

    conn.execute(text("TRUNCATE TABLE staging.stg_orders; INSERT INTO staging.stg_orders SELECT * FROM tmp_stg_orders;"))
    conn.execute(text("TRUNCATE TABLE staging.stg_customers; INSERT INTO staging.stg_customers SELECT * FROM tmp_stg_customers;"))
    conn.execute(text("TRUNCATE TABLE staging.stg_order_items; INSERT INTO staging.stg_order_items SELECT * FROM tmp_stg_order_items;"))
    conn.execute(text("TRUNCATE TABLE staging.stg_payments; INSERT INTO staging.stg_payments SELECT * FROM tmp_stg_payments;"))
    conn.execute(text("TRUNCATE TABLE staging.stg_reviews; INSERT INTO staging.stg_reviews SELECT * FROM tmp_stg_reviews;"))

    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stg_orders_cust ON staging.stg_orders(customer_id);"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stg_customers_uniq ON staging.stg_customers(customer_unique_id);"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stg_items_order ON staging.stg_order_items(order_id);"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stg_payments_order ON staging.stg_payments(order_id);"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stg_reviews_order ON staging.stg_reviews(order_id);"))

    print("Staging tables updated successfully.\n")


def refresh_mart(conn: Connection) -> None:
    print("Refreshing mart_order_summary...")
    sql_file = SQL_DIR / "02_create_mart.sql"
    statements = parse_sql_statements(sql_file.read_text(encoding="utf-8"))

    for stmt in statements:
        conn.execute(text(stmt))

    candidate_count = conn.execute(text("SELECT COUNT(1) FROM tmp_mart_order_summary;")).scalar()
    stg_orders_count = conn.execute(text("SELECT COUNT(1) FROM staging.stg_orders;")).scalar()

    if candidate_count != stg_orders_count:
        raise ValueError(f"Mart count mismatch: {candidate_count} vs expected {stg_orders_count}")

    null_count = conn.execute(text("SELECT COUNT(1) FROM tmp_mart_order_summary WHERE order_id IS NULL;")).scalar()
    if null_count > 0:
        raise ValueError(f"NULL order_id count: {null_count}")

    dup_count = conn.execute(text("""
        SELECT COUNT(1) FROM (
            SELECT order_id FROM tmp_mart_order_summary GROUP BY order_id HAVING COUNT(1) > 1
        ) d;
    """)).scalar()
    if dup_count > 0:
        raise ValueError(f"Duplicate order_ids found: {dup_count}")

    check_table_dependencies(conn, "public", "mart_order_summary")
    check_mart_schema_compatibility(conn)

    conn.execute(text("TRUNCATE TABLE public.mart_order_summary; INSERT INTO public.mart_order_summary SELECT * FROM tmp_mart_order_summary;"))

    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_mart_customer_unique_id ON public.mart_order_summary(customer_unique_id);"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_mart_purchase_timestamp ON public.mart_order_summary(purchase_timestamp);"))
    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_mart_customer_state ON public.mart_order_summary(customer_state);"))

    print("Mart refreshed successfully.\n")


def audit_pipeline(conn: Connection) -> None:
    print("Auditing pipeline output...")
    staging_tables = ["stg_orders", "stg_customers", "stg_order_items", "stg_payments", "stg_reviews"]
    for tbl in staging_tables:
        cnt = get_table_row_count(conn, "staging", tbl)
        print(f" - staging.{tbl}: {cnt:,} rows")

    mart_count = get_table_row_count(conn, "public", "mart_order_summary")
    stg_orders_count = get_table_row_count(conn, "staging", "stg_orders")

    if mart_count != stg_orders_count:
        raise ValueError(f"Mart row count mismatch: mart ({mart_count}) != orders ({stg_orders_count})")

    null_orders = conn.execute(
        text("SELECT COUNT(1) FROM public.mart_order_summary WHERE order_id IS NULL;")
    ).scalar()
    if null_orders > 0:
        raise ValueError(f"Found {null_orders} NULL order_ids in mart")

    duplicate_orders = conn.execute(
        text("SELECT COUNT(1) FROM (SELECT order_id FROM public.mart_order_summary GROUP BY order_id HAVING COUNT(1) > 1) d;")
    ).scalar()
    if duplicate_orders > 0:
        raise ValueError(f"Found {duplicate_orders} duplicate order_ids in mart")

    print(f" - public.mart_order_summary: {mart_count:,} rows")
    print("Audit checks passed.\n")


def run_pipeline() -> None:
    print("Starting pipeline...")
    engine = get_engine()

    validate_csvs_and_compare_db(engine, DATA_RAW_DIR)

    with engine.begin() as conn:
        refresh_staging(conn)
        refresh_mart(conn)
        audit_pipeline(conn)
        run_data_quality_checks(conn)

    print("Pipeline execution completed successfully.")


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as err:
        print(f"Pipeline error: {err}")
        sys.exit(1)
