# Excel practice guides — Chapters 5–10

These instructions target an English-language Excel desktop workflow. They are development instructions: the files were calculated and rendered with Artifact Tool, but the clicks have not been executed in Microsoft Excel. Record your Excel version when testing. Formula examples use commas; some regional settings require semicolons. Use a copy of the starting file and keep Raw inputs unchanged. Do not enable macros: these files contain none.

All business records are fictional. This pack is self-contained; earlier chapter success is not a prerequisite. The core sample contains 183 completed sale lines from 72 selected orders across 2025. It is a small, non-random teaching sample, not an annual total. INR amounts exclude tax and refunds. Chapter 7 intentionally uses a different 202-row import. Do not carry its totals into the other chapters.


# Chapter 5 — Finding your way around Excel
Meera asks you to organize the sample so a colleague can find a store's sales without losing records.

## CH05-E01 — Make a table
Open `excel_navigation_start.xlsx`. Choose File > Save As and save your copy as `sales_table.xlsx`. On Sales, click the Name Box to the left of the formula bar, type `A6:M189`, and press Enter. Select Insert > Table. Confirm the exact range and tick My table has headers. Click OK. With a cell in the table selected, use Table Design > Table Name to enter `SalesData`.

The title and note above row 6 are not table records. Pass: 183 data rows and 13 fields; headers begin at row 6. The original range is not already a native table, so this task creates one.

## CH05-E02 — Format without changing values
Select C7:C189. Press Ctrl+1, select Custom, enter `dd mmm yyyy`, and confirm. Select I7:M189; use a Number format with two decimal places, or the supplied INR format. Click a price and inspect the formula bar: formatting has not changed the underlying numeric value. Units in H should have zero decimal places.

## CH05-E03 — Apply two filters
Open the Location header arrow. Clear Select All, select S01, and confirm. In Category, select Electronics in the same way. Pass: 8 visible rows, with sales after discount INR 47,187.50. For a visible-only sum in a blank cell outside the table, use `=SUBTOTAL(109,M7:M189)`. Ordinary SUM includes filtered-out rows. Record your observation, then clear both filters.

## CH05-E04 — Sort safely
Use the Sale date header arrow to sort newest to oldest. Inspect one complete record across the row. Then sort oldest to newest. Do not select and sort an isolated column. Pass: 183 rows, 72 original order IDs and unchanged total sales INR 490,492.10. Save with all filters cleared. The solution file represents a complete, unfiltered table; it is not a screenshot of the temporary filter exercise.


# Chapter 6 — Formulas that answer business questions
Kabir needs calculations that change when the inputs change. Work from `formulas_start.xlsx`; save as `sales_calculations.xlsx`.

## CH06-E01 — Calculate each line
On Sales, click L7 and type `=ROUND(H7*I7,2)`. Press Enter. Select L7:L189 and press Ctrl+D to fill down if the table has not already filled the column. In M7 enter `=L7-J7`; fill M7:M189. The discount in J is the entire line's discount, not a per-unit discount. Do not multiply it by quantity again.

On Calculations, enter `=SUM(Sales!L7:L189)` in B7, `=SUM(Sales!J7:J189)` in B8 and `=SUM(Sales!M7:M189)` in B9. Expected values: INR 557,026.00, INR 66,533.90 and INR 490,492.10, respectively. Inspect a first, middle and final line before trusting the total.

## CH06-E02 — Copy a fixed reference
Calculations E7 holds a hypothetical extra rate of 5%. Back on Sales, type `=ROUND(M7*Calculations!$E$7,2)` in N7 and `=M7-N7` in O7. Fill both formulas to row 189. The row reference M7 moves; $E$7 stays fixed. Round each extra line discount before summing.

On Calculations, E8 is `=B9`, E9 is `=SUM(Sales!N7:N189)`, and E10 is `=E8-E9`. Pass: E9 = INR 24,524.67, E10 = INR 465,967.43. Change E7 to 0%; E10 should equal B9. Restore 5%. These scenario amounts do not rewrite historical sales.

