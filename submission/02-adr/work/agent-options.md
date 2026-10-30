# Exactly-once submission to PayEx: options (agent draft)

Inputs: `submission/SCENARIO.md` and `submission/02-adr/work/payex-evidence.md` (cited as F/I/U ids). This is an agent draft to react to, not a decision.

## Assumptions and unknowns

These are not facts. Each one changes the answer.

- **A1 (U4):** PayEx may or may not honour an idempotency key or deduplicate on invoice Id. The evidence is silent.
- **A2 (U3):** After a 30 s timeout, PayEx may or may not have processed the request. SCENARIO says a timeout "does not reliably mean the submission failed".
- **A3 (U1, U2):** PayEx's success and failure contract is unknown beyond "returns a reference on success".
- **A4 (U5):** The 2.14.3 retry policy is known only by its title (F21). Nothing here assumes how it behaves.
- **A5:** PayEx may offer a lookup or listing by our reference. This is unknown, and options C and D lean on it.

Facts that drive the analysis:

- 2.14.0 approved the invoice, then called PayEx inline. A failure left an approved, unsubmitted invoice, and nothing recovers it (F3, I1, F10, U9).
- Users re-approve after a 500 (F23), which is a duplicate path (I7).
- Peak is about 80 approvals/min, with 3 instances today (F20).
- Azure SQL is to be added, and Service Bus is provisioned but unused.
- Approval actions are auditable for seven years, and two of six engineers are new.

## Options

- **A. Idempotency key + dedupe table.** Send a stable key per invoice to PayEx. Record state in a SQL table with a unique constraint.
- **B. Transactional outbox + worker.** The approval and an outbox row commit in one SQL transaction. A worker claims rows and submits.
- **C. Optimistic submission + nightly reconciliation.** Submit inline after approving. A nightly job compares our records with PayEx's.
- **D. Combination (added): B + A + C.** Outbox for atomicity, a stable idempotency key on every attempt, an explicit `InDoubt` state after a timeout, and nightly reconciliation as the detective control.
- **E. Outbox + Service Bus relay (added).** As B, but the outbox publishes to Service Bus and a consumer submits.

Not an option, but a prerequisite: ask PayEx now whether it supports an idempotency key and lookup by our reference (A1, A5).

## Comparison

| Criterion | A. Key + dedupe table | B. Outbox + worker | C. Optimistic + nightly reconciliation | D. Outbox + key + in-doubt + reconciliation | E. Outbox + Service Bus |
|---|---|---|---|---|---|
| **PayEx times out, outcome unknown** | Safe to retry only if PayEx honours the key (A1). If not, the table cannot say what PayEx did. | Worker re-sends, so a timed-out request can be sent twice (A2). Not safe alone. | The timeout is ignored at the time. A duplicate or a loss is found the next day, if at all. | Row goes to `InDoubt`. Retry with the same key if PayEx honours it. If not, resolve by lookup (A5) or manually. Best of the five, still bounded by A1/A5. | Same as B. The broker adds redelivery, so it needs the same key. |
| **Dual-write gap (approve vs submit)** | Not closed. A crash between approve and submit leaves an approved, unsent invoice (I1). | Closed. Approval and outbox row are one transaction. | Not closed. This is the 2.14.0 failure mode (F3). | Closed. | Closed at the outbox. A second gap opens between outbox and broker unless the relay is built carefully. |
| **Month-end peak (~80/min)** | Fine for the table. Inline 30 s calls hold request threads, which is the INC-2041 coupling (F3, F15). | Fine. Load moves off the request path. A queue builds if PayEx is slow and drains afterwards. | Same inline coupling as A. | Same as B. | Fine, but more capacity than 80/min needs. |
| **Multiple App Service instances** | The unique constraint stops two instances recording the same invoice. | Needs a lease or claim (`UPDLOCK, READPAST`) so two workers do not take one row. | No coordination needed for submit. The reconciliation job must run once. | Claim lease for the worker. Run reconciliation on a single instance or under a lock. | The broker handles competing consumers. The outbox relay still needs a claim. |
| **Seven-year auditability** | Good. The table is a durable per-invoice record. | Good. Outbox plus attempt rows show what was sent and when. They must be retained, not purged. | Weak. The record is the app log plus a nightly report. | Best. One row per invoice with state history, attempts and reconciliation result. | Good at the outbox. Broker messages are not an audit store. |
| **New on-call engineer at 3 a.m.** | Hard to tell stuck from in-flight. The runbook is ambiguous. | Query stuck rows, replay one. Clear, but replay can duplicate without a key. | Nothing alerts at night. The problem appears the next morning. | Query `InDoubt` and `Failed` rows, replay or resolve each. Needs a short runbook and a dashboard. | Two places to look (outbox and broker), and dead-letter handling to learn. INC-2047 shows broker paths failing silently. |
| **Build cost** | Low to medium. A table, a key and a client change. | Medium. Outbox, worker, claim logic, retry and tests. | Low to medium. The reconciliation job depends on a PayEx query API (A5). | Medium to high. B plus key handling, state machine and reconciliation. | High. D plus broker, relay and consumer. |
| **Run cost** | Low. SQL only. | Low. SQL and a worker in the existing App Service. | Low. A nightly job. | Low to medium. SQL, worker, nightly job and monitoring. | Medium. Adds Service Bus usage and more things to monitor. |

## Recommendation

**Option D, without Service Bus initially.**

- The outbox closes the dual-write gap, which is the loss path 2.14.0 left open (F3, I1, U9).
- A stable per-invoice key, with one outbox row per invoice, makes a re-approval a no-op. That covers the duplicate path in F23 and I7.
- The explicit `InDoubt` state is the honest answer to a timeout that does not mean failure.
- Nightly reconciliation is a safety net that finds what the other controls miss.
- At about 80/min a SQL-backed worker is enough. Service Bus (option E) adds a second failure surface with no benefit at this volume. The outbox keeps it available later.

**The assumption it depends on most:** PayEx honours an idempotency key, or allows lookup by our reference, so a retry after a 30 s timeout is safe (A1/A5).

If that is false, a timed-out submission can only be resolved by lookup or by hand. The achievable guarantee is then "at-least-once, with duplicates detected and reversed", not exactly-once, and the ADR must say that plainly.

## What would change this

- **PayEx has neither a key nor a lookup:** exactly-once is not achievable from our side. Keep the outbox and `InDoubt` state, drop the claim of exactly-once, and make reconciliation plus a manual resolution runbook the main control.
- **PayEx honours a key:** reconciliation can shrink to a simple audit job, and A or B plus the key may be enough.
- **Volume grows well past 80/min, or other consumers need approval events:** revisit E.
