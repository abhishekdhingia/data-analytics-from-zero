# Excel review pack validation

Version 0.2; original foundation 0.1.0. All data is fictional.

## Executed
- 201 Artifact Tool calculation checks passed, including lookup matches, totals and changing the extra-discount input to zero and restoring it.
- 354 saved-file checks passed: cached results, exact source arithmetic, table/chart objects, date types, cleaning totals, lookup/fallback agreement, monthly and store controls, and restart identity.
- 12 original workbooks were rendered across 41 worksheet views. Six restart workbooks are byte-for-byte copies of their verified solution/reference. Layout reviewed at normal rendered scale and via contact sheets.
- No cached spreadsheet error cells, VBA projects or external workbook links were found.
- Microsoft documentation was read for tables, PivotTables and XLOOKUP; see official_sources.md.

## Exact completion boundary
No Microsoft Excel process was used. Native Excel open/recalculate, sort/filter, XLOOKUP fallback compatibility, PivotTable construction/refresh, and one-page printing are NOT TESTED. Chapter 9 has zero native PivotTable objects, by disclosed design; its reference uses SUMIFS. Chapter 10 uses editable charts on formula summaries; the native pivot-backed version is pending. Inspecting exported XML is not application execution.

## Numerical controls
Shared sample: 183 sale lines, 72 completed orders, 556 units. Gross sales INR 557,026.00, discounts INR 66,533.90, sales after discount INR 490,492.10. Refunds are excluded from this stage.
CH06 extra scenario: 5% rounded per sale line gives INR 24,524.67 extra discount and INR 465,967.43 adjusted sales. Zero rate restores historical sales. The wrong relative-reference example intentionally retains 5, 0, 0 beside the corrected 5, 10, 15.
CH07: 202 source records = 197 accepted + 5 quarantined. Accepted sales INR 444,087.00. A dirty-source sales total is deliberately unavailable.
CH08: one unmatched P999 is retained, 182 matches; sales value unchanged. Numeric supplier key normalized by a documented mapping rule.
CH09 append record: +1 line, +1 order, +2 units, +INR 324 sales. Actual native pivot refresh remains pending.

Known construction issue resolved: summary formulas initially referenced a sheet before it was created. The builder now creates referenced sheets first. Final source/runtime checks are recorded in artifact_checks.json and export_checks.csv.

Publication is gated on resolving the native checks above, not on this report's file-generation passes alone.