## CH06-E03 — Summarize one store
In B10 enter `=SUMIFS(Sales!M7:M189,Sales!D7:D189,"S01")`. B11 uses `=COUNTIFS(Sales!D7:D189,"S01")`. B12 is `=COUNT(Sales!I7:I189)`; B13 is `=COUNTA(Sales!A7:A189)`. Pass: store sales INR 60,028.40, 26 S01 lines, and 183 in each final count. These are line counts, not distinct orders.

## CH06-E04 — Diagnose mistakes
In D18 type `=IF(C18=0,"Undefined",B18/C18)` and fill to D19. The answers are Undefined and 5. Undefined is not zero.

Inspect C25:C27: the copied relative rate reference produces 5, 0, 0 because the rate moves into blank cells. In D25 enter `=A25*$B$25`, then fill through D27. Correct results: 5, 10, 15. Explain the difference in one sentence. This intentionally faulty demonstration remains visible in the solution for comparison.


# Chapter 7 — Cleaning a messy sales file
The import disagrees with finance. Your task is to explain which rows can be trusted, not to force a plausible total. Start from `sales_dirty.xlsx`, save as `sales_cleaned.xlsx`, and work on Working. Raw must remain unchanged.

## CH07-E01 — Profile first
Headers are at row 6 and the 202 imported records occupy rows 7–208. Count source-row IDs separately from sale-line IDs. Check whether dates, units and prices are text, numeric, or blank. Do not publish a raw revenue total: the source contains a missing price and an invalid quantity. A SUM that skips invalid values is incomplete.

## CH07-E02 — Repair with evidence
Use temporary helper columns to trim category whitespace with `=TRIM(E7)` and compare the product key in D against Products. Use the approved category in Products, not an invented spelling. SRC0003 has surrounding whitespace and SRC0005 has a case variant. SRC0009 has whitespace around its units; trim and convert it to a number. Record the source-row ID, old value, new value and reason in a cleaning log.

## CH07-E03 — Resolve the date convention
The supplier declares slash dates as DD/MM/YYYY. SRC0007 is the controlled example. Do not let your locale silently interpret it as MM/DD/YYYY. For a slash date in C13, construct the date explicitly with `=DATE(VALUE(RIGHT(C13,4)),VALUE(MID(C13,4,2)),VALUE(LEFT(C13,2)))`. Compare against the ISO-format neighbors. Format the numeric result as yyyy-mm-dd. Apply this rule only to the documented slash-date case; do not apply its text positions to ISO dates.

## CH07-E04 — Separate unresolved rows
Filter Source row ID and move copies of SRC0011, SRC0013 and SRC0015 into Quarantine: missing price, unapproved quantity text and unknown product key. Do not fill a price from a current catalog or guess that a word means a permitted quantity.

SRC0201 and SRC0202 are confirmed duplicate imports of SRC0021 and SRC0031. Compare line ID and every source field, not just product and amount. Quarantine the duplicate copies and retain the originals. Different line IDs can be legitimate similar purchases. SRC0017's missing customer ID is a legitimate guest and stays blank.

## CH07-E05 — Reconcile
Create Accepted from the remaining repaired records, using actual numeric prices and units and real Excel dates. In J7 enter `=ROUND(F7*G7-H7,2)` and fill down. Pass: 197 accepted rows + 3 unresolved originals + 2 duplicate copies = 202 inputs; accepted sales after discount = INR 444,087.00. Accepted must have unique line IDs. Quarantine retains the original values. The separate solution workbook supplies Accepted, Quarantine, Raw, Products and the decision log.


# Chapter 8 — Bringing information together
Finance wants consistent product labels. Open `lookups_start.xlsx` and save as `sales_enriched.xlsx`. Sales F/G and N:Q are deliberately blank. Unit cost in K is historical and must stay unchanged.

