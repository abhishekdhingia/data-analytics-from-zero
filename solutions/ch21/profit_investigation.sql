-- Worked examples for the review manuscript. Attempt exercises first.
-- Load core/retail_database_setup.sql, then solutions/ch15/completed_sales_setup.sql.

-- Case 21_view
CREATE VIEW dafz_practice.finance_events AS
SELECT 'sale'::text AS event_type,
       s.order_item_id::text AS event_id,
       s.sale_date AS event_date,s.location_id,p.category,
       s.gross_sales_paise AS gross_paise,
       s.discount_paise,
       s.sales_after_discount_paise AS sales_paise,
       0::bigint AS refund_paise,
       s.sale_cost_paise,
       0::bigint AS recovered_cost_paise
FROM dafz_practice.completed_sales AS s
JOIN dafz_v01.products AS p ON p.product_id=s.product_id
UNION ALL
SELECT 'return'::text,r.return_id::text,
       r.return_date,o.location_id,p.category,
       0::bigint,0::bigint,0::bigint,r.refund_paise,
       0::bigint,r.recovered_cost_paise
FROM dafz_v01.returns AS r
JOIN dafz_v01.order_items AS i
  ON i.order_item_id=r.order_item_id
JOIN dafz_v01.orders AS o ON o.order_id=i.order_id
JOIN dafz_v01.products AS p ON p.product_id=i.product_id
WHERE o.status='Completed';

-- Case 21_count
SELECT COUNT(*) AS rows,
       SUM(sales_paise) AS sales_paise,
       SUM(refund_paise) AS refund_paise
FROM dafz_practice.finance_events;

-- Case 21_annual
WITH yearly AS (
  SELECT 2024 AS year,
    SUM(gross_sales_paise) AS gross_paise,
    SUM(discount_paise) AS discount_paise,
    SUM(sales_after_discount_paise) AS sales_paise,
    SUM(refunds_paise) AS refund_paise,
    SUM(sale_cost_paise) AS sale_cost_paise,
    SUM(recovered_cost_paise) AS recovered_cost_paise
  FROM dafz_v01.historical_monthly_summary
  WHERE month_start>=DATE '2024-01-01'
    AND month_start<DATE '2025-01-01'
  UNION ALL
  SELECT 2025,SUM(gross_paise),SUM(discount_paise),
    SUM(sales_paise),SUM(refund_paise),
    SUM(sale_cost_paise),SUM(recovered_cost_paise)
  FROM dafz_practice.finance_events
  WHERE event_date>=DATE '2025-01-01'
    AND event_date<DATE '2026-01-01'
), metrics AS (
  SELECT *,sales_paise-refund_paise AS net_sales_paise,
    sale_cost_paise-recovered_cost_paise AS net_cogs_paise
  FROM yearly
)
SELECT *,net_sales_paise-net_cogs_paise AS gross_profit_paise,
  CASE WHEN net_sales_paise>0 THEN
    ROUND(100.0*(net_sales_paise-net_cogs_paise)
      /net_sales_paise,2)
  END AS gross_margin_pct
FROM metrics
ORDER BY year;

-- Case 21_category
WITH amounts AS (
  SELECT 2024 AS year,category AS segment,
    SUM(sales_after_discount_paise-refunds_paise) AS net_paise,
    SUM(sales_after_discount_paise-refunds_paise
        -sale_cost_paise+recovered_cost_paise) AS profit_paise
  FROM dafz_v01.historical_monthly_summary
  WHERE month_start>=DATE '2024-01-01'
    AND month_start<DATE '2025-01-01'
  GROUP BY category
  UNION ALL
  SELECT 2025,category,
    SUM(sales_paise-refund_paise),
    SUM(sales_paise-refund_paise-sale_cost_paise
        +recovered_cost_paise)
  FROM dafz_practice.finance_events
  WHERE event_date>=DATE '2025-01-01'
    AND event_date<DATE '2026-01-01'
  GROUP BY category
)
SELECT segment,
  SUM(CASE WHEN year=2024 THEN net_paise ELSE 0 END)
    AS net_2024_paise,
  SUM(CASE WHEN year=2025 THEN net_paise ELSE 0 END)
    AS net_2025_paise,
  SUM(CASE WHEN year=2024 THEN profit_paise ELSE 0 END)
    AS profit_2024_paise,
  SUM(CASE WHEN year=2025 THEN profit_paise ELSE 0 END)
    AS profit_2025_paise
