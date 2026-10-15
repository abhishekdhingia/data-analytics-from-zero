# Metric rules, version 0.1.0
All businesses, records, identifiers, amounts and outcomes are fictional and generated specifically for this project. No real customer names, contacts, or addresses are included. Retailer naming remains undecided.

## Units and rounding
Canonical money columns end in _paise and contain integer paise: INR 1 = 100 paise. Convert to INR by dividing by 100.0, not by relabeling the column. CSV files are UTF-8 with headers, comma delimiters, ISO dates and empty fields for nulls. There are no thousands separators. INR teaching exports have exactly two decimal places. Reconcile canonical money exactly (tolerance 0 paise); after conversion to INR compare rounded values to two decimals. Calculated percentages use the full ratio, displayed to two decimal percentage points. Half-up applies when generating target paise. Do not sum rounded margin percentages.

## Eligibility and grain
Orders have one row per order; order_items one row per line; returns one row per return event. Only Completed orders contribute sales, sold quantity, order counts and sale costs. Cancelled orders and their lines are retained for status exercises but contribute zero recognized sales/cost. Customer null means guest or unidentified, not a failed numeric conversion. No anonymous identity is inferred. Missing product/location keys are forbidden in core.

Gross sales = SUM(quantity × unit_price_paise) on eligible sale lines.
Discount = SUM(discount_paise), a LINE total, not a per-unit amount.
Sales after discount = gross sales − discount.
Refunds = SUM(refund_paise) by return event date.
Net sales = eligible sales after discount posted in the period − refunds posted in the period.
Sale cost = SUM(quantity × transaction-time unit_cost_paise).
Net COGS = sale cost − recovered inventory cost posted on return dates.
Gross profit = net sales − net COGS.
Gross margin = gross profit / net sales only when net sales > 0; otherwise undefined/blank, with the amounts still shown.
Basic sales AOV = sales after discount / distinct completed orders in the sale period. Under product/category filters, count distinct orders containing eligible lines in the selected slice. Slice order counts are not additive across categories. With no completed orders AOV is undefined, including a return-only period.
Return-adjusted cohort AOV = (sales after discount for chosen original orders − their refunds up to an explicit as-of date) / distinct chosen completed orders. Never label event-period net sales divided by new orders as basic sales AOV.

## Returns and reporting cutoff
Each event references its original line. Per-unit discounted selling price is (quantity × unit price − discount) / quantity. Generation ensures this is an integer number of paise. Partial refund = returned quantity × that original discounted unit price. Cumulative returns cannot exceed sold quantity or line sales. Recovered cost is explicitly recorded: damaged goods recover zero, other modeled returns recover their original unit cost. This simplified policy is fictional, not a claim about real accounting practice.
Core sale dates: 2025-01-01 through 2025-12-31. Core event cutoff: 2026-01-31. Thus late returns are available for cohort analysis but excluded from 2025 event-period totals. January 2026 is a return-only period in this frozen dataset. Calendar extends through 2026 for the future quarter and refresh exercises; future calendar rows are not sales records. Returns are attributed to the original sale location/product, not a separately modeled processing location. No pre-2025-origin returns enter 2025: the simulation explicitly excludes opening return obligations. The 2024 comparator also excludes opening obligations and includes only events posted in 2024.

## Comparison, targets and scope
2024 summary is a separate seeded synthetic scenario aggregated to month-location-category, with matching currency and metric definitions. No 2024 customer-level inference is supported by the distributed summary. Targets are 110% of prior-year net sales and 108% of prior-year gross profit per month-location, rounded half-up to one paise. Targets have no category breakdown. Never multiply monthly targets by joining them to sale lines.
Inventory snapshots are end-of-month point-in-time values; do not sum them across months or infer lost sales from a zero stock observation. Snapshot movements are not a modeled stock ledger.
All sale values exclude tax. Shipping, payroll, rent, and other operating expenses are absent. Gross profit is available; net profit is not.
Discount depth and product mix vary by scenario. These are deliberately designed teaching patterns. Observed associations do not establish promotional causation or forecast real performance.
