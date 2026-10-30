# Independent cross-check of the eval answer key

Reviewer: Claude Code (claude-sonnet-5-5), reading `ops/evals/cases/case-01.diff` to `case-10.diff` and `ops/evals/README.md`. `submission/04-evals/answer-key.csv` was **not opened** before this file was written. Line numbers are new-file line numbers computed from each hunk header, so they hold only for the lines the diff shows. I cannot see unchanged code outside the hunks.

Review prompt used (from the README): find defects; give file, line, what goes wrong, confidence; say explicitly if nothing is found.

| Case | Verdict | Confidence |
|---|---|---|
| 01 | defect | high (90%) |
| 02 | defect | very high (98%) |
| 03 | defect | medium (70%) |
| 04 | clean | high (90%) |
| 05 | defect | high (90%) |
| 06 | clean | high (85%) |
| 07 | defect | medium (60%) |
| 08 | defect | high (90%) |
| 09 | defect | high (85%) |
| 10 | defect | very high (97%) |

Totals: 8 defect, 2 clean.

## case-01: defect (90%)

File `backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs`, lines 49-51 (`BulkApprove`).

- `BulkApproveRequest(List<string>? Ids)` is nullable, and `foreach (var id in request.Ids)` (line 49) dereferences it without a check. A body of `{}` or `{"ids": null}` throws `NullReferenceException`, which returns 500. An empty list silently returns 200 with nothing approved.
- Line 51 calls `_approvals.Approve` directly, not through `Handle(...)`. A missing invoice (`KeyNotFoundException`) or a non-pending one (`InvalidOperationException`) escapes as a 500 instead of the 404 or 409 that `ApiControllerBase` maps everywhere else.
- The loop is not atomic. If the third id fails, the first two stay approved, and the caller gets no indication of which ones.

## case-02: defect (98%)

File `backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs`, lines 28 and 32 (`Search`).

SQL injection. `customer` and `status` are concatenated into the SQL string through interpolation (`'%{customer}%'`, `Status = '{status}'`) and sent to `_queries.Run(sql)`. A `customer` of `' OR 1=1 --` returns every invoice, and a stacked statement may run, depending on `Run`. It also bypasses the repository, and the app has no SQL at all today. Secondary: `customer` is non-nullable but not required, so a missing value gives `%%` (everything).

## case-03: defect (70%)

File `backend/src/InvoiceApp.Domain/DiscountCalculator.cs`, lines 16-17 (`Apply`).

The change silently switches money rounding from `MidpointRounding.AwayFromZero` to `ToZero`, and rounds twice (the discount, then the result). The discount is now truncated, so the customer is charged more. Example: amount 33.33, 15%: the discount is 4.9995. Before: 33.33 − 4.9995 = 28.3305, which rounds to 28.33. After: the discount truncates to 4.99, giving 28.34. Totals differ by a cent on common inputs, and nothing in the diff says this is intended. Confidence is medium because this could be a deliberate policy change, but the diff has no test or explanation for it.

## case-04: clean (90%)

`backend/src/InvoiceApp.Domain/ApprovalService.cs`.

A pure rename of `_repository` to `_invoices`. The field, the constructor parameter and assignment, and all four uses are changed (`Submit`, `Approve`, `Reject` and `Find`), so it compiles and behaves the same. Residual risk: I only see the hunks, so a missed use elsewhere in the file would be a compile error that CI catches.

## case-05: defect (90%)

File `backend/src/InvoiceApp.Api/Controllers/InvoicesController.cs`, lines 44-45 (`Delete`).

The new `[HttpDelete("{id}")]` endpoint has no `[RequireRole("Admin")]`. Any signed-in user can delete any invoice. The project rule is that destructive actions are Admin only, and the next endpoint (`Update`, line 17 of the diff) carries `[RequireRole("Admin")]`. Secondary: `_repository.Delete` may not exist (the repository has `Remove`), and the delete result is ignored, so a missing id still returns 204.

## case-06: clean (85%)

`backend/tests/InvoiceApp.Tests/ApprovalServiceTests.cs`.

Three new tests: a whitespace reject reason throws `ArgumentException`, approve records the approver and time, and an unknown invoice throws `KeyNotFoundException`. Each matches the service behaviour: the reason check precedes the lookup, `Approve` sets `DecidedBy` and `DecidedAt`, and `Find` throws `KeyNotFoundException`. They use `FakeInvoiceRepository` as the conventions require. The `InRange` bound is valid. Nitpick only: the `Pending(...)` helper must already exist.

## case-07: defect (60%)

File `backend/src/InvoiceApp.Api/Controllers/ApprovalsController.cs`, lines 34-36 (`Approve`).

The new log line destructures the full invoice (`{@Invoice}`) and the whole session object (`{@Session}`) at Information level. Customer names and amounts go into application logs, and a session object is auth state that belongs nowhere near a log sink; if it ever carries a token, the token is logged. Confidence is medium: in this repository `UserSession` holds only username and role, so the session risk depends on what `CurrentUser` returns here. The invoice data is a smaller concern. `_logger` also has to exist on the controller.

## case-08: defect (90%)

File `backend/src/InvoiceApp.Api/InMemoryInvoiceRepository.cs`, line 9 (field) and lines 19-24 (`Add`).

`ConcurrentDictionary` is replaced by a plain `Dictionary` in a repository that is shared across requests (a singleton). Concurrent writes can corrupt the dictionary, and reads during a write can throw or loop. `Add` is also now check-then-set (`ContainsKey`, then `_invoices[...] =`), so two threads with the same id can both pass the check and one silently overwrites the other, where `TryAdd` was atomic.

## case-09: defect (85%)

File `README.md`, lines 21-25.

The new text is wrong about the code. "Sign out and sign in again" does not reset the sample data: sign-in and sign-out only create and remove a session in `SessionStore`, and the invoices live in a singleton `InMemoryInvoiceRepository` that is seeded once at startup. The statement that the accounts "exist only in the in-memory store" is also wrong: demo users come from `appsettings.json`, not the repository. The `appsettings.json` change in the same diff (`Microsoft.AspNetCore` log level to Warning) is harmless.

## case-10: defect (97%)

File `backend/src/InvoiceApp.Api/Controllers/ApiControllerBase.cs`, lines 35-38.

The new `catch (Exception)` returns `Ok(new { status = "completed" })`. Any unexpected failure (null reference, a repository error, a timeout) now reports success to the caller, the exception is swallowed with no log, and the 500 that would trigger alerts disappears. A failed approval looks completed.
