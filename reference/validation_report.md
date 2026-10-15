# Data foundation validation report

Dataset version 0.1.0. Seed 20261012. Checks run using Python 3.12.14 and SQLite 3.53.1.

Executed checks: 76. Passed: 76. Failed: 0. Full evidence: validation_checks.csv.

## Core records

|Table|Rows|
|---|---:|
|products|60|
|customers|2,500|
|locations|7|
|orders|12,000|
|order_items|30,000|
|returns|3,272|
|inventory|5,040|
|targets|84|
|calendar|1,096|
|historical_monthly_summary|420|

Completed orders: 11,707; eligible sale lines: 29,268. Cancelled orders remain in the source but contribute no sales.

## Annual comparison (event-period rules)

|Metric|2024|2025|
|---|---:|---:|
|gross sales|INR 42,601,920.00|INR 72,283,936.00|
|discount|INR 1,273,991.10|INR 8,462,926.00|
|sales after discount|INR 41,327,928.90|INR 63,821,010.00|
|refunds|INR 1,459,248.10|INR 3,699,982.60|
|net sales|INR 39,868,680.80|INR 60,121,027.40|
|net cogs|INR 30,066,270.52|INR 54,542,019.28|
|gross profit|INR 9,802,410.28|INR 5,579,008.12|

2025 gross margin: 9.28%. Basic sales AOV: INR 5,451.53.

Higher sales, lower gross profit, deeper discounting and higher electronics share are verified features of this constructed dataset. They support investigation; they do not prove a causal effect of promotions. See the exact checks and metric rules.

## Teaching cases

First assignment: 12 rows, INR 14,708.00 sales.
Cleaning source: 202 inputs = 197 accepted + 3 unresolved originals + 2 duplicate imports. Accepted sales after discount: INR 444,087.00. Raw financial totals must be labeled unavailable because missing price and text quantity cannot be summed reliably.
Join fixture: 3 sale lines become 4 joined rows; apparent sales rise from INR 3,500 to INR 4,500. Pre-aggregation restores INR 3,500 sales and INR 600 refunds.
January 2026: no new core sales, INR 111,654.40 refunds. The date spine must preserve this return-only period.
Refresh fixture: +1 completed order, +1 line, +INR 324 sales and +INR 108 gross profit. Duplicate reapplication is rejected. SQL test changes were rolled back.

## Execution limits and next gates

Executed: Python generation, independent Decimal calculations, SQLite schema/import constraints, relationships, return limits, 420 current slices, 420 historical slices, chapter numeric fixtures and controlled source append. Monetary equality is exact in paise.
NOT executed: PostgreSQL application/database setup, Excel formulas/PivotTables, Power Query/DAX/PBIX refresh, desktop UI steps, platform/licensing checks or GitHub download tests. No application pass is inferred from this report.
The archive is a data foundation. Native XLSX/PBIX chapter files, remaining exercises and answer ledger entries, Q1 2026 and service-desk projects, publication downloads and manuscript remain pending.

## Reproduction and integrity

Use scripts/build_data.py followed by scripts/validate_data.py in a copy of the edition folder. Manifest lists SHA-256 hashes for all included files except the manifest itself. validation.sqlite is an author QA database. Historical build_inputs are author QA evidence for the distributed 2024 summary, not a substitute for a future learner project.
