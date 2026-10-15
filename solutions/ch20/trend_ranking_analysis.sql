-- Worked examples for the review manuscript. Attempt exercises first.
-- Load core/retail_database_setup.sql, then solutions/ch15/completed_sales_setup.sql.

-- Case 20_1
WITH product_sales AS (
  SELECT p.category,p.product_id,p.product_name,
         SUM(s.sales_after_discount_paise) AS sales_paise
  FROM dafz_practice.completed_sales AS s
  JOIN dafz_v01.products AS p ON p.product_id=s.product_id
  GROUP BY p.category,p.product_id,p.product_name
), ranked AS (
  SELECT *,
    RANK() OVER (
      PARTITION BY category ORDER BY sales_paise DESC
    ) AS sales_rank,
    ROW_NUMBER() OVER (
      PARTITION BY category
      ORDER BY sales_paise DESC,product_id
    ) AS display_position
  FROM product_sales
)
SELECT category,product_id,product_name,
       ROUND(sales_paise/100.0,2) AS sales_inr,
       sales_rank,display_position
FROM ranked
WHERE display_position<=2
ORDER BY category,display_position;

-- Case 20_2
WITH monthly AS (
  SELECT DATE_TRUNC('month',sale_date)::date AS month_start,
         SUM(sales_after_discount_paise) AS sales_paise
  FROM dafz_practice.completed_sales
  GROUP BY DATE_TRUNC('month',sale_date)::date
), compared AS (
  SELECT *,LAG(sales_paise) OVER (
    ORDER BY month_start
  ) AS previous_paise
  FROM monthly
)
SELECT month_start,ROUND(sales_paise/100.0,2) AS sales_inr,
       ROUND(previous_paise/100.0,2) AS previous_inr,
       ROUND((sales_paise-previous_paise)/100.0,2)
         AS change_inr,
       CASE WHEN previous_paise>0
         THEN ROUND(100.0*(sales_paise-previous_paise)
                    /previous_paise,2)
       END AS change_pct
FROM compared
ORDER BY month_start;

-- Case 20_3
WITH monthly AS (
  SELECT DATE_TRUNC('month',sale_date)::date AS month_start,
         SUM(sales_after_discount_paise) AS sales_paise
  FROM dafz_practice.completed_sales
  GROUP BY DATE_TRUNC('month',sale_date)::date
)
SELECT month_start,
       ROUND(SUM(sales_paise) OVER (
         ORDER BY month_start
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       )/100.0,2) AS running_sales_inr
FROM monthly
ORDER BY month_start;

-- Case 20_4
WITH months AS (
  SELECT DISTINCT month_start
  FROM dafz_v01.calendar
  WHERE calendar_date>=DATE '2025-01-01'
    AND calendar_date<DATE '2025-04-01'
), supplied(month_start,sales_paise) AS (
  VALUES (DATE '2025-01-01',10000),
         (DATE '2025-03-01',30000)
), aligned AS (
  SELECT m.month_start,s.sales_paise
  FROM months AS m
  LEFT JOIN supplied AS s ON s.month_start=m.month_start
)
SELECT month_start,sales_paise,
       LAG(sales_paise) OVER (ORDER BY month_start)
         AS previous_month_paise
FROM aligned
ORDER BY month_start;
