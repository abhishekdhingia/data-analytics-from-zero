# DATA ANALYTICS FROM ZERO — Original data foundation v0.1.0
Author: Abhishek Dhingia. All records and business results are fictional.

## Start here
Read reference/validation_report.md for executed checks and exact totals. Read reference/metric_rules.md before using financial figures. Monetary columns ending _paise are integer paise; divide by 100 for INR. Open chapters/ch01/assignment_brief.md for the first 12-row exercise or chapters/ch18/join_cases.sql for the join fixture.

## Included
Ten canonical CSV tables; two derived fact exports; reproducible original generator; PostgreSQL schema/data setup; field dictionary; metric rules; validation code and executed report; control totals; defect ledger; partial answer ledger; first-assignment, table-grain, cleaning-source and join teaching samples; a controlled refresh batch; solutions and restart sources for the implemented samples.

## Rebuild and validate
From this folder run `python3 scripts/build_data.py` then `python3 scripts/validate_data.py`. These commands replace generated files within this edition folder, so rebuild a COPY if preserving the distributed version. They use only Python's standard library. They do not access the internet, modify an external database or upload to GitHub. Review scripts before running. The validation database is a SQLite author QA artifact; it is not the PostgreSQL learner database. For PostgreSQL use core/retail_database_setup.sql in a dedicated training database after native verification.

## Release status
This is the first data-foundation milestone. Chapter XLSX/PBIX deliverables, all remaining chapter exercises and answer keys, the Q1 2026 capstone, the independent service-desk dataset, application walkthroughs, GitHub release and the book remain to be produced. No claim of native Excel/PostgreSQL/Power BI testing is made. The 2026 calendar is provided but does not imply the capstone data exists. The full book PDF requires author review; Kindle preparation follows approval.

This author review archive is not a replacement for the book's promised adjacent direct-download links. Published exercise links will be created only after resources have been uploaded, pinned and anonymously tested.
