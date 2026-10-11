CREATE TABLE IF NOT EXISTS public.mart_order_summary (
    order_id TEXT PRIMARY KEY,
    customer_unique_id TEXT,
    customer_state TEXT,
    order_status TEXT,
    purchase_timestamp TIMESTAMP,
    delivered_date TIMESTAMP,
    estimated_delivery_date TIMESTAMP,
    total_item_value NUMERIC(12, 2),
    total_freight NUMERIC(12, 2),
    total_payment NUMERIC(12, 2),
    average_review_score NUMERIC(5, 2),
    delivery_days INTEGER,
    delivery_delay_days INTEGER
);

DROP TABLE IF EXISTS tmp_mart_order_summary;

CREATE TEMP TABLE tmp_mart_order_summary AS
WITH item_agg AS (
    SELECT
        order_id,
        COALESCE(SUM(price), 0)::NUMERIC(12, 2) AS total_item_value,
        COALESCE(SUM(freight_value), 0)::NUMERIC(12, 2) AS total_freight
    FROM staging.stg_order_items
    GROUP BY order_id
),
payment_agg AS (
    SELECT
        order_id,
        COALESCE(SUM(payment_value), 0)::NUMERIC(12, 2) AS total_payment
    FROM staging.stg_payments
    GROUP BY order_id
),
review_agg AS (
    SELECT
        order_id,
        ROUND(AVG(review_score), 2)::NUMERIC(5, 2) AS average_review_score
    FROM staging.stg_reviews
    GROUP BY order_id
)
SELECT
    o.order_id,
    c.customer_unique_id,
    c.customer_state,
    o.order_status,
    o.purchase_timestamp,
    o.delivered_date,
    o.estimated_delivery_date,
    COALESCE(i.total_item_value, 0.00) AS total_item_value,
    COALESCE(i.total_freight, 0.00) AS total_freight,
    COALESCE(p.total_payment, 0.00) AS total_payment,
    r.average_review_score,
    CASE
        WHEN o.delivered_date IS NOT NULL AND o.purchase_timestamp IS NOT NULL
        THEN (o.delivered_date::DATE - o.purchase_timestamp::DATE)::INTEGER
        ELSE NULL
    END AS delivery_days,
    CASE
        WHEN o.delivered_date IS NOT NULL AND o.estimated_delivery_date IS NOT NULL
        THEN (o.delivered_date::DATE - o.estimated_delivery_date::DATE)::INTEGER
        ELSE NULL
    END AS delivery_delay_days
FROM staging.stg_orders o
LEFT JOIN staging.stg_customers c ON o.customer_id = c.customer_id
LEFT JOIN item_agg i ON o.order_id = i.order_id
LEFT JOIN payment_agg p ON o.order_id = p.order_id
LEFT JOIN review_agg r ON o.order_id = r.order_id;
