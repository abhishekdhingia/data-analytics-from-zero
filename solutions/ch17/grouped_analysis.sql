-- Worked examples for the review manuscript. Attempt exercises first.
-- Load core/retail_database_setup.sql, then solutions/ch15/completed_sales_setup.sql.

-- Case 17_1
SELECT location_id,
       COUNT(*) AS sale_lines,
       COUNT(DISTINCT order_id) AS completed_orders,
       SUM(sales_after_discount_paise) AS sales_paise,
       ROUND(SUM(sales_after_discount_paise)/100.0,2) AS sales_inr
FROM dafz_practice.completed_sales
GROUP BY location_id
ORDER BY location_id;

-- Case 17_2
SELECT COUNT(*) AS sale_lines,
       COUNT(order_id) AS nonnull_order_ids,
       COUNT(DISTINCT order_id) AS completed_orders,
       SUM(quantity) AS units
FROM dafz_practice.completed_sales;

-- Case 17_3
SELECT ROUND(SUM(sales_after_discount_paise)/100.0,2) AS sales_inr,
       COUNT(DISTINCT order_id) AS completed_orders,
       ROUND(SUM(sales_after_discount_paise)/100.0
         /NULLIF(COUNT(DISTINCT order_id),0),2) AS sales_aov_inr,
       ROUND(AVG(sales_after_discount_paise)/100.0,2) AS mean_line_inr
FROM dafz_practice.completed_sales;

-- Case 17_4
SELECT location_id,
       ROUND(SUM(sales_after_discount_paise)/100.0,2) AS sales_inr
FROM dafz_practice.completed_sales
WHERE sale_date >= DATE '2025-01-01'
  AND sale_date < DATE '2025-02-01'
GROUP BY location_id
HAVING SUM(sales_after_discount_paise) > 70000000
ORDER BY sales_inr DESC, location_id;
