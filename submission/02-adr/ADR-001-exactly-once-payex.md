# ADR-001: Submitting approved invoices to PayEx exactly once

- Status: Accepted, conditional on PayEx confirming idempotency-key or lookup support (see "What would make me revisit this")
- Date: 2026-10-30
- Author: Sayantan Chakraborty
- Evidence: `submission/SCENARIO.md`, `work/payex-evidence.md` (F/I/U ids), `submission/01-architecture/inferred.md`

## Context

- The service becomes tier-2 in January: 24x7 on-call, a published SLO, and a new PayEx submission (SCENARIO.md). About 40,000 invoices a month, 60% in the last three working days, peaking near 80 approvals a minute.
- PayEx times out at 30 seconds, and a timeout does not reliably mean the submission failed (SCENARIO.md, PayEx row).
- Release 2.14.0 in INC-2041 approved the invoice first, then called PayEx inline. A failure leaves an approved, never-submitted invoice and nothing recovers it (F3, I1, U9). Users re-approved after 500s (F23), which is a duplicate path (I7).
- Persistence does not exist today: the repository is in-memory (as-built diagrams).
- The code overwrites the last decision and keeps no history, and an approver can also be the submitter (`inferred.md` section 2 row 10, section 4). SOC 2 needs approval actions auditable for seven years (SCENARIO.md).
- Unknown: whether PayEx honours an idempotency key or supports lookup by our reference, and what it did with a request that timed out (U3, U4). Nothing in the repository answers this.

## What "exactly once" means here

- Each approved invoice causes at most one PayEx payment and reaches a terminal state (Submitted or Failed) or is visibly InDoubt. It is never silently lost.
- That is achieved as at-least-once delivery plus an idempotent receiver (a stable key). Exactly-once over a call that can time out is not achievable by the sender alone. If PayEx cannot deduplicate, the guarantee falls to at-least-once with detection.

## Options considered

| Criterion | A: key + dedupe table | B: outbox + worker | C: optimistic submit + nightly reconciliation | D: B + A + C (chosen) |
|---|---|---|---|---|
| Timeout, unknown outcome | Retry is safe only if PayEx honours the key | Re-sends, so can duplicate without a key | Nothing stops a resubmission | InDoubt state, resolved by lookup or retry with the same key |
| Dual-write gap (approved, never sent) | Not closed | Closed | Not closed | Closed |
| Month-end peak (~80/min) | Inline 30 s calls hold request threads | Worker absorbs the backlog | Detection lag is longest after month-end | Backlog absorbed, circuit breaker |
| Multiple instances | Unique constraint | Lease claim | n/a | Lease longer than the PayEx timeout |
| 7-year audit | Dedupe table is a record | Outbox and attempt rows | Thin: logs and a nightly report | Append-only audit events in the approve transaction |
| 3 a.m. burden | Unclear if stuck or in flight | Query stuck rows | Found the next morning | Alerts, kill switch, runbook |
| Build cost (estimate) | Low to medium | Medium | Low to medium (about 10-15 person-days) | Highest (about 32-50 person-days) |
| Run cost | Low | Low | Low | Low Azure delta; on-call time moderate |

## Decision

Option D, without Service Bus at first.
- On approval, one SQL transaction writes the status change, an append-only audit event and one outbox row, unique per invoice.
- A worker claims rows with a lease longer than the 30 s PayEx timeout plus margin, and sends the invoice Id as the idempotency key on every attempt.
- States: Pending, Submitting, then Submitted, Failed or InDoubt. Timeouts and 5xx responses go to InDoubt; 4xx responses go to Failed. InDoubt rows are resolved by lookup or by a retry with the same key, never by a bulk reset.
- Nightly reconciliation against PayEx is the detective control, and skips rows still in flight.
- Go-live safeguards: a concurrency cap and circuit breaker, a worker kill switch, alerts (oldest pending age, InDoubt count, PayEx timeout rate), reason codes on rows, and a runbook.
- Azure SQL persistence is a prerequisite, scoped separately.

## Strongest objection, and why it does not change the decision

Objection: D is too heavy for a service one person maintained part-time, with six engineers (two new) and a January start. Estimates are about 32-50 person-days against about 10-15 for C. At 40,000 invoices a month, inline submit with a stable key and nightly reconciliation could be enough.

Response: C does not close the dual-write gap that 2.14.0 left open (F3, I1, U9), and it detects duplicates up to a day late, when 60% of volume lands in three days. The logs already show repeated approves after 500s (F23, I7). I accept the cost difference for those two reasons. The objection would win if PayEx deduplicates on our key and finance accepts a one-day detection window (see revisit triggers).

