-- Worked examples for the review manuscript. Attempt exercises first.
-- Load core/retail_database_setup.sql, then solutions/ch15/completed_sales_setup.sql.

-- Case view_setup
CREATE SCHEMA dafz_practice;
CREATE VIEW dafz_practice.completed_sales AS
SELECT i.order_item_id, i.order_id, o.order_date AS sale_date,
       o.location_id, o.customer_id, i.product_id, i.quantity,
       i.quantity*i.unit_price_paise AS gross_sales_paise,
       i.discount_paise,
       i.quantity*i.unit_price_paise-i.discount_paise
         AS sales_after_discount_paise,
       i.quantity*i.unit_cost_paise AS sale_cost_paise
FROM dafz_v01.order_items AS i
JOIN dafz_v01.orders AS o ON o.order_id=i.order_id
WHERE o.status='Completed';
