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


## Environment note
These instructions target an English-language Excel desktop workflow. They are development instructions: the files were calculated and rendered with Artifact Tool, but the clicks have not been executed in Microsoft Excel. Record your Excel version when testing. Formula examples use commas; some regional settings require semicolons. Use a copy of the starting file and keep Raw inputs unchanged. Do not enable macros: these files contain none.

All business records are fictional. This pack is self-contained; earlier chapter success is not a prerequisite. The core sample contains 183 completed sale lines from 72 selected orders across 2025. It is a small, non-random teaching sample, not an annual total. INR amounts exclude tax and refunds. Chapter 7 intentionally uses a different 202-row import. Do not carry its totals into the other chapters.
