Critique of ADR-001 (`/Users/sayantanchakraborty/workspace/poc-workspace/ai-in-sdlc/ai-in-sdlc-assignment/submission/02-adr/ADR-001-exactly-once-payex.md`). Evidence read: `work/payex-evidence.md` and `SCENARIO.md`. I did not read `inferred.md`, so claims that rest only on it are unchecked. I also did not open the raw INC-2041 files and relied on the evidence file's F/I/U ids. Each objection is tagged FACT, INFERENCE or UNKNOWN.

## 1. Strongest objection: the central mechanism (InDoubt resolved by "lookup or retry with the same key") rests on U3 and U4, which are unanswered, and nothing gates the build on them.

Sequence on the last working day:
- 23:58, about 80 approvals a minute. A worker claims the row for invoice X with a lease of about 35 s and sends the invoice Id as the key.
- PayEx pays at T+29 s. Its response is lost, or arrives after our client gave up. The ADR sets no client timeout (see objection 3).
- The worker records InDoubt (line 40: "Timeouts and 5xx responses go to InDoubt").
- Someone, or an automated retry, takes the "retry with the same key" path at 00:05. If PayEx ignores the key (U4), it pays X twice.
- If PayEx has no lookup, the "lookup" branch does not exist. The nightly reconciliation (line 41) also needs a PayEx-side ledger. The evidence says no such ledger exists, and its closing note names one as the single most valuable missing item.
- The duplicate is found when the vendor or finance complains. The audit trail shows two attempts with the same key but cannot say which one PayEx honoured.
- Under the same condition, InDoubt rows pile up with no data to decide pay or not pay. At 80 a minute during a PayEx slowdown, every call times out, so every row goes InDoubt. Line 63 prices manual resolution at 0.1% to 0.5% of invoices. A correlated outage is the opposite case, not 0.5%. For example, 60 minutes at 60 rows a minute is 3,600 rows. At the ADR's own 5 minutes each, that is 300 hours, and the 0.5% InDoubt alert (line 79) fires as noise.

Where this shows up in the ADR:
- Line 3 says "Accepted, conditional". Line 76 says that if PayEx supports neither key nor lookup, the design and runbook are "reopened". That means 32-50 person-days could be spent first.
- The ADR's own table (row 2, line 94) says the recommendation "is not decision-ready until PayEx's contract is known". Status "Accepted" contradicts that.
- Lines 20 and 71 fall back to "at-least-once with detection". Without lookup or a ledger there is no detection mechanism, so the fallback is empty.
- The ADR sets no gate, owner or date for asking PayEx, though the question looks cheap to ask.

Basis: UNKNOWN (U3, U4, U6), plus an INFERENCE that the fallback has no detection path. The SCENARIO PayEx row ("a timeout does not reliably mean the submission failed") is documented, and the ADR agrees with it.

## 2. Ranked further objections

**2. The 4xx to Failed rule can lose payments, and Failed has no alert.** (INFERENCE from UNKNOWN U1/U2. Line 40, line 42.)
- The ADR classifies by status code while the evidence says the code contract is unknown (U1, U2).
- A 429 under peak load is a 4xx. It becomes terminal Failed, so an approved invoice is never paid.
- A 409 or 422 "duplicate" reply from a PayEx that deduplicates also lands in Failed, although the payment exists.
- The alerts (line 42) cover oldest pending age, InDoubt count and timeout rate. They do not cover Failed count. The ADR does not say who sees a Failed row, who resubmits it, or whether approvers and finance are told.
- The definition on line 19 says "never silently lost". A Failed row nobody alerts on fits that wording but is still a lost payment.

**3. The lease is checked against the wrong timeout.** (FACT F5, F6, F9; INFERENCE I2. Lines 39, 54.)
- The ADR sets the lease against "the 30 s PayEx timeout". That is PayEx's server-side limit.
- What matters is our own HttpClient timeout. In 2.14.0 it silently became 100 s (F12, I2), and the configured 10 s was never wired in (F9).
- If the client waits 100 s and the lease is about 35 s, a second worker reclaims the row mid-call. That is the two-concurrent-attempts failure the ADR describes at line 54.
- The ADR does not specify the client timeout or HttpClient lifecycle, even though the socket-exhaustion pattern (F5, F11) is the documented failure.
- A worker crash or App Service restart or slot swap after PayEx accepts but before the write to Submitted has the same effect. Lines 66 and 55 put the worker in the web app process but say nothing about graceful shutdown or deploys during month-end. Every deploy therefore creates human-resolved InDoubt rows.

**4. Key lifetime and key choice are unaddressed.** (UNKNOWN U4. Line 39, line 40.)
- Even if PayEx honours a key, the ADR does not say how long PayEx remembers it.
- InDoubt rows resolved "next morning", or after a weekend, may outlive the key window. The retry would then pay again.
- Using the invoice Id as the key also assumes one payment per invoice for ever. Reversals, amendments and re-issues are not covered.

