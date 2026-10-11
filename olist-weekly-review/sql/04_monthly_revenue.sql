-- ============================================================================
-- Query 1: Monthly Revenue and Month-over-Month (MoM) Growth
-- File: sql/04_monthly_revenue.sql
-- Description:
--   Calculates monthly Gross Merchandise Value (GMV: item price excluding freight)
--   and Month-over-Month (MoM) revenue growth using the LAG() window function.
--
-- Business Rules & Methodology:
--   1. Revenue Definition: Exclusively item price value (total_item_value), excluding freight.
--   2. Order Eligibility: Excludes non-fulfilled orders (order_status NOT IN ('canceled', 'unavailable')).
--   3. Complete Calendar Timeline: Uses generate_series() to ensure no missing months.
--   4. Operational Period Classification (month_period_flag):
--      - 'LAUNCH_PILOT'   : Sep 2016 - Oct 2016 (Initial test transactions)
--      - 'ZERO_REVENUE'   : Nov 2016 (Operational pause between pilot and formal launch)
--      - 'RAMP_UP'        : Dec 2016 (Pre-launch validation transaction)
--      - 'FULL_OPERATION' : Jan 2017 - Aug 2018 (Continuous marketplace operations)
--      - 'PARTIAL_TAIL'   : Sep 2018 (Public dataset collection cutoff early in month)
-- ============================================================================

WITH date_bounds AS (
    SELECT 
        DATE_TRUNC('month', MIN(purchase_timestamp)) AS min_month,
        DATE_TRUNC('month', MAX(purchase_timestamp)) AS max_month
    FROM public.mart_order_summary
    WHERE order_status NOT IN ('canceled', 'unavailable')
),

-- Continuous series of calendar months across active lifetime
all_months AS (
    SELECT generate_series(min_month, max_month, '1 month'::interval)::timestamp AS order_month
    FROM date_bounds
),

-- Aggregate item revenue (excluding freight) at monthly grain
monthly_aggregated AS (
    SELECT 
        DATE_TRUNC('month', purchase_timestamp) AS order_month,
        COUNT(order_id) AS total_orders,
        COALESCE(SUM(total_item_value), 0)::NUMERIC(12, 2) AS monthly_revenue
    FROM public.mart_order_summary
    WHERE order_status NOT IN ('canceled', 'unavailable')
    GROUP BY DATE_TRUNC('month', purchase_timestamp)
)

SELECT 
    TO_CHAR(m.order_month, 'YYYY-MM') AS month_year,
    CASE
        WHEN m.order_month IN ('2016-09-01'::timestamp, '2016-10-01'::timestamp) THEN 'LAUNCH_PILOT'
        WHEN m.order_month = '2016-11-01'::timestamp THEN 'ZERO_REVENUE'
        WHEN m.order_month = '2016-12-01'::timestamp THEN 'RAMP_UP'
        WHEN m.order_month = '2018-09-01'::timestamp THEN 'PARTIAL_TAIL'
        ELSE 'FULL_OPERATION'
    END AS month_period_flag,
    COALESCE(r.total_orders, 0) AS total_orders,
    COALESCE(r.monthly_revenue, 0.00) AS monthly_revenue,
    LAG(COALESCE(r.monthly_revenue, 0.00)) OVER (ORDER BY m.order_month) AS prev_month_revenue,
    ROUND(
        (COALESCE(r.monthly_revenue, 0.00) - LAG(COALESCE(r.monthly_revenue, 0.00)) OVER (ORDER BY m.order_month))
        / NULLIF(LAG(COALESCE(r.monthly_revenue, 0.00)) OVER (ORDER BY m.order_month), 0) * 100.0,
        2
    ) AS mom_growth_pct
FROM all_months m
LEFT JOIN monthly_aggregated r ON m.order_month = r.order_month
ORDER BY m.order_month;
