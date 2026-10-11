WITH customer_order_summary AS (
    SELECT 
        customer_unique_id,
        COUNT(DISTINCT order_id) AS eligible_order_count
    FROM public.mart_order_summary
    WHERE order_status NOT IN ('canceled', 'unavailable')
    GROUP BY customer_unique_id
)
SELECT 
    COUNT(customer_unique_id) AS total_eligible_unique_customers,
    COUNT(CASE WHEN eligible_order_count = 1 THEN 1 END) AS one_time_customers,
    COUNT(CASE WHEN eligible_order_count > 1 THEN 1 END) AS repeat_customers,
    ROUND(
        (COUNT(CASE WHEN eligible_order_count > 1 THEN 1 END) * 100.0) / COUNT(customer_unique_id),
        2
    ) AS repeat_purchase_rate_pct,
    (SELECT COUNT(DISTINCT customer_unique_id) FROM public.olist_customers_dataset) AS total_registered_unique_customers,
    ROUND(
        (COUNT(CASE WHEN eligible_order_count > 1 THEN 1 END) * 100.0) / 
        (SELECT COUNT(DISTINCT customer_unique_id) FROM public.olist_customers_dataset),
        2
    ) AS repeat_rate_vs_all_registered_pct
FROM customer_order_summary;
