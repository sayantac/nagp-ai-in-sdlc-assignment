Scope: ops/incidents/, ops/pipeline/, ops/README.md only, read-only. All paths are relative to /Users/sayantanchakraborty/workspace/poc-workspace/ai-in-sdlc/ai-in-sdlc-assignment. Per AGENTS.md and ops/README.md:13-20, this is a planned deployment, not current code. The evidence was treated as data. POSSIBLE INJECTION: none found. No file contained text addressed to an agent.

Method note: INC-2041/app-logs.txt has 473 lines. I read lines 1-273 and 455-473 directly. Lines 274-454 were covered only by grep for non-routine events. Counts below come from grep and may be line-based.

## FACT

| # | Statement | Citation |
|---|---|---|
| F1 | The service calls PayEx over HTTPS. | ops/incidents/INC-2041/README.md:30 |
| F2 | Release 2.14.0 (commit 7c41ab9, previous 2.13.4) "adds the PayEx submission call to the approval path". | ops/incidents/INC-2041/deploy-diff.patch:1,5-7 |
| F3 | In 2.14.0, `Approve` becomes async. It calls `_approvals.Approve(id, user)` first, then `await _payEx.SubmitAsync(invoice)`, then returns 200 with the receipt. The call is synchronous inside the HTTP request. | deploy-diff.patch:79-89 |
| F4 | Submission is `POST /v2/payments` with a payload of invoice Id, Amount and CustomerName. Auth is an `X-Api-Key` header. | deploy-diff.patch:52,50,66-69 |
| F5 | 2.14.0 changes `PayExClient.SubmitAsync` to build a new `new HttpClient{...}` on every call. It no longer takes an injected `HttpClient`. | deploy-diff.patch:46-52 (removed injected field at :30,37) |
| F6 | 2.14.0 removes the typed `AddHttpClient<IPayExClient,PayExClient>` registration. That registration had set `client.Timeout = 10 seconds`. `PayExClient` is now registered as a singleton. | deploy-diff.patch:114-119 |
| F7 | On success, `EnsureSuccessStatusCode()` is called, then the receipt is read. If the receipt is empty, an `InvalidOperationException` is thrown. Success is logged as "Submitted invoice {InvoiceId} to PayEx, reference {Reference}". | deploy-diff.patch:53-61 |
| F8 | `EnsureSuccessStatusCode` is retained. | deploy-diff.patch:53 |
| F9 | `appsettings.Production.json` has `"PayEx": { "BaseUrl": "https://api.payex.example", "Timeout": "00:00:10" }`. The diff shows no code that reads `Timeout`. The diff has only the client code shown. | deploy-diff.patch:136; client code at :46-52 |
| F10 | The diff contains no retry, backoff, circuit-breaker or idempotency-key code in the PayEx client or controller. | deploy-diff.patch:18-91 |
| F11 | PayEx failure log (a): `SocketException (10048): Only one usage of each socket address is normally permitted at PayExClient.SubmitAsync(invoice=...)`. First instance is INV-41872 at 10:19:15.978Z, on web-01. It recurs on web-01, web-02 and web-03. grep counted 81 matching lines. | ops/incidents/INC-2041/app-logs.txt:157, 171, 180, 185 |
| F12 | PayEx failure log (b): `TaskCanceledException: ... configured HttpClient.Timeout of 100 seconds elapsing at PayExClient.SubmitAsync(...)`. First instance is INV-41786 at 10:23:23Z. grep counted 25 matching lines. | app-logs.txt:179, 184, 242, 462-470 |
| F13 | Approve requests returning `status=500` log WARN with elapsed_ms of roughly 11.9 s to 25.9 s. grep counted 24 such lines. First is INV-41873 at 10:13:14Z, 14560 ms. | app-logs.txt:129, 140, 161, 167, 193, 217, 457, 471 |
| F14 | Before 10:13Z all logged approvals are 200. Latency grows from about 50-120 ms at 09:40-10:02 to 1-5 s by 10:17-10:35. | app-logs.txt:7-81 (early); 144-150, 244-252 (later) |
| F15 | The metrics file shows `outbound_connections` rising from about 55-70 (09:40-09:54) to about 330-400 from 09:55. It then climbs to 1,000+ by 10:14, 2,000+ by 10:27 and about 2,900 at 10:39. `http_5xx` is 0 until 10:04 and reaches 44 at 10:39. p95 latency was 111-148 ms before 09:55 and 5-18 s later. | ops/incidents/INC-2041/metrics.csv rows 2-16 (baseline), 17 (09:55), 36 (10:14), 49 (10:27), 61 (10:39), 66 (10:44) |
| F16 | The traffic step (requests_per_min about 60 to about 350) begins at 09:55Z, before the 09:58 deploy. The log also records "Approval volume for the last 5 minutes: 384 (7-day average for this window: 96)". | metrics.csv row 17; app-logs.txt:79; deploy at :70-71 |
| F17 | No PayEx success line ("Submitted invoice ... reference") appears anywhere in INC-2041. In the lines read plus grep, no `[PayEx]` or retry log category appears. | grep over ops/incidents/ returned only deploy-diff.patch:60 |
| F18 | PayEx status page showed all systems operational. It was checked at the time of the alert and again at 10:44Z. The README states PayEx reported no incident that day. | ops/incidents/INC-2041/alert.md:18, 24; README.md:30-31 |
| F19 | Restarting web-02 at 10:41Z reduced the error rate for about 3 minutes, then it returned. No rollback was done as of the 11:14Z export. | alert.md:22-23, 27-28 |
| F20 | The service runs 3 instances behind a load balancer. | INC-2041/README.md:32 |
| F21 | Retry-related changes are named only in titles. "2.14.3, 2026-01-16, commit 3f82ad1: Retry policy for the PayEx client, pooled handler". The PayEx API key was rotated 2026-01-23. | ops/incidents/INC-2047/recent-changes.md:7, 33 |
| F22 | The pipeline's run-timings.csv records a branch `feature/payex-retry`, as a pull_request run on 2026-01-30 with conclusion success. That is all it holds about retries. The CI yml has no PayEx or retry step. | ops/pipeline/run-timings.csv rows 266-284; ops/pipeline/ci-pipeline.yml:1-106 |
| F23 | The same invoice ID appears in multiple approve requests, in some cases with a 500 and a 200. INV-41873: 200 at 09:43:21, 500 at 10:13:14. INV-41384: 200 at 10:08:42, 500 at 10:15:50. INV-41360: 500 at 10:21:52, 200 at 10:27:01. INV-41988: 500 at 10:21:29, 200 at 10:24:11. INV-41711: 200 at 10:30:24, 500 at 10:30:34. | app-logs.txt:19 and 129; 113 and 140; 169 and 201; 167 and 183; 215 and 217 |
| F24 | Repeated approve calls on one invoice also occur before the 09:58 deploy, when no PayEx call existed. Examples: INV-41639 at 09:41:50 and 09:51:24; INV-41956 at 09:54:30 and 10:03:08. INV-41521 also repeats later, at 10:04:08 and 10:10:47. | app-logs.txt:12 and 48; 57 and 92; 97 and 119 |
| F25 | INC-2047 is about internal notifications, not PayEx. 2.15.1 changed the eventType from `InvoiceApproved` to `invoice.approved`. The `notification-worker` subscription rule filters on `InvoiceApproved`. The worker shows 0 processed since 2026-01-27. 54 messages sit active on `audit-archive`. All subscriptions show 0 dead-letter. No ERROR or WARN entries were logged. | INC-2047/publisher-logs.txt:6-30, 32; servicebus-status.txt:13-17, 19-31; worker-logs.txt:17-21, 26; recent-changes.md:15-26 |
| F26 | The approval request returned 200 and the audit trail was complete in INC-2047. Finance had not been told how many notifications are affected, because nobody had counted yet. | INC-2047/alert.md:22-24, 31-32 |
| F27 | The published messages carry a unique `messageId` and an eventType. | INC-2047/publisher-logs.txt:6-30 |

