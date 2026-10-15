-- Run join_cases.sql in this same session first. No DISTINCT used to hide duplication.
-- E01: Many completed lines to one unique product.
SELECT COUNT(*) AS sale_lines, SUM(i.quantity*i.unit_price_paise-i.discount_paise) AS sales_paise
FROM order_items i JOIN orders o ON o.order_id=i.order_id WHERE o.status='Completed';
SELECT COUNT(*) AS sale_lines, SUM(i.quantity*i.unit_price_paise-i.discount_paise) AS sales_paise
FROM order_items i JOIN orders o ON o.order_id=i.order_id
JOIN products p ON p.product_id=i.product_id WHERE o.status='Completed';
-- E02: One missing identifier and one unknown identifier, separately visible.
SELECT a.line_id,a.product_id,
 CASE WHEN a.product_id IS NULL THEN 'Missing identifier' ELSE 'Unknown identifier' END AS issue
FROM audit_input a LEFT JOIN products p ON p.product_id=a.product_id
WHERE p.product_id IS NULL ORDER BY a.line_id;
-- E04: One row per sale line after pre-aggregation; all three sales survive.
WITH return_totals AS (
 SELECT line_id,SUM(refund_paise) AS refund_paise FROM join_returns GROUP BY line_id
)
SELECT COUNT(*) AS joined_rows,SUM(s.sales_paise) AS sales_paise,
       SUM(COALESCE(r.refund_paise,0)) AS refund_paise
FROM join_sales s LEFT JOIN return_totals r ON r.line_id=s.line_id;