FROM amounts
GROUP BY segment
ORDER BY segment;

-- Case 21_channel
WITH amounts AS (
  SELECT 2024 AS year,CASE WHEN location_id='WEB' THEN 'Online' ELSE 'Stores' END AS segment,
    SUM(sales_after_discount_paise-refunds_paise) AS net_paise,
    SUM(sales_after_discount_paise-refunds_paise
        -sale_cost_paise+recovered_cost_paise) AS profit_paise
  FROM dafz_v01.historical_monthly_summary
  WHERE month_start>=DATE '2024-01-01'
    AND month_start<DATE '2025-01-01'
  GROUP BY CASE WHEN location_id='WEB' THEN 'Online' ELSE 'Stores' END
  UNION ALL
  SELECT 2025,CASE WHEN location_id='WEB' THEN 'Online' ELSE 'Stores' END,
    SUM(sales_paise-refund_paise),
    SUM(sales_paise-refund_paise-sale_cost_paise
        +recovered_cost_paise)
  FROM dafz_practice.finance_events
  WHERE event_date>=DATE '2025-01-01'
    AND event_date<DATE '2026-01-01'
  GROUP BY CASE WHEN location_id='WEB' THEN 'Online' ELSE 'Stores' END
)
SELECT segment,
  SUM(CASE WHEN year=2024 THEN net_paise ELSE 0 END)
    AS net_2024_paise,
  SUM(CASE WHEN year=2025 THEN net_paise ELSE 0 END)
    AS net_2025_paise,
  SUM(CASE WHEN year=2024 THEN profit_paise ELSE 0 END)
    AS profit_2024_paise,
  SUM(CASE WHEN year=2025 THEN profit_paise ELSE 0 END)
    AS profit_2025_paise
FROM amounts
GROUP BY segment
ORDER BY segment;

-- Case 21_drivers
SELECT EXTRACT(YEAR FROM event_date)::integer AS year,
       ROUND(100.0*SUM(discount_paise)
         /NULLIF(SUM(gross_paise),0),2) AS discount_depth_pct,
       ROUND(100.0*SUM(refund_paise)
         /NULLIF(SUM(sales_paise),0),2) AS refund_amount_ratio_pct,
       SUM(refund_paise-recovered_cost_paise)
         AS return_profit_reduction_paise
FROM dafz_practice.finance_events
WHERE event_date>=DATE '2025-01-01'
  AND event_date<DATE '2026-01-01'
GROUP BY EXTRACT(YEAR FROM event_date)::integer;

-- Case 21_monthly
SELECT DATE_TRUNC('month',event_date)::date AS month_start,
       SUM(sales_paise-refund_paise) AS net_sales_paise,
       SUM(sales_paise-refund_paise-sale_cost_paise
           +recovered_cost_paise) AS profit_paise
FROM dafz_practice.finance_events
WHERE event_date>=DATE '2025-01-01'
  AND event_date<DATE '2026-01-01'
GROUP BY DATE_TRUNC('month',event_date)::date
ORDER BY month_start;

-- Case 21_returnonly
SELECT SUM(sales_paise) AS sales_paise,
       SUM(refund_paise) AS refunds_paise,
       SUM(recovered_cost_paise) AS recovered_paise
FROM dafz_practice.finance_events
WHERE event_date>=DATE '2026-01-01'
  AND event_date<DATE '2026-02-01';