## INFERENCE

| # | Statement | Based on |
|---|---|---|
| I1 | In the 2.14.0 code shown, the invoice is approved in the domain service before the PayEx call. A PayEx failure therefore throws after approval state has changed. The 500 would not undo that approval, unless the repository or service rolls back, and nothing in the diff does. | F3 |
| I2 | The 100 s timeout in the log fits the 2.14.0 client creating a bare `new HttpClient`, which has no timeout set. The earlier 10 s limit was configured in the removed registration. `appsettings` "Timeout" is not wired to the new client in the shown diff. | F6, F9, F12 |
| I3 | The new-HttpClient-per-call pattern and the growth in outbound connections are consistent with each other, as is the SocketException 10048 on `SubmitAsync`. This is a correlation. The evidence does not state a cause. | F5, F11, F15 |
| I4 | The 500s taking 12-26 s while the logged timeout is 100 s means the two do not map one-to-one. Some 500s may come from a path other than the 100 s timeout. Which PayEx failure produced each 500 is not logged. | F12, F13 |
| I5 | The 10:19 and 10:23 PayEx errors are logged under category `[Notifications]`, with no linked request ID. Matching an error to a specific approve response needs a join on invoice ID, and not every errored invoice has a matching 500 in the visible log. For example, INV-41872 and INV-41786 have no 500 line in the visible range. | F11-F13 |
| I6 | The traffic step starting at 09:55, before the 09:58 deploy, means load rose independently of the release. Whether the deploy and the load jointly caused the failures is not determinable from the evidence. | F15, F16 |
| I7 | Users appear to resubmit approvals on the same invoice after a 500, for example INV-41360 and INV-41988. A re-approve may call `SubmitAsync` again for an already-approved invoice. That would be a duplicate-risk path. The evidence does not show a second PayEx call or a duplicate. | F23, I1, F10 |
| I8 | For retries, 2.14.0 has no retry. A retry policy was added later in 2.14.3, and a `feature/payex-retry` PR exists on 2026-01-30. The current configuration is not visible in the evidence. | F10, F21, F22 |
| I9 | For losses, INC-2047 shows missed internal notifications caused by a filter mismatch, but nothing about payments to PayEx. This is not evidence of lost PayEx submissions. | F25, F26 |

