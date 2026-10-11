-- ============================================================================
-- Query 3: Seven-Calendar-Day Rolling Average of Daily Orders
-- File: sql/06_rolling_7_day_orders.sql
-- Description:
--   Computes daily order volume and a 7-calendar-day rolling average across
--   a continuous daily timeline.
--
-- Business Rules & Methodology:
--   1. Full Calendar Continuity: Uses generate_series() from min to max purchase dates
--      to ensure zero-order days are included rather than omitted.
--   2. Window Specification:
--        AVG(...) OVER (ORDER BY c.order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
--      - First 6 Days (Ramp-up): Evaluated over available preceding days (window sizes 1 through 6).
--      - Day 7 Onwards: Evaluated over strictly 7 consecutive calendar days (window size = 7).
--   3. Excludes canceled and unavailable orders.
--   4. Explicitly outputs window_calendar_days to verify window progression.
-- ============================================================================

WITH date_bounds AS (
    SELECT 
        MIN(purchase_timestamp::date) AS min_date,
        MAX(purchase_timestamp::date) AS max_date
    FROM public.mart_order_summary
    WHERE order_status NOT IN ('canceled', 'unavailable')
),

-- Complete uninterrupted daily calendar series
calendar_days AS (
    SELECT generate_series(min_date, max_date, '1 day'::interval)::date AS order_date
    FROM date_bounds
),

-- Aggregate daily order counts (days without orders will be absent here)
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
    -- Actual number of calendar days in the window (ramps from 1 to 7 over the first 6 days)
    COUNT(c.order_date) OVER (
        ORDER BY c.order_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS window_calendar_days,
    -- 7-calendar-day rolling average
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
