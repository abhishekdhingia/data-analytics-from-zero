# Chapter 9 — Summarizing performance with PivotTables
Open `pivots_start.xlsx` and save as `performance_pivots.xlsx`. SalesData contains the verified source and a first-order-line helper for counting distinct orders over the full sample. The helper is not additive across arbitrary filtered categories.

**Delivery status:** This pack does not contain a completed native PivotTable workbook. `pivot_reference.xlsx` contains live SUMIFS reference results, clearly labeled as such. Follow the steps below in Excel to create the native solution; record its version and test refresh before publication.

## CH09-E01 — Store by category
Click inside SalesData. Select Insert > PivotTable > From Table/Range if that submenu appears. Confirm SalesData as the source and choose New Worksheet. Drag Location to Rows, Category to Columns, and Sales after discount to Values. Open the value field settings and select Sum if Excel has chosen Count. Rename the sheet Store pivot. Pass: seven reporting locations, five categories and grand total INR 490,492.10. Compare every matrix cell against the reference workbook.

## CH09-E02 — Monthly trend
Create another PivotTable from SalesData on a new sheet. Put Sale date in Rows and Sales after discount in Values. Right-click one date and choose Group; select Years and Months. If grouping is unavailable, inspect the source for text dates or blanks. Pass: 12 chronological 2025 months and the same grand total. The exact monthly values are in reference/controls.json and the reference workbook.

## CH09-E03 — Units and sales
Create a third pivot with Category in Rows and both Units and Sales after discount in Values, each summarized by Sum. Units total 556. Label the two measures clearly: an amount is not a quantity. Compare each category to the reference table.

## CH09-E04 — Refresh a copy
Save a separate copy before this test. Open `refresh_test_row.csv`; transfer its one record into the row directly below SalesData. Confirm the table expands. If needed use Table Design > Resize Table to include the new row. Preserve the date as a real date and fill any calculated columns. Right-click each PivotTable and choose Refresh.

Pass: 184 lines, 73 orders, 558 units and sales INR 490,816.10. The increment is 324 INR and belongs to January / S01 / Kitchen. Re-appending the same test row is a duplicate, not another sale. Close the test copy; keep the original baseline unchanged. The formula-reference workbook uses bounded ranges, so extending its source also requires extending those formulas; it does not demonstrate native pivot refresh.

## CH09-E05 — Count the right grain
The baseline has 183 lines but only 72 distinct order IDs. Count of Order ID in an ordinary pivot counts line occurrences. Check the full-sample order count by summing First order line, then explain why counting rows would overstate orders. Never add distinct-order counts across overlapping categories.


## Environment note
These instructions target an English-language Excel desktop workflow. They are development instructions: the files were calculated and rendered with Artifact Tool, but the clicks have not been executed in Microsoft Excel. Record your Excel version when testing. Formula examples use commas; some regional settings require semicolons. Use a copy of the starting file and keep Raw inputs unchanged. Do not enable macros: these files contain none.

All business records are fictional. This pack is self-contained; earlier chapter success is not a prerequisite. The core sample contains 183 completed sale lines from 72 selected orders across 2025. It is a small, non-random teaching sample, not an annual total. INR amounts exclude tax and refunds. Chapter 7 intentionally uses a different 202-row import. Do not carry its totals into the other chapters.