## UNKNOWN

| # | Statement | Why unknown |
|---|---|---|
| U1 | What PayEx returns on success (status codes, body, `Reference` format, latency). | No success line or PayEx response sample is in the evidence. F7 names only the shape the client expects. |
| U2 | What PayEx returns on failure, such as 4xx/5xx codes or a body. | Only client-side exceptions are logged (F11, F12). |
| U3 | PayEx timeout behaviour, i.e. whether a timed-out request was processed by PayEx. | No PayEx-side record exists. A client-side cancel is not evidence of PayEx's outcome. |
| U4 | Whether PayEx supports or requires an idempotency key, or deduplicates on invoice Id. | Not in payload (F4), headers or docs. Cannot be filled from general knowledge. |
| U5 | Retry configuration in production: count, backoff, which errors, any idempotency guard, and whether 2.14.3 changed submission behaviour. | The 2.14.3 diff and the config are absent. Only the title exists (F21). |
| U6 | Whether duplicate payments or submissions to PayEx occurred. | No PayEx-side ledger or reconciliation exists. App logs show repeated approves (F23, F24) but no receipt or reference. |
| U7 | Whether any approved invoice was never submitted to PayEx (loss). | Per I1, an approval can persist while the submit fails. No reconciliation query or count exists. 24 500s and 106 PayEx errors were counted by grep. They were not tied to the number of approved-but-unsubmitted invoices. |
| U8 | Whether 500s come from PayEx errors, socket exhaustion, or other causes. | Not logged per request (I4, I5). |
| U9 | How the system recovers from a failed submit: any outbox, queue or reconciliation job for PayEx. | The diff shows none (F10). Other files are silent. |
| U10 | The final outcome of INC-2041: root cause, rollback, recovery. | The export ends 11:10Z with the release still live (alert.md:27-28). |
| U11 | The log lines in app-logs.txt 274-454 beyond what grep targeted. | Read only via pattern search. Unmatched lines of an unforeseen kind could exist. |
| U12 | PayEx submission has any connection to the Service Bus path in INC-2047. | Neither pack links them. |

Out of scope, not analysed: ops/evals/cases/case-11.diff contains a `PayExSubmitter` with a "PayEx gives up after 30 seconds" comment and a retry log line. It is eval material, not incident evidence, and it is outside the requested scope.

Single most valuable extra evidence: a PayEx-side transaction ledger or reconciliation export for 2026-01-14 09:58Z-11:10Z, keyed by invoice ID and status (reference, count, timestamp). Compared with the 2.14.0 approve log, it would answer U1, U3, U6 and U7 directly.

Files read: ops/README.md; ops/incidents/INC-2041/{README.md,alert.md,app-logs.txt,deploy-diff.patch,metrics.csv}; ops/incidents/INC-2047/{README.md,alert.md,publisher-logs.txt,recent-changes.md,servicebus-status.txt,worker-logs.txt}; ops/pipeline/{ci-pipeline.yml,run-timings.csv}.

---

## Open questions for the ADR

The exactly-once decision depends on these UNKNOWNs. The evidence above cannot answer them, so the ADR must either resolve them with PayEx or design around them.

1. **Idempotency support (U4).** Does PayEx accept an idempotency key or deduplicate on invoice Id? This decides whether exactly-once can be delegated to PayEx or must be built on our side.
2. **Timeout outcome (U3).** When a request times out client-side, did PayEx process it? Without this, a retry after timeout cannot be proven safe.
3. **Success and failure contract (U1, U2).** Which status codes and bodies signal success, definitive failure and ambiguous failure? Retry rules depend on this split.
4. **Current retry behaviour (U5).** What does the retry policy added in 2.14.3 (and `feature/payex-retry`) do in production, and does it carry any idempotency guard?
5. **Duplicates observed (U6).** Did duplicate PayEx submissions happen? A PayEx-side ledger or reconciliation export for the incident window is needed. Repeated approve calls (F23, F24) show the risk path but not an actual duplicate.
6. **Losses observed (U7, U9).** Were any approved invoices never submitted? The 2.14.0 code approves before submitting (I1) and has no outbox, queue or reconciliation job, so a loss path exists. Its size is unknown.
7. **Cause of the 500s (U8).** Were they PayEx errors, socket exhaustion or something else? This determines whether failure handling is the real problem or the client lifecycle is.
8. **Re-approve behaviour (I7).** Does approving an already-approved invoice call `SubmitAsync` again? Needs a check against the code and the target design. This is the main duplicate path.
