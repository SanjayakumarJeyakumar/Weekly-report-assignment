-- ============================================================================
-- Query 5: Delivery Delay vs. Review Score Correlation
-- File: sql/08_delivery_delay_vs_reviews.sql
-- Description:
--   Analyzes customer review ratings (1 to 5) against delivery delay metrics.
--
-- Multi-Review Decoupling & Grain Methodology:
--   1. An order can have multiple review records in olist_order_reviews_dataset.
--      To eliminate double-counting ambiguity, this query explicitly reports:
--      - total_review_records: total review records submitted
--      - distinct_delivered_orders: unique orders evaluated (order-level grain)
--      - multi_review_records_count: duplicate review rows for the same order
--   2. Percentage of late deliveries is calculated and reported at BOTH grains:
--      - pct_late_deliveries_order_grain  : (distinct late orders / distinct orders) * 100.0
--      - pct_late_deliveries_review_grain : (late review rows / total review rows) * 100.0
--   3. Delivery Delay Definition:
--        delivery_delay_days = (delivered_date::DATE - estimated_delivery_date::DATE)
--        - Positive (> 0): Order delivered LATE (after promised estimate date)
--        - Zero or Negative (<= 0): Order delivered ON TIME or EARLY
--   4. Excludes unfulfilled orders (focuses on order_status = 'delivered' with valid dates).
-- ============================================================================

SELECT 
    r.review_score,
    -- Volume counts
    COUNT(r.review_id) AS total_review_records,
    COUNT(DISTINCT m.order_id) AS distinct_delivered_orders,
    COUNT(r.review_id) - COUNT(DISTINCT m.order_id) AS multi_review_records_count,
    
    -- Delivery transit metrics
    ROUND(AVG(m.delivery_days), 2) AS avg_actual_delivery_days,
    ROUND(AVG(m.delivery_delay_days), 2) AS avg_days_relative_to_estimate,
    
    -- Order-grain late delivery metrics (Primary business metric)
    COUNT(DISTINCT CASE WHEN m.delivery_delay_days > 0 THEN m.order_id END) AS distinct_late_orders,
    ROUND(
        COUNT(DISTINCT CASE WHEN m.delivery_delay_days > 0 THEN m.order_id END) * 100.0 / NULLIF(COUNT(DISTINCT m.order_id), 0),
        2
    ) AS pct_late_deliveries_order_grain,
    
    -- Severity of delay among delayed orders
    ROUND(
        AVG(CASE WHEN m.delivery_delay_days > 0 THEN m.delivery_delay_days END),
        2
    ) AS avg_days_late_when_delayed,
    
    -- Order-grain on-time / early delivery metrics
    COUNT(DISTINCT CASE WHEN m.delivery_delay_days <= 0 THEN m.order_id END) AS distinct_on_time_or_early_orders,
    ROUND(
        COUNT(DISTINCT CASE WHEN m.delivery_delay_days <= 0 THEN m.order_id END) * 100.0 / NULLIF(COUNT(DISTINCT m.order_id), 0),
        2
    ) AS pct_on_time_or_early_order_grain,
    
    -- Review-grain late delivery percentage (for cross-grain comparison)
    ROUND(
        COUNT(CASE WHEN m.delivery_delay_days > 0 THEN 1 END) * 100.0 / NULLIF(COUNT(r.review_id), 0),
        2
    ) AS pct_late_deliveries_review_grain
FROM public.olist_order_reviews_dataset r
JOIN public.mart_order_summary m ON r.order_id = m.order_id
WHERE m.order_status = 'delivered'
  AND m.delivered_date IS NOT NULL
  AND m.estimated_delivery_date IS NOT NULL
GROUP BY r.review_score
ORDER BY r.review_score;
