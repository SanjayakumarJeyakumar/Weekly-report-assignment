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
