# ADR-001: Submitting approved invoices to PayEx exactly once

- Status: TODO (proposed / accepted)
- Date: TODO
- Author: Sayantan Chakraborty (written by hand; the agent's input is in `work/`, and the use of it is described in the last section)
- Evidence: `submission/SCENARIO.md`, `work/payex-evidence.md`

## Context
<!-- What forces the decision. Facts only, each with a citation. Include what PayEx does on timeout and the unknowns from work/payex-evidence.md. -->

## What "exactly once" means here
<!-- Define the guarantee you are actually making, and the one you cannot make. -->

## Options considered
<!-- At least: (a) idempotency key + dedupe table, (b) transactional outbox + worker, (c) optimistic submit + nightly reconciliation, plus any combination. -->

| Criterion | (a) | (b) | (c) | Chosen |
|---|---|---|---|---|
| Timeout with unknown outcome | | | | |
| Dual-write gap (approved but never sent) | | | | |
| Month-end peak (~80/min) | | | | |
| Multiple App Service instances | | | | |
| 7-year audit trail | | | | |
| 3 a.m. on-call burden | | | | |
| Build cost | | | | |
| Run cost | | | | |

## Decision

## Strongest objection, and why it does not change the decision

## How it fails at 3 a.m. on the last day of the month, and what limits the damage

## Cost
### To build
### To run (Azure, and on-call)

## Consequences

## What would make me revisit this
<!-- Measurable triggers only, e.g. "unknown-state rate above X% for a day", "any duplicate PayEx reference observed". -->

## Where the agent was wrong or useless
<!-- Specifics with log ids. Include the three stress tests: did the recommendation move when you stated a preference, and was the reason new? Was the 3 a.m. answer specific or generic? Were the cost numbers grounded? -->

| # | What the agent said | Why it was wrong or useless | Log id |
|---|---|---|---|