## CH08-E01 — Validate the lookup master
Products A7:A66 contains 60 approved keys. In a temporary column, `=COUNTIFS($A$7:$A$66,A7)` filled down should return 1 for every key. The Duplicate case sheet is an isolated optional fixture: P001 occurs twice with conflicting categories. Flag it as Ambiguous; do not use it as the live product master.

## CH08-E02 — Normalize and match
The supplier's documented numeric-code rule is P followed by three digits (25 maps to P025). On Sales, enter `=IF(ISNUMBER(E7),"P"&TEXT(E7,"000"),TRIM(E7))` in N7. In O7 enter `=COUNTIFS(Products!$A$7:$A$66,N7)`. In P7 enter `=IF(O7=0,"Unmatched",IF(O7>1,"Ambiguous","Matched"))`. Fill each to row 189.

Enter `=IF(O7<>1,P7,XLOOKUP(N7,Products!$A$7:$A$66,Products!$B$7:$B$66,"Unmatched",0))` in F7. In G7 use the same formula but return Products C7:C66. Fill both columns down. Exact-match lookup is allowed only after the uniqueness check.

## CH08-E03 — Preserve the exception
The first row contains P999, which has no approved match. Expected: one Unmatched row, 182 Matched rows and no row removal. Keep its sales amount in totals while describing the unknown category. Total sales stays INR 490,492.10. Do not silently exclude the unresolved row from overall sales.

## CH08-E04 — Check the repaired numeric key
E8 is a number representing the original product code. N8 must be `P011` and its name/category should match Products. The normalization uses a declared supplier rule, not a universal rule about IDs.

For Excel versions without XLOOKUP, Q7 demonstrates the category fallback: `=IF(O7<>1,P7,INDEX(Products!$C$7:$C$66,MATCH(N7,Products!$A$7:$A$66,0)))`. Fill down; compare Q with G. Microsoft states that XLOOKUP is unavailable in Excel 2016 and 2019. Native execution of either path is still pending. The saved solution uses the required compatibility prefix internally; type the normal XLOOKUP name in Excel.


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


# Chapter 10 — Building your first Excel business report
Open `report_start.xlsx` and save as `excel_business_report.xlsx`. The Summary sheet provides formula-based values so you can begin without completing Chapter 9. The workbook remains a reference implementation until the native PivotTable path is built and tested.

## CH10-E01 — Choose charts for questions
For the trend, select Summary A18:B30 and choose Insert > Line > a two-dimensional line chart. Move it to Report and title it Monthly sample sales (INR). The source has January–December labels and twelve values; do not include the grand-total row.

For categories, copy or link the five category sales values into a compact table. Sort the full two-column table by sales descending. Insert a two-dimensional bar or column chart. Keep its value axis starting at zero. Exclude totals, avoid 3D effects, and retain readable category names. The supplied reference uses a column chart, a vertical bar comparison. Charts are editable workbook objects, not pictures.

## CH10-E02 — Define the scope
State: selected completed orders, 2025, INR, sales after discount before refunds, excluding tax. Report sales INR 490,492.10, 183 sale lines and 72 selected orders. These are sample values. Gross profit and net profit cannot be read from this sales report.

## CH10-E03 — Write supported findings
Write three observations with evidence. Possible answers: Electronics contributes INR 405,987.50; December has the largest sample month at INR 74,238.40; Online contributes INR 175,946.70. Each statement is descriptive. The sample is non-random and small, so it cannot establish annual store rankings, promotion effects, or annual seasonality.

## CH10-E04 — Review and hand over
Compare every plotted value to Summary. Confirm no chart covers a table or note. Resize charts and check labels at ordinary zoom. Check the chart sources exclude totals. The supplied formula summaries always use all source rows; worksheet filters do not change SUMIFS results. In a temporary copy, increase one sale's units and verify the line amount, summary and chart change, then restore the source. If adding rows, extend the bounded source ranges and re-sort categories. Record any remaining limits. The native PivotTable-backed report and one-page Excel print layout are still publication checks, not completed tests.
