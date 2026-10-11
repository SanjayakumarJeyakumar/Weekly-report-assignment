SELECT 
    r.review_score,
    COUNT(r.review_id) AS total_review_records,
    COUNT(DISTINCT m.order_id) AS distinct_delivered_orders,
    COUNT(r.review_id) - COUNT(DISTINCT m.order_id) AS multi_review_records_count,
    ROUND(AVG(m.delivery_days), 2) AS avg_actual_delivery_days,
    ROUND(AVG(m.delivery_delay_days), 2) AS avg_days_relative_to_estimate,
    COUNT(DISTINCT CASE WHEN m.delivery_delay_days > 0 THEN m.order_id END) AS distinct_late_orders,
    ROUND(
        COUNT(DISTINCT CASE WHEN m.delivery_delay_days > 0 THEN m.order_id END) * 100.0 / NULLIF(COUNT(DISTINCT m.order_id), 0),
        2
    ) AS pct_late_deliveries_order_grain,
    ROUND(
        AVG(CASE WHEN m.delivery_delay_days > 0 THEN m.delivery_delay_days END),
        2
    ) AS avg_days_late_when_delayed,
    COUNT(DISTINCT CASE WHEN m.delivery_delay_days <= 0 THEN m.order_id END) AS distinct_on_time_or_early_orders,
    ROUND(
        COUNT(DISTINCT CASE WHEN m.delivery_delay_days <= 0 THEN m.order_id END) * 100.0 / NULLIF(COUNT(DISTINCT m.order_id), 0),
        2
    ) AS pct_on_time_or_early_order_grain,
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
