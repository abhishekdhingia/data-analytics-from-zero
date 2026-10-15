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


## Environment note
These instructions target an English-language Excel desktop workflow. They are development instructions: the files were calculated and rendered with Artifact Tool, but the clicks have not been executed in Microsoft Excel. Record your Excel version when testing. Formula examples use commas; some regional settings require semicolons. Use a copy of the starting file and keep Raw inputs unchanged. Do not enable macros: these files contain none.

All business records are fictional. This pack is self-contained; earlier chapter success is not a prerequisite. The core sample contains 183 completed sale lines from 72 selected orders across 2025. It is a small, non-random teaching sample, not an annual total. INR amounts exclude tax and refunds. Chapter 7 intentionally uses a different 202-row import. Do not carry its totals into the other chapters.
