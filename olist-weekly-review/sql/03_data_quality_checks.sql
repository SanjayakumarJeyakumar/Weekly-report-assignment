SELECT
    1 AS check_id,
    'Duplicate Order IDs in Mart' AS check_name,
    'CRITICAL' AS severity,
    COUNT(*) AS failed_row_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Ensures exactly one row per order grain in public.mart_order_summary' AS explanation
FROM (
    SELECT order_id
    FROM public.mart_order_summary
    WHERE order_id IS NOT NULL
    GROUP BY order_id
    HAVING COUNT(*) > 1
) dupes

UNION ALL

SELECT
    2 AS check_id,
    'Null Order IDs in Mart' AS check_name,
    'CRITICAL' AS severity,
    COUNT(*) AS failed_row_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Ensures primary key non-null constraint in public.mart_order_summary' AS explanation
FROM public.mart_order_summary
WHERE order_id IS NULL

UNION ALL

SELECT
    3 AS check_id,
    'Orders Delivered Before Purchase' AS check_name,
    'CRITICAL' AS severity,
    COUNT(*) AS failed_row_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Temporal validity: delivered_date must be >= purchase_timestamp and purchase_timestamp cannot be null for delivered orders' AS explanation
FROM public.mart_order_summary
WHERE delivered_date IS NOT NULL
  AND (purchase_timestamp IS NULL OR delivered_date < purchase_timestamp)

UNION ALL

SELECT
    4 AS check_id,
    'Invalid Review Scores Outside 1-5' AS check_name,
    'CRITICAL' AS severity,
    COUNT(*) AS failed_row_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Domain validity: review scores in olist_order_reviews_dataset must range strictly between 1 and 5' AS explanation
FROM public.olist_order_reviews_dataset
WHERE review_score < 1 OR review_score > 5 OR review_score IS NULL

UNION ALL

SELECT
    5 AS check_id,
    'Orphan Orders Without Customer Record' AS check_name,
    'CRITICAL' AS severity,
    COUNT(*) AS failed_row_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS status,
    'Referential integrity: every order must match a valid customer record in olist_customers_dataset' AS explanation
FROM public.olist_orders_dataset o
LEFT JOIN public.olist_customers_dataset c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL OR o.customer_id IS NULL

UNION ALL

SELECT
    6 AS check_id,
    'Payment Total Reconciliation Variance' AS check_name,
    'WARNING' AS severity,
    COUNT(*) AS failed_row_count,
    CASE WHEN COUNT(*) = 0 THEN 'PASS' ELSE 'WARN' END AS status,
    'Variance between total_payment and items+freight for delivered orders (expected due to financing interest or voucher subsidies)' AS explanation
FROM public.mart_order_summary
WHERE order_status = 'delivered'
  AND (
      total_payment IS NULL
      OR total_item_value IS NULL
      OR total_freight IS NULL
      OR ABS(total_payment - (total_item_value + total_freight)) > 0.01
  )

ORDER BY check_id;
