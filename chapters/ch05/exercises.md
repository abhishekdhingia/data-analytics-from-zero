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


## Environment note
These instructions target an English-language Excel desktop workflow. They are development instructions: the files were calculated and rendered with Artifact Tool, but the clicks have not been executed in Microsoft Excel. Record your Excel version when testing. Formula examples use commas; some regional settings require semicolons. Use a copy of the starting file and keep Raw inputs unchanged. Do not enable macros: these files contain none.

All business records are fictional. This pack is self-contained; earlier chapter success is not a prerequisite. The core sample contains 183 completed sale lines from 72 selected orders across 2025. It is a small, non-random teaching sample, not an annual total. INR amounts exclude tax and refunds. Chapter 7 intentionally uses a different 202-row import. Do not carry its totals into the other chapters.
