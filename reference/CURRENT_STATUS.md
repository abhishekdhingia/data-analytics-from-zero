# Current coverage and verification - 15 October 2026
The 30-chapter review manuscript is drafted. This package supplies the current available practice assets, not a claim that every chapter has a native checkpoint.

- Chapters 1-4: supplied CSV selections plus printed cases and worksheets in the book.
- Chapters 5-10: six XLSX starters, six solutions/reference workbooks and six checkpoints. Native Excel testing pending. Chapters 9-10 references are not native pivot checkpoints.
- Chapters 11-14: printed cases in the book; canonical comparison data is under core/ and reference/.
- Chapters 15-21: canonical PostgreSQL setup, import/join fixtures and added worked-query scripts in solutions/. Load the canonical setup and completed_sales view before later query files. Chapter 18's two solution scripts serve different scopes: validated_joins.sql belongs to the foundation fixture; chapter18_worked_queries.sql follows the book query sequence.
- Chapters 22-26: canonical CSVs and Chapter 26 refresh fixture supplied. Enter the printed M/DAX in Power BI Desktop. No PBIX or native-tested report checkpoint exists in this package.
- Chapter 27: printed decision exercise.
- Chapters 28-29: all five final-project CSVs supplied, with repaired quarterly data under solutions/ch28/.
- Chapter 30: project presentation and query-review exercise in the book.

Verification: 76 foundation checks passed; 18 XLSX archives opened with no stored errors or broken #REF! references; Chapter 6's 732 line formulas/cached values agreed with independent arithmetic; 45 SQL setup/query cases executed in PGlite. Eight Power BI source scenarios were recalculated outside Power BI. These are not native application acceptance tests.

The earlier reference/chapter_coverage.md, manifests and validation reports are milestone records. They do not inventory the combined package. UPLOAD_MANIFEST.csv is the current package inventory. Original Excel reference collisions are renamed excel_answer_ledger.csv, excel_manifest.json and excel_validation_report.md.

Open release work: native Excel and pgAdmin workflow checks; real pivot and PBIX checkpoints; Power BI measures/interactions/refresh; public download checks; direct links beside book exercises; final proofreading. No public upload was performed while preparing this package.