**5. The option comparison does not discriminate, and the "strongest objection" section is a strawman.** (Lines 24-33, 45-49.)
- D is B+A+C bundled. Every advantage in the D column comes from adding the outbox (B). The incremental value of A and C over B is never shown, and no "B plus key, without the full safeguards" option is costed.
- Line 26 shows B "can duplicate without a key". D has the same exposure (objection 1).
- The "strongest objection" the ADR answers is cost. The real weakness is the PayEx dependency. The ADR admits it elsewhere, but the section meant to test the decision does not test it.
- The response cites F23 and I7 as evidence for the choice. See the unsupported claims below.

**6. SOC 2 and segregation of duties are deferred with no owner or date.** (Lines 14, 70, 82; SCENARIO Compliance row.)
- The audit is in six months. An approver who is also the submitter is a control gap on payments. The ADR leaves it to "a separate decision" in `inferred.md`.
- Its only trigger is "a SOC 2 auditor finding on the approval trail" (line 82). That is after the fact.
- "Append-only" is not defined: no DB permissions, immutability or retention mechanism. Line 55 itself says editing rows in SQL breaks the audit trail.
- The audit event is written only in the approval transaction (line 38). The ADR does not say whether submission attempts and their outcomes, including manual InDoubt resolution, are audited.

**7. Schedule and scope are not decided.** (Lines 42-43, 61; table row 3, line 95.)
- It is 2026-10-30 and January is the start. The 32-50 days exclude Azure SQL, which is the critical path and "scoped separately" with no estimate.
- Line 42 lists every safeguard as a go-live safeguard. The ADR's own table (row 3, line 95) says the agent did not split blockers from follow-ups and that the author "had to decide the split". The ADR never states that split.
- The team is six engineers, two of them new.

## 3. Claims asserted without evidence or measurement

- Line 12: "A failure leaves an approved, never-submitted invoice and nothing recovers it (F3, I1, U9)."
  - U9 only says the diff shows no recovery. F21 and I8 show a retry policy was added in 2.14.3 and U5 says its behaviour is unknown.
  - Also, INC-2041 is under `ops/`, which AGENTS.md says describes a planned deployment. It is not a description of the current system.
  - U7 says there is no count of actually lost invoices.
- Line 12: "Users re-approved after 500s (F23), which is a duplicate path (I7)."
  - F23 includes 200-then-500 orders, for example INV-41873 at 09:43 and then 10:13, and INV-41711 at 10:30:24 and then 10:30:34.
  - F24 shows repeat approves before the PayEx call existed, so repeats are not caused by 500s.
  - I7 says the evidence does not show a second PayEx call.
- Line 49: "The logs already show repeated approves after 500s (F23, I7)." Same problem. It is used as a decisive reason for D.
- Line 55: "restarting an instance cuts in-flight calls (INC-2041)." F19 says only that a web-02 restart reduced errors for about 3 minutes. It does not show in-flight calls being cut.
- Line 55: "scaling out workers hits a struggling PayEx (F5, F11)." F5 and F11 are client-side port and socket exhaustion. F18 says PayEx reported all systems operational. I3 says the cause is correlation only. PayEx was not shown to be struggling.
- Line 28: "Worker absorbs the backlog". Line 54 admits the concurrency cap "is not yet set" and the ADR gives no throughput maths. With 30 s calls, a cap of 10 gives about 20 calls a minute against 80 arriving.
- Lines 32, 33, 61, 62, 63: build days, "Low Azure delta" and on-call hours are labelled estimates. Line 60 says no data backs them. They are still used as the baseline for the revisit trigger at line 81 ("exceeded by more than half").
- Line 79: the 0.5% InDoubt threshold and the 15-minute pending age have no basis.
- Line 31: "Found the next morning" and "Unclear if stuck or in flight" are asserted without measurement.

## 4. What the ADR is silent about

- Who asks PayEx the U3 and U4 questions, by when, and what blocks the build until they are answered.
- The production state of the existing retry from 2.14.3 and PR `feature/payex-retry` (U5, F21, F22).
- Whether duplicates or losses already happened (U6, U7). No PayEx-side export has been requested, though the evidence names it as most valuable.
- Re-approve behaviour on an already-approved invoice (the evidence's own open question 8). The unique outbox row implies protection, but the ADR does not say that approving a non-Pending invoice is rejected or is a no-op.
- The client timeout, HttpClient lifecycle and graceful worker shutdown.
- Failed row ownership and alerting. How InDoubt rows are triaged during a correlated outage. What happens to rows already InDoubt when the circuit breaker opens or the kill switch is thrown.
- Rollback or cutover plan, and what the first month-end looks like. The "revisit" thresholds are set only after it.
- Reconciliation source: which PayEx endpoint or file, and who owns the nightly report.
- Who can resolve InDoubt rows, with what access, and how that is audited (touches SoD, line 70).
