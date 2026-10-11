CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.stg_orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    order_status TEXT,
    purchase_timestamp TIMESTAMP,
    delivered_date TIMESTAMP,
    estimated_delivery_date TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.stg_customers (
    customer_id TEXT PRIMARY KEY,
    customer_unique_id TEXT,
    customer_state TEXT
);

CREATE TABLE IF NOT EXISTS staging.stg_order_items (
    order_id TEXT,
    product_id TEXT,
    seller_id TEXT,
    price NUMERIC(10, 2),
    freight_value NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS staging.stg_payments (
    order_id TEXT,
    payment_type TEXT,
    payment_value NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS staging.stg_reviews (
    order_id TEXT,
    review_score INTEGER
);

DROP TABLE IF EXISTS tmp_stg_orders;
CREATE TEMP TABLE tmp_stg_orders AS
SELECT
    order_id::TEXT,
    customer_id::TEXT,
    order_status::TEXT,
    order_purchase_timestamp::TIMESTAMP AS purchase_timestamp,
    order_delivered_customer_date::TIMESTAMP AS delivered_date,
    order_estimated_delivery_date::TIMESTAMP AS estimated_delivery_date
FROM public.olist_orders_dataset;

DROP TABLE IF EXISTS tmp_stg_customers;
CREATE TEMP TABLE tmp_stg_customers AS
SELECT
    customer_id::TEXT,
    customer_unique_id::TEXT,
    customer_state::TEXT
FROM public.olist_customers_dataset;

DROP TABLE IF EXISTS tmp_stg_order_items;
CREATE TEMP TABLE tmp_stg_order_items AS
SELECT
    order_id::TEXT,
    product_id::TEXT,
    seller_id::TEXT,
    price::NUMERIC(10, 2) AS price,
    freight_value::NUMERIC(10, 2) AS freight_value
FROM public.olist_order_items_dataset;

DROP TABLE IF EXISTS tmp_stg_payments;
CREATE TEMP TABLE tmp_stg_payments AS
SELECT
    order_id::TEXT,
    payment_type::TEXT,
    payment_value::NUMERIC(10, 2) AS payment_value
FROM public.olist_order_payments_dataset;

DROP TABLE IF EXISTS tmp_stg_reviews;
CREATE TEMP TABLE tmp_stg_reviews AS
SELECT
    order_id::TEXT,
    review_score::INTEGER AS review_score
FROM public.olist_order_reviews_dataset
WHERE review_score BETWEEN 1 AND 5;
