-- ============================================================================
-- Query 4: Customer Repeat Purchase Rate
-- File: sql/07_repeat_purchase_rate.sql
-- Description:
--   Calculates customer retention and repeat purchase rate at the individual human
--   customer level using customer_unique_id (from olist_customers_dataset).
--
-- Business Rules & Denominator Methodology:
--   1. Grain: Evaluated strictly by customer_unique_id, NOT customer_id.
--      In Olist, a new customer_id is assigned per transaction, whereas
--      customer_unique_id tracks the actual persistent individual.
--   2. Eligible Orders: Excludes canceled and unavailable orders so that retention
--      reflects fulfilled commercial transactions.
--   3. Population Comparison & Denominator Clarification:
--      - 99,441 total customer_id records in dataset (transactional IDs)
--      - 96,096 distinct customer_unique_id records across entire dataset
--      - 94,990 distinct customer_unique_id records with eligible (fulfilled) orders
--        (1,106 customers placed only canceled or unavailable orders and are excluded
--         from the active purchasing customer denominator).
--   4. Classification:
--      - Repeat Customers: distinct customer_unique_id with > 1 distinct eligible orders.
--      - One-Time Customers: distinct customer_unique_id with exactly 1 eligible order.
--      - Repeat Purchase Rate %: (repeat_customers * 100.0) / total_eligible_unique_customers.
-- ============================================================================

WITH customer_order_summary AS (
    SELECT 
        customer_unique_id,
        COUNT(DISTINCT order_id) AS eligible_order_count
    FROM public.mart_order_summary
    WHERE order_status NOT IN ('canceled', 'unavailable')
    GROUP BY customer_unique_id
)

SELECT 
    -- Active purchasing customer base (denominator)
    COUNT(customer_unique_id) AS total_eligible_unique_customers,
    COUNT(CASE WHEN eligible_order_count = 1 THEN 1 END) AS one_time_customers,
    COUNT(CASE WHEN eligible_order_count > 1 THEN 1 END) AS repeat_customers,
    -- Retention rate across eligible purchasing customers
    ROUND(
        (COUNT(CASE WHEN eligible_order_count > 1 THEN 1 END) * 100.0) / COUNT(customer_unique_id),
        2
    ) AS repeat_purchase_rate_pct,
    -- Context comparison against the overall raw customer population
    (SELECT COUNT(DISTINCT customer_unique_id) FROM public.olist_customers_dataset) AS total_registered_unique_customers,
    ROUND(
        (COUNT(CASE WHEN eligible_order_count > 1 THEN 1 END) * 100.0) / 
        (SELECT COUNT(DISTINCT customer_unique_id) FROM public.olist_customers_dataset),
        2
    ) AS repeat_rate_vs_all_registered_pct
FROM customer_order_summary;