## How it fails at 3 a.m. on the last day of the month

- The backlog grows first, not approvals. Approvals still commit, but each timed-out call holds a worker slot for 30 s, so oldest-pending age climbs. The rate depends on the concurrency cap, which is not yet set.
- If the lease is shorter than the PayEx timeout, a second worker reclaims a row mid-call. That gives two concurrent attempts on one invoice, and only the idempotency key prevents a double payment.
- The obvious on-call actions make things worse: restarting an instance cuts in-flight calls (INC-2041); bulk-resetting InDoubt rows to Pending can duplicate payments if PayEx does not honour the key; scaling out workers hits a struggling PayEx (F5, F11); editing rows in SQL breaks the audit trail.
- Mitigations built into the design: lease longer than the timeout, concurrency cap and circuit breaker, kill switch, alerts, reason codes, a runbook rule against resetting InDoubt rows without a lookup or key check, and reconciliation that skips in-flight rows.

## Cost

Estimates only. No velocity data, quote or measurement backs these figures.
- **To build:** about 26-40 person-days, 32-50 with contingency. This excludes Azure SQL persistence, which is needed anyway.
- **To run, Azure:** a small delta on top of a database that must exist anyway (not priced). Service Bus is provisioned and unused, so $0 extra.
- **To run, on-call:** about 5 hours a month reading the reconciliation report, plus manual resolution of InDoubt rows. If 0.1% of invoices land InDoubt at 5 minutes each, that is about 3 hours a month; at 0.5%, about 17. The real rate is unknown.

## Consequences

- Approval and submission are decoupled: approvals stay fast during a PayEx slowdown, but a submission backlog is possible and must be watched.
- The worker shares resources with the web app, and its concurrency must be capped.
- Fixes the audit-trail gap with an append-only event written in the approval transaction.
- Does not fix segregation of duties (approver can equal submitter). That is recorded in `inferred.md` for a separate decision.
- Without PayEx's answer on the key or lookup, the guarantee is at-least-once with detection, and InDoubt rows need a person.

## What would make me revisit this

Initial thresholds, to be tuned after the first month-end.
- PayEx confirms no idempotency key and no lookup: the guarantee is downgraded, and the design and runbook are reopened.
- PayEx confirms it deduplicates on our key and finance accepts a one-day detection window: reconsider the simpler option C.
- Any duplicate payment observed in production.
- InDoubt rate above 0.5% of submissions in a day, or oldest-pending age above 15 minutes outside month-end.
- Volume sustained above twice the 80/min peak, or the backlog not clearing within an hour after month-end: consider the Service Bus relay.
- The build estimate is exceeded by more than half at the midpoint review: phase the work.
- A SOC 2 auditor finding on the approval trail.

## Where the agent was wrong or useless

Stress test results first:
- **Stated a preference for C:** the recommendation did not move, and no new facts were offered. It gave reasons from the evidence and the conditions that would change its mind (20261030T131500Z-task-2-adr-options-prefer-c).
- **3 a.m. scenario:** the answer was specific (lease against the 30 s timeout, bulk-reset trap, worker kill switch) and checked against SCENARIO.md (20261030T132000Z-task-2-adr-stress-3am).
- **Cost:** the numbers were labelled as estimates but have no basis (20261030T132500Z-task-2-adr-stress-cost).

| # | What the agent said | Why it was wrong or useless | Log id |
|---|---|---|---|
| 1 | Build estimates (26-40 person-days; C at 10-15), Azure "tens of dollars", and a 3-17 hours a month InDoubt load | No velocity data, no pricing and no PayEx rate exists. The agent said so itself, so the figures are useful as structure only and appear above as assumptions | 20261030T132500Z-task-2-adr-stress-cost |
| 2 | Recommended D, resting on PayEx honouring an idempotency key or lookup | The agent cannot resolve this, and nothing in the repository answers it. It flagged the dependency honestly, but the recommendation is not decision-ready until PayEx's contract is known | work/agent-options.md |
| 3 | Listed seven mitigations to add to the design | It did not say which are go-live blockers and which can follow. For a six-person team with a January start, that is scope risk, and I had to decide the split myself | 20261030T132000Z-task-2-adr-stress-3am |
| 4 | Added options D and E and a "what would change this" section unasked, and offered to write failure modes into its own draft | Mildly useful, but beyond what I asked. I declined the offer: the failure analysis belongs in my ADR, not in the agent's draft | work/agent-options.md |