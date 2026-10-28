---
description: Task 3 - run the first-response incident summary workflow on one incident pack (argument INC-2041 or INC-2047)
argument-hint: <INC-2041 | INC-2047>
---
Before doing anything else, check that `submission/03-autonomy/work/$ARGUMENTS-human-notes.md` exists and is committed. Run `git log --oneline -- submission/03-autonomy/work/$ARGUMENTS-human-notes.md` to check. If it is missing or not committed, STOP and tell the human to write and commit their own notes first: the comparison is only valid if the human view came first.

Otherwise, use the incident-first-responder subagent on `ops/incidents/$ARGUMENTS/` and save its output unchanged to `submission/03-autonomy/work/$ARGUMENTS-ai-summary.md`.

Do not compare it with the human notes yourself. The human scores it in `submission/03-autonomy/first-response-scores.md`.
