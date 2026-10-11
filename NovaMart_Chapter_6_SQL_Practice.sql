-- NovaMart original sample dataset: SQLite compatible
CREATE TABLE sales (order_id INTEGER PRIMARY KEY, product TEXT, units INTEGER, unit_price INTEGER, region TEXT, month TEXT);
INSERT INTO sales VALUES (3001, 'Laptop', 2, 50000, 'Delhi', 'Jan');
INSERT INTO sales VALUES (3002, 'Chair', 5, 5000, 'Mumbai', 'Jan');
INSERT INTO sales VALUES (3003, 'Mouse', 10, 800, 'Delhi', 'Jan');
INSERT INTO sales VALUES (3004, 'Laptop', 1, 50000, 'Mumbai', 'Feb');
INSERT INTO sales VALUES (3005, 'Chair', 8, 5000, 'Delhi', 'Feb');
INSERT INTO sales VALUES (3006, 'Mouse', 4, 800, 'Pune', 'Feb');
INSERT INTO sales VALUES (3007, 'Laptop', 3, 50000, 'Delhi', 'Mar');
INSERT INTO sales VALUES (3008, 'Chair', 4, 5000, 'Mumbai', 'Mar');
INSERT INTO sales VALUES (3009, 'Mouse', 6, 800, 'Pune', 'Mar');
INSERT INTO sales VALUES (3010, 'Monitor', 2, 15000, 'Delhi', 'Mar');
INSERT INTO sales VALUES (3011, 'Monitor', 1, 15000, 'Mumbai', 'Feb');
INSERT INTO sales VALUES (3012, 'Chair', 3, 5000, 'Pune', 'Jan');

-- Mission 1: show Delhi orders
SELECT * FROM sales WHERE region = 'Delhi';
-- Mission 2: revenue by product
SELECT product, SUM(units * unit_price) AS revenue FROM sales GROUP BY product ORDER BY revenue DESC;
