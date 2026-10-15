-- Worked examples for the review manuscript. Attempt exercises first.
-- Load core/retail_database_setup.sql, then solutions/ch15/completed_sales_setup.sql.

-- Case 18_1
SELECT COUNT(*) AS sale_lines,
       SUM(s.sales_after_discount_paise) AS sales_paise
FROM dafz_practice.completed_sales AS s
JOIN products AS p ON p.product_id=s.product_id;

-- Case 18_enriched
SELECT s.order_item_id,s.product_id,p.product_name,p.category
FROM dafz_practice.completed_sales AS s
JOIN products AS p ON p.product_id=s.product_id
ORDER BY s.order_item_id
LIMIT 5;

-- Case 18_fixture
CREATE TEMP TABLE join_sales
(line_id TEXT PRIMARY KEY,product_id TEXT,sales_paise INTEGER);
INSERT INTO join_sales VALUES
('J1','P001',100000),('J2','P002',200000),('J3','P003',50000);
CREATE TEMP TABLE join_returns
(return_id TEXT PRIMARY KEY,line_id TEXT,refund_paise INTEGER);
INSERT INTO join_returns VALUES
('JR1','J1',20000),('JR2','J1',30000),('JR3','J3',10000);
CREATE TEMP TABLE audit_input (line_id TEXT PRIMARY KEY,product_id TEXT);
INSERT INTO audit_input VALUES
('A1','P001'),('A2','P999'),('A3',NULL);

-- Case 18_2
SELECT a.line_id,a.product_id,
       CASE WHEN a.product_id IS NULL THEN 'Missing identifier'
            ELSE 'Unknown identifier' END AS issue
FROM audit_input AS a
LEFT JOIN products AS p ON p.product_id=a.product_id
WHERE p.product_id IS NULL
ORDER BY a.line_id;

-- Case 18_3
SELECT COUNT(*) AS joined_rows,
       SUM(s.sales_paise) AS sales_paise,
       SUM(r.refund_paise) AS refunds_paise
FROM join_sales AS s
LEFT JOIN join_returns AS r ON r.line_id=s.line_id;

-- Case 18_detail
SELECT s.line_id,s.sales_paise,r.return_id,r.refund_paise
FROM join_sales AS s
LEFT JOIN join_returns AS r ON r.line_id=s.line_id
ORDER BY s.line_id,r.return_id;

-- Case 18_4
WITH return_totals AS (
  SELECT line_id,SUM(refund_paise) AS refund_paise
  FROM join_returns
  GROUP BY line_id
)
SELECT COUNT(*) AS joined_rows,
       SUM(s.sales_paise) AS sales_paise,
       SUM(COALESCE(r.refund_paise,0)) AS refunds_paise,
       SUM(s.sales_paise-COALESCE(r.refund_paise,0))
         AS remaining_sales_paise
FROM join_sales AS s
LEFT JOIN return_totals AS r ON r.line_id=s.line_id;
