WITH date_bounds AS (
    SELECT 
        MIN(purchase_timestamp::date) AS min_date,
        MAX(purchase_timestamp::date) AS max_date
    FROM public.mart_order_summary
    WHERE order_status NOT IN ('canceled', 'unavailable')
),
calendar_days AS (
    SELECT generate_series(min_date, max_date, '1 day'::interval)::date AS order_date
    FROM date_bounds
),
daily_counts AS (
    SELECT 
        purchase_timestamp::date AS order_date,
        COUNT(order_id) AS daily_order_count
    FROM public.mart_order_summary
    WHERE order_status NOT IN ('canceled', 'unavailable')
    GROUP BY purchase_timestamp::date
)
SELECT 
    c.order_date,
    COALESCE(d.daily_order_count, 0) AS daily_orders,
    COUNT(c.order_date) OVER (
        ORDER BY c.order_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS window_calendar_days,
    ROUND(
        AVG(COALESCE(d.daily_order_count, 0)) OVER (
            ORDER BY c.order_date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS rolling_7_day_avg_orders
FROM calendar_days c
LEFT JOIN daily_counts d ON c.order_date = d.order_date
ORDER BY c.order_date;
