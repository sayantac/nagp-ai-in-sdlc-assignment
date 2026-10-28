---
description: Task 2 - agent lays out exactly-once options and trade-offs (use plan mode; no edits except the output file)
---
Context: `submission/SCENARIO.md` and `submission/02-adr/work/payex-evidence.md`.

Question: how do we guarantee that an approved invoice reaches PayEx exactly once?

Consider at least:
(a) an idempotency key with a dedupe table
(b) a transactional outbox with a worker
(c) optimistic submission with nightly reconciliation
Add any option or combination you think is missing.

Compare them in one table against these criteria: behaviour when PayEx times out with an unknown outcome; the dual-write gap between approving and submitting; the month-end peak of about 80 approvals a minute; multiple App Service instances; seven-year auditability; what a new on-call engineer has to do at 3 a.m.; build cost; run cost.

Then give your recommendation and the single assumption it depends on most. Save the result to `submission/02-adr/work/agent-options.md`.
