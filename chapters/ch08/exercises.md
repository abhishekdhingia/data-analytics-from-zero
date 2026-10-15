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


## Environment note
These instructions target an English-language Excel desktop workflow. They are development instructions: the files were calculated and rendered with Artifact Tool, but the clicks have not been executed in Microsoft Excel. Record your Excel version when testing. Formula examples use commas; some regional settings require semicolons. Use a copy of the starting file and keep Raw inputs unchanged. Do not enable macros: these files contain none.

All business records are fictional. This pack is self-contained; earlier chapter success is not a prerequisite. The core sample contains 183 completed sale lines from 72 selected orders across 2025. It is a small, non-random teaching sample, not an annual total. INR amounts exclude tax and refunds. Chapter 7 intentionally uses a different 202-row import. Do not carry its totals into the other chapters.
