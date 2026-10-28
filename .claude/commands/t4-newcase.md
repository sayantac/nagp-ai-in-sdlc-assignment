---
description: Task 4 - turn a real defect you have seen into an eval case diff (argument case number + description)
argument-hint: <11|12> <defect description, or "clean: description of a correct change">
---
Create `ops/evals/cases/case-$1.diff`: a unified diff against the current code in this repository, in the same style and size as the existing cases in `ops/evals/cases/`. Read two of the existing cases first to match their format.

Description from the human: $ARGUMENTS

- If the description starts with "clean:", the change must be correct and must contain no defect. Look for anything that could be called a defect and remove it.
- Otherwise, the diff must contain exactly that defect, plausibly written, without comments or names that give it away.

Then show the diff and remind the human to add the case's row to `submission/04-evals/answer-key.csv` and commit both before any eval run.
