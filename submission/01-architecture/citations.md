# Citations

Every element in the diagrams has an ID: `C#` container/component, `A#` actor/external system, `E#` connection, `S#` sequence step. Paths are repository-relative. `python3 scripts/verify_citations.py` checks that every ID used in a diagram has a row here, that the path exists, and that the symbol appears in the file. Its latest output is in `evidence/citation-check.txt`.

## As-built

| ID | Element | Path | Symbol | Line |
|---|---|---|---|---|

## Target (planned, not built)

New elements cite the ADR section or the scenario fact that requires them. Elements that already exist keep their as-built IDs and rows. Check with `python3 scripts/verify_citations.py --target`.

| ID | Element | Path | Symbol | Line |
|---|---|---|---|---|
