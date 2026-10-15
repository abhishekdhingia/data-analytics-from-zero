-- Worked examples for the review manuscript. Attempt exercises first.
-- Load core/retail_database_setup.sql, then solutions/ch15/completed_sales_setup.sql.

-- Case 19_1
WITH classified AS (
  SELECT order_item_id,sales_after_discount_paise,
    CASE
      WHEN gross_sales_paise<=0 THEN 'Review denominator'
      WHEN discount_paise=0 THEN 'No discount'
      WHEN discount_paise*100<=gross_sales_paise*10
        THEN 'Up to 10%'
      WHEN discount_paise*100<=gross_sales_paise*20
        THEN 'Above 10% to 20%'
      ELSE 'Above 20%'
    END AS discount_band
  FROM dafz_practice.completed_sales
)
SELECT discount_band,COUNT(*) AS lines,
       SUM(sales_after_discount_paise) AS sales_paise
FROM classified
GROUP BY discount_band
ORDER BY discount_band;

-- Case 19_2
WITH monthly_category AS (
  SELECT DATE_TRUNC('month',s.sale_date)::date AS month_start,
         p.category,
         SUM(s.sales_after_discount_paise) AS sales_paise
  FROM dafz_practice.completed_sales AS s
  JOIN dafz_v01.products AS p ON p.product_id=s.product_id
  GROUP BY DATE_TRUNC('month',s.sale_date)::date,p.category
)
SELECT month_start,category,
       ROUND(sales_paise/100.0,2) AS sales_inr
FROM monthly_category
ORDER BY month_start,category;

-- Case 19_3
SELECT c.customer_id,c.segment
FROM dafz_v01.customers AS c
WHERE c.customer_id IN (
  SELECT customer_id
  FROM dafz_v01.orders
  WHERE status='Completed' AND customer_id IS NOT NULL
    AND order_date>=DATE '2025-01-01'
    AND order_date<DATE '2025-02-01'
  GROUP BY customer_id
  HAVING COUNT(*)>=2
)
ORDER BY c.customer_id;

-- Case 19_4
WITH monthly AS (
  SELECT DATE_TRUNC('month',sale_date)::date AS month_start,
         SUM(sales_after_discount_paise) AS sales_paise
  FROM dafz_practice.completed_sales
  GROUP BY DATE_TRUNC('month',sale_date)::date
)
SELECT SUM(sales_paise) AS staged_paise,
       (SELECT SUM(sales_after_discount_paise)
        FROM dafz_practice.completed_sales) AS direct_paise
FROM monthly;
