-- Worked examples for the review manuscript. Attempt exercises first.
-- Load core/retail_database_setup.sql, then solutions/ch15/completed_sales_setup.sql.

-- Case 16_1
SELECT product_id AS product_code, product_name, category
FROM products
ORDER BY product_id
LIMIT 5;

-- Case 16_2
SELECT order_id, order_date, location_id, status
FROM orders
WHERE status='Completed'
  AND location_id='WEB'
  AND order_date >= DATE '2025-01-01'
  AND order_date < DATE '2025-02-01'
ORDER BY order_date, order_id;

-- Case 16_3
SELECT order_id, location_id, status
FROM orders
WHERE status='Completed'
  AND (location_id='S01' OR location_id='WEB')
ORDER BY order_id;

-- Case 16_4
SELECT order_id, order_date, location_id, customer_id
FROM orders
WHERE status='Completed' AND customer_id IS NULL
ORDER BY order_date, order_id;

-- Case 16_5
SELECT order_item_id, order_id, quantity,
       ROUND(sales_after_discount_paise/100.0,2) AS sales_inr
FROM dafz_practice.completed_sales
ORDER BY quantity DESC, order_item_id ASC
LIMIT 5;
