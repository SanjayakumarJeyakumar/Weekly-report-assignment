-- ============================================================================
-- Query 2: Top 3 Product Categories by Customer State
-- File: sql/05_top_categories_by_state.sql
-- Description:
--   Ranks the top 3 product categories by GMV for each Brazilian customer state
--   using DENSE_RANK() window function.
--
-- Business Rules & Methodology:
--   1. Joins:
--      - staging.stg_order_items (item prices)
--      - staging.stg_orders (order eligibility)
--      - staging.stg_customers (customer_state)
--      - public.olist_products_dataset (product categories)
--      - public.product_category_name_translation (English translations)
--   2. Revenue Definition: Pure item price value (SUM(price)), strictly excluding freight.
--   3. Category Labeling: Prefers English translation, falling back to original Portuguese
--      or 'uncategorized' if undefined.
--   4. Excludes canceled and unavailable orders.
--   5. DENSE_RANK() partitions by customer_state and orders by total_revenue DESC.
-- ============================================================================

WITH category_state_revenue AS (
    SELECT 
        c.customer_state,
        COALESCE(t.product_category_name_english, p.product_category_name, 'uncategorized') AS category_name,
        SUM(i.price)::NUMERIC(12, 2) AS total_revenue
    FROM staging.stg_order_items i
    JOIN staging.stg_orders o ON i.order_id = o.order_id
    JOIN staging.stg_customers c ON o.customer_id = c.customer_id
    JOIN public.olist_products_dataset p ON i.product_id = p.product_id
    LEFT JOIN public.product_category_name_translation t ON p.product_category_name = t.product_category_name
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY 
        c.customer_state,
        COALESCE(t.product_category_name_english, p.product_category_name, 'uncategorized')
),

ranked_categories AS (
    SELECT 
        customer_state,
        category_name,
        total_revenue,
        DENSE_RANK() OVER (
            PARTITION BY customer_state 
            ORDER BY total_revenue DESC
        ) AS category_rank
    FROM category_state_revenue
)

SELECT 
    customer_state,
    category_rank,
    category_name,
    total_revenue
FROM ranked_categories
WHERE category_rank <= 3
ORDER BY customer_state, category_rank;
