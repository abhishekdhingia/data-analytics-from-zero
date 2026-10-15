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


## Environment note
These instructions target an English-language Excel desktop workflow. They are development instructions: the files were calculated and rendered with Artifact Tool, but the clicks have not been executed in Microsoft Excel. Record your Excel version when testing. Formula examples use commas; some regional settings require semicolons. Use a copy of the starting file and keep Raw inputs unchanged. Do not enable macros: these files contain none.

All business records are fictional. This pack is self-contained; earlier chapter success is not a prerequisite. The core sample contains 183 completed sale lines from 72 selected orders across 2025. It is a small, non-random teaching sample, not an annual total. INR amounts exclude tax and refunds. Chapter 7 intentionally uses a different 202-row import. Do not carry its totals into the other chapters.
