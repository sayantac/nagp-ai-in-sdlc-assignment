# Inferred items and corrections

## 1. Inferred during the scoped as-built run (no citation found)

| # | What the agent suspected | Why | Verdict (human) | Correction |
|---|---|---|---|---|
| 1 | Tests, e2e and CI exist (xUnit with FakeInvoiceRepository, Playwright page objects) | Subagent did not open backend/tests, e2e/ or .github/workflows; matches naming conventions only | Confirmed | Exist: `backend/tests/InvoiceApp.Tests/ApprovalServiceTests.cs`, `FakeInvoiceRepository.cs`; `e2e/` (Playwright config, pages, tests); `.github/workflows/ci.yml`. Out of scope for the runtime diagrams, so not drawn. |
| 2 | Demo user roles and passwords | Seen only in grep output (appsettings.json:9, UserSession.cs:12), full content not read | Confirmed | `appsettings.json:9-12` defines two users: `demo.approver` (Approver) and `demo.admin` (Admin), bound to `DemoUsersOptions` (`UserSession.cs`). Only two roles exist. |
| 3 | Invoice defaults, InvoiceStatus values and DiscountCalculator use | Files not read; DiscountCalculator not referenced in the traced approval path | Confirmed | `Invoice.cs`: `Status = Draft`, `CreatedAt = UtcNow`. `InvoiceStatus`: Draft, PendingApproval, Approved, Rejected. `DiscountCalculator` is referenced nowhere in the app or tests: unused code, correctly not drawn. |
| 4 | Sessions never expire | SessionStore has no TTL code in the files read; absence not confirmed across the project | Confirmed | `SessionStore.cs` is an in-memory `ConcurrentDictionary` with no expiry; sessions are removed only on logout (`AuthController.cs:44`) and lost on restart. |
| 5 | Further access rules on GET, create and submit beyond sign-in | Only Delete carries [RequireRole] in InvoicesController.cs:73; other rules not confirmed | Confirmed | GET, create and submit need only a session (`SessionAuthMiddleware`). Role checks: Delete is Admin-only (`InvoicesController.cs:73`); approve and reject are Approver or Admin (`ApprovalsController.cs:9`). Any signed-in user can create and submit. |
| 6 | No database, message topic or payment provider in code | None found in the files read; InvoiceApp.Api.csproj not read, so an unused package reference is not ruled out | Confirmed | `InvoiceApp.Api.csproj` has only a `ProjectReference` to Domain: no packages, so no database, messaging or HTTP client. |

## 2. Present in the unscoped run, absent from the code

These items come from the agent reading planning documents (`ops/`, `docs/`, READMEs) as if they described the running system.

| # | Element or claim | Came from | Correction (human) |
|---|---|---|---|

## 3. Other corrections made to agent output

| # | What was wrong | How it was caught | Log id |
|---|---|---|---|

## 4. Observations about the as-built code (not drawn)

These are read from the code by the cartographer subagent, and I re-read the cited lines. They are behaviours, not elements or edges, so they are not in the diagrams or `citations.md`.

| # | Observation | File and line |
|---|---|---|
| 1 | Nothing stops the approver being the submitter. `ApprovalService.Approve(invoiceId, approver)` only checks that the invoice is pending, then records the approver's name. `Submit` takes no user at all, and `Invoice` has no field for who submitted it, so there is nothing to compare against. | `backend/src/InvoiceApp.Domain/ApprovalService.cs:16` (`Submit`), `:31-41` (`Approve`); `backend/src/InvoiceApp.Domain/Invoice.cs:5-12` (no submitter field) |
| 2 | The repository mutates the object it hands out. `GetById` returns the stored `Invoice` instance, `ApprovalService` changes its fields in place, and `Update` then writes the same instance back. The status change is visible to anyone holding the reference before `Update` runs, and `Update` does not make the change atomic. The `lock` covers only the list operations. `GetAll` copies the list but returns the same `Invoice` objects. | `backend/src/InvoiceApp.Api/InMemoryInvoiceRepository.cs:27` (`GetById`), `:22` (`GetAll`), `:50-56` (`Update`); `backend/src/InvoiceApp.Domain/ApprovalService.cs:36-39` (fields set, then `Update`) |

Checked: `ApprovalsController.cs:22-23` passes only the signed-in `Username` as the approver, with no submitter comparison, and any signed-in user, including an Approver, can submit (section 1, item 5). Observation 1 is confirmed. Observation 2 depends on `InMemoryInvoiceRepository` being registered as a singleton (`Program.cs:14`) and `ApprovalService` as scoped (`Program.cs:15`), as recorded in citations E13 and E14.
