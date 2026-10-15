# DATA ANALYTICS FROM ZERO — Excel practice review pack v0.2
Author: Abhishek Dhingia. All records are fictional and created for this project.

This is the Chapter 5–10 development pack, based on data foundation 0.1.0. It contains 6 starters, 6 solution/reference workbooks and 6 restart copies (18 XLSX files), exercise guides, expected values, provenance and validation records. It is not the finished manuscript or a publication-ready native Excel release.

## How to start
1. Open chapters/ch05/excel_navigation_start.xlsx and chapters/ch05/exercises.md.
2. Save a working copy with the name specified in the guide.
3. Attempt the tasks before opening solutions/ch05/sales_table.xlsx.
4. Every later chapter has its own complete starting file; no earlier mistakes block progress.

Most chapters use 183 sale lines from 72 completed orders, drawn by taking six date-spaced orders in each 2025 month and retaining all their lines. This deliberately small sample is not statistically representative. Prices are converted from exact integer paise into numeric INR values; dates are real Excel date values. Sales after discount = INR 490,492.10. Chapter 7 uses its separate 202-row dirty import and reconciles to 197 accepted rows, 5 quarantined rows and INR 444,087.00 accepted sales.

## Exact completion boundary
Chapters 5–8: starters and worked solutions are built, calculated and rendered with Artifact Tool; Microsoft Excel execution is pending.
Chapter 9: starter, verified formula-based reference answers, refresh record and native build instructions are supplied. No native PivotTable object is present. Native pivot solution/refresh testing is unfinished because the available generator does not reliably export PivotTables.
Chapter 10: starter and editable formula-based chart report are supplied. Its native pivot-backed variant and Excel print-layout test are unfinished.
Checkpoints are explicit copies of worked/reference end states. Chapters 9–10 checkpoints are not native pivot checkpoints.

## Checks and limitations
Read reference/validation_report.md for checks actually executed. Formula recalculation by Artifact Tool is not Microsoft Excel testing. Official documentation was checked for table creation, pivot setup and XLOOKUP; it does not certify UI execution or licensing. No workbook contains macros or external data connections. Formula-reference ranges are bounded; extend them when adding rows. Native Excel PivotTables built over SalesData need a refresh after an append.

## Source and next work
reference/source_provenance.json records foundation source hashes; source_data.json preserves the exact author inputs used to build these workbooks. scripts/build.mjs is the reproducible authoring script and requires the Codex primary runtime's @oai/artifact-tool package. It is not a reader installation requirement. Existing foundation files were not modified.

Next publication gates: execute the Windows Excel learner path, create/test native pivots and the pivot-backed report, capture screenshots, draft the full lessons, and publish tested direct-download links in a new GitHub edition folder. No GitHub upload was performed. The complete manuscript PDF requires Abhishek's review; Kindle follows approval.
