# DATA ANALYTICS FROM ZERO - practice files
Author: Abhishek Dhingia. Fictional data for the current 30-chapter review manuscript.

## Review release - 15 October 2026
This combines Data Foundation v0.1, Excel Practice Pack v0.2, worked SQL examples and the final project CSVs. It replaces the older NovaMart_Chapter_* practice edition. Do not mix the old and current files.

Download the repository as a ZIP and extract it before opening files. Use the exact chapter starter named in the book, save a working copy and compare with the pass criteria. XLSX files open in Excel, CSV files in Excel or a text editor, and SQL scripts in the database tool. A PDF is not a substitute for an editable practice workbook.

- core/: canonical tables, derived sales/returns facts and PostgreSQL database setup.
- chapters/: supplied chapter starters and briefs. Chapters 28 and 29 contain final project CSVs.
- checkpoints/: supplied restart states.
- solutions/: worked examples; try the exercise first.
- reference/: definitions, controls, historical validation notes and current status.
- scripts/: original authoring/validation utilities, not required for readers. Some use author-specific dependencies.

Read reference/CURRENT_STATUS.md before testing. Historical pack notes describe earlier milestones and are retained for provenance; CURRENT_STATUS.md governs current coverage. The book manuscript is not included in this public practice package.

## Current limitations
Native Windows Excel/pgAdmin workflows and Power BI Desktop tests remain pending. Chapter 9 reference workbooks do not contain native PivotTables; Chapter 10's report is formula-based. No tested PBIX is supplied. Some chapters use printed exercises instead of a separate starter. This is not the final publication release.
