-- CH18: Run after core/retail_database_setup.sql, using the edition schema.
-- E01: Compare line count and sales before/after enriching completed lines with products.
-- E02: LEFT JOIN the temporary audit input; list unmatched keys.
-- E03: Run the intentionally faulty query. Record row count and inflated sales.
-- E04: Aggregate return events by sale line, LEFT JOIN, and reconcile again.
-- Save as validated_joins.sql. Compare solutions/ch18 and join_control_totals.csv.
CREATE TEMP TABLE join_sales (line_id TEXT PRIMARY KEY, product_id TEXT, sales_paise INTEGER);
INSERT INTO join_sales VALUES ('J1','P001',100000),('J2','P002',200000),('J3','P003',50000);
CREATE TEMP TABLE join_returns (return_id TEXT PRIMARY KEY,line_id TEXT,refund_paise INTEGER);
INSERT INTO join_returns VALUES ('JR1','J1',20000),('JR2','J1',30000),('JR3','J3',10000);
CREATE TEMP TABLE audit_input (line_id TEXT PRIMARY KEY,product_id TEXT);
INSERT INTO audit_input VALUES ('A1','P001'),('A2','P999'),('A3',NULL);
-- Intentionally faulty: one sales amount is counted once per return event.
SELECT COUNT(*) AS joined_rows,SUM(s.sales_paise) AS sales_paise,
       SUM(r.refund_paise) AS refund_paise
FROM join_sales s LEFT JOIN join_returns r ON r.line_id=s.line_id;
