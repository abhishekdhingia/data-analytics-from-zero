# Controlled cleaning exercise source
This CSV is the source for the planned sales_dirty.xlsx, which is not yet authored. Keep the raw file unchanged. Dates use ISO YYYY-MM-DD or explicitly documented DD/MM/YYYY. Blank customer IDs are legitimate guests. Category mapping is supplied in products.csv. Source row IDs identify imported rows; order_item_id identifies a business sale line. Duplicate imports may be quarantined only after comparing the business key and full record.

Blank prices, unapproved quantities, and unknown product keys must be quarantined, not guessed. There is no authority in this learner pack to recover them from the full database. The author-only defect ledger retains canonical truth for verification.

Starting file: sales_dirty_source.csv. Save outputs as accepted.csv, quarantine.csv and cleaning_log.csv. Pass: 202 = 197 accepted + 3 unresolved original rows + 2 duplicate imports. Blank customer IDs stay blank. Accepted total must match the answer ledger. Full XLSX starting file and UI walkthrough remain pending.
